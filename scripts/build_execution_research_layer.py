#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW_KLINES = ROOT / "data" / "raw" / "klines"
DOCS = ROOT / "docs"

EXCLUDED_SCENARIOS = {"PAIR_REMOVAL_ONLY", "UNKNOWN_MANUAL_REVIEW"}


def yn(value: Any) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def safe_float(value: Any) -> float | None:
    value = pd.to_numeric(value, errors="coerce")
    if pd.isna(value):
        return None
    return float(value)


def iso(ts: pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class PathMetrics:
    path_data_available: bool
    max_adverse_excursion: float | None = None
    max_favorable_excursion: float | None = None
    time_to_mae_hours: float | None = None
    time_to_mfe_hours: float | None = None
    high_time: str = ""
    low_time: str = ""
    last_close: float | None = None
    max_high: float | None = None
    min_low: float | None = None
    max_close: float | None = None


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[tuple[str, str, str], pd.DataFrame] = {}

    def load(self, pair: str, market_type: str, interval: str) -> pd.DataFrame:
        if not pair or str(pair) == "nan":
            return pd.DataFrame()
        market_dir = "futures" if market_type == "futures" else "spot"
        key = (market_dir, str(pair), interval)
        if key in self.cache:
            return self.cache[key]
        folder = RAW_KLINES / market_dir / str(pair)
        files = sorted(folder.glob(f"{interval}_*_paged.json"))
        frames = []
        for path in files:
            try:
                data = json.loads(path.read_text())
            except Exception:
                continue
            if not data:
                continue
            rows = []
            for item in data:
                if len(item) < 6:
                    continue
                rows.append(
                    {
                        "open_time": pd.to_datetime(int(item[0]), unit="ms", utc=True),
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4]),
                        "volume": float(item[5]),
                        "close_time": pd.to_datetime(int(item[6]), unit="ms", utc=True) if len(item) > 6 else pd.NaT,
                        "quote_volume": float(item[7]) if len(item) > 7 else np.nan,
                    }
                )
            if rows:
                frames.append(pd.DataFrame(rows))
        if not frames:
            df = pd.DataFrame()
        else:
            df = pd.concat(frames, ignore_index=True)
            df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        self.cache[key] = df
        return df


def select_event_market(price_windows: pd.DataFrame) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    rows = price_windows.copy()
    rows = rows[rows["symbol_pair"].notna()]
    rows["_missing"] = rows["missing_price_flag"].map(yn)
    rows["_rank"] = rows["_missing"].astype(int)
    for event_id, grp in rows.sort_values(["_rank", "market_type"]).groupby("event_id", dropna=False):
        row = grp.iloc[0]
        out[str(event_id)] = {
            "symbol_pair": str(row["symbol_pair"]),
            "market_type": str(row["market_type"]),
            "price_source": str(row.get("price_source", "")),
        }
    return out


def compute_path_metrics(
    store: KlineStore,
    pair: str,
    market_type: str,
    event_time: pd.Timestamp,
    entry_price: float | None,
    horizon_hours: int,
    preferred_interval: str,
) -> PathMetrics:
    if entry_price is None or entry_price <= 0 or pd.isna(event_time):
        return PathMetrics(False)
    df = store.load(pair, market_type, preferred_interval)
    if df.empty and preferred_interval == "15m":
        df = store.load(pair, market_type, "1h")
    if df.empty:
        return PathMetrics(False)
    end = event_time + pd.Timedelta(hours=horizon_hours)
    sub = df[(df["open_time"] >= event_time) & (df["open_time"] <= end)].copy()
    if sub.empty:
        return PathMetrics(False)

    high_idx = sub["high"].idxmax()
    low_idx = sub["low"].idxmin()
    max_high = float(sub.loc[high_idx, "high"])
    min_low = float(sub.loc[low_idx, "low"])
    high_time = pd.Timestamp(sub.loc[high_idx, "open_time"])
    low_time = pd.Timestamp(sub.loc[low_idx, "open_time"])
    last_close = float(sub.iloc[-1]["close"])
    max_close = float(sub["close"].max())
    return PathMetrics(
        True,
        max_adverse_excursion=max_high / entry_price - 1,
        max_favorable_excursion=entry_price / min_low - 1,
        time_to_mae_hours=(high_time - event_time).total_seconds() / 3600,
        time_to_mfe_hours=(low_time - event_time).total_seconds() / 3600,
        high_time=iso(high_time),
        low_time=iso(low_time),
        last_close=last_close,
        max_high=max_high,
        min_low=min_low,
        max_close=max_close,
    )


def sustained_close_flag(
    store: KlineStore,
    pair: str,
    market_type: str,
    event_time: pd.Timestamp,
    entry_price: float | None,
    direction: str,
    days: int = 30,
    min_consecutive: int = 3,
) -> str:
    if entry_price is None or entry_price <= 0 or pd.isna(event_time):
        return "unknown"
    df = store.load(pair, market_type, "1d")
    if df.empty:
        return "unknown"
    sub = df[(df["open_time"] >= event_time) & (df["open_time"] <= event_time + pd.Timedelta(days=days))]
    if sub.empty:
        return "unknown"
    cond = sub["close"] > entry_price if direction == "above" else sub["close"] < entry_price
    run = 0
    for value in cond:
        run = run + 1 if bool(value) else 0
        if run >= min_consecutive:
            return "yes"
    return "no"


def build_clean_universe() -> pd.DataFrame:
    scenario = read_csv("scenario_classification.csv")
    resolution = read_csv("price_resolution.csv")
    fallback = read_csv("fallback_data_quality.csv")
    price_windows = read_csv("price_windows.csv")

    quality = (
        price_windows.assign(
            missing=price_windows["missing_price_flag"].map(yn),
            benchmark=price_windows["benchmark_gap"].map(yn),
            unresolved=price_windows["missing_price_reason"].fillna("").str.contains("unresolved_pair_or_symbol"),
            true_gap=price_windows["missing_price_reason"].fillna("").str.contains("true_data_gap"),
        )
        .groupby("token_symbol", dropna=False)
        .agg(
            price_window_rows=("event_id", "count"),
            missing_price_rows=("missing", "sum"),
            benchmark_gap_rows=("benchmark", "sum"),
            unresolved_pair_rows=("unresolved", "sum"),
            true_data_gap_rows=("true_gap", "sum"),
        )
        .reset_index()
    )
    for col in ["missing_price_rows", "benchmark_gap_rows", "unresolved_pair_rows", "true_data_gap_rows"]:
        quality[col] = pd.to_numeric(quality[col], errors="coerce").fillna(0)
    quality["true_data_gap_rate"] = quality["true_data_gap_rows"] / quality["price_window_rows"].replace(0, np.nan)
    quality["benchmark_gap_rate"] = quality["benchmark_gap_rows"] / quality["price_window_rows"].replace(0, np.nan)

    df = scenario.merge(resolution, on="token_symbol", how="left", suffixes=("", "_resolution"))
    df = df.merge(fallback, on="token_symbol", how="left")
    df = df.merge(quality, on="token_symbol", how="left")

    rows = []
    for _, row in df.iterrows():
        reasons = []
        if str(row["primary_scenario"]) == "PAIR_REMOVAL_ONLY":
            reasons.append("pair_removal_control_only")
        if str(row["primary_scenario"]) == "UNKNOWN_MANUAL_REVIEW":
            reasons.append("unknown_manual_review")
        if yn(row.get("manual_review_required", "no")):
            reasons.append("manual_review_required")
        if pd.isna(row.get("spot_pair")) and pd.isna(row.get("futures_pair")):
            reasons.append("no_resolved_binance_pair")
        if float(row.get("unresolved_pair_rows", 0) or 0) > 0:
            reasons.append("unresolved_pair_or_symbol")
        if yn(row.get("fallback_provider_unavailable", "no")):
            reasons.append("fallback_provider_unavailable")
        if yn(row.get("suspicious_fallback_spike", "no")):
            reasons.append("suspicious_fallback_spike")
        true_gap_rate = float(row.get("true_data_gap_rate", 0) or 0)
        bench_gap_rate = float(row.get("benchmark_gap_rate", 0) or 0)
        if true_gap_rate >= 0.25:
            reasons.append("true_data_gap_heavy")
        if bench_gap_rate >= 0.25:
            reasons.append("benchmark_gap_heavy")

        score = 1.0
        score -= 0.30 if "pair_removal_control_only" in reasons else 0.0
        score -= 0.30 if "unknown_manual_review" in reasons else 0.0
        score -= 0.20 if "manual_review_required" in reasons else 0.0
        score -= 0.20 if "unresolved_pair_or_symbol" in reasons else 0.0
        score -= 0.20 if "fallback_provider_unavailable" in reasons else 0.0
        score -= 0.20 if "suspicious_fallback_spike" in reasons else 0.0
        score -= min(0.25, true_gap_rate * 0.35)
        score -= min(0.15, bench_gap_rate * 0.25)
        score = max(0.0, round(score, 3))
        eligible = not reasons
        confidence = "high" if score >= 0.85 else "medium" if score >= 0.65 else "low"
        rows.append(
            {
                **row.to_dict(),
                "is_research_eligible": "yes" if eligible else "no",
                "exclusion_reason": ";".join(reasons),
                "data_quality_score": score,
                "confidence_level": confidence,
            }
        )
    out = pd.DataFrame(rows)
    keep_cols = [
        "token_entity_id",
        "token_symbol",
        "final_outcome",
        "primary_scenario",
        "secondary_flags",
        "anchor_event_id",
        "anchor_event_type",
        "spot_pair",
        "futures_pair",
        "fallback_provider",
        "price_window_rows",
        "missing_price_rows",
        "benchmark_gap_rows",
        "unresolved_pair_rows",
        "true_data_gap_rows",
        "true_data_gap_rate",
        "benchmark_gap_rate",
        "is_research_eligible",
        "exclusion_reason",
        "data_quality_score",
        "confidence_level",
    ]
    out = out[[c for c in keep_cols if c in out.columns]]
    out.to_csv(PROCESSED / "clean_research_universe.csv", index=False)
    out.to_parquet(PROCESSED / "clean_research_universe.parquet", index=False)
    return out


def build_execution_features(clean: pd.DataFrame) -> pd.DataFrame:
    events = read_csv("events.csv")
    scenario = read_csv("scenario_classification.csv")
    price_windows = read_csv("price_windows.csv")
    market_map = select_event_market(price_windows)
    store = KlineStore()
    clean_map = clean.set_index("token_symbol").to_dict("index")
    event_map = events.set_index("event_id").to_dict("index")
    pw_event = price_windows.groupby("event_id", dropna=False)

    rows = []
    candidates = scenario[~scenario["primary_scenario"].isin(EXCLUDED_SCENARIOS)].copy()
    for _, row in candidates.iterrows():
        event_id = str(row.get("anchor_event_id", ""))
        if not event_id or event_id == "nan" or event_id not in event_map:
            continue
        ev = event_map[event_id]
        event_time = pd.to_datetime(ev.get("publication_datetime_utc"), errors="coerce", utc=True)
        token = str(row["token_symbol"])
        cinfo = clean_map.get(token, {})
        event_windows = pw_event.get_group(event_id) if event_id in pw_event.groups else pd.DataFrame()
        entry = safe_float(event_windows["event_price"].dropna().iloc[0]) if not event_windows.empty and event_windows["event_price"].notna().any() else safe_float(row.get("return_24h"))
        baseline = safe_float(event_windows["baseline_vwap_7d"].dropna().iloc[0]) if not event_windows.empty and event_windows["baseline_vwap_7d"].notna().any() else None
        market = market_map.get(event_id, {})
        pair = market.get("symbol_pair", "")
        market_type = market.get("market_type", "")
        m24 = compute_path_metrics(store, pair, market_type, event_time, entry, 24, "15m")
        m7 = compute_path_metrics(store, pair, market_type, event_time, entry, 24 * 7, "1h")
        rebound = "unknown"
        if m7.path_data_available and m7.low_time and m7.high_time and m7.min_low and m7.max_high:
            low_ts = pd.to_datetime(m7.low_time, utc=True)
            high_ts = pd.to_datetime(m7.high_time, utc=True)
            rebound = "yes" if low_ts < high_ts and (m7.max_high / m7.min_low - 1) >= 0.10 else "no"
        vwap_fail = "unknown"
        if m24.path_data_available and baseline and m24.max_high and m24.last_close:
            vwap_fail = "yes" if m24.max_high >= baseline and m24.last_close < baseline else "no"
        rows.append(
            {
                "event_id": event_id,
                "token_entity_id": row["token_entity_id"],
                "token_symbol": token,
                "event_type": ev.get("event_type", ""),
                "scenario": row["primary_scenario"],
                "event_time": iso(event_time),
                "symbol_pair": pair,
                "market_type": market_type,
                "is_research_eligible": cinfo.get("is_research_eligible", "no"),
                "data_quality_score": cinfo.get("data_quality_score", np.nan),
                "confidence_level": cinfo.get("confidence_level", "low"),
                "entry_reference_price": entry,
                "entry_reference_type": "event_price",
                "return_1h": row.get("return_1h"),
                "return_4h": next((safe_float(x) for x in event_windows.loc[event_windows["window"] == "+4h", "raw_return"].head(1)), np.nan) if not event_windows.empty else np.nan,
                "return_24h": row.get("return_24h"),
                "return_7d": row.get("return_7d"),
                "return_30d": row.get("return_30d"),
                "max_adverse_excursion_24h": m24.max_adverse_excursion,
                "max_favorable_excursion_24h": m24.max_favorable_excursion,
                "max_adverse_excursion_7d": m7.max_adverse_excursion,
                "max_favorable_excursion_7d": m7.max_favorable_excursion,
                "time_to_mfe": m7.time_to_mfe_hours,
                "time_to_mae": m7.time_to_mae_hours,
                "post_event_low_time": m7.low_time,
                "post_event_high_time": m7.high_time,
                "rebound_after_initial_drop": rebound,
                "vwap_reclaim_failure": vwap_fail,
                "sustained_close_above_entry": sustained_close_flag(store, pair, market_type, event_time, entry, "above"),
                "sustained_close_below_entry": sustained_close_flag(store, pair, market_type, event_time, entry, "below"),
                "path_data_available_24h": "yes" if m24.path_data_available else "no",
                "path_data_available_7d": "yes" if m7.path_data_available else "no",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "execution_features.csv", index=False)
    out.to_parquet(PROCESSED / "execution_features.parquet", index=False)
    return out


def build_pump_fade_features(clean: pd.DataFrame) -> pd.DataFrame:
    pump = read_csv("pump_analysis.csv")
    events = read_csv("events.csv")
    price_windows = read_csv("price_windows.csv")
    market_map = select_event_market(price_windows)
    store = KlineStore()
    clean_map = clean.set_index("token_symbol").to_dict("index")
    event_map = events.set_index("event_id").to_dict("index")
    rows = []
    for _, row in pump.iterrows():
        event_id = str(row["event_id"])
        ev = event_map.get(event_id, {})
        event_time = pd.to_datetime(ev.get("publication_datetime_utc"), errors="coerce", utc=True)
        token = str(row["token_symbol"])
        cinfo = clean_map.get(token, {})
        market = market_map.get(event_id, {})
        pair = market.get("symbol_pair", "")
        market_type = market.get("market_type", "")
        entry = safe_float(row.get("baseline_price"))
        path = compute_path_metrics(store, pair, market_type, event_time, entry, 24 * 7, "1h")
        pump_size = max(
            [
                safe_float(row.get(c)) or -np.inf
                for c in [
                    "max_return_1h",
                    "max_return_4h",
                    "max_return_24h",
                    "max_return_3d",
                    "max_return_7d",
                    "max_return_until_effective_delisting",
                ]
            ]
        )
        if pump_size == -np.inf:
            pump_size = np.nan
        pump_duration = path.time_to_mae_hours if path.path_data_available else np.nan
        time_to_drawdown = np.nan
        wick_vs_close = np.nan
        if path.path_data_available and path.high_time:
            high_ts = pd.to_datetime(path.high_time, utc=True)
            future = store.load(pair, market_type, "1h")
            future = future[(future["open_time"] >= high_ts) & (future["open_time"] <= event_time + pd.Timedelta(days=7))]
            if not future.empty:
                low_idx = future["low"].idxmin()
                low_ts = pd.Timestamp(future.loc[low_idx, "open_time"])
                time_to_drawdown = (low_ts - high_ts).total_seconds() / 3600
            if path.max_high and path.max_close and path.max_close > 0:
                wick_vs_close = path.max_high / path.max_close - 1
        failed_breakout = "yes" if yn(row.get("pump20_flag")) and safe_float(row.get("post_pump_drawdown")) is not None and safe_float(row.get("post_pump_drawdown")) <= -0.30 else "no"
        score = 0.0
        score += 0.30 if yn(row.get("pump20_flag")) else 0.0
        score += 0.30 if yn(row.get("pump_and_dump_flag")) else 0.0
        score += 0.20 if failed_breakout == "yes" else 0.0
        dd = safe_float(row.get("post_pump_drawdown"))
        score += 0.10 if dd is not None and dd <= -0.50 else 0.0
        score += 0.10 if cinfo.get("is_research_eligible") == "yes" else 0.0
        score -= 0.20 if yn(row.get("manual_review_required")) else 0.0
        score -= 0.20 if "suspicious_fallback_spike" in str(cinfo.get("exclusion_reason", "")) else 0.0
        score = max(0.0, min(1.0, round(score, 3)))
        rows.append(
            {
                "event_id": event_id,
                "token_symbol": token,
                "event_time": iso(event_time),
                "scenario": cinfo.get("primary_scenario", ""),
                "is_research_eligible": cinfo.get("is_research_eligible", "no"),
                "confidence_level": cinfo.get("confidence_level", "low"),
                "pump_size": pump_size,
                "pump_duration": pump_duration,
                "post_pump_drawdown": row.get("post_pump_drawdown"),
                "time_to_drawdown": time_to_drawdown,
                "wick_vs_close_pump": wick_vs_close,
                "failed_breakout_flag": failed_breakout,
                "pump_and_dump_flag": row.get("pump_and_dump_flag"),
                "manual_review_required": row.get("manual_review_required"),
                "short_fade_candidate_score": score,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "pump_fade_features.csv", index=False)
    out.to_parquet(PROCESSED / "pump_fade_features.parquet", index=False)
    return out


def build_monitoring_tag_features(clean: pd.DataFrame) -> pd.DataFrame:
    events = read_csv("events.csv")
    lifecycle = read_csv("token_lifecycle.csv")
    scenario = read_csv("scenario_classification.csv")
    price_windows = read_csv("price_windows.csv")
    recovery = read_csv("recovery_analysis.csv")
    market_map = select_event_market(price_windows)
    store = KlineStore()
    clean_map = clean.set_index("token_symbol").to_dict("index")
    rec_map = recovery.set_index("token_symbol").to_dict("index")
    sc_map = scenario.set_index("token_symbol").to_dict("index")

    monitor_events = events[events["event_type"] == "MONITORING_TAG_ADDED"].copy()
    monitor_events["event_time"] = pd.to_datetime(monitor_events["publication_datetime_utc"], errors="coerce", utc=True)
    all_events = events.copy()
    all_events["event_time"] = pd.to_datetime(all_events["publication_datetime_utc"], errors="coerce", utc=True)
    life_map = lifecycle.set_index("token_symbol").to_dict("index")

    rows = []
    for _, ev in monitor_events.iterrows():
        token = str(ev["token_symbol"])
        event_id = str(ev["event_id"])
        event_time = ev["event_time"]
        cinfo = clean_map.get(token, {})
        sinfo = sc_map.get(token, {})
        linfo = life_map.get(token, {})
        rec = rec_map.get(token, {})
        future = all_events[
            (all_events["token_symbol"].astype(str) == token)
            & (all_events["event_time"] > event_time)
            & (all_events["event_type"].isin(["VOTE_TO_DELIST_STARTED", "VOTE_TO_DELIST_RESULT", "SPOT_TOKEN_DELISTING_ANNOUNCED", "MONITORING_TAG_REMOVED"]))
        ].sort_values("event_time")
        time_next = np.nan
        next_type = ""
        if not future.empty:
            time_next = (future.iloc[0]["event_time"] - event_time).total_seconds() / 86400
            next_type = str(future.iloc[0]["event_type"])

        market = market_map.get(event_id, {})
        pair = market.get("symbol_pair", "")
        market_type = market.get("market_type", "")
        pw = price_windows[price_windows["event_id"].astype(str) == event_id]
        entry = safe_float(pw["event_price"].dropna().iloc[0]) if not pw.empty and pw["event_price"].notna().any() else None
        path = compute_path_metrics(store, pair, market_type, event_time, entry, 24 * 90, "1d")
        max_drawdown = None if not path.path_data_available or entry is None or path.min_low is None else path.min_low / entry - 1
        failed_recovery = "yes" if not yn(rec.get("recovery_90_sustained", "no")) else "no"
        score = 0.0
        score += 0.25 if str(sinfo.get("primary_scenario", "")).startswith("TAG_TO_DELISTING") else 0.0
        score += 0.20 if failed_recovery == "yes" else 0.0
        r30 = safe_float(sinfo.get("alt_adj_return_30d"))
        r90 = safe_float(sinfo.get("alt_adj_return_90d"))
        score += 0.20 if r30 is not None and r30 <= -0.20 else 0.0
        score += 0.15 if r90 is not None and r90 <= -0.30 else 0.0
        score += 0.10 if max_drawdown is not None and max_drawdown <= -0.40 else 0.0
        score += 0.10 if cinfo.get("is_research_eligible") == "yes" else 0.0
        score = max(0.0, min(1.0, round(score, 3)))
        rows.append(
            {
                "event_id": event_id,
                "token_symbol": token,
                "event_time": iso(event_time),
                "scenario": sinfo.get("primary_scenario", ""),
                "is_research_eligible": cinfo.get("is_research_eligible", "no"),
                "confidence_level": cinfo.get("confidence_level", "low"),
                "next_risk_event_type": next_type,
                "time_from_tag_to_next_risk_event": time_next,
                "time_from_tag_to_delisting": linfo.get("days_from_monitoring_tag_to_delisting", np.nan),
                "return_7d_after_tag": sinfo.get("return_7d", np.nan),
                "return_30d_after_tag": sinfo.get("return_30d", np.nan),
                "return_90d_after_tag": sinfo.get("return_90d", np.nan),
                "alt_adj_return_30d_after_tag": sinfo.get("alt_adj_return_30d", np.nan),
                "alt_adj_return_90d_after_tag": sinfo.get("alt_adj_return_90d", np.nan),
                "max_drawdown_after_tag": max_drawdown,
                "recovery_after_tag": rec.get("recovery_90_sustained", "unknown"),
                "failed_recovery_flag": failed_recovery,
                "delayed_collapse_candidate_score": score,
                "path_data_available_90d": "yes" if path.path_data_available else "no",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "monitoring_tag_path_features.csv", index=False)
    out.to_parquet(PROCESSED / "monitoring_tag_path_features.parquet", index=False)
    return out


def describe_dist(df: pd.DataFrame, col: str) -> str:
    x = pd.to_numeric(df[col], errors="coerce").dropna()
    if x.empty:
        return "n=0"
    qs = x.quantile([0.25, 0.5, 0.75])
    return f"n={len(x)}, p25={qs.iloc[0]:.3f}, median={qs.iloc[1]:.3f}, p75={qs.iloc[2]:.3f}"


def write_reports(clean: pd.DataFrame, execution: pd.DataFrame, pump_fade: pd.DataFrame, monitoring: pd.DataFrame) -> None:
    eligible = clean[clean["is_research_eligible"] == "yes"]
    excluded = clean[clean["is_research_eligible"] != "yes"]
    q = [
        "# Execution Feature Quality Report",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Universe",
        "",
        f"- Total lifecycle/scenario rows: {len(clean)}",
        f"- Research eligible rows: {len(eligible)}",
        f"- Excluded or flagged rows: {len(excluded)}",
        "",
        "## Exclusion Reasons",
        "",
    ]
    reason_counts = clean["exclusion_reason"].fillna("").str.get_dummies(sep=";").sum().sort_values(ascending=False)
    for reason, count in reason_counts.items():
        if reason:
            q.append(f"- `{reason}`: {int(count)}")
    q.extend(
        [
            "",
            "## Feature Coverage",
            "",
            f"- Execution feature rows: {len(execution)}",
            f"- Execution rows with 24h path data: {int((execution['path_data_available_24h'] == 'yes').sum())}",
            f"- Execution rows with 7d path data: {int((execution['path_data_available_7d'] == 'yes').sum())}",
            f"- Pump fade rows: {len(pump_fade)}",
            f"- Monitoring Tag path rows: {len(monitoring)}",
            f"- Monitoring rows with 90d path data: {int((monitoring['path_data_available_90d'] == 'yes').sum())}",
            "",
            "## Duplicate Checks",
            "",
            f"- clean universe duplicate token_entity_id: {int(clean.duplicated(['token_entity_id']).sum())}",
            f"- execution duplicate event/token: {int(execution.duplicated(['event_id', 'token_symbol']).sum())}",
            f"- pump fade duplicate event/token: {int(pump_fade.duplicated(['event_id', 'token_symbol']).sum())}",
            f"- monitoring duplicate event/token: {int(monitoring.duplicated(['event_id', 'token_symbol']).sum())}",
            "",
            "## Data Quality Notes",
            "",
            "- `PAIR_REMOVAL_ONLY` is retained in clean universe as excluded/control, not used as token-risk short signal.",
            "- Path features use locally cached Binance 15m/1h/1d klines only. Fallback-only path reconstruction is not attempted in v1.",
            "- Missing/fallback-heavy rows remain present with lower confidence rather than being silently dropped.",
        ]
    )
    (DOCS / "execution_feature_quality_report.md").write_text("\n".join(q) + "\n")

    eligible_execution = execution[execution["is_research_eligible"] == "yes"]
    hyp = [
        "# Trading Hypothesis Summary",
        "",
        "This is a research summary for short/risk-event hypotheses, not a live tradability claim or investment advice.",
        "",
        "## Most Useful Short-Research Event Types",
        "",
    ]
    by_scenario = (
        eligible_execution.groupby("scenario")
        .agg(
            n=("event_id", "count"),
            median_mfe_24h=("max_favorable_excursion_24h", "median"),
            median_mae_24h=("max_adverse_excursion_24h", "median"),
            median_mfe_7d=("max_favorable_excursion_7d", "median"),
            median_mae_7d=("max_adverse_excursion_7d", "median"),
            rebound_rate=("rebound_after_initial_drop", lambda s: (s.astype(str) == "yes").mean()),
            vwap_fail_rate=("vwap_reclaim_failure", lambda s: (s.astype(str) == "yes").mean()),
        )
        .reset_index()
        .sort_values("median_mfe_7d", ascending=False)
    )
    hyp.append(by_scenario.to_markdown(index=False))
    hyp.extend(
        [
            "",
            "## Pump-Fade Candidates",
            "",
            f"- Pump rows: {len(pump_fade)}.",
            f"- Research-eligible pump rows: {int((pump_fade['is_research_eligible'] == 'yes').sum())}.",
            f"- Pump-fade score distribution: {describe_dist(pump_fade, 'short_fade_candidate_score')}.",
            f"- Post-pump drawdown distribution: {describe_dist(pump_fade, 'post_pump_drawdown')}.",
            "",
            "Interpretation: pump-fade research should focus on events where pump20 and pump-and-dump flags are present, but manual-review and suspicious fallback cases should be excluded or separately verified.",
            "",
            "## Monitoring Tag Delayed-Collapse Candidates",
            "",
            f"- Monitoring Tag rows: {len(monitoring)}.",
            f"- Research-eligible Monitoring rows: {int((monitoring['is_research_eligible'] == 'yes').sum())}.",
            f"- Delayed-collapse score distribution: {describe_dist(monitoring, 'delayed_collapse_candidate_score')}.",
            f"- Max drawdown after tag distribution: {describe_dist(monitoring, 'max_drawdown_after_tag')}.",
            "",
            "Interpretation: Monitoring Tag looks most useful as a regime filter plus failed-recovery framework, not just as an immediate-candle short signal.",
            "",
            "## Noisy Or Not-Yet-Tradeable Areas",
            "",
            "- `PAIR_REMOVAL_ONLY`: useful control group, not token delisting signal.",
            "- `UNKNOWN_MANUAL_REVIEW`: not clean enough for signal research without manual review.",
            "- Fallback-provider-unavailable and unresolved-symbol rows: useful for data-quality reports, not clean execution tests.",
            "- Futures-only rows: structurally different mechanics; require funding/open-interest/liquidation features before execution claims.",
            "",
            "## Stop-Loss Risk Zones",
            "",
            "- Delisting announcements have pump/squeeze risk; stop zones based only on immediate entry candle are statistically dangerous.",
            "- 90%/100% pre-event baseline reclaim remains a practical invalidation concept.",
            "- Pump-fade shorts should avoid entering before failed breakout confirmation because pump20 events exist in about one-fifth of delisting rows.",
            "",
            "## Historically Plausible Take-Profit Zones",
            "",
            "- Announcement shock shorts: first target around +24h/+7d favorable excursion distributions, not fixed percentage.",
            "- Failed Monitoring Tag recovery: +30d/+90d drift is more relevant than +1h reaction.",
            "- Pump-fade: post-pump drawdown tail is large, but only after excluding suspicious fallback and liquidity artifacts.",
            "",
            "## Backtest Priority",
            "",
            "1. Spot delisting announcement shock with rebound-failure entry.",
            "2. Delisting pump-fade after failed breakout confirmation.",
            "3. Monitoring Tag failed-recovery delayed-collapse.",
            "4. Delisted-without-known-tag shock response as a separate high-uncertainty class.",
            "5. Futures-only delisting only after adding futures market-structure features.",
        ]
    )
    (DOCS / "trading_hypothesis_summary.md").write_text("\n".join(hyp) + "\n")


def main() -> None:
    clean = build_clean_universe()
    execution = build_execution_features(clean)
    pump_fade = build_pump_fade_features(clean)
    monitoring = build_monitoring_tag_features(clean)
    write_reports(clean, execution, pump_fade, monitoring)
    print(
        {
            "clean_research_universe_rows": len(clean),
            "research_eligible": int((clean["is_research_eligible"] == "yes").sum()),
            "execution_features_rows": len(execution),
            "pump_fade_features_rows": len(pump_fade),
            "monitoring_tag_path_features_rows": len(monitoring),
            "outputs": [
                str(PROCESSED / "clean_research_universe.csv"),
                str(PROCESSED / "execution_features.csv"),
                str(PROCESSED / "pump_fade_features.csv"),
                str(PROCESSED / "monitoring_tag_path_features.csv"),
                str(DOCS / "execution_feature_quality_report.md"),
                str(DOCS / "trading_hypothesis_summary.md"),
            ],
        }
    )


if __name__ == "__main__":
    main()
