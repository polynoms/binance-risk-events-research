#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW_KLINES = ROOT / "data" / "raw" / "klines"
DOCS = ROOT / "docs"
COST_BPS = [20, 50, 100, 200, 500]


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def load_current_futures_exchange_info() -> tuple[dict[str, dict[str, Any]], str]:
    path = RAW_KLINES / "futures_exchange_info.json"
    if not path.exists():
        return {}, ""
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}, ""
    snapshot_time = ""
    if data.get("serverTime"):
        snapshot_time = iso(pd.to_datetime(int(data["serverTime"]), unit="ms", utc=True))
    symbols = {str(item.get("symbol")): item for item in data.get("symbols", []) if item.get("symbol")}
    return symbols, snapshot_time


def iso(ts: pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100 * float(value):.1f}%"


def profit_factor(returns: pd.Series) -> float:
    wins = returns[returns > 0].sum()
    losses = -returns[returns < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[tuple[str, str], pd.DataFrame] = {}

    def load_futures(self, pair: str) -> pd.DataFrame:
        if not pair or str(pair) == "nan":
            return pd.DataFrame()
        key = ("futures", str(pair))
        if key in self.cache:
            return self.cache[key]
        folder = RAW_KLINES / "futures" / str(pair)
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
                        "quote_volume": float(item[7]) if len(item) > 7 else np.nan,
                    }
                )
            if rows:
                frames.append(pd.DataFrame(rows))
        if frames:
            df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        else:
            df = pd.DataFrame()
        self.cache[key] = df
        return df


def candidate_futures_symbols(row: pd.Series) -> list[str]:
    symbols: list[str] = []
    token = str(row["token_symbol"])
    for col in ["futures_pair_proxy"]:
        val = row.get(col)
        if pd.notna(val) and str(val).strip() and str(val) != "nan":
            symbols.append(str(val))
    symbols.append(f"{token}USDT")
    symbols.append(f"{token}BUSD")
    out = []
    for sym in symbols:
        if sym not in out:
            out.append(sym)
    return out


def futures_ohlcv_available(store: KlineStore, symbols: list[str], entry_time: pd.Timestamp) -> tuple[bool, str, int]:
    if pd.isna(entry_time):
        return False, "", 0
    start = entry_time - pd.Timedelta(hours=6)
    end = entry_time + pd.Timedelta(hours=6)
    for sym in symbols:
        df = store.load_futures(sym)
        if df.empty:
            continue
        sub = df[(df["open_time"] >= start) & (df["open_time"] <= end)]
        if not sub.empty:
            return True, sym, int(len(sub))
    return False, "", 0


def futures_delisting_inference(events: pd.DataFrame, token: str, entry_time: pd.Timestamp) -> tuple[str, str, str, str]:
    fut = events[
        (events["token_symbol"].astype(str) == token)
        & (events["event_type"].astype(str) == "FUTURES_CONTRACT_DELISTING_ANNOUNCED")
    ].copy()
    if fut.empty or pd.isna(entry_time):
        return "no", "", "", ""
    fut["pub"] = pd.to_datetime(fut["publication_datetime_utc"], utc=True, errors="coerce")
    fut["eff"] = pd.to_datetime(fut["effective_datetime_utc"], utc=True, errors="coerce")
    active_window = fut[(fut["pub"] <= entry_time) & (fut["eff"] >= entry_time)]
    if not active_window.empty:
        r = active_window.sort_values("pub").iloc[-1]
        return "yes", str(r["event_id"]), iso(r["pub"]), iso(r["eff"])
    after_entry = fut[fut["pub"] > entry_time]
    if not after_entry.empty:
        r = after_entry.sort_values("pub").iloc[0]
        return "weak_after_entry_announcement", str(r["event_id"]), iso(r["pub"]), iso(r["eff"])
    before_entry = fut[fut["eff"] < entry_time]
    if not before_entry.empty:
        r = before_entry.sort_values("eff").iloc[-1]
        return "delisted_before_entry", str(r["event_id"]), iso(r["pub"]), iso(r["eff"])
    return "no", "", "", ""


def cache_presence(symbols: list[str]) -> str:
    present = [s for s in symbols if (RAW_KLINES / "futures" / s).exists()]
    return ",".join(present)


def funding_or_oi_cache_available(symbols: list[str], kind: str) -> tuple[str, str]:
    patterns = {
        "funding": ["*funding*", "*fundingRate*"],
        "open_interest": ["*open*interest*", "*openInterest*", "*oi*"],
    }[kind]
    hits: list[str] = []
    for sym in symbols:
        for pattern in patterns:
            hits.extend(str(p) for p in (RAW_KLINES / "futures" / sym).glob(pattern))
            hits.extend(str(p) for p in RAW_KLINES.glob(f"**/{sym}/{pattern}"))
    return ("yes" if hits else "no", ";".join(sorted(set(hits))[:5]))


def build_shortability() -> pd.DataFrame:
    live = read_csv("monitoring_live_feasibility.csv")
    events = read_csv("events.csv")
    lifecycle = read_csv("token_lifecycle.csv")
    store = KlineStore()
    current_futures_info, current_futures_snapshot_utc = load_current_futures_exchange_info()

    lifecycle_small = lifecycle[["token_symbol", "final_outcome", "manual_review_required"]].drop_duplicates("token_symbol")
    live = live.merge(lifecycle_small, on="token_symbol", how="left", suffixes=("", "_lifecycle"))

    rows = []
    for _, row in live.iterrows():
        entry_time = pd.to_datetime(row["entry_time"], utc=True, errors="coerce")
        token = str(row["token_symbol"])
        spot_symbol = str(row["symbol_pair"])
        symbols = candidate_futures_symbols(row)
        current_matches = [sym for sym in symbols if sym in current_futures_info]
        current_status = ";".join(f"{sym}:{current_futures_info[sym].get('status', '')}" for sym in current_matches)
        ohlcv_ok, ohlcv_symbol, ohlcv_rows = futures_ohlcv_available(store, symbols, entry_time)
        announcement_state, announcement_event_id, announcement_pub, announcement_eff = futures_delisting_inference(events, token, entry_time)
        funding_ok, funding_paths = funding_or_oi_cache_available(symbols, "funding")
        oi_ok, oi_paths = funding_or_oi_cache_available(symbols, "open_interest")

        perp_delisted_before_entry = announcement_state == "delisted_before_entry"
        perp_listed_before_entry = ohlcv_ok or announcement_state == "yes"
        had_perp = ohlcv_ok or announcement_state == "yes"
        if ohlcv_ok:
            confidence = "high"
            tier = "high"
            blocker = ""
        elif announcement_state == "yes":
            confidence = "medium"
            tier = "medium"
            blocker = "inferred_from_futures_delisting_announcement_no_local_futures_ohlcv"
        elif perp_delisted_before_entry:
            confidence = "medium"
            tier = "low"
            blocker = "perp_delisted_before_entry"
        else:
            confidence = "unknown"
            tier = "unknown"
            if announcement_state == "weak_after_entry_announcement":
                blocker = "only_later_futures_delisting_announcement_not_proof_at_entry"
            else:
                blocker = "missing_historical_perp_listing_or_borrow_data"

        rows.append(
            {
                "event_id": row["event_id"],
                "token_entity_id": row["token_entity_id"],
                "token_symbol": token,
                "spot_symbol": spot_symbol,
                "futures_symbol_candidate": ",".join(symbols),
                "entry_time": row["entry_time"],
                "event_time": row["event_time"],
                "had_binance_perp_at_entry": "yes" if had_perp else ("no" if perp_delisted_before_entry else "unknown"),
                "perp_listed_before_entry": "yes" if perp_listed_before_entry else "unknown",
                "perp_delisted_before_entry": "yes" if perp_delisted_before_entry else "no",
                "perp_status_confidence": confidence,
                "futures_ohlcv_available_around_entry": "yes" if ohlcv_ok else "no",
                "futures_ohlcv_symbol": ohlcv_symbol,
                "futures_ohlcv_rows_around_entry": ohlcv_rows,
                "funding_available_around_entry": funding_ok,
                "funding_cache_paths": funding_paths,
                "open_interest_available_around_entry": oi_ok,
                "open_interest_cache_paths": oi_paths,
                "futures_delisting_announcement_state": announcement_state,
                "futures_delisting_event_id": announcement_event_id,
                "futures_delisting_publication_utc": announcement_pub,
                "futures_delisting_effective_utc": announcement_eff,
                "futures_cache_symbol_dirs_present": cache_presence(symbols),
                "current_futures_exchangeinfo_snapshot_utc": current_futures_snapshot_utc,
                "current_futures_exchangeinfo_symbol_status": current_status,
                "current_exchangeinfo_used_as_historical_proof": "no",
                "shortability_tier": tier,
                "shortability_blocker": blocker,
                "feasibility_tier": row["feasibility_tier"],
                "low_liquidity_flag": row["low_liquidity_flag"],
                "extreme_first_hour_wick_gap": row["extreme_first_hour_wick_gap"],
                "abnormal_candle_gap": row["abnormal_candle_gap"],
                "quote_volume_24h_around_entry": row["quote_volume_24h_around_entry"],
                "gross_return": row["gross_return"],
                "net_return_20bps": row["net_return_20bps"],
                "net_return_50bps": row["net_return_50bps"],
                "net_return_100bps": row["net_return_100bps"],
                "net_return_200bps": row["net_return_200bps"],
                "net_return_500bps": row["net_return_500bps"],
                "max_adverse_excursion": row["max_adverse_excursion"],
                "max_favorable_excursion": row["max_favorable_excursion"],
                "confidence_tier": row["confidence_tier"],
                "scenario": row["scenario"],
                "final_outcome": row.get("final_outcome", ""),
                "manual_review_required": row.get("manual_review_required", ""),
            }
        )

    out = pd.DataFrame(rows).sort_values(["entry_time", "token_symbol"]).reset_index(drop=True)
    out.to_csv(PROCESSED / "monitoring_shortability.csv", index=False)
    out.to_parquet(PROCESSED / "monitoring_shortability.parquet", index=False)
    return out


def summarize_returns(df: pd.DataFrame) -> pd.DataFrame:
    views = [
        ("confirmed_or_inferred_shortable", df["shortability_tier"].isin(["high", "medium"])),
        ("unknown_shortability", df["shortability_tier"].eq("unknown")),
        ("low_or_blocked_shortability", df["shortability_tier"].eq("low")),
        ("medium_feasibility_plus_confirmed_or_inferred_shortable", df["feasibility_tier"].isin(["high", "medium"]) & df["shortability_tier"].isin(["high", "medium"])),
    ]
    rows = []
    for view, mask in views:
        sub = df[mask].copy()
        for cost in COST_BPS:
            ret = pd.to_numeric(sub[f"net_return_{cost}bps"], errors="coerce").dropna()
            mae = pd.to_numeric(sub["max_adverse_excursion"], errors="coerce")
            mfe = pd.to_numeric(sub["max_favorable_excursion"], errors="coerce")
            rows.append(
                {
                    "view": view,
                    "cost_bps": cost,
                    "n_trades": int(len(ret)),
                    "win_rate": float((ret > 0).mean()) if len(ret) else np.nan,
                    "median_return": float(ret.median()) if len(ret) else np.nan,
                    "average_return": float(ret.mean()) if len(ret) else np.nan,
                    "p25_return": float(ret.quantile(0.25)) if len(ret) else np.nan,
                    "p75_return": float(ret.quantile(0.75)) if len(ret) else np.nan,
                    "worst_trade": float(ret.min()) if len(ret) else np.nan,
                    "best_trade": float(ret.max()) if len(ret) else np.nan,
                    "median_mae": float(mae.median()) if mae.notna().any() else np.nan,
                    "median_mfe": float(mfe.median()) if mfe.notna().any() else np.nan,
                    "profit_factor": profit_factor(ret) if len(ret) else np.nan,
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(PROCESSED / "monitoring_strategy_tradeable_subset_summary.csv", index=False)
    return summary


def write_gap_report(shortability: pd.DataFrame, summary: pd.DataFrame) -> None:
    confirmed = int(shortability["shortability_tier"].eq("high").sum())
    inferred = int(shortability["shortability_tier"].eq("medium").sum())
    unknown = int(shortability["shortability_tier"].eq("unknown").sum())
    low = int(shortability["shortability_tier"].eq("low").sum())
    ohlcv = int(shortability["futures_ohlcv_available_around_entry"].eq("yes").sum())
    funding = int(shortability["funding_available_around_entry"].eq("yes").sum())
    oi = int(shortability["open_interest_available_around_entry"].eq("yes").sum())
    current_snapshot = shortability["current_futures_exchangeinfo_snapshot_utc"].dropna()
    current_snapshot_utc = current_snapshot.iloc[0] if not current_snapshot.empty else ""
    current_matches = int(shortability["current_futures_exchangeinfo_symbol_status"].fillna("").ne("").sum())

    manual_tokens = shortability.loc[
        shortability["shortability_tier"].isin(["unknown", "low"]),
        ["token_symbol", "entry_time", "shortability_blocker", "futures_symbol_candidate", "futures_cache_symbol_dirs_present"],
    ].drop_duplicates()

    t100 = summary[summary["cost_bps"] == 100].copy()
    display = t100.copy()
    for col in ["win_rate", "median_return", "average_return", "p25_return", "p75_return", "worst_trade", "best_trade", "median_mae", "median_mfe"]:
        display[col] = display[col].map(pct)

    report = [
        "# Shortability Data Gaps Report",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: Monitoring Tag candidate `immediate_1h_confirmation + negative_1h_confirmation` only.",
        "",
        "Current Binance futures `exchangeInfo` is not used as historical proof. It is insufficient for determining whether a contract existed at a 2023-2026 entry timestamp.",
        "",
        "## Coverage",
        "",
        f"- Candidate trades: {len(shortability)}",
        f"- Confirmed Binance perp availability from local futures OHLCV around entry: {confirmed}",
        f"- Inferred availability from futures delisting announcement active window: {inferred}",
        f"- Unknown shortability: {unknown}",
        f"- Low/blocked shortability: {low}",
        f"- Futures OHLCV around entry available: {ohlcv}",
        f"- Funding cache around entry available: {funding}",
        f"- Open interest cache around entry available: {oi}",
        f"- Current futures exchangeInfo snapshot UTC: {current_snapshot_utc or 'missing'}",
        f"- Candidate symbols present in current futures exchangeInfo: {current_matches} (not used as historical proof)",
        "",
        "## Tradeable Subset Metrics at 100 bps",
        "",
        display.to_markdown(index=False),
        "",
        "## Main Gap",
        "",
        "For most candidates, the historical market signal can be measured from spot OHLCV, but short execution cannot be proven because we lack historical borrow availability and/or historical perp listing metadata at entry time.",
        "",
        "## Manual Exchange Lookup Queue",
        "",
        manual_tokens.head(80).to_markdown(index=False),
        "",
        "## Required Next Data",
        "",
        "- Historical Binance USD-M futures exchangeInfo snapshots or symbol listing/delisting history.",
        "- Funding rate history and open interest history around each entry.",
        "- Spot margin borrow availability and borrow fee history by asset.",
        "- Historical bid/ask spread or order book snapshots to convert volume proxy into executable size assumptions.",
        "",
    ]
    (DOCS / "shortability_data_gaps_report.md").write_text("\n".join(report))


def main() -> None:
    shortability = build_shortability()
    summary = summarize_returns(shortability)
    write_gap_report(shortability, summary)
    print(
        {
            "rows": int(len(shortability)),
            "confirmed_high": int(shortability["shortability_tier"].eq("high").sum()),
            "inferred_medium": int(shortability["shortability_tier"].eq("medium").sum()),
            "unknown": int(shortability["shortability_tier"].eq("unknown").sum()),
            "low": int(shortability["shortability_tier"].eq("low").sum()),
            "output_csv": str(PROCESSED / "monitoring_shortability.csv"),
            "summary_csv": str(PROCESSED / "monitoring_strategy_tradeable_subset_summary.csv"),
            "report": str(DOCS / "shortability_data_gaps_report.md"),
        }
    )


if __name__ == "__main__":
    main()
