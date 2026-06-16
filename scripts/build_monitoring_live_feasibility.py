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


def yn(value: Any) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


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
        self.cache: dict[tuple[str, str, str], pd.DataFrame] = {}

    def load(self, pair: str, market_type: str, interval: str = "1h") -> pd.DataFrame:
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


def iso(ts: pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def has_futures_path(store: KlineStore, pair: str, event_time: pd.Timestamp) -> bool:
    df = store.load(pair, "futures", "1h")
    if df.empty or pd.isna(event_time):
        return False
    start = event_time - pd.Timedelta(days=1)
    end = event_time + pd.Timedelta(days=1)
    return not df[(df["open_time"] >= start) & (df["open_time"] <= end)].empty


def max_close_gap(path: pd.DataFrame) -> float:
    if path.empty or len(path) < 2:
        return np.nan
    closes = pd.to_numeric(path["close"], errors="coerce")
    return float(closes.pct_change().abs().max())


def first_hour_wick(df: pd.DataFrame, event_time: pd.Timestamp) -> tuple[float, float]:
    if df.empty or pd.isna(event_time):
        return np.nan, np.nan
    sub = df[df["open_time"] >= event_time].head(1)
    if sub.empty:
        return np.nan, np.nan
    row = sub.iloc[0]
    close = float(row["close"])
    if close <= 0:
        return np.nan, np.nan
    up = float(row["high"]) / close - 1
    down = close / float(row["low"]) - 1 if float(row["low"]) > 0 else np.nan
    return up, down


def event_cluster_flag(events: pd.DataFrame, token_symbol: str, event_id: str, event_time: pd.Timestamp) -> str:
    token_events = events[(events["token_symbol"].astype(str) == token_symbol) & (events["event_id"].astype(str) != str(event_id))].copy()
    if token_events.empty or pd.isna(event_time):
        return "no"
    token_events["dt"] = pd.to_datetime(token_events["publication_datetime_utc"], utc=True, errors="coerce")
    delta_days = (token_events["dt"] - event_time).abs().dt.total_seconds() / 86400
    return "yes" if (delta_days <= 7).any() else "no"


def feasibility_tier(row: dict[str, Any]) -> tuple[str, str]:
    reasons = []
    if row["missing_1h_path"] == "yes":
        return "low", "missing_1h_path"
    if row["low_liquidity_flag"] == "yes":
        reasons.append("low_liquidity")
    if row["fallback_only_path"] == "yes":
        reasons.append("fallback_only_path")
    if row["extreme_first_hour_wick_gap"] == "yes":
        reasons.append("extreme_first_hour_wick_gap")
    if row["abnormal_candle_gap"] == "yes":
        reasons.append("abnormal_candle_gap")
    if row["borrow_availability_unknown"] == "yes":
        reasons.append("borrow_unknown")
    if reasons:
        hard = {"low_liquidity", "fallback_only_path", "extreme_first_hour_wick_gap", "abnormal_candle_gap"}
        tier = "low" if hard.intersection(reasons) else "medium"
        return tier, ";".join(reasons)
    if row["quote_volume_24h_around_entry"] >= 10_000_000 and row["zero_volume_candle_count"] == 0 and row["live_shortability_confidence"] in {"medium", "high"}:
        return "high", "liquid_volume_stable_candles_derivative_proxy"
    return "medium", "moderate_volume_or_shortability_uncertain"


def build_feasibility() -> pd.DataFrame:
    trades = read_csv("backtest_trades.csv")
    execution = read_csv("execution_features.csv")
    universe = read_csv("clean_research_universe.csv")
    events = read_csv("events.csv")
    scenarios = read_csv("scenario_classification.csv")
    resolution = read_csv("price_resolution.csv") if (PROCESSED / "price_resolution.csv").exists() else pd.DataFrame()

    candidates = trades[
        (trades["hypothesis"] == "monitoring_tag_failed_recovery_delayed_collapse")
        & (trades["sub_strategy"] == "tag_immediate_1h")
        & (trades["roundtrip_cost_bps"] == 0)
        & (trades["status"] == "ok")
    ].copy()
    exec_small = execution[
        [
            "event_id",
            "return_1h",
            "return_24h",
            "max_adverse_excursion_24h",
            "max_favorable_excursion_24h",
            "path_data_available_24h",
            "path_data_available_7d",
        ]
    ].drop_duplicates("event_id")
    candidates = candidates.merge(exec_small, on="event_id", how="left")
    candidates = candidates[pd.to_numeric(candidates["return_1h"], errors="coerce") < 0].copy()
    candidates = candidates.merge(
        universe[
            [
                "token_symbol",
                "token_entity_id",
                "is_research_eligible",
                "exclusion_reason",
                "data_quality_score",
                "true_data_gap_rate",
                "benchmark_gap_rate",
                "fallback_provider",
                "spot_pair",
                "futures_pair",
            ]
        ].drop_duplicates("token_symbol"),
        on="token_symbol",
        how="left",
    )
    candidates = candidates.merge(
        scenarios[["token_symbol", "primary_scenario", "manual_review_required", "fallback_used"]].drop_duplicates("token_symbol"),
        on="token_symbol",
        how="left",
    )
    if not resolution.empty:
        candidates = candidates.merge(
            resolution[["token_symbol", "futures_pair", "futures_missing", "exact_futures_contract"]].drop_duplicates("token_symbol"),
            on="token_symbol",
            how="left",
            suffixes=("", "_resolution"),
        )

    store = KlineStore()
    rows = []
    for _, row in candidates.iterrows():
        token = str(row["token_symbol"])
        pair = str(row["symbol_pair"])
        event_id = str(row["event_id"])
        event_time = pd.to_datetime(row["event_time"], utc=True, errors="coerce")
        entry_time = pd.to_datetime(row["entry_time"], utc=True, errors="coerce")
        df = store.load(pair, "spot", "1h")
        missing_path = df.empty
        before = pd.DataFrame()
        after = pd.DataFrame()
        around = pd.DataFrame()
        pre_confirmation = pd.DataFrame()
        if not missing_path:
            before = df[(df["open_time"] >= entry_time - pd.Timedelta(hours=24)) & (df["open_time"] < entry_time)]
            after = df[(df["open_time"] >= entry_time) & (df["open_time"] < entry_time + pd.Timedelta(hours=24))]
            around = df[(df["open_time"] >= entry_time - pd.Timedelta(hours=24)) & (df["open_time"] < entry_time + pd.Timedelta(hours=24))]
            pre_confirmation = df[(df["open_time"] >= event_time) & (df["open_time"] <= entry_time)]

        quote_24h = float(after["quote_volume"].sum()) if not after.empty and after["quote_volume"].notna().any() else np.nan
        base_24h = float(after["volume"].sum()) if not after.empty else np.nan
        med_before = float(before["quote_volume"].median()) if not before.empty and before["quote_volume"].notna().any() else np.nan
        med_after = float(after["quote_volume"].median()) if not after.empty and after["quote_volume"].notna().any() else np.nan
        zero_count = int((around["volume"] <= 0).sum()) if not around.empty else np.nan
        deterioration = (med_after / med_before - 1) if med_before and med_before > 0 and pd.notna(med_after) else np.nan
        first_up_wick, first_down_wick = first_hour_wick(df, event_time)
        pre_high_adv = np.nan
        if not pre_confirmation.empty and float(row["entry_price"]) > 0:
            pre_high_adv = float(pre_confirmation["high"].max()) / float(row["entry_price"]) - 1

        close_gap = max_close_gap(around)
        fallback_history_used = pd.notna(row.get("fallback_provider")) and str(row.get("fallback_provider")) != ""
        fallback_only = missing_path and fallback_history_used
        low_liquidity = (
            pd.isna(quote_24h)
            or quote_24h < 1_000_000
            or (pd.notna(med_after) and med_after < 25_000)
            or (not pd.isna(zero_count) and zero_count > 0)
        )
        extreme_first = (
            (pd.notna(first_up_wick) and first_up_wick >= 0.20)
            or (pd.notna(first_down_wick) and first_down_wick >= 0.20)
            or (pd.notna(pre_high_adv) and pre_high_adv >= 0.20)
        )
        abnormal_gap = pd.notna(close_gap) and close_gap >= 0.25
        event_clustered = event_cluster_flag(events, token, event_id, event_time)

        fut_pair = row.get("futures_pair_resolution")
        if pd.isna(fut_pair) or str(fut_pair) == "":
            fut_pair = row.get("futures_pair")
        futures_available = has_futures_path(store, str(fut_pair), event_time) if pd.notna(fut_pair) and str(fut_pair) else False
        borrow_unknown = "no" if futures_available else "yes"
        short_conf = "medium" if futures_available else "unknown"

        out = {
            "event_id": event_id,
            "token_entity_id": row.get("token_entity_id"),
            "token_symbol": token,
            "event_type": row["event_type"],
            "scenario": row.get("primary_scenario", row.get("scenario")),
            "confidence_tier": row["confidence_tier"],
            "symbol_pair": pair,
            "event_time": iso(event_time),
            "entry_time": iso(entry_time),
            "entry_price": row["entry_price"],
            "gross_return": row["gross_return"],
            "return_1h": row.get("return_1h"),
            "return_24h": row.get("return_24h"),
            "max_adverse_excursion": row["max_adverse_excursion"],
            "max_favorable_excursion": row["max_favorable_excursion"],
            "quote_volume_24h_around_entry": quote_24h,
            "base_volume_24h_around_entry": base_24h,
            "median_1h_quote_volume_before_entry": med_before,
            "median_1h_quote_volume_after_entry": med_after,
            "zero_volume_candle_count": zero_count,
            "volume_deterioration_after_event": deterioration,
            "low_liquidity_flag": "yes" if low_liquidity else "no",
            "extreme_first_hour_wick_gap": "yes" if extreme_first else "no",
            "first_hour_up_wick": first_up_wick,
            "first_hour_down_wick": first_down_wick,
            "huge_adverse_move_before_confirmation": "yes" if pd.notna(pre_high_adv) and pre_high_adv >= 0.20 else "no",
            "pre_confirmation_adverse_move": pre_high_adv,
            "missing_1h_path": "yes" if missing_path else "no",
            "fallback_only_path": "yes" if fallback_only else "no",
            "fallback_history_used_elsewhere": "yes" if fallback_history_used else "no",
            "abnormal_candle_gap": "yes" if abnormal_gap else "no",
            "max_abs_1h_close_gap_around_entry": close_gap,
            "event_clustered_with_another_risk_event": event_clustered,
            "futures_pair_proxy": fut_pair if pd.notna(fut_pair) else "",
            "futures_available_around_event_proxy": "yes" if futures_available else "no",
            "borrow_availability_unknown": borrow_unknown,
            "live_shortability_confidence": short_conf,
            "is_research_eligible": row.get("is_research_eligible"),
            "exclusion_reason": row.get("exclusion_reason"),
            "data_quality_score": row.get("data_quality_score"),
            "true_data_gap_rate": row.get("true_data_gap_rate"),
            "benchmark_gap_rate": row.get("benchmark_gap_rate"),
            "manual_review_required": row.get("manual_review_required"),
            "fallback_used": row.get("fallback_used"),
        }
        tier, reason = feasibility_tier(out)
        out["feasibility_tier"] = tier
        out["feasibility_reason"] = reason
        out["slippage_proxy_tier"] = tier
        for cost in COST_BPS:
            out[f"net_return_{cost}bps"] = float(row["gross_return"]) - cost / 10000
        rows.append(out)

    result = pd.DataFrame(rows).sort_values(["event_time", "token_symbol"]).reset_index(drop=True)
    result.to_csv(PROCESSED / "monitoring_live_feasibility.csv", index=False)
    result.to_parquet(PROCESSED / "monitoring_live_feasibility.parquet", index=False)
    return result


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    views = [
        ("all_candidate_trades", pd.Series(True, index=df.index)),
        ("high_medium_feasibility", df["feasibility_tier"].isin(["high", "medium"])),
        ("high_feasibility_only", df["feasibility_tier"].eq("high")),
        ("excluding_low_liquidity", df["low_liquidity_flag"].ne("yes")),
        ("excluding_extreme_wick_gap", df["extreme_first_hour_wick_gap"].ne("yes") & df["abnormal_candle_gap"].ne("yes")),
        ("excluding_unknown_shortability", df["borrow_availability_unknown"].ne("yes")),
    ]
    rows = []
    for view_name, mask in views:
        sub = df[mask].copy()
        for cost in COST_BPS:
            col = f"net_return_{cost}bps"
            ret = pd.to_numeric(sub[col], errors="coerce").dropna()
            mae = pd.to_numeric(sub["max_adverse_excursion"], errors="coerce")
            mfe = pd.to_numeric(sub["max_favorable_excursion"], errors="coerce")
            rows.append(
                {
                    "view": view_name,
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
    return pd.DataFrame(rows)


def write_report(df: pd.DataFrame) -> None:
    summary = summarize(df)
    summary.to_csv(PROCESSED / "monitoring_live_feasibility_summary.csv", index=False)

    main = summary[summary["cost_bps"] == 100].copy()
    table = main.copy()
    for c in ["win_rate", "median_return", "average_return", "p25_return", "p75_return", "worst_trade", "best_trade", "median_mae", "median_mfe"]:
        table[c] = table[c].map(pct)

    cost = summary[summary["view"].isin(["all_candidate_trades", "high_medium_feasibility"])].copy()
    for c in ["win_rate", "median_return", "average_return", "profit_factor"]:
        if c == "profit_factor":
            continue
        cost[c] = cost[c].map(pct)

    counts = {
        "candidate_trades": len(df),
        "high": int(df["feasibility_tier"].eq("high").sum()),
        "medium": int(df["feasibility_tier"].eq("medium").sum()),
        "low": int(df["feasibility_tier"].eq("low").sum()),
        "low_liquidity": int(df["low_liquidity_flag"].eq("yes").sum()),
        "extreme_wick_gap": int(df["extreme_first_hour_wick_gap"].eq("yes").sum()),
        "abnormal_gap": int(df["abnormal_candle_gap"].eq("yes").sum()),
        "fallback_only": int(df["fallback_only_path"].eq("yes").sum()),
        "borrow_unknown": int(df["borrow_availability_unknown"].eq("yes").sum()),
        "futures_proxy_available": int(df["futures_available_around_event_proxy"].eq("yes").sum()),
        "clustered": int(df["event_clustered_with_another_risk_event"].eq("yes").sum()),
    }

    report = [
        "# Monitoring Live Feasibility v1",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: only the recommended Monitoring Tag candidate rule: `immediate_1h_confirmation + negative_1h_confirmation`.",
        "",
        "This is not a live tradability claim. It separates the historical market signal from execution feasibility proxies. The biggest unresolved blocker is true borrow/shortability data.",
        "",
        "## Candidate Universe",
        "",
        f"- Candidate trades: {counts['candidate_trades']}",
        f"- Feasibility tiers: high={counts['high']}, medium={counts['medium']}, low={counts['low']}",
        f"- Low liquidity flags: {counts['low_liquidity']}",
        f"- Extreme first-hour wick/gap flags: {counts['extreme_wick_gap']}",
        f"- Abnormal candle gap flags: {counts['abnormal_gap']}",
        f"- Fallback-only path flags: {counts['fallback_only']}",
        f"- Futures/perp proxy available around event: {counts['futures_proxy_available']}",
        f"- Borrow availability unknown: {counts['borrow_unknown']}",
        f"- Event clustered with another risk event within +/-7d: {counts['clustered']}",
        "",
        "## Metrics by Feasibility View at 100 bps",
        "",
        table.to_markdown(index=False),
        "",
        "## Cost Sensitivity Snapshot",
        "",
        cost[["view", "cost_bps", "n_trades", "win_rate", "median_return", "average_return", "profit_factor"]].to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- The historical signal remains separate from execution feasibility. A trade can have good retrospective return and still be untradeable if borrow, depth, or spread is unavailable.",
        "- `high` feasibility requires strong quote volume, stable candles, no low-liquidity flags, and a futures/perp proxy around the event. This is only a proxy for shortability, not proof of borrow availability.",
        "- `medium` usually means market path is usable but shortability is unknown or volume is only moderate.",
        "- `low` means at least one hard execution issue appears: low liquidity, fallback-only path, abnormal gap, missing path, or extreme wick/gap.",
        "- Excluding unknown shortability is intentionally strict and may leave too few trades if futures proxy coverage is incomplete.",
        "",
        "## Additional Data Required Before Live Claims",
        "",
        "- Historical order book snapshots or bid/ask spreads around event and entry.",
        "- Borrow availability and borrow fee history for spot margin shorts.",
        "- Perp listing status at event time, funding rate, open interest, and liquidation intensity.",
        "- Venue-specific max order size, market impact estimates, and maintenance/outage flags.",
        "- Cross-venue liquidity if Binance spot is deteriorating after the tag.",
        "",
    ]
    (DOCS / "monitoring_live_feasibility_report.md").write_text("\n".join(report))


def main() -> None:
    df = build_feasibility()
    write_report(df)
    print(
        {
            "rows": int(len(df)),
            "output_csv": str(PROCESSED / "monitoring_live_feasibility.csv"),
            "report": str(DOCS / "monitoring_live_feasibility_report.md"),
        }
    )


if __name__ == "__main__":
    main()
