#!/usr/bin/env python3
"""Sample/full bottom and rebound analysis for Binance risk-event tokens."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import median

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_SPOT = ROOT / "data/raw/klines/spot"
PROCESSED = ROOT / "data/processed"
CONFIG = ROOT / "config/research_thresholds.yaml"
TOKEN_EXCLUSIONS = ROOT / "config/manual_token_exclusions.yaml"

DEFAULT_SAMPLE = [
    "EPIC",
    "HEI",
    "ALCX",
    "COOKIE",
    "TLM",
    "AERGO",
    "BADGER",
    "COS",
    "HIGH",
    "MBOX",
    "CVX",
    "ZEC",
    "AKRO",
    "0G",
]

HORIZONS = {
    "24h": pd.Timedelta(hours=24),
    "3d": pd.Timedelta(days=3),
    "7d": pd.Timedelta(days=7),
    "14d": pd.Timedelta(days=14),
    "30d": pd.Timedelta(days=30),
    "60d": pd.Timedelta(days=60),
    "90d": pd.Timedelta(days=90),
}

BOTTOM_WINDOWS = [7, 14, 30, 60, 90]
RISK_ANCHOR_EVENT_TYPES = [
    "MONITORING_TAG_ADDED",
    "MONITORING_TAG_REMOVED",
    "SPOT_TOKEN_DELISTING_ANNOUNCED",
    "VOTE_TO_DELIST_STARTED",
    "VOTE_TO_DELIST_RESULT",
]
CONTROL_ANCHOR_EVENT_TYPES = ["SPOT_PAIR_REMOVED"]


@dataclass
class Thresholds:
    deep_drawdown_min: float = -0.50
    extreme_drawdown_min: float = -0.80
    capitulation_volume_zscore_min: float = 2.0
    rebound_20: float = 0.20
    rebound_50: float = 0.50
    rebound_100: float = 1.00
    rebound_200: float = 2.00
    pump_and_dump_drawdown_min: float = -0.30
    sustained_rebound_min_closes: int = 3
    reclaim_pct_from_low: float = 0.10
    higher_low_min_pct: float = 0.05
    breakout_volume_zscore_min: float = 1.5
    low_liquidity_quote_volume_min: float = 100000.0
    bottom_liquidity_threshold: float = 25000.0
    signal_liquidity_threshold: float = 100000.0
    rebound_liquidity_threshold: float = 100000.0
    suspicious_wick_ratio_min: float = 0.70
    signal_lookback_hours: int = 72
    signal_forward_hours: int = 336


def load_thresholds() -> Thresholds:
    vals = {}
    if CONFIG.exists():
        in_section = False
        for raw in CONFIG.read_text().splitlines():
            line = raw.rstrip()
            if not line.strip() or line.strip().startswith("#"):
                continue
            if not raw.startswith(" ") and line.startswith("bottom_rebound:"):
                in_section = True
                continue
            if in_section and raw.startswith("  "):
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    v = v.strip()
                    try:
                        vals[k] = int(v) if "." not in v else float(v)
                    except ValueError:
                        vals[k] = v
            elif in_section and not raw.startswith(" "):
                break
    return Thresholds(**{k: v for k, v in vals.items() if hasattr(Thresholds, k)})


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def read_klines(symbol: str, interval: str) -> pd.DataFrame:
    pair = f"{symbol}USDT"
    path = RAW_SPOT / pair
    files = sorted(path.glob(f"{interval}_*_paged.json"))
    rows = []
    for fp in files:
        try:
            data = json.loads(fp.read_text())
        except Exception:
            continue
        rows.extend(data)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp")
    return df


def volume_zscores(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    roll = df["quote_volume"].rolling(24, min_periods=6)
    mean = roll.mean()
    std = roll.std().replace(0, pd.NA)
    return ((df["quote_volume"] - mean) / std).fillna(0)


def choose_anchor(events: pd.DataFrame, lifecycle: pd.Series, symbol: str, allowed_event_types: set[str] | None = None) -> pd.Series | None:
    token_events = events[events["token_symbol"] == symbol].copy()
    if allowed_event_types is not None:
        token_events = token_events[token_events["event_type"].isin(allowed_event_types)]
    priorities = [
        "MONITORING_TAG_ADDED",
        "SPOT_TOKEN_DELISTING_ANNOUNCED",
        "MONITORING_TAG_REMOVED",
        "VOTE_TO_DELIST_STARTED",
        "VOTE_TO_DELIST_RESULT",
        "SPOT_PAIR_REMOVED",
    ]
    for event_type in priorities:
        rows = token_events[token_events["event_type"] == event_type].sort_values("publication_datetime_utc")
        if not rows.empty:
            return rows.iloc[0]
    return None


def parse_event_types(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {x.strip().upper() for x in value.split(",") if x.strip()}


def load_excluded_symbols() -> set[str]:
    if not TOKEN_EXCLUSIONS.exists():
        return set()
    excluded: set[str] = set()
    for raw in TOKEN_EXCLUSIONS.read_text().splitlines():
        line = raw.strip()
        if line.startswith("- token_symbol:"):
            symbol = line.split(":", 1)[1].strip().strip("\"'").upper()
            if symbol:
                excluded.add(symbol)
    return excluded


def token_universe_for_events(lifecycle: pd.DataFrame, events: pd.DataFrame, allowed_event_types: set[str] | None) -> list[str]:
    excluded = load_excluded_symbols()
    symbols = lifecycle["token_symbol"].dropna().astype(str).str.upper().tolist()
    symbols = [symbol for symbol in symbols if symbol not in excluded]
    if allowed_event_types is None:
        return symbols
    available = set(events[events["event_type"].isin(allowed_event_types)]["token_symbol"].dropna().astype(str).str.upper())
    return [symbol for symbol in symbols if symbol in available]


def baseline_from_path(df: pd.DataFrame, event_ts: pd.Timestamp) -> dict:
    if df.empty or "timestamp" not in df.columns:
        return {
            "baseline_vwap_7d": math.nan,
            "baseline_median_close_7d": math.nan,
            "baseline_close_1d": math.nan,
            "baseline_median_close_30d": math.nan,
            "event_price": math.nan,
        }
    pre7 = df[(df["timestamp"] < event_ts) & (df["timestamp"] >= event_ts - pd.Timedelta(days=7))]
    pre30 = df[(df["timestamp"] < event_ts) & (df["timestamp"] >= event_ts - pd.Timedelta(days=30))]
    pre1 = df[df["timestamp"] < event_ts].tail(24)
    event_row = df[df["timestamp"] >= event_ts].head(1)
    vwap7 = (pre7["close"] * pre7["quote_volume"]).sum() / pre7["quote_volume"].sum() if pre7["quote_volume"].sum() else math.nan
    return {
        "baseline_vwap_7d": vwap7,
        "baseline_median_close_7d": pre7["close"].median() if len(pre7) else math.nan,
        "baseline_close_1d": pre1["close"].iloc[-1] if len(pre1) else math.nan,
        "baseline_median_close_30d": pre30["close"].median() if len(pre30) else math.nan,
        "event_price": event_row["open"].iloc[0] if len(event_row) else math.nan,
    }


def selected_baseline(base: dict) -> float:
    for key in ["baseline_vwap_7d", "baseline_median_close_7d", "baseline_close_1d", "event_price"]:
        val = base.get(key)
        if pd.notna(val) and val and val > 0:
            return float(val)
    return math.nan


def wick_ratio(row: pd.Series) -> float:
    rng = row["high"] - row["low"]
    if not rng or pd.isna(rng):
        return 0.0
    return max(0.0, min(1.0, (row["close"] - row["low"]) / rng))


def sustained_daily(daily: pd.DataFrame, start_ts: pd.Timestamp, threshold: float, min_closes: int) -> str:
    if daily.empty or "timestamp" not in daily.columns or "close" not in daily.columns:
        return "unknown"
    d = daily[daily["timestamp"] >= start_ts].head(max(10, min_closes + 5))
    if len(d) < min_closes:
        return "unknown"
    streak = 0
    for close in d["close"]:
        streak = streak + 1 if close >= threshold else 0
        if streak >= min_closes:
            return "yes"
    return "no"


def bottom_metrics(symbol: str, event: pd.Series, hourly: pd.DataFrame, daily: pd.DataFrame, th: Thresholds) -> tuple[dict, dict]:
    event_ts = pd.to_datetime(event["publication_datetime_utc"], utc=True)
    if hourly.empty or "timestamp" not in hourly.columns:
        result = {
            "token_entity_id": event.get("token_entity_id", symbol),
            "token_symbol": symbol,
            "anchor_event_id": event.get("event_id", ""),
            "anchor_event_type": event.get("event_type", ""),
            "publication_datetime_utc": event_ts.isoformat(),
            "manual_review_required": "yes",
            "notes": "missing_1h_path",
        }
        return result, {"post": pd.DataFrame(), "daily": daily, "baseline": math.nan, "event_ts": event_ts}
    post = hourly[hourly["timestamp"] >= event_ts].copy()
    post["volume_zscore"] = volume_zscores(post)
    base = baseline_from_path(hourly, event_ts)
    baseline = selected_baseline(base)
    result = {
        "token_entity_id": event.get("token_entity_id", symbol),
        "token_symbol": symbol,
        "anchor_event_id": event.get("event_id", ""),
        "anchor_event_type": event.get("event_type", ""),
        "publication_datetime_utc": event.get("publication_datetime_utc", ""),
        **{k: base.get(k, math.nan) for k in ["baseline_vwap_7d", "baseline_median_close_7d", "baseline_close_1d"]},
    }
    notes = []
    lows = {}
    for days in BOTTOM_WINDOWS:
        w = post[post["timestamp"] <= event_ts + pd.Timedelta(days=days)]
        if w.empty or pd.isna(baseline):
            result[f"post_event_low_{days}d"] = ""
            result[f"drawdown_to_low_{days}d"] = ""
            if days in [7, 30, 90]:
                result[f"days_from_event_to_low_{days}d"] = ""
            continue
        idx = w["low"].idxmin()
        row = w.loc[idx]
        dd = row["low"] / baseline - 1
        lows[days] = row
        result[f"post_event_low_{days}d"] = row["low"]
        result[f"drawdown_to_low_{days}d"] = dd
        if days in [7, 30, 90]:
            result[f"days_from_event_to_low_{days}d"] = (row["timestamp"] - event_ts).total_seconds() / 86400
    row = None
    for window_days in [90, 60, 30, 14, 7]:
        if window_days in lows:
            row = lows[window_days]
            break
    if row is None:
        result.update(
            {
                "low_timestamp_utc": "",
                "low_price": "",
                "volume_at_low": "",
                "quote_volume_at_low": "",
                "volume_zscore_at_low": "",
                "wick_ratio_at_low": "",
                "volatility_before_low": "",
                "volatility_after_low": "",
                "capitulation_flag": "no",
                "liquidity_death_flag": "yes",
                "low_liquidity_wick_flag": "yes",
                "absolute_bottom_confidence_score": 0.2,
                "manual_review_required": "yes",
                "notes": "missing_1h_path_or_no_post_event_data",
            }
        )
        return result, {"baseline": baseline, "low_row": None}

    low_ts = row["timestamp"]
    before = post[(post["timestamp"] < low_ts) & (post["timestamp"] >= low_ts - pd.Timedelta(days=7))]
    after = post[(post["timestamp"] > low_ts) & (post["timestamp"] <= low_ts + pd.Timedelta(days=7))]
    vol_before = before["close"].pct_change().std() if len(before) > 2 else math.nan
    vol_after = after["close"].pct_change().std() if len(after) > 2 else math.nan
    dd90 = row["low"] / baseline - 1 if pd.notna(baseline) else math.nan
    wr = wick_ratio(row)
    low_liq = row["quote_volume"] < th.low_liquidity_quote_volume_min
    low_wick = low_liq and wr >= th.suspicious_wick_ratio_min
    next_candles = post[(post["timestamp"] > low_ts) & (post["timestamp"] <= low_ts + pd.Timedelta(hours=6))]
    no_lower_low = not len(next_candles) or next_candles["low"].min() >= row["low"]
    reclaim = len(after[after["high"] >= row["low"] * (1 + th.reclaim_pct_from_low)]) > 0
    cap = (
        pd.notna(dd90)
        and dd90 <= th.deep_drawdown_min
        and row.get("volume_zscore", 0) >= th.capitulation_volume_zscore_min
        and reclaim
        and no_lower_low
        and not low_wick
    )
    confidence = 0.85
    if low_liq:
        confidence -= 0.25
        notes.append("low_quote_volume_at_low")
    if low_wick:
        confidence -= 0.25
        notes.append("low_liquidity_wick")
    if len(post) < 24 * 7:
        confidence -= 0.2
        notes.append("short_post_event_history")
    result.update(
        {
            "low_timestamp_utc": low_ts.isoformat(),
            "low_price": row["low"],
            "volume_at_low": row["volume"],
            "quote_volume_at_low": row["quote_volume"],
            "volume_zscore_at_low": row.get("volume_zscore", 0),
            "wick_ratio_at_low": wr,
            "volatility_before_low": vol_before,
            "volatility_after_low": vol_after,
            "capitulation_flag": "yes" if cap else "no",
            "liquidity_death_flag": "yes" if low_liq else "no",
            "low_liquidity_wick_flag": "yes" if low_wick else "no",
            "absolute_bottom_confidence_score": max(0.05, round(confidence, 3)),
            "manual_review_required": "yes" if confidence < 0.75 or low_wick else "no",
            "notes": ";".join(notes),
        }
    )
    return result, {"baseline": baseline, "low_row": row, "daily": daily, "post": post}


def rebound_metrics(bottom: dict, ctx: dict, th: Thresholds) -> dict:
    symbol = bottom["token_symbol"]
    row = ctx.get("low_row")
    post = ctx.get("post", pd.DataFrame())
    daily = ctx.get("daily", pd.DataFrame())
    out = {
        "token_entity_id": bottom["token_entity_id"],
        "token_symbol": symbol,
        "anchor_event_id": bottom["anchor_event_id"],
        "anchor_event_type": bottom["anchor_event_type"],
        "bottom_timestamp_utc": bottom.get("low_timestamp_utc", ""),
        "bottom_price": bottom.get("low_price", ""),
    }
    if row is None or post.empty:
        out.update({"manual_review_required": "yes", "notes": "missing_bottom_or_path"})
        return out
    low_ts = pd.to_datetime(bottom["low_timestamp_utc"], utc=True)
    low_price = float(bottom["low_price"])
    best_ret = -999.0
    best_row = None
    for label, delta in HORIZONS.items():
        w = post[(post["timestamp"] > low_ts) & (post["timestamp"] <= low_ts + delta)]
        if w.empty:
            out[f"max_rebound_{label}"] = ""
            continue
        idx = w["high"].idxmax()
        hi = w.loc[idx]
        ret = hi["high"] / low_price - 1
        out[f"max_rebound_{label}"] = ret
        if ret > best_ret:
            best_ret = ret
            best_row = hi
    if best_row is None:
        best_ret = math.nan
    out["rebound_20_flag"] = "yes" if pd.notna(best_ret) and best_ret >= th.rebound_20 else "no"
    out["rebound_50_flag"] = "yes" if pd.notna(best_ret) and best_ret >= th.rebound_50 else "no"
    out["rebound_100_flag"] = "yes" if pd.notna(best_ret) and best_ret >= th.rebound_100 else "no"
    out["rebound_200_flag"] = "yes" if pd.notna(best_ret) and best_ret >= th.rebound_200 else "no"
    if best_row is not None:
        high_ts = best_row["timestamp"]
        out["days_from_bottom_to_max_rebound"] = (high_ts - low_ts).total_seconds() / 86400
        out["rebound_high_timestamp_utc"] = high_ts.isoformat()
        out["rebound_high_price"] = best_row["high"]
        out["volume_on_rebound"] = best_row["volume"]
        out["quote_volume_on_rebound"] = best_row["quote_volume"]
        out["volume_zscore_on_rebound"] = best_row.get("volume_zscore", 0)
        after_high = post[post["timestamp"] > high_ts]
        post_dd = after_high["low"].min() / best_row["high"] - 1 if len(after_high) else math.nan
    else:
        post_dd = math.nan
    sustained_threshold = low_price * (1 + th.rebound_20)
    sustained = sustained_daily(daily, low_ts, sustained_threshold, th.sustained_rebound_min_closes)
    out["rebound_sustained_3d"] = sustained
    out["rebound_sustained_7d"] = sustained
    out["post_rebound_drawdown"] = post_dd
    pump_dump = pd.notna(best_ret) and best_ret >= th.rebound_50 and pd.notna(post_dd) and post_dd <= th.pump_and_dump_drawdown_min and sustained != "yes"
    dead_cat = pd.notna(best_ret) and best_ret >= th.rebound_20 and sustained != "yes" and pd.notna(post_dd) and post_dd <= th.pump_and_dump_drawdown_min
    low_liq = bottom.get("liquidity_death_flag") == "yes"
    out.update(
        {
            "pump_and_dump_after_bottom": "yes" if pump_dump else "no",
            "dead_cat_bounce_flag": "yes" if dead_cat else "no",
            "low_liquidity_rebound_flag": "yes" if low_liq else "no",
            "fallback_used": "no",
            "price_source": "binance_spot",
            "exchange": "binance",
            "manual_review_required": "yes" if bottom.get("manual_review_required") == "yes" or low_liq else "no",
            "notes": "",
        }
    )
    return out


def find_signals(bottom: dict, ctx: dict, rebound: dict, th: Thresholds) -> list[dict]:
    row = ctx.get("low_row")
    post = ctx.get("post", pd.DataFrame())
    baseline = ctx.get("baseline", math.nan)
    if row is None or post.empty or pd.isna(baseline):
        return []
    low_ts = pd.to_datetime(bottom["low_timestamp_utc"], utc=True)
    low_price = float(bottom["low_price"])
    after = post[(post["timestamp"] > low_ts) & (post["timestamp"] <= low_ts + pd.Timedelta(days=30))].copy()
    signals = []
    if after.empty:
        return signals

    # CAPITULATION_RECLAIM: first close >= low * reclaim after the low.
    reclaim_level = low_price * (1 + th.reclaim_pct_from_low)
    reclaim_rows = after[after["close"] >= reclaim_level]
    if bottom.get("capitulation_flag") == "yes" and not reclaim_rows.empty:
        sig = reclaim_rows.iloc[0]
        signals.append(make_signal(bottom, post, sig, "CAPITULATION_RECLAIM", low_ts, low_price, low_price * 0.98, "close_reclaimed_low_plus_pct", th))

    # HIGHER_LOW_BREAKOUT: simple causal proxy. Find a bounce high, then a pullback low above low, then breakout.
    first_window = after.head(72)
    if len(first_window) >= 12:
        bounce_idx = first_window["high"].idxmax()
        bounce = first_window.loc[bounce_idx]
        pullback = after[(after["timestamp"] > bounce["timestamp"]) & (after["timestamp"] <= bounce["timestamp"] + pd.Timedelta(days=10))]
        if len(pullback):
            pb_idx = pullback["low"].idxmin()
            pb = pullback.loc[pb_idx]
            if pb["low"] >= low_price * (1 + th.higher_low_min_pct):
                breakout = after[(after["timestamp"] > pb["timestamp"]) & (after["close"] > bounce["high"])]
                if len(breakout):
                    sig = breakout.iloc[0]
                    signals.append(make_signal(bottom, post, sig, "HIGHER_LOW_BREAKOUT", pb["timestamp"], pb["low"], pb["low"] * 0.98, "breakout_after_higher_low", th))

    # SLOW_BLEED_SQUEEZE_BREAKOUT: first volume breakout after at least 7 days and deep drawdown.
    dd = low_price / baseline - 1
    later = post[(post["timestamp"] >= pd.to_datetime(bottom["publication_datetime_utc"], utc=True) + pd.Timedelta(days=7))]
    breakout = later[(later.get("volume_zscore", 0) >= th.breakout_volume_zscore_min) & (later["close"] > later["open"])]
    if pd.notna(dd) and dd <= th.deep_drawdown_min and len(breakout):
        sig = breakout.iloc[0]
        recent = post[(post["timestamp"] < sig["timestamp"]) & (post["timestamp"] >= sig["timestamp"] - pd.Timedelta(hours=th.signal_lookback_hours))]
        if len(recent):
            recent_low = recent.loc[recent["low"].idxmin()]
            signals.append(make_signal(bottom, post, sig, "SLOW_BLEED_SQUEEZE_BREAKOUT", recent_low["timestamp"], recent_low["low"], recent_low["low"] * 0.98, "volume_breakout_after_squeeze_proxy", th))
    return signals


def score_signal(row: dict, th: Thresholds) -> dict:
    quote_signal = float(row.get("quote_volume_at_signal") or 0)
    quote_bottom = float(row.get("quote_volume_at_bottom") or 0)
    vz = float(row.get("volume_zscore_at_signal") or 0)
    close_pos = float(row.get("close_position_in_signal_candle") or 0)
    next_ok = row.get("next_3_candles_confirmation") == "yes"
    rr7 = float(row.get("risk_reward_7d") or 0)
    stop_dist = abs(float(row.get("stop_distance_pct") or row.get("risk_pct") or 0))
    manual = row.get("manual_review_required") == "yes"
    wick = row.get("suspicious_signal_wick") == "yes"
    low_sig = quote_signal < th.signal_liquidity_threshold
    low_bot = quote_bottom < th.bottom_liquidity_threshold

    bottom_liquidity_score = min(1.0, quote_bottom / max(th.bottom_liquidity_threshold * 4, 1))
    signal_liquidity_score = min(1.0, quote_signal / max(th.signal_liquidity_threshold * 3, 1))
    signal_confirmation_score = (0.45 if vz >= th.breakout_volume_zscore_min else 0.15) + (0.35 if close_pos >= 0.60 else 0.15) + (0.20 if next_ok else 0)
    structure_score = 0.8 if not wick and stop_dist <= 0.25 else (0.45 if not wick else 0.2)
    risk_management_score = 0.35 if stop_dist > 0.35 else (0.65 if stop_dist > 0.22 else 0.9)
    risk_reward_score = min(1.0, max(0.0, rr7 / 3.0))
    mae_before = abs(float(row.get("max_adverse_excursion_before_mfe") or 0))
    execution_quality_score = 0.85 if mae_before <= max(stop_dist, 0.01) and row.get("signal_failed_stop") != "yes" else 0.35
    data_quality_score = 1.0
    source_quality_score = 1.0
    manual_review_penalty = 0.0
    if manual and not low_bot:
        manual_review_penalty += 0.25
    if low_sig:
        manual_review_penalty += 0.35
    if low_bot and not low_sig:
        row["execution_quality_notes"] = (row.get("execution_quality_notes", "") + ";low liquidity at bottom, but signal liquidity improved").strip(";")
        manual_review_penalty += 0.08
    score = (
        0.22 * signal_liquidity_score
        + 0.20 * min(1.0, signal_confirmation_score)
        + 0.16 * risk_management_score
        + 0.18 * risk_reward_score
        + 0.14 * execution_quality_score
        + 0.10 * data_quality_score
        - manual_review_penalty
    )
    score = max(0.0, min(1.0, score))
    if manual or low_sig or wick:
        tier = "Manual Review"
    elif score >= 0.80 and rr7 >= 3 and not low_bot:
        tier = "A"
    elif score >= 0.55 and rr7 >= 1.5:
        tier = "B"
    else:
        tier = "C"
    return {
        "bottom_liquidity_score": round(bottom_liquidity_score, 3),
        "signal_liquidity_score": round(signal_liquidity_score, 3),
        "signal_confirmation_score": round(min(1.0, signal_confirmation_score), 3),
        "risk_management_score": round(risk_management_score, 3),
        "execution_quality_score": round(execution_quality_score, 3),
        "data_quality_score": round(data_quality_score, 3),
        "liquidity_score": round(signal_liquidity_score, 3),
        "confirmation_score": round(min(1.0, signal_confirmation_score), 3),
        "structure_score": round(structure_score, 3),
        "risk_reward_score": round(risk_reward_score, 3),
        "source_quality_score": source_quality_score,
        "manual_review_penalty": round(manual_review_penalty, 3),
        "signal_quality_score": round(score, 3),
        "final_tradeability_score": round(score, 3),
        "tradeability_tier": tier,
    }


def make_signal(bottom: dict, post: pd.DataFrame, sig: pd.Series, signal_type: str, recent_low_ts, recent_low_price, stop_price, confirmation: str, th: Thresholds) -> dict:
    signal_price = float(sig["close"])
    future = post[(post["timestamp"] > sig["timestamp"]) & (post["timestamp"] <= sig["timestamp"] + pd.Timedelta(hours=th.signal_forward_hours))]
    risk_pct = stop_price / signal_price - 1
    candle_range = sig["high"] - sig["low"]
    close_pos = (sig["close"] - sig["low"]) / candle_range if candle_range else 0
    sig_wick = close_pos < 0.35 and candle_range / signal_price > 0.08 if signal_price else False
    next3 = post[(post["timestamp"] > sig["timestamp"]) & (post["timestamp"] <= sig["timestamp"] + pd.Timedelta(hours=3))]
    next_confirm = "yes" if len(next3) >= 3 and next3["low"].min() > stop_price and next3["close"].iloc[-1] >= signal_price else "no"
    bottom_quote = float(bottom.get("quote_volume_at_low") or 0)
    low_signal = sig.get("quote_volume", 0) < th.signal_liquidity_threshold
    low_bottom = bottom_quote < th.bottom_liquidity_threshold
    if future.empty:
        mae = mfe24 = mfe3 = mfe7 = mfe14 = math.nan
        stopped = "unknown"
        mae_before_mfe = math.nan
        time_to_mfe = time20 = time50 = time100 = math.nan
    else:
        mae = future["low"].min() / signal_price - 1
        stopped = "yes" if future["low"].min() <= stop_price else "no"
        def mfe(days):
            w = future[future["timestamp"] <= sig["timestamp"] + pd.Timedelta(days=days)]
            return w["high"].max() / signal_price - 1 if len(w) else math.nan
        mfe24, mfe3, mfe7, mfe14 = mfe(1), mfe(3), mfe(7), mfe(14)
        hi_idx = future["high"].idxmax()
        hi_row = future.loc[hi_idx]
        time_to_mfe = (hi_row["timestamp"] - sig["timestamp"]).total_seconds() / 3600
        before_hi = future[future["timestamp"] <= hi_row["timestamp"]]
        mae_before_mfe = before_hi["low"].min() / signal_price - 1 if len(before_hi) else math.nan
        def target_time(target):
            hits = future[future["high"] >= signal_price * (1 + target)]
            return (hits.iloc[0]["timestamp"] - sig["timestamp"]).total_seconds() / 3600 if len(hits) else math.nan
        time20, time50, time100 = target_time(0.20), target_time(0.50), target_time(1.00)
    risk_abs = abs(risk_pct) if pd.notna(risk_pct) and risk_pct < 0 else math.nan
    def rr(x):
        return x / risk_abs if pd.notna(x) and pd.notna(risk_abs) and risk_abs else math.nan
    row = {
        "token_entity_id": bottom["token_entity_id"],
        "token_symbol": bottom["token_symbol"],
        "anchor_event_id": bottom["anchor_event_id"],
        "signal_timestamp_utc": sig["timestamp"].isoformat(),
        "signal_type": signal_type,
        "signal_price": signal_price,
        "recent_low_timestamp_utc": pd.Timestamp(recent_low_ts).isoformat(),
        "recent_low_price": recent_low_price,
        "stop_price": stop_price,
        "risk_pct": risk_pct,
        "stop_distance_pct": risk_pct,
        "max_adverse_excursion_after_signal": mae,
        "max_adverse_excursion_before_mfe": mae_before_mfe,
        "max_favorable_excursion_24h": mfe24,
        "max_favorable_excursion_3d": mfe3,
        "max_favorable_excursion_7d": mfe7,
        "max_favorable_excursion_14d": mfe14,
        "risk_reward_24h": rr(mfe24),
        "risk_reward_3d": rr(mfe3),
        "risk_reward_7d": rr(mfe7),
        "quote_volume_at_bottom": bottom_quote,
        "quote_volume_at_signal": sig.get("quote_volume", ""),
        "signal_volume_zscore": sig.get("volume_zscore", 0),
        "signal_quote_volume": sig.get("quote_volume", ""),
        "volume_zscore_at_signal": sig.get("volume_zscore", 0),
        "candle_range_at_signal": candle_range,
        "wick_ratio_at_signal": wick_ratio(sig),
        "close_position_in_signal_candle": close_pos,
        "next_3_candles_confirmation": next_confirm,
        "time_to_mfe_hours": time_to_mfe,
        "time_to_20_target_hours": time20,
        "time_to_50_target_hours": time50,
        "time_to_100_target_hours": time100,
        "signal_liquidity_flag": "low" if low_signal else "ok",
        "bottom_liquidity_flag": "low" if low_bottom else "ok",
        "low_liquidity_at_bottom": "yes" if low_bottom else "no",
        "low_liquidity_at_signal": "yes" if low_signal else "no",
        "suspicious_signal_wick": "yes" if sig_wick else "no",
        "false_breakout_flag": "yes" if stopped == "yes" and pd.notna(mfe7) and mfe7 < 0.20 else "no",
        "confirmation_type": confirmation,
        "signal_success_20": "yes" if pd.notna(mfe7) and mfe7 >= 0.20 else "no",
        "signal_success_50": "yes" if pd.notna(mfe14) and mfe14 >= 0.50 else "no",
        "signal_success_100": "yes" if pd.notna(mfe14) and mfe14 >= 1.00 else "no",
        "signal_failed_stop": stopped,
        "manual_review_required": "yes" if low_signal or sig_wick else "no",
        "execution_quality_notes": "",
        "signal_failure_reason": "",
        "no_signal_reason": "",
        "notes": "causal_signal_after_confirmation;no_future_low_used",
    }
    if row["signal_failed_stop"] == "yes":
        reasons = []
        if row["false_breakout_flag"] == "yes":
            reasons.append("false_breakout")
        if low_signal:
            reasons.append("low_liquidity_at_signal")
        if next_confirm == "no":
            reasons.append("next_3_candles_failed_confirmation")
        row["signal_failure_reason"] = ";".join(reasons) or "stop_hit_after_signal"
    scores = score_signal(row, th)
    row.update(scores)
    return row


def classify(bottom: dict, rebound: dict, signals: list[dict], lifecycle_row: pd.Series, th: Thresholds) -> tuple[dict, dict | None]:
    max_reb = max([float(rebound.get(f"max_rebound_{h}", "nan") or math.nan) for h in HORIZONS], default=math.nan)
    dd = bottom.get("drawdown_to_low_90d") or bottom.get("drawdown_to_low_30d") or ""
    dd_val = float(dd) if dd != "" and pd.notna(dd) else math.nan
    sustained = rebound.get("rebound_sustained_3d") == "yes" or rebound.get("rebound_sustained_7d") == "yes"
    manual = bottom.get("manual_review_required") == "yes" or rebound.get("manual_review_required") == "yes"
    final_outcome = lifecycle_row.get("final_outcome", "")
    scenario = "NO_CLEAR_BOTTOM_REBOUND_PATTERN"
    flags = []
    if final_outcome == "spot_pair_removed_only":
        scenario = "NO_CLEAR_BOTTOM_REBOUND_PATTERN"
        flags.append("control_spot_pair_removed_only")
    elif manual:
        scenario = "MANUAL_REVIEW_REQUIRED"
    elif final_outcome == "delisted_after_tag" and pd.notna(dd_val) and dd_val <= th.deep_drawdown_min and (pd.isna(max_reb) or max_reb < th.rebound_20):
        scenario = "DELISTING_DEATH_SPIRAL"
    elif rebound.get("pump_and_dump_after_bottom") == "yes":
        scenario = "DEAD_CAT_BOUNCE"
    elif bottom.get("capitulation_flag") == "yes" and pd.notna(max_reb) and max_reb >= th.rebound_50:
        scenario = "CAPITULATION_THEN_PUMP"
    elif pd.notna(max_reb) and max_reb >= th.rebound_50 and signals:
        scenario = "SLOW_BLEED_THEN_SQUEEZE"
    elif pd.notna(dd_val) and dd_val <= th.deep_drawdown_min and (pd.isna(max_reb) or max_reb < th.rebound_20):
        scenario = "NO_BOTTOM_CONTINUED_BLEED"
    if final_outcome == "tag_removed" and pd.notna(max_reb) and max_reb >= th.rebound_20:
        flags.append("tag_removed_rebound")
    epic_like = (
        pd.notna(dd_val)
        and dd_val <= th.deep_drawdown_min
        and pd.notna(max_reb)
        and max_reb >= th.rebound_50
        and bool(signals)
        and bottom.get("low_liquidity_wick_flag") != "yes"
        and rebound.get("low_liquidity_rebound_flag") != "yes"
    )
    if epic_like:
        scenario = "EPIC_LIKE_REBOUND"
        flags.append("epic_like_candidate")
    best_signal = max(signals, key=lambda r: (float(r.get("risk_reward_7d") or -999)), default=None)
    scenario_row = {
        "token_entity_id": bottom["token_entity_id"],
        "token_symbol": bottom["token_symbol"],
        "primary_bottom_rebound_scenario": scenario,
        "secondary_flags": ";".join(flags),
        "anchor_event_id": bottom["anchor_event_id"],
        "anchor_event_type": bottom["anchor_event_type"],
        "baseline_price": bottom.get("baseline_vwap_7d") or bottom.get("baseline_median_close_7d"),
        "max_drawdown_after_event": dd_val,
        "days_to_bottom": bottom.get("days_from_event_to_low_90d") or bottom.get("days_from_event_to_low_30d"),
        "max_rebound_after_bottom": max_reb,
        "rebound_sustained": "yes" if sustained else "no",
        "pump_and_dump_after_bottom": rebound.get("pump_and_dump_after_bottom", ""),
        "low_liquidity_wick_flag": bottom.get("low_liquidity_wick_flag", ""),
        "tradable_signal_found": "yes" if signals else "no",
        "best_signal_type": best_signal.get("signal_type", "") if best_signal else "",
        "best_signal_risk_reward": best_signal.get("risk_reward_7d", "") if best_signal else "",
        "scenario_confidence_score": 0.55 if manual else 0.8,
        "manual_review_required": "yes" if manual else "no",
        "notes": "control_only_not_token_risk" if final_outcome == "spot_pair_removed_only" else "",
    }
    epic_row = None
    if epic_like or bottom["token_symbol"] == "EPIC":
        epic_row = {
            "token_entity_id": bottom["token_entity_id"],
            "token_symbol": bottom["token_symbol"],
            "anchor_event_id": bottom["anchor_event_id"],
            "anchor_event_type": bottom["anchor_event_type"],
            "drawdown_before_rebound": dd_val,
            "days_from_event_to_bottom": scenario_row["days_to_bottom"],
            "max_rebound_after_bottom": max_reb,
            "days_from_bottom_to_rebound": rebound.get("days_from_bottom_to_max_rebound", ""),
            "volume_zscore_on_rebound": rebound.get("volume_zscore_on_rebound", ""),
            "rebound_sustained": "yes" if sustained else "no",
            "post_rebound_drawdown": rebound.get("post_rebound_drawdown", ""),
            "fallback_used": rebound.get("fallback_used", ""),
            "suspicious_spike_flag": "yes" if rebound.get("manual_review_required") == "yes" else "no",
            "low_liquidity_flag": rebound.get("low_liquidity_rebound_flag", ""),
            "epic_similarity_score": round((0.25 if pd.notna(dd_val) and dd_val <= th.deep_drawdown_min else 0) + (0.35 if pd.notna(max_reb) and max_reb >= th.rebound_50 else 0) + (0.2 if signals else 0) + (0.2 if sustained else 0), 3),
            "manual_review_required": scenario_row["manual_review_required"],
            "notes": "manual_case_study=false;epic_evaluated_by_same_rules" if bottom["token_symbol"] == "EPIC" else "",
        }
    return scenario_row, epic_row


def no_signal_reason(bottom: dict, rebound: dict, signals: list[dict]) -> str:
    if signals:
        return ""
    reasons = []
    max_reb = max([float(rebound.get(f"max_rebound_{h}", "nan") or math.nan) for h in HORIZONS], default=math.nan)
    if bottom.get("manual_review_required") == "yes":
        reasons.append("bottom_manual_review")
    if bottom.get("liquidity_death_flag") == "yes":
        reasons.append("low_liquidity_at_bottom")
    if pd.notna(max_reb) and max_reb >= 0.50:
        reasons.append("strong_rebound_without_causal_confirmation")
    elif pd.notna(max_reb) and max_reb < 0.20:
        reasons.append("weak_rebound_below_20pct")
    if bottom.get("capitulation_flag") != "yes":
        reasons.append("no_capitulation_reclaim")
    return ";".join(reasons) or "no_valid_signal_pattern"


def build_signal_quality_rows(signal_rows: list[dict]) -> list[dict]:
    rows = []
    for r in signal_rows:
        rows.append(
            {
                "token_entity_id": r.get("token_entity_id"),
                "token_symbol": r.get("token_symbol"),
                "anchor_event_id": r.get("anchor_event_id"),
                "signal_timestamp_utc": r.get("signal_timestamp_utc"),
                "signal_type": r.get("signal_type"),
                "signal_price": r.get("signal_price"),
                "recent_low_price": r.get("recent_low_price"),
                "stop_price": r.get("stop_price"),
                "risk_pct": r.get("risk_pct"),
                "quote_volume_at_signal": r.get("quote_volume_at_signal"),
                "volume_zscore_at_signal": r.get("volume_zscore_at_signal"),
                "bottom_liquidity_score": r.get("bottom_liquidity_score"),
                "signal_liquidity_score": r.get("signal_liquidity_score"),
                "signal_confirmation_score": r.get("signal_confirmation_score"),
                "risk_management_score": r.get("risk_management_score"),
                "execution_quality_score": r.get("execution_quality_score"),
                "data_quality_score": r.get("data_quality_score"),
                "liquidity_score": r.get("liquidity_score"),
                "confirmation_score": r.get("confirmation_score"),
                "structure_score": r.get("structure_score"),
                "risk_reward_score": r.get("risk_reward_score"),
                "source_quality_score": r.get("source_quality_score"),
                "manual_review_penalty": r.get("manual_review_penalty"),
                "signal_quality_score": r.get("signal_quality_score"),
                "final_tradeability_score": r.get("final_tradeability_score"),
                "tradeability_tier": r.get("tradeability_tier"),
                "manual_review_required": r.get("manual_review_required"),
                "notes": r.get("execution_quality_notes") or r.get("notes"),
            }
        )
    return rows


def build_case_comparison(scenarios: list[dict], rebounds: list[dict], signals: list[dict], no_signal: dict[str, str]) -> list[dict]:
    rebound_by = {r["token_symbol"]: r for r in rebounds}
    sig_by = {}
    for s in signals:
        cur = sig_by.get(s["token_symbol"])
        if cur is None or float(s.get("risk_reward_7d") or -999) > float(cur.get("risk_reward_7d") or -999):
            sig_by[s["token_symbol"]] = s
    rows = []
    for sc in scenarios:
        sym = sc["token_symbol"]
        sig = sig_by.get(sym, {})
        rb = rebound_by.get(sym, {})
        main_reason = ""
        if sym == "0G":
            main_reason = "control_only_pair_removal_excluded_from_token_risk"
        elif sig:
            if sig.get("signal_failed_stop") == "yes":
                main_reason = sig.get("signal_failure_reason") or "signal_failed_stop"
            elif sig.get("tradeability_tier") == "Manual Review":
                main_reason = "signal_exists_but_manual_review_required"
            else:
                main_reason = "causal_signal_found"
        else:
            main_reason = no_signal.get(sym, "")
        rows.append(
            {
                "token_symbol": sym,
                "scenario": sc.get("primary_bottom_rebound_scenario"),
                "drawdown_to_bottom": sc.get("max_drawdown_after_event"),
                "max_rebound_after_bottom": sc.get("max_rebound_after_bottom"),
                "tradable_signal_found": sc.get("tradable_signal_found"),
                "best_signal_type": sig.get("signal_type", sc.get("best_signal_type")),
                "signal_quality_score": sig.get("signal_quality_score", ""),
                "tradeability_tier": sig.get("tradeability_tier", ""),
                "stop_failed": sig.get("signal_failed_stop", ""),
                "max_adverse_excursion": sig.get("max_adverse_excursion_after_signal", ""),
                "max_favorable_excursion_7d": sig.get("max_favorable_excursion_7d", ""),
                "risk_reward_7d": sig.get("risk_reward_7d", ""),
                "manual_review_required": sc.get("manual_review_required"),
                "main_reason": main_reason,
                "notes": sc.get("notes") or rb.get("notes") or sig.get("notes", ""),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["sample", "full"], default="sample")
    parser.add_argument("--tokens")
    parser.add_argument("--risk-only", action="store_true", help="Use token-risk anchors only; excludes spot pair removals.")
    parser.add_argument("--control-only", action="store_true", help="Use spot-pair-removal controls only.")
    parser.add_argument("--event-types", help="Comma-separated anchor event types to include.")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int)
    parser.add_argument("--batch-id")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--use-existing-price-data", action="store_true")
    parser.add_argument("--skip-tradable-signals", action="store_true")
    args = parser.parse_args()
    if args.risk_only and args.control_only:
        parser.error("--risk-only and --control-only cannot be used together")

    th = load_thresholds()
    events = pd.read_csv(PROCESSED / "events.csv")
    lifecycle = pd.read_csv(PROCESSED / "token_lifecycle.csv")
    events["publication_datetime_utc"] = pd.to_datetime(events["publication_datetime_utc"], utc=True, errors="coerce")
    allowed_event_types = parse_event_types(args.event_types)
    if args.risk_only:
        allowed_event_types = set(RISK_ANCHOR_EVENT_TYPES) if allowed_event_types is None else allowed_event_types & set(RISK_ANCHOR_EVENT_TYPES)
    if args.control_only:
        allowed_event_types = set(CONTROL_ANCHOR_EVENT_TYPES) if allowed_event_types is None else allowed_event_types & set(CONTROL_ANCHOR_EVENT_TYPES)
    sample_tokens = [t.strip().upper() for t in (args.tokens.split(",") if args.tokens else DEFAULT_SAMPLE)]
    if args.mode == "full" and not args.tokens:
        sample_tokens = token_universe_for_events(lifecycle, events, allowed_event_types)
        sample_tokens = sample_tokens[args.start_index : args.end_index]

    bottom_rows, rebound_rows, signal_rows, scenario_rows, epic_rows = [], [], [], [], []
    no_signal_reasons: dict[str, str] = {}
    qa = {"tokens_requested": len(sample_tokens), "processed": 0, "missing_1h_path": [], "anchors": {}, "manual_review": 0}

    for symbol in sample_tokens:
        lc_rows = lifecycle[lifecycle["token_symbol"] == symbol]
        if lc_rows.empty:
            continue
        lc = lc_rows.iloc[0]
        anchor = choose_anchor(events, lc, symbol, allowed_event_types)
        if anchor is None:
            continue
        hourly = read_klines(symbol, "1h")
        daily = read_klines(symbol, "1d")
        if hourly.empty:
            qa["missing_1h_path"].append(symbol)
        bottom, ctx = bottom_metrics(symbol, anchor, hourly, daily, th)
        rebound = rebound_metrics(bottom, ctx, th)
        signals = [] if args.skip_tradable_signals else find_signals(bottom, ctx, rebound, th)
        ns_reason = no_signal_reason(bottom, rebound, signals)
        if ns_reason:
            no_signal_reasons[symbol] = ns_reason
            for sig_row in signals:
                sig_row["no_signal_reason"] = ""
        scenario, epic = classify(bottom, rebound, signals, lc, th)
        bottom_rows.append(bottom)
        rebound_rows.append(rebound)
        signal_rows.extend(signals)
        scenario_rows.append(scenario)
        if epic:
            epic_rows.append(epic)
        qa["processed"] += 1
        qa["anchors"][anchor["event_type"]] = qa["anchors"].get(anchor["event_type"], 0) + 1
        if bottom.get("manual_review_required") == "yes" or rebound.get("manual_review_required") == "yes" or scenario.get("manual_review_required") == "yes":
            qa["manual_review"] += 1

    suffix = "_sample" if args.mode == "sample" else (f"_{args.batch_id}" if args.batch_id else "")
    outdir = PROCESSED
    bottom_fields = [
        "token_entity_id","token_symbol","anchor_event_id","anchor_event_type","publication_datetime_utc","baseline_vwap_7d","baseline_median_close_7d","baseline_close_1d",
        "post_event_low_7d","post_event_low_14d","post_event_low_30d","post_event_low_60d","post_event_low_90d",
        "drawdown_to_low_7d","drawdown_to_low_14d","drawdown_to_low_30d","drawdown_to_low_60d","drawdown_to_low_90d",
        "days_from_event_to_low_7d","days_from_event_to_low_30d","days_from_event_to_low_90d","low_timestamp_utc","low_price","volume_at_low","quote_volume_at_low","volume_zscore_at_low","wick_ratio_at_low","volatility_before_low","volatility_after_low","capitulation_flag","liquidity_death_flag","low_liquidity_wick_flag","absolute_bottom_confidence_score","manual_review_required","notes"
    ]
    rebound_fields = [
        "token_entity_id","token_symbol","anchor_event_id","anchor_event_type","bottom_timestamp_utc","bottom_price","max_rebound_24h","max_rebound_3d","max_rebound_7d","max_rebound_14d","max_rebound_30d","max_rebound_60d","max_rebound_90d","rebound_20_flag","rebound_50_flag","rebound_100_flag","rebound_200_flag","days_from_bottom_to_max_rebound","rebound_high_timestamp_utc","rebound_high_price","volume_on_rebound","quote_volume_on_rebound","volume_zscore_on_rebound","rebound_sustained_3d","rebound_sustained_7d","post_rebound_drawdown","pump_and_dump_after_bottom","dead_cat_bounce_flag","low_liquidity_rebound_flag","fallback_used","price_source","exchange","manual_review_required","notes"
    ]
    signal_fields = [
        "token_entity_id","token_symbol","anchor_event_id","signal_timestamp_utc","signal_type","signal_price","recent_low_timestamp_utc","recent_low_price","stop_price","risk_pct","max_adverse_excursion_after_signal","max_favorable_excursion_24h","max_favorable_excursion_3d","max_favorable_excursion_7d","max_favorable_excursion_14d","risk_reward_24h","risk_reward_3d","risk_reward_7d","signal_volume_zscore","signal_quote_volume","confirmation_type","signal_success_20","signal_success_50","signal_success_100","signal_failed_stop","manual_review_required","notes"
    ]
    signal_fields = [
        "token_entity_id","token_symbol","anchor_event_id","signal_timestamp_utc","signal_type","signal_price","recent_low_timestamp_utc","recent_low_price","stop_price","risk_pct",
        "quote_volume_at_bottom","quote_volume_at_signal","volume_zscore_at_signal","candle_range_at_signal","wick_ratio_at_signal","close_position_in_signal_candle","next_3_candles_confirmation","stop_distance_pct",
        "max_adverse_excursion_after_signal","max_adverse_excursion_before_mfe","max_favorable_excursion_24h","max_favorable_excursion_3d","max_favorable_excursion_7d","max_favorable_excursion_14d","risk_reward_24h","risk_reward_3d","risk_reward_7d",
        "time_to_mfe_hours","time_to_20_target_hours","time_to_50_target_hours","time_to_100_target_hours","signal_volume_zscore","signal_quote_volume","confirmation_type","signal_success_20","signal_success_50","signal_success_100","signal_failed_stop",
        "signal_liquidity_flag","bottom_liquidity_flag","low_liquidity_at_bottom","low_liquidity_at_signal","suspicious_signal_wick","false_breakout_flag","signal_quality_score","tradeability_tier","execution_quality_notes","signal_failure_reason","no_signal_reason","manual_review_required","notes"
    ]
    signal_quality_fields = [
        "token_entity_id","token_symbol","anchor_event_id","signal_timestamp_utc","signal_type","signal_price","recent_low_price","stop_price","risk_pct","quote_volume_at_signal","volume_zscore_at_signal","bottom_liquidity_score","signal_liquidity_score","signal_confirmation_score","risk_management_score","execution_quality_score","data_quality_score","liquidity_score","confirmation_score","structure_score","risk_reward_score","source_quality_score","manual_review_penalty","signal_quality_score","final_tradeability_score","tradeability_tier","manual_review_required","notes"
    ]
    scenario_fields = [
        "token_entity_id","token_symbol","primary_bottom_rebound_scenario","secondary_flags","anchor_event_id","anchor_event_type","baseline_price","max_drawdown_after_event","days_to_bottom","max_rebound_after_bottom","rebound_sustained","pump_and_dump_after_bottom","low_liquidity_wick_flag","tradable_signal_found","best_signal_type","best_signal_risk_reward","scenario_confidence_score","manual_review_required","notes"
    ]
    epic_fields = [
        "token_entity_id","token_symbol","anchor_event_id","anchor_event_type","drawdown_before_rebound","days_from_event_to_bottom","max_rebound_after_bottom","days_from_bottom_to_rebound","volume_zscore_on_rebound","rebound_sustained","post_rebound_drawdown","fallback_used","suspicious_spike_flag","low_liquidity_flag","epic_similarity_score","manual_review_required","notes"
    ]
    case_fields = [
        "token_symbol","scenario","drawdown_to_bottom","max_rebound_after_bottom","tradable_signal_found","best_signal_type","signal_quality_score","tradeability_tier","stop_failed","max_adverse_excursion","max_favorable_excursion_7d","risk_reward_7d","manual_review_required","main_reason","notes"
    ]
    write_csv(outdir / f"bottom_analysis{suffix}.csv", bottom_rows, bottom_fields)
    write_csv(outdir / f"rebound_analysis{suffix}.csv", rebound_rows, rebound_fields)
    write_csv(outdir / f"tradable_bottom_signals{suffix}.csv", signal_rows, signal_fields)
    signal_quality_rows = build_signal_quality_rows(signal_rows)
    write_csv(outdir / f"signal_quality{suffix}.csv", signal_quality_rows, signal_quality_fields)
    write_csv(outdir / f"bottom_rebound_scenarios{suffix}.csv", scenario_rows, scenario_fields)
    write_csv(outdir / f"epic_like_cases{suffix}.csv", epic_rows, epic_fields)
    case_rows = build_case_comparison(scenario_rows, rebound_rows, signal_rows, no_signal_reasons)
    write_csv(outdir / f"bottom_rebound_case_comparison{suffix}.csv", case_rows, case_fields)

    risk_anchor_set = set(RISK_ANCHOR_EVENT_TYPES)
    token_risk_bottom_rows = [r for r in bottom_rows if r.get("anchor_event_type") in risk_anchor_set]
    token_risk_symbols = {r.get("token_symbol") for r in token_risk_bottom_rows}
    token_risk_signal_rows = [r for r in signal_rows if r.get("token_symbol") in token_risk_symbols]
    token_risk_epic_rows = [r for r in epic_rows if r.get("token_symbol") in token_risk_symbols]
    token_risk_manual = len(
        [
            r
            for r in scenario_rows
            if r.get("token_symbol") in token_risk_symbols and r.get("manual_review_required") == "yes"
        ]
    )
    token_risk_anchor_counts: dict[str, int] = {}
    for row in token_risk_bottom_rows:
        event_type = row.get("anchor_event_type", "")
        token_risk_anchor_counts[event_type] = token_risk_anchor_counts.get(event_type, 0) + 1

    report = ROOT / f"docs/bottom_rebound{suffix}_report.md"
    report.write_text(
        "\n".join(
            [
                f"# Bottom/Rebound {args.mode.title()} Report",
                "",
                "## Run Filters",
                "",
                f"- risk_only: {args.risk_only}",
                f"- control_only: {args.control_only}",
                f"- event_types: {sorted(allowed_event_types) if allowed_event_types else 'all'}",
                f"- start_index: {args.start_index}",
                f"- end_index: {args.end_index}",
                "",
                "## All Anchors",
                "",
                f"- tokens_requested: {qa['tokens_requested']}",
                f"- tokens_processed: {qa['processed']}",
                f"- anchor_events: {qa['anchors']}",
                f"- missing_1h_path: {qa['missing_1h_path']}",
                f"- absolute_bottoms_found: {len([r for r in bottom_rows if r.get('low_price') not in ['', None]])}",
                f"- tradable_signals_found: {len(signal_rows)}",
                f"- signal_quality_rows: {len(signal_quality_rows)}",
                f"- epic_like_rows: {len(epic_rows)}",
                f"- manual_review_count: {qa['manual_review']}",
                "",
                "## Token-Risk Relevant Anchors Only",
                "",
                f"- token_risk_tokens_processed: {len(token_risk_bottom_rows)}",
                f"- token_risk_anchor_events: {token_risk_anchor_counts}",
                f"- token_risk_missing_1h_path: {[r.get('token_symbol') for r in token_risk_bottom_rows if r.get('notes') == 'missing_1h_path']}",
                f"- token_risk_absolute_bottoms_found: {len([r for r in token_risk_bottom_rows if r.get('low_price') not in ['', None]])}",
                f"- token_risk_tradable_signals_found: {len(token_risk_signal_rows)}",
                f"- token_risk_epic_like_rows: {len(token_risk_epic_rows)}",
                f"- token_risk_manual_review_count: {token_risk_manual}",
                "",
                "Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"processed": qa["processed"], "signals": len(signal_rows), "manual_review": qa["manual_review"], "report": str(report)})


if __name__ == "__main__":
    main()
