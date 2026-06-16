#!/usr/bin/env python3
"""Optional 15m QA refinement for selected bottom/rebound signal candidates."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/klines/spot"
PROCESSED = ROOT / "data/processed"


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


def wick_position(row: pd.Series) -> float:
    rng = row["high"] - row["low"]
    if not rng:
        return 0.0
    return max(0.0, min(1.0, (row["close"] - row["low"]) / rng))


def target_time_hours(future: pd.DataFrame, entry_time: pd.Timestamp, entry_price: float, target: float) -> float:
    hits = future[future["high"] >= entry_price * (1 + target)]
    if hits.empty:
        return math.nan
    return (hits.iloc[0]["timestamp"] - entry_time).total_seconds() / 3600


def metrics_after_entry(df: pd.DataFrame, entry_time: pd.Timestamp, entry_price: float, stop_price: float) -> dict:
    future = df[(df["timestamp"] > entry_time) & (df["timestamp"] <= entry_time + pd.Timedelta(days=7))]
    if future.empty or not entry_price or not stop_price:
        return {}
    high_row = future.loc[future["high"].idxmax()]
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
        "time_to_20_target_hours": target_time_hours(future, entry_time, entry_price, 0.20),
        "time_to_50_target_hours": target_time_hours(future, entry_time, entry_price, 0.50),
        "time_to_100_target_hours": target_time_hours(future, entry_time, entry_price, 1.00),
        "stop_failed": "yes" if future["low"].min() <= stop_price else "no",
    }


def empty_row(symbol: str, notes: str) -> dict:
    return {
        "token_symbol": symbol,
        "signal_type": "NO_EXISTING_SIGNAL_15M_QA",
        "original_1h_signal_time": "",
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


def refine_signal(signal: pd.Series) -> dict:
    symbol = str(signal["token_symbol"]).upper()
    df = read_klines(symbol)
    if df.empty:
        return empty_row(symbol, "missing_15m_path")
    original_time = pd.to_datetime(signal["signal_timestamp_utc"], utc=True, errors="coerce")
    if pd.isna(original_time):
        return empty_row(symbol, "missing_signal_timestamp")
    entry_cands = df[df["timestamp"] >= original_time]
    if entry_cands.empty:
        return empty_row(symbol, "missing_15m_entry_after_signal")
    entry = entry_cands.iloc[0]
    lookback = df[(df["timestamp"] < entry["timestamp"]) & (df["timestamp"] >= entry["timestamp"] - pd.Timedelta(hours=72))]
    recent_low = lookback["low"].min() if len(lookback) else pd.to_numeric(signal.get("recent_low_price"), errors="coerce")
    stop = float(recent_low) * 0.98 if pd.notna(recent_low) else math.nan
    entry_price = float(entry["close"])
    candle_range = (entry["high"] - entry["low"]) / entry_price if entry_price else math.nan
    row = empty_row(symbol, "")
    row.update(
        {
            "signal_type": signal.get("signal_type", ""),
            "original_1h_signal_time": original_time.isoformat(),
            "refined_15m_entry_time": entry["timestamp"].isoformat(),
            "refined_15m_entry_price": entry_price,
            "refined_15m_stop_price": stop,
            "refined_stop_distance_pct": stop / entry_price - 1 if entry_price and pd.notna(stop) else math.nan,
            "wick_risk_flag": "yes" if wick_position(entry) < 0.35 or candle_range > 0.08 else "no",
            "single_candle_artifact_flag": "no",
            "missed_15m_signal_flag": "no",
            "false_breakout_warning_flag": "yes" if signal.get("signal_failed_stop") == "yes" else "no",
            "liquidity_at_15m_entry": entry["quote_volume"],
            "volume_zscore_at_15m_entry": entry["volume_zscore"],
        }
    )
    row.update(metrics_after_entry(df, entry["timestamp"], entry_price, stop))
    next3 = df[(df["timestamp"] > entry["timestamp"]) & (df["timestamp"] <= entry["timestamp"] + pd.Timedelta(minutes=45))]
    if len(next3) >= 3 and next3["close"].iloc[-1] < entry_price and next3["high"].max() <= entry["high"]:
        row["single_candle_artifact_flag"] = "yes"
    notes = []
    if row["wick_risk_flag"] == "yes":
        notes.append("15m_entry_has_wick_or_large_range")
    if row["single_candle_artifact_flag"] == "yes":
        notes.append("next_3_15m_candles_failed_to_extend")
    if float(row["liquidity_at_15m_entry"]) < 25_000:
        notes.append("low_15m_entry_liquidity")
    row["refinement_notes"] = ";".join(notes)
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-signals", default=str(PROCESSED / "tradable_bottom_signals_sample.csv"))
    parser.add_argument("--tokens", help="Comma-separated selected tokens. Defaults to all tokens in input signals.")
    parser.add_argument("--output", default=str(PROCESSED / "signal_15m_refinement.csv"))
    args = parser.parse_args()

    signals = pd.read_csv(args.input_signals)
    selected = [t.strip().upper() for t in args.tokens.split(",")] if args.tokens else sorted(signals["token_symbol"].dropna().astype(str).str.upper().unique())
    rows = []
    for symbol in selected:
        token_signals = signals[signals["token_symbol"].astype(str).str.upper() == symbol]
        if token_signals.empty:
            rows.append(empty_row(symbol, "no_existing_1h_signal_for_selected_token"))
            continue
        for _, signal in token_signals.iterrows():
            rows.append(refine_signal(signal))
    write_csv(Path(args.output), rows)
    print({"rows": len(rows), "output": args.output})


if __name__ == "__main__":
    main()
