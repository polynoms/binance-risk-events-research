#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW_KLINES = ROOT / "data" / "raw" / "klines"
DOCS = ROOT / "docs"

MARGIN_USDT = 100.0
LEVERAGE = 10.0
NOTIONAL_USDT = MARGIN_USDT * LEVERAGE
LIQUIDATION_MOVE = 1 / LEVERAGE
HOLD_WINDOWS = {
    "1d": ("+24h", pd.Timedelta(days=1)),
    "3d": ("+3d", pd.Timedelta(days=3)),
    "7d": ("+7d", pd.Timedelta(days=7)),
    "14d": ("+14d", pd.Timedelta(days=14)),
    "30d": ("+30d", pd.Timedelta(days=30)),
}


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[str, pd.DataFrame] = {}

    def load_spot_1h(self, pair: str) -> pd.DataFrame:
        if not pair or str(pair) == "nan":
            return pd.DataFrame()
        pair = str(pair)
        if pair in self.cache:
            return self.cache[pair]
        folder = RAW_KLINES / "spot" / pair
        frames = []
        for path in sorted(folder.glob("1h_*_paged.json")):
            try:
                data = json.loads(path.read_text())
            except Exception:
                continue
            rows = []
            for item in data or []:
                if len(item) < 7:
                    continue
                rows.append(
                    {
                        "open_time": pd.to_datetime(int(item[0]), unit="ms", utc=True),
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4]),
                        "volume": float(item[5]),
                        "close_time": pd.to_datetime(int(item[6]), unit="ms", utc=True),
                    }
                )
            if rows:
                frames.append(pd.DataFrame(rows))
        if frames:
            df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        else:
            df = pd.DataFrame()
        self.cache[pair] = df
        return df


def short_return(entry: float, exit_price: float) -> float:
    if entry <= 0 or exit_price <= 0:
        return np.nan
    return entry / exit_price - 1


def path_metrics(store: KlineStore, pair: str, event_time: pd.Timestamp, entry_price: float, horizon: pd.Timedelta) -> dict[str, Any]:
    df = store.load_spot_1h(pair)
    if df.empty or pd.isna(event_time) or entry_price <= 0:
        return {
            "path_available": "no",
            "max_adverse_return_path": np.nan,
            "max_favorable_return_path": np.nan,
            "liquidation_touched_approx": "unknown",
            "liquidation_time_utc": "",
        }
    end = event_time + horizon
    path = df[(df["open_time"] >= event_time) & (df["open_time"] <= end)].copy()
    if path.empty:
        return {
            "path_available": "no",
            "max_adverse_return_path": np.nan,
            "max_favorable_return_path": np.nan,
            "liquidation_touched_approx": "unknown",
            "liquidation_time_utc": "",
        }
    adverse = float(path["high"].max() / entry_price - 1)
    favorable = float(entry_price / path["low"].min() - 1) if float(path["low"].min()) > 0 else np.nan
    liq_rows = path[path["high"] >= entry_price * (1 + LIQUIDATION_MOVE)]
    liq = not liq_rows.empty
    liq_time = pd.Timestamp(liq_rows.iloc[0]["close_time"]).strftime("%Y-%m-%dT%H:%M:%SZ") if liq else ""
    return {
        "path_available": "yes",
        "max_adverse_return_path": adverse,
        "max_favorable_return_path": favorable,
        "liquidation_touched_approx": "yes" if liq else "no",
        "liquidation_time_utc": liq_time,
    }


def build_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    pw = read_csv("price_windows.csv")
    events = read_csv("events.csv")
    lifecycle = read_csv("token_lifecycle.csv")
    store = KlineStore()

    mt = pw[pw["event_type"].eq("MONITORING_TAG_ADDED") & pw["window"].isin([v[0] for v in HOLD_WINDOWS.values()])].copy()
    meta_cols = [
        "event_id",
        "token_symbol",
        "announcement_title",
        "announcement_url",
        "publication_datetime_utc",
        "manual_review_required",
        "confidence_score",
    ]
    mt = mt.merge(events[meta_cols].drop_duplicates("event_id"), on=["event_id", "token_symbol"], how="left", suffixes=("", "_event"))
    mt = mt.merge(
        lifecycle[["token_symbol", "final_outcome", "was_delisted_after_tag", "delisting_announcement_datetime_utc", "effective_delisting_datetime_utc"]].drop_duplicates("token_symbol"),
        on="token_symbol",
        how="left",
    )
    mt["publication_datetime_utc"] = mt["publication_datetime_utc"].fillna(mt["publication_datetime_utc_event"])
    mt["event_dt"] = pd.to_datetime(mt["publication_datetime_utc"], utc=True, errors="coerce")
    mt["cluster_date_utc"] = mt["event_dt"].dt.strftime("%Y-%m-%d")
    mt["cluster_id"] = mt["cluster_date_utc"]

    rows = []
    for _, row in mt.iterrows():
        window_label = None
        horizon = None
        for label, (window, td) in HOLD_WINDOWS.items():
            if row["window"] == window:
                window_label = label
                horizon = td
                break
        if window_label is None:
            continue
        entry_price = pd.to_numeric(row["event_price"], errors="coerce")
        exit_price = pd.to_numeric(row["window_price"], errors="coerce")
        raw_return = pd.to_numeric(row["raw_return"], errors="coerce")
        missing = str(row.get("missing_price_flag", "no")) == "yes" or pd.isna(entry_price) or pd.isna(exit_price)
        sr = short_return(float(entry_price), float(exit_price)) if not missing else np.nan
        pnl_no_liq = NOTIONAL_USDT * sr if pd.notna(sr) else np.nan
        pm = path_metrics(store, str(row["symbol_pair"]), row["event_dt"], float(entry_price) if pd.notna(entry_price) else np.nan, horizon)
        if pm["liquidation_touched_approx"] == "yes":
            pnl_liq = -MARGIN_USDT
            roi_liq = -1.0
        elif pd.notna(pnl_no_liq):
            pnl_liq = max(pnl_no_liq, -MARGIN_USDT)
            roi_liq = pnl_liq / MARGIN_USDT
        else:
            pnl_liq = np.nan
            roi_liq = np.nan
        rows.append(
            {
                "cluster_id": row["cluster_id"],
                "cluster_date_utc": row["cluster_date_utc"],
                "announcement_title": row.get("announcement_title", ""),
                "announcement_url": row.get("announcement_url", ""),
                "event_id": row["event_id"],
                "token_symbol": row["token_symbol"],
                "symbol_pair": row["symbol_pair"],
                "final_outcome": row.get("final_outcome", ""),
                "was_delisted_after_tag": row.get("was_delisted_after_tag", ""),
                "publication_datetime_utc": row["publication_datetime_utc"],
                "hold_window": window_label,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "spot_raw_return": raw_return,
                "short_return_no_liq": sr,
                "margin_usdt": MARGIN_USDT,
                "leverage": LEVERAGE,
                "notional_usdt": NOTIONAL_USDT,
                "pnl_usdt_no_liq": pnl_no_liq,
                "roi_on_margin_no_liq": pnl_no_liq / MARGIN_USDT if pd.notna(pnl_no_liq) else np.nan,
                "pnl_usdt_liq_cap": pnl_liq,
                "roi_on_margin_liq_cap": roi_liq,
                "liquidation_threshold_adverse_move": LIQUIDATION_MOVE,
                **pm,
                "price_source": row.get("price_source", ""),
                "window_price_source": row.get("window_price_source", ""),
                "missing_price_flag": row.get("missing_price_flag", ""),
                "missing_price_reason": row.get("missing_price_reason", ""),
                "manual_review_required": row.get("manual_review_required", ""),
                "confidence_score": row.get("confidence_score", ""),
            }
        )
    token = pd.DataFrame(rows)
    token.to_csv(PROCESSED / "monitoring_tag_cluster_token_whatif.csv", index=False)
    token.to_parquet(PROCESSED / "monitoring_tag_cluster_token_whatif.parquet", index=False)

    summary_rows = []
    for (cluster_id, hold), grp in token.groupby(["cluster_id", "hold_window"], dropna=False):
        valid = grp[grp["missing_price_flag"].astype(str).ne("yes") & grp["pnl_usdt_liq_cap"].notna()].copy()
        summary_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_date_utc": grp["cluster_date_utc"].iloc[0],
                "hold_window": hold,
                "tokens_in_cluster": int(grp["token_symbol"].nunique()),
                "valid_token_results": int(len(valid)),
                "missing_token_results": int(len(grp) - len(valid)),
                "liquidation_count_approx": int(valid["liquidation_touched_approx"].eq("yes").sum()),
                "down_tokens_at_exit": int((pd.to_numeric(valid["spot_raw_return"], errors="coerce") < 0).sum()),
                "up_tokens_at_exit": int((pd.to_numeric(valid["spot_raw_return"], errors="coerce") > 0).sum()),
                "total_margin_usdt": float(len(valid) * MARGIN_USDT),
                "total_notional_usdt": float(len(valid) * NOTIONAL_USDT),
                "total_pnl_usdt_no_liq": float(pd.to_numeric(valid["pnl_usdt_no_liq"], errors="coerce").sum()),
                "total_pnl_usdt_liq_cap": float(pd.to_numeric(valid["pnl_usdt_liq_cap"], errors="coerce").sum()),
                "roi_on_margin_no_liq": float(pd.to_numeric(valid["pnl_usdt_no_liq"], errors="coerce").sum() / (len(valid) * MARGIN_USDT)) if len(valid) else np.nan,
                "roi_on_margin_liq_cap": float(pd.to_numeric(valid["pnl_usdt_liq_cap"], errors="coerce").sum() / (len(valid) * MARGIN_USDT)) if len(valid) else np.nan,
                "median_token_pnl_liq_cap": float(pd.to_numeric(valid["pnl_usdt_liq_cap"], errors="coerce").median()) if len(valid) else np.nan,
                "best_token_pnl_liq_cap": float(pd.to_numeric(valid["pnl_usdt_liq_cap"], errors="coerce").max()) if len(valid) else np.nan,
                "worst_token_pnl_liq_cap": float(pd.to_numeric(valid["pnl_usdt_liq_cap"], errors="coerce").min()) if len(valid) else np.nan,
                "tokens": ",".join(sorted(valid["token_symbol"].astype(str).unique())),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["cluster_date_utc", "hold_window"])
    summary.to_csv(PROCESSED / "monitoring_tag_cluster_summary_whatif.csv", index=False)
    summary.to_parquet(PROCESSED / "monitoring_tag_cluster_summary_whatif.parquet", index=False)
    return token, summary


def write_report(token: pd.DataFrame, summary: pd.DataFrame) -> None:
    overall = summary.groupby("hold_window").agg(
        clusters=("cluster_id", "nunique"),
        valid_token_results=("valid_token_results", "sum"),
        liquidations=("liquidation_count_approx", "sum"),
        total_pnl_liq_cap=("total_pnl_usdt_liq_cap", "sum"),
        total_margin=("total_margin_usdt", "sum"),
        median_cluster_roi=("roi_on_margin_liq_cap", "median"),
    ).reset_index()
    overall["overall_roi_on_margin_liq_cap"] = overall["total_pnl_liq_cap"] / overall["total_margin"]
    report = [
        "# Monitoring Tag Cluster What-If",
        "",
        "Assumption: short every token in each same-day Monitoring Tag cluster immediately at announcement/event price.",
        "",
        "- Margin per token: `100 USDT`.",
        "- Leverage: `10x`.",
        "- Notional per token: `1000 USDT`.",
        "- Liquidation approximation: if post-entry 1h path trades `+10%` against the short, PnL is capped at `-100 USDT`.",
        "- Fees, funding, borrow, slippage, and real liquidation maintenance margin are not included.",
        "",
        "## Overall By Hold Window",
        "",
        overall.to_markdown(index=False),
        "",
        "## Outputs",
        "",
        "- `data/processed/monitoring_tag_cluster_token_whatif.csv`",
        "- `data/processed/monitoring_tag_cluster_summary_whatif.csv`",
    ]
    (DOCS / "monitoring_tag_cluster_whatif_report.md").write_text("\n".join(report))


def main() -> None:
    token, summary = build_outputs()
    write_report(token, summary)
    print(
        {
            "token_rows": int(len(token)),
            "summary_rows": int(len(summary)),
            "clusters": int(token["cluster_id"].nunique()),
            "output_token": str(PROCESSED / "monitoring_tag_cluster_token_whatif.csv"),
            "output_summary": str(PROCESSED / "monitoring_tag_cluster_summary_whatif.csv"),
            "report": str(DOCS / "monitoring_tag_cluster_whatif_report.md"),
        }
    )


if __name__ == "__main__":
    main()
