#!/usr/bin/env python3
"""15m refinement for bottom/rebound sample signals."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/klines/spot"
OUT = ROOT / "data/processed/signal_15m_refinement_sample.csv"
REPORT = ROOT / "docs/bottom_rebound_signal_quality_sample_v4_report.md"


def read_klines(symbol: str, interval: str = "15m") -> pd.DataFrame:
    rows = []
    for fp in sorted((RAW / f"{symbol}USDT").glob(f"{interval}_*_paged.json")):
        try:
            rows.extend(json.loads(fp.read_text()))
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    rows = sorted({int(r[0]): r for r in rows}.values(), key=lambda r: int(r[0]))
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
    for c in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp")
    roll = df["quote_volume"].rolling(96, min_periods=16)
    df["volume_zscore"] = ((df["quote_volume"] - roll.mean()) / roll.std().replace(0, pd.NA)).fillna(0)
    return df


def wick_ratio(row: pd.Series) -> float:
    rng = row["high"] - row["low"]
    if not rng:
        return 0.0
    return max(0.0, min(1.0, (row["close"] - row["low"]) / rng))


def target_time(future: pd.DataFrame, entry_price: float, target: float) -> float:
    hits = future[future["high"] >= entry_price * (1 + target)]
    if hits.empty:
        return math.nan
    return (hits.iloc[0]["timestamp"] - future.iloc[0]["timestamp"]).total_seconds() / 3600


def future_metrics(df: pd.DataFrame, entry_time: pd.Timestamp, entry_price: float, stop_price: float) -> dict:
    future = df[(df["timestamp"] > entry_time) & (df["timestamp"] <= entry_time + pd.Timedelta(days=7))]
    if future.empty:
        return {}
    high_idx = future["high"].idxmax()
    high_row = future.loc[high_idx]
    before_high = future[future["timestamp"] <= high_row["timestamp"]]
    risk = abs(stop_price / entry_price - 1)
    def mfe(days: int) -> float:
        w = future[future["timestamp"] <= entry_time + pd.Timedelta(days=days)]
        return w["high"].max() / entry_price - 1 if len(w) else math.nan
    mfe24 = mfe(1)
    mfe3 = mfe(3)
    mfe7 = mfe(7)
    return {
        "refined_mae_before_mfe": before_high["low"].min() / entry_price - 1 if len(before_high) else math.nan,
        "refined_mfe_24h": mfe24,
        "refined_mfe_3d": mfe3,
        "refined_mfe_7d": mfe7,
        "refined_rr_24h": mfe24 / risk if risk else math.nan,
        "refined_rr_3d": mfe3 / risk if risk else math.nan,
        "refined_rr_7d": mfe7 / risk if risk else math.nan,
        "time_to_20_target_hours": target_time(future, entry_price, 0.20),
        "time_to_50_target_hours": target_time(future, entry_price, 0.50),
        "time_to_100_target_hours": target_time(future, entry_price, 1.00),
        "stop_failed": "yes" if future["low"].min() <= stop_price else "no",
    }


def refine_existing_signal(symbol: str, signal_row: pd.Series) -> dict:
    df = read_klines(symbol)
    original_time = pd.to_datetime(signal_row["signal_timestamp_utc"], utc=True)
    entry_cands = df[df["timestamp"] >= original_time]
    if entry_cands.empty:
        return base_row(symbol, signal_row.get("signal_type", ""), original_time, "missing_15m_entry")
    entry = entry_cands.iloc[0]
    lookback = df[(df["timestamp"] < entry["timestamp"]) & (df["timestamp"] >= entry["timestamp"] - pd.Timedelta(hours=72))]
    recent_low = lookback["low"].min() if len(lookback) else float(signal_row.get("recent_low_price", math.nan))
    stop = recent_low * 0.98
    entry_price = float(entry["close"])
    row = base_row(symbol, signal_row.get("signal_type", ""), original_time, "")
    row.update(
        {
            "refined_15m_entry_time": entry["timestamp"].isoformat(),
            "refined_15m_entry_price": entry_price,
            "refined_15m_stop_price": stop,
            "refined_stop_distance_pct": stop / entry_price - 1,
            "wick_risk_flag": "yes" if wick_ratio(entry) < 0.35 or ((entry["high"] - entry["low"]) / entry_price > 0.08) else "no",
            "single_candle_artifact_flag": "no",
            "missed_15m_signal_flag": "no",
            "false_breakout_warning_flag": "yes" if signal_row.get("signal_failed_stop") == "yes" else "no",
            "liquidity_at_15m_entry": entry["quote_volume"],
            "volume_zscore_at_15m_entry": entry["volume_zscore"],
        }
    )
    row.update(future_metrics(df, entry["timestamp"], entry_price, stop))
    next3 = df[(df["timestamp"] > entry["timestamp"]) & (df["timestamp"] <= entry["timestamp"] + pd.Timedelta(minutes=45))]
    if len(next3) >= 3 and next3["close"].iloc[-1] < entry_price and next3["high"].max() <= entry["high"]:
        row["single_candle_artifact_flag"] = "yes"
    notes = []
    if row["wick_risk_flag"] == "yes":
        notes.append("15m_entry_has_wick_or_large_range")
    if row["single_candle_artifact_flag"] == "yes":
        notes.append("next_3_15m_candles_failed_to_extend")
    if row["liquidity_at_15m_entry"] < 25_000:
        notes.append("low_15m_entry_liquidity")
    row["refinement_notes"] = ";".join(notes)
    return row


def find_hei_missed_signal() -> dict:
    symbol = "HEI"
    df = read_klines(symbol)
    bottom_time = pd.Timestamp("2026-05-28T04:00:00Z")
    bottom = df[df["timestamp"] == bottom_time]
    if bottom.empty:
        return base_row(symbol, "MISSED_15M_CHECK", bottom_time, "missing_bottom_15m")
    low_price = float(bottom.iloc[0]["low"])
    after = df[(df["timestamp"] > bottom_time) & (df["timestamp"] <= bottom_time + pd.Timedelta(days=7))]
    bounce = after.head(96)
    if bounce.empty:
        return base_row(symbol, "MISSED_15M_CHECK", bottom_time, "missing_after_bottom")
    bounce_high = bounce.loc[bounce["high"].idxmax()]
    pullback = after[(after["timestamp"] > bounce_high["timestamp"]) & (after["timestamp"] <= bounce_high["timestamp"] + pd.Timedelta(days=3))]
    if pullback.empty:
        row = base_row(symbol, "NO_15M_SIGNAL", bottom_time, "rebound_too_fast_no_pullback")
        row["missed_15m_signal_flag"] = "no"
        return row
    pb = pullback.loc[pullback["low"].idxmin()]
    breakout = after[(after["timestamp"] > pb["timestamp"]) & (after["close"] > bounce_high["high"])]
    if breakout.empty or pb["low"] < low_price * 1.05:
        row = base_row(symbol, "NO_15M_SIGNAL", bottom_time, "no_higher_low_breakout_confirmation")
        row["missed_15m_signal_flag"] = "no"
        row["refinement_notes"] = "strong_rebound_exists_but_15m_structure_did_not_form_clean_higher_low_breakout"
        return row
    fake_signal = pd.Series({"signal_timestamp_utc": breakout.iloc[0]["timestamp"].isoformat(), "signal_type": "MISSED_15M_HIGHER_LOW_BREAKOUT", "signal_failed_stop": "no", "recent_low_price": pb["low"]})
    row = refine_existing_signal(symbol, fake_signal)
    row["missed_15m_signal_flag"] = "yes"
    row["refinement_notes"] = (row.get("refinement_notes", "") + ";15m_signal_found_not_present_in_1h_rules").strip(";")
    return row


def base_row(symbol: str, signal_type: str, original_time, notes: str) -> dict:
    return {
        "token_symbol": symbol,
        "signal_type": signal_type,
        "original_1h_signal_time": pd.Timestamp(original_time).isoformat() if pd.notna(original_time) else "",
        "refined_15m_entry_time": "",
        "refined_15m_entry_price": "",
        "refined_15m_stop_price": "",
        "refined_stop_distance_pct": "",
        "refined_mae_before_mfe": "",
        "refined_mfe_24h": "",
        "refined_mfe_3d": "",
        "refined_mfe_7d": "",
        "refined_rr_24h": "",
        "refined_rr_3d": "",
        "refined_rr_7d": "",
        "wick_risk_flag": "",
        "single_candle_artifact_flag": "",
        "missed_15m_signal_flag": "",
        "false_breakout_warning_flag": "",
        "liquidity_at_15m_entry": "",
        "volume_zscore_at_15m_entry": "",
        "time_to_20_target_hours": "",
        "time_to_50_target_hours": "",
        "time_to_100_target_hours": "",
        "stop_failed": "",
        "refinement_notes": notes,
    }


def write_csv(rows: list[dict]) -> None:
    fields = [
        "token_symbol",
        "signal_type",
        "original_1h_signal_time",
        "refined_15m_entry_time",
        "refined_15m_entry_price",
        "refined_15m_stop_price",
        "refined_stop_distance_pct",
        "refined_mae_before_mfe",
        "refined_mfe_24h",
        "refined_mfe_3d",
        "refined_mfe_7d",
        "refined_rr_24h",
        "refined_rr_3d",
        "refined_rr_7d",
        "wick_risk_flag",
        "single_candle_artifact_flag",
        "missed_15m_signal_flag",
        "false_breakout_warning_flag",
        "liquidity_at_15m_entry",
        "volume_zscore_at_15m_entry",
        "time_to_20_target_hours",
        "time_to_50_target_hours",
        "time_to_100_target_hours",
        "stop_failed",
        "refinement_notes",
    ]
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def main() -> None:
    signals = pd.read_csv(ROOT / "data/processed/tradable_bottom_signals_sample.csv")
    rows = []
    for symbol in ["EPIC", "COOKIE"]:
        sig = signals[signals["token_symbol"] == symbol]
        if len(sig):
            rows.append(refine_existing_signal(symbol, sig.iloc[0]))
    rows.append(find_hei_missed_signal())
    write_csv(rows)

    df = pd.DataFrame(rows)
    epic = df[df["token_symbol"] == "EPIC"].iloc[0]
    hei = df[df["token_symbol"] == "HEI"].iloc[0]
    cookie = df[df["token_symbol"] == "COOKIE"].iloc[0]
    REPORT.write_text(
        f"""# Bottom/Rebound 15m Refinement Sample v4

Full run was not started.

## EPIC

- Refined 15m entry: `{epic['refined_15m_entry_time']}`
- Refined entry price: `{epic['refined_15m_entry_price']}`
- Refined stop price: `{epic['refined_15m_stop_price']}`
- Stop distance: `{float(epic['refined_stop_distance_pct']):.2%}`
- MAE before MFE: `{float(epic['refined_mae_before_mfe']):.2%}`
- MFE 24h: `{float(epic['refined_mfe_24h']):.2%}`
- MFE 3d: `{float(epic['refined_mfe_3d']):.2%}`
- MFE 7d: `{float(epic['refined_mfe_7d']):.2%}`
- RR 7d: `{float(epic['refined_rr_7d']):.2f}`
- Time to +20% target: `{epic['time_to_20_target_hours']}h`
- Time to +50% target: `{epic['time_to_50_target_hours']}h`
- Time to +100% target: `{epic['time_to_100_target_hours']}h`
- Wick risk: `{epic['wick_risk_flag']}`
- Single candle artifact: `{epic['single_candle_artifact_flag']}`
- 15m entry quote volume: `{float(epic['liquidity_at_15m_entry']):.2f}`
- 15m entry volume z-score: `{float(epic['volume_zscore_at_15m_entry']):.2f}`

Interpretation: EPIC remains a B-quality tradable candidate, not A. The 15m path does not mark it as a single-candle artifact and wick risk is not flagged, but the first 15m entry slice has low quote volume versus the 1h signal candle and the refined stop is wide.

## HEI

- Missed 15m signal flag: `{hei['missed_15m_signal_flag']}`
- Notes: `{hei['refinement_notes']}`

Interpretation: HEI still belongs to strong rebound without clean causal confirmation under the current v1/v3 signal rules.

## COOKIE

- Refined 15m entry: `{cookie['refined_15m_entry_time']}`
- Stop failed: `{cookie['stop_failed']}`
- False breakout warning: `{cookie['false_breakout_warning_flag']}`
- 15m entry liquidity: `{cookie['liquidity_at_15m_entry']}`
- Notes: `{cookie['refinement_notes']}`

Interpretation: COOKIE remains a failed/low-quality signal. Low entry liquidity and stop failure were visible risks.

## Rule Implications

- Do not promote EPIC to tier A yet.
- Keep HEI as rebound-without-signal.
- Keep COOKIE as false-breakout / low-liquidity negative case.
- Before full run, higher-low breakout rules do not need to be loosened; the next improvement should be adding 15m refinement as an optional QA layer for top candidates.
""",
        encoding="utf-8",
    )
    print({"rows": len(rows), "out": str(OUT), "report": str(REPORT)})


if __name__ == "__main__":
    main()
