#!/usr/bin/env python3
"""Cluster basket short backtest for Monitoring Tag announcements with stop/BE rules."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"
RAW_KLINES = ROOT / "data/raw/klines/spot"
DOCS = ROOT / "docs"

MARGIN_USDT = 100.0
LEVERAGE = 10.0
NOTIONAL_USDT = MARGIN_USDT * LEVERAGE
HOLD_WINDOWS = {
    "1h": pd.Timedelta(hours=1),
    "4h": pd.Timedelta(hours=4),
    "12h": pd.Timedelta(hours=12),
    "1d": pd.Timedelta(days=1),
    "3d": pd.Timedelta(days=3),
    "7d": pd.Timedelta(days=7),
    "14d": pd.Timedelta(days=14),
    "30d": pd.Timedelta(days=30),
    "60d": pd.Timedelta(days=60),
    "90d": pd.Timedelta(days=90),
}
STOP_MODELS = {
    "no_stop": None,
    "stop_10": 0.10,
    "stop_15": 0.15,
    "stop_20": 0.20,
    "stop_30": 0.30,
    "stop_50": 0.50,
}
BE_TRIGGERS = {
    "no_be": None,
    "be_after_5": 0.05,
    "be_after_10": 0.10,
    "be_after_15": 0.15,
    "be_after_20": 0.20,
}


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[str, pd.DataFrame] = {}

    def load(self, pair: str, interval: str) -> pd.DataFrame:
        if not pair or str(pair) == "nan":
            return pd.DataFrame()
        pair = str(pair)
        cache_key = f"{pair}:{interval}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        folder = RAW_KLINES / pair
        frames = []
        for path in sorted(folder.glob(f"{interval}_*_paged.json")):
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
        self.cache[cache_key] = df
        return df


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def short_return(entry: float, exit_price: float) -> float:
    if entry <= 0 or exit_price <= 0:
        return np.nan
    return entry / exit_price - 1


def pnl_from_short_return(ret: float) -> float:
    return NOTIONAL_USDT * ret if pd.notna(ret) else np.nan


def load_shortable_map() -> dict[str, str]:
    path = PROCESSED / "derivatives_availability.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    statuses: dict[str, str] = {}
    for symbol, grp in df.groupby("token_symbol"):
        confirmed = grp.get("confirmed_binance_perp", pd.Series(dtype=str)).astype(str).str.lower().eq("yes").any()
        inferred = grp.get("inferred_from_futures_klines", pd.Series(dtype=str)).astype(str).str.lower().eq("yes").any()
        no_evidence = grp.get("no_binance_perp_evidence", pd.Series(dtype=str)).astype(str).str.lower().eq("yes").all()
        if confirmed:
            statuses[str(symbol).upper()] = "confirmed"
        elif inferred:
            statuses[str(symbol).upper()] = "inferred"
        elif no_evidence:
            statuses[str(symbol).upper()] = "no_evidence"
        else:
            statuses[str(symbol).upper()] = "unknown"
    return statuses


def monitoring_events(shortable_only: bool) -> pd.DataFrame:
    events = read_csv("events.csv")
    lifecycle = read_csv("token_lifecycle.csv")
    events = events[events["event_type"].eq("MONITORING_TAG_ADDED")].copy()
    events["event_dt"] = pd.to_datetime(events["publication_datetime_utc"], utc=True, errors="coerce")
    events["cluster_date_utc"] = events["event_dt"].dt.strftime("%Y-%m-%d")
    events = events.merge(
        lifecycle[["token_symbol", "final_outcome", "was_delisted_after_tag"]].drop_duplicates("token_symbol"),
        on="token_symbol",
        how="left",
    )
    shortable = load_shortable_map()
    events["shortability_status"] = events["token_symbol"].astype(str).str.upper().map(shortable).fillna("unknown")
    if shortable_only:
        events = events[events["shortability_status"].isin(["confirmed", "inferred"])].copy()
    return events.sort_values(["event_dt", "token_symbol"]).reset_index(drop=True)


def entry_path(store: KlineStore, token_symbol: str, event_time: pd.Timestamp, horizon: pd.Timedelta, interval: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    pair = f"{token_symbol}USDT"
    df = store.load(pair, interval)
    if df.empty or pd.isna(event_time):
        return pd.DataFrame(), {"path_issue": f"missing_{interval}_path", "symbol_pair": pair}
    entry_rows = df[df["open_time"] >= event_time]
    if entry_rows.empty:
        return pd.DataFrame(), {"path_issue": "missing_entry_after_event", "symbol_pair": pair}
    entry = entry_rows.iloc[0]
    end = entry["open_time"] + horizon
    path = df[(df["open_time"] >= entry["open_time"]) & (df["open_time"] <= end)].copy()
    if path.empty:
        return pd.DataFrame(), {"path_issue": "missing_horizon_path", "symbol_pair": pair}
    return path, {
        "path_issue": "",
        "symbol_pair": pair,
        "entry_time": entry["open_time"],
        "entry_price": float(entry["open"]),
        "entry_quote_volume": float(entry.get("quote_volume", np.nan)),
    }


def simulate(path: pd.DataFrame, entry_time: pd.Timestamp, entry_price: float, horizon: pd.Timedelta, stop: float | None, be_trigger: float | None) -> dict[str, Any]:
    stop_price = entry_price * (1 + stop) if stop is not None else math.inf
    be_active = False
    be_time = pd.NaT
    max_adv = 0.0
    max_fav = 0.0
    mfe_time = pd.NaT
    mae_time = pd.NaT
    exit_price = float(path.iloc[-1]["close"])
    exit_time = pd.Timestamp(path.iloc[-1]["close_time"])
    exit_reason = "time_exit"
    stop_triggered = "no"
    be_triggered = "no"
    stop_time = ""
    be_stop_time = ""

    for _, candle in path.iterrows():
        high = float(candle["high"])
        low = float(candle["low"])
        close_time = pd.Timestamp(candle["close_time"])
        adv = high / entry_price - 1
        fav = entry_price / low - 1 if low > 0 else np.nan
        if pd.notna(adv) and adv > max_adv:
            max_adv = adv
            mae_time = close_time
        if pd.notna(fav) and fav > max_fav:
            max_fav = fav
            mfe_time = close_time

        if stop is not None and not be_active and high >= stop_price:
            exit_price = stop_price
            exit_time = close_time
            exit_reason = f"fixed_stop_{int(stop * 100)}"
            stop_triggered = "yes"
            stop_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            break

        if be_trigger is not None and not be_active and low <= entry_price * (1 - be_trigger):
            be_active = True
            be_time = close_time

        if be_active and high >= entry_price:
            exit_price = entry_price
            exit_time = close_time
            exit_reason = f"breakeven_after_{int(be_trigger * 100)}"
            be_triggered = "yes"
            be_stop_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            break

    ret = short_return(entry_price, exit_price)
    return {
        "exit_timestamp_utc": exit_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "holding_period_hours": (exit_time - entry_time).total_seconds() / 3600,
        "short_return": ret,
        "pnl_usdt": pnl_from_short_return(ret),
        "roi_on_margin": pnl_from_short_return(ret) / MARGIN_USDT if pd.notna(ret) else np.nan,
        "max_favorable_excursion": max_fav,
        "max_adverse_excursion": max_adv,
        "time_to_mfe_hours": (mfe_time - entry_time).total_seconds() / 3600 if pd.notna(mfe_time) else np.nan,
        "time_to_mae_hours": (mae_time - entry_time).total_seconds() / 3600 if pd.notna(mae_time) else np.nan,
        "stop_loss_triggered": stop_triggered,
        "time_stop_triggered": stop_time,
        "breakeven_triggered": be_triggered,
        "breakeven_time_utc": pd.Timestamp(be_time).strftime("%Y-%m-%dT%H:%M:%SZ") if pd.notna(be_time) else "",
        "breakeven_stop_time_utc": be_stop_time,
    }


def profit_factor(values: pd.Series) -> float:
    gains = values[values > 0].sum()
    losses = -values[values < 0].sum()
    if losses == 0:
        return np.inf if gains > 0 else np.nan
    return gains / losses


def build(shortable_only: bool, start_cluster: int | None, end_cluster: int | None, interval: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    events = monitoring_events(shortable_only)
    clusters = sorted(events["cluster_date_utc"].dropna().unique())
    if start_cluster is not None or end_cluster is not None:
        clusters = clusters[start_cluster or 0 : end_cluster]
        events = events[events["cluster_date_utc"].isin(clusters)].copy()
    store = KlineStore()
    rows = []
    for _, event in events.iterrows():
        event_time = pd.Timestamp(event["event_dt"])
        for hold, horizon in HOLD_WINDOWS.items():
            path, meta = entry_path(store, str(event["token_symbol"]), event_time, horizon, interval)
            if path.empty:
                for stop_name, stop in STOP_MODELS.items():
                    for be_name, be in BE_TRIGGERS.items():
                        rows.append(
                            {
                                "cluster_id": event["cluster_date_utc"],
                                "cluster_date_utc": event["cluster_date_utc"],
                                "event_id": event["event_id"],
                                "token_symbol": event["token_symbol"],
                                "symbol_pair": meta.get("symbol_pair", ""),
                                "announcement_title": event.get("announcement_title", ""),
                                "announcement_url": event.get("announcement_url", ""),
                                "publication_datetime_utc": event.get("publication_datetime_utc", ""),
                                "hold_window": hold,
                                "price_interval": interval,
                                "stop_model": stop_name,
                                "be_model": be_name,
                                "shortability_status": event.get("shortability_status", ""),
                                "entry_timestamp_utc": "",
                                "entry_price": np.nan,
                                "exit_timestamp_utc": "",
                                "exit_price": np.nan,
                                "exit_reason": "missing_path",
                                "pnl_usdt": np.nan,
                                "roi_on_margin": np.nan,
                                "missing_path_flag": "yes",
                                "path_issue": meta.get("path_issue", ""),
                                "manual_review_required": "yes",
                            }
                        )
                continue
            entry_time = pd.Timestamp(meta["entry_time"])
            entry_price = float(meta["entry_price"])
            for stop_name, stop in STOP_MODELS.items():
                for be_name, be in BE_TRIGGERS.items():
                    # BE without a stop still models a risk-reduction exit after favorable move.
                    result = simulate(path, entry_time, entry_price, horizon, stop, be)
                    rows.append(
                        {
                            "cluster_id": event["cluster_date_utc"],
                            "cluster_date_utc": event["cluster_date_utc"],
                            "event_id": event["event_id"],
                            "token_symbol": event["token_symbol"],
                            "symbol_pair": meta.get("symbol_pair", ""),
                            "announcement_title": event.get("announcement_title", ""),
                            "announcement_url": event.get("announcement_url", ""),
                            "publication_datetime_utc": event.get("publication_datetime_utc", ""),
                            "hold_window": hold,
                            "price_interval": interval,
                            "stop_model": stop_name,
                            "be_model": be_name,
                            "shortability_status": event.get("shortability_status", ""),
                            "entry_timestamp_utc": entry_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "entry_price": entry_price,
                            "entry_quote_volume": meta.get("entry_quote_volume", np.nan),
                            "missing_path_flag": "no",
                            "path_issue": "",
                            "manual_review_required": event.get("manual_review_required", "no"),
                            **result,
                        }
                    )
    token = pd.DataFrame(rows)
    valid = token[token["missing_path_flag"].eq("no") & token["pnl_usdt"].notna()].copy()
    cluster_rows = []
    for keys, grp in valid.groupby(["cluster_id", "cluster_date_utc", "hold_window", "stop_model", "be_model"], dropna=False):
        cluster_id, date, hold, stop_name, be_name = keys
        pnl = pd.to_numeric(grp["pnl_usdt"], errors="coerce")
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_date_utc": date,
                "hold_window": hold,
                "stop_model": stop_name,
                "be_model": be_name,
                "tokens_count": int(grp["token_symbol"].nunique()),
                "total_margin_usdt": float(len(grp) * MARGIN_USDT),
                "total_notional_usdt": float(len(grp) * NOTIONAL_USDT),
                "total_pnl_usdt": float(pnl.sum()),
                "roi_on_margin": float(pnl.sum() / (len(grp) * MARGIN_USDT)) if len(grp) else np.nan,
                "winning_tokens": int((pnl > 0).sum()),
                "losing_tokens": int((pnl < 0).sum()),
                "stopped_tokens": int(grp["stop_loss_triggered"].eq("yes").sum()),
                "breakeven_tokens": int(grp["breakeven_triggered"].eq("yes").sum()),
                "median_token_pnl": float(pnl.median()) if len(pnl) else np.nan,
                "worst_token_pnl": float(pnl.min()) if len(pnl) else np.nan,
                "best_token_pnl": float(pnl.max()) if len(pnl) else np.nan,
                "tokens": ",".join(sorted(grp["token_symbol"].astype(str).unique())),
            }
        )
    cluster = pd.DataFrame(cluster_rows)
    summary_rows = []
    for keys, grp in valid.groupby(["hold_window", "stop_model", "be_model"], dropna=False):
        hold, stop_name, be_name = keys
        pnl = pd.to_numeric(grp["pnl_usdt"], errors="coerce")
        cl = cluster[(cluster["hold_window"].eq(hold)) & (cluster["stop_model"].eq(stop_name)) & (cluster["be_model"].eq(be_name))]
        summary_rows.append(
            {
                "hold_window": hold,
                "stop_model": stop_name,
                "be_model": be_name,
                "token_trades": int(len(grp)),
                "clusters": int(grp["cluster_id"].nunique()),
                "total_margin_usdt": float(len(grp) * MARGIN_USDT),
                "total_pnl_usdt": float(pnl.sum()),
                "roi_on_margin": float(pnl.sum() / (len(grp) * MARGIN_USDT)) if len(grp) else np.nan,
                "token_win_rate": float((pnl > 0).mean()) if len(grp) else np.nan,
                "cluster_win_rate": float((cl["total_pnl_usdt"] > 0).mean()) if len(cl) else np.nan,
                "median_token_pnl": float(pnl.median()) if len(pnl) else np.nan,
                "median_cluster_roi": float(cl["roi_on_margin"].median()) if len(cl) else np.nan,
                "p25_token_pnl": float(pnl.quantile(0.25)) if len(pnl) else np.nan,
                "p75_token_pnl": float(pnl.quantile(0.75)) if len(pnl) else np.nan,
                "best_token_pnl": float(pnl.max()) if len(pnl) else np.nan,
                "worst_token_pnl": float(pnl.min()) if len(pnl) else np.nan,
                "profit_factor": float(profit_factor(pnl)),
                "stopped_out_rate": float(grp["stop_loss_triggered"].eq("yes").mean()) if len(grp) else np.nan,
                "breakeven_exit_rate": float(grp["breakeven_triggered"].eq("yes").mean()) if len(grp) else np.nan,
                "median_mfe": float(pd.to_numeric(grp["max_favorable_excursion"], errors="coerce").median()),
                "median_mae": float(pd.to_numeric(grp["max_adverse_excursion"], errors="coerce").median()),
                "max_mae": float(pd.to_numeric(grp["max_adverse_excursion"], errors="coerce").max()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    best = summary.sort_values(["roi_on_margin", "profit_factor"], ascending=[False, False]).copy()
    return token, cluster, summary, best


def write_outputs(token: pd.DataFrame, cluster: pd.DataFrame, summary: pd.DataFrame, shortable_only: bool, interval: str) -> None:
    universe_suffix = "shortable_only" if shortable_only else "all"
    suffix = f"{universe_suffix}_{interval}"
    token_path = PROCESSED / f"monitoring_cluster_stop_token_{suffix}.csv"
    cluster_path = PROCESSED / f"monitoring_cluster_stop_cluster_{suffix}.csv"
    summary_path = PROCESSED / f"monitoring_cluster_stop_summary_{suffix}.csv"
    token.to_csv(token_path, index=False)
    cluster.to_csv(cluster_path, index=False)
    summary.to_csv(summary_path, index=False)
    top = summary.sort_values(["roi_on_margin", "profit_factor"], ascending=[False, False]).head(30)
    by_hold = (
        summary.groupby("hold_window")
        .agg(best_roi=("roi_on_margin", "max"), median_roi=("roi_on_margin", "median"), variants=("roi_on_margin", "count"))
        .reset_index()
    )
    report = [
        "# Monitoring Tag Cluster Stop/BE Backtest",
        "",
        "Retrospective basket backtest, not a trading recommendation.",
        "",
        f"- universe: `{universe_suffix}`",
        f"- price interval: `{interval}`",
        f"- margin per token: `{MARGIN_USDT}` USDT",
        f"- leverage: `{LEVERAGE}x`",
        f"- entry: first available {interval} candle open after Monitoring Tag announcement",
        f"- path: Binance spot {interval} OHLCV proxy",
        "- conservative conflict rule: fixed stop is evaluated before BE activation within the same candle",
        "- fees/funding/slippage/orderbook/real liquidation maintenance margin are not included",
        "",
        "## Best Variants",
        "",
        top.to_markdown(index=False),
        "",
        "## By Holding Window",
        "",
        by_hold.to_markdown(index=False),
        "",
        "## Outputs",
        "",
        f"- `{token_path.relative_to(ROOT)}`",
        f"- `{cluster_path.relative_to(ROOT)}`",
        f"- `{summary_path.relative_to(ROOT)}`",
    ]
    (DOCS / f"monitoring_cluster_stop_backtest_{suffix}.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shortable-only", action="store_true")
    parser.add_argument("--start-cluster", type=int)
    parser.add_argument("--end-cluster", type=int)
    parser.add_argument("--interval", choices=["1h", "15m"], default="1h")
    args = parser.parse_args()
    token, cluster, summary, _ = build(args.shortable_only, args.start_cluster, args.end_cluster, args.interval)
    write_outputs(token, cluster, summary, args.shortable_only, args.interval)
    print(
        {
            "shortable_only": args.shortable_only,
            "interval": args.interval,
            "token_rows": len(token),
            "cluster_rows": len(cluster),
            "summary_rows": len(summary),
            "clusters": token["cluster_id"].nunique() if len(token) else 0,
            "valid_token_rows": int(token["missing_path_flag"].eq("no").sum()) if len(token) else 0,
        }
    )


if __name__ == "__main__":
    main()
