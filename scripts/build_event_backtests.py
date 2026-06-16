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


ROUNDTRIP_COST_BPS = [0, 20]


def yn(value: Any) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


def safe_float(value: Any) -> float | None:
    v = pd.to_numeric(value, errors="coerce")
    if pd.isna(v):
        return None
    return float(v)


def iso(ts: pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


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
        if not frames:
            df = pd.DataFrame()
        else:
            df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        self.cache[key] = df
        return df


@dataclass
class TradeSpec:
    hypothesis: str
    sub_strategy: str
    token_symbol: str
    event_id: str
    event_type: str
    scenario: str
    confidence_tier: str
    pair: str
    market_type: str
    event_time: pd.Timestamp
    entry_time: pd.Timestamp
    entry_price: float
    stop_loss_pct: float
    take_profit_pct: float
    max_holding_days: int
    entry_rule: str
    invalidation_rule: str
    lower_confidence_sensitivity: str = "no"


def nearest_close_after(df: pd.DataFrame, ts: pd.Timestamp) -> tuple[pd.Timestamp | None, float | None]:
    if df.empty or pd.isna(ts):
        return None, None
    sub = df[df["open_time"] >= ts]
    if sub.empty:
        return None, None
    row = sub.iloc[0]
    return pd.Timestamp(row["close_time"]), float(row["close"])


def first_pump_confirmation(
    df: pd.DataFrame,
    event_time: pd.Timestamp,
    baseline: float,
    threshold: float = 0.20,
    max_hours: int = 72,
) -> tuple[pd.Timestamp | None, float | None]:
    if df.empty or baseline <= 0:
        return None, None
    end = event_time + pd.Timedelta(hours=max_hours)
    sub = df[(df["open_time"] >= event_time) & (df["open_time"] <= end)]
    if sub.empty:
        return None, None
    hit = sub[sub["high"] >= baseline * (1 + threshold)]
    if hit.empty:
        return None, None
    row = hit.iloc[0]
    return pd.Timestamp(row["close_time"]), float(row["close"])


def first_failed_breakout_after_pump(
    df: pd.DataFrame,
    pump_time: pd.Timestamp,
    baseline: float,
    failure_level: float = 0.10,
    max_hours_after_pump: int = 72,
) -> tuple[pd.Timestamp | None, float | None]:
    if df.empty or baseline <= 0 or pd.isna(pump_time):
        return None, None
    end = pump_time + pd.Timedelta(hours=max_hours_after_pump)
    sub = df[(df["open_time"] > pump_time) & (df["open_time"] <= end)]
    if sub.empty:
        return None, None
    failed = sub[sub["close"] <= baseline * (1 + failure_level)]
    if failed.empty:
        return None, None
    row = failed.iloc[0]
    return pd.Timestamp(row["close_time"]), float(row["close"])


def simulate_short_trade(store: KlineStore, spec: TradeSpec, roundtrip_cost_bps: int) -> dict[str, Any]:
    df = store.load(spec.pair, spec.market_type, "1h")
    if df.empty:
        df = store.load(spec.pair, spec.market_type, "15m")
    end_time = spec.entry_time + pd.Timedelta(days=spec.max_holding_days)
    path = df[(df["open_time"] > spec.entry_time) & (df["open_time"] <= end_time)].copy()
    if path.empty:
        return {**spec.__dict__, "roundtrip_cost_bps": roundtrip_cost_bps, "status": "no_path_data"}

    sl_price = spec.entry_price * (1 + spec.stop_loss_pct)
    tp_price = spec.entry_price * (1 - spec.take_profit_pct)
    exit_reason = "time_exit"
    exit_time = pd.Timestamp(path.iloc[-1]["close_time"])
    exit_price = float(path.iloc[-1]["close"])
    time_to_sl = np.nan
    time_to_tp = np.nan

    max_high = float(path["high"].max())
    min_low = float(path["low"].min())
    mae = max_high / spec.entry_price - 1
    mfe = spec.entry_price / min_low - 1

    for _, row in path.iterrows():
        high = float(row["high"])
        low = float(row["low"])
        ts = pd.Timestamp(row["close_time"])
        # Conservative same-candle handling for shorts: stop is counted before TP.
        if high >= sl_price:
            exit_reason = "stop_loss"
            exit_time = ts
            exit_price = sl_price
            time_to_sl = (exit_time - spec.entry_time).total_seconds() / 3600
            break
        if low <= tp_price:
            exit_reason = "take_profit"
            exit_time = ts
            exit_price = tp_price
            time_to_tp = (exit_time - spec.entry_time).total_seconds() / 3600
            break

    gross_return = spec.entry_price / exit_price - 1
    net_return = gross_return - roundtrip_cost_bps / 10000
    return {
        "hypothesis": spec.hypothesis,
        "sub_strategy": spec.sub_strategy,
        "token_symbol": spec.token_symbol,
        "event_id": spec.event_id,
        "event_type": spec.event_type,
        "scenario": spec.scenario,
        "confidence_tier": spec.confidence_tier,
        "symbol_pair": spec.pair,
        "market_type": spec.market_type,
        "event_time": iso(spec.event_time),
        "entry_time": iso(spec.entry_time),
        "entry_price": spec.entry_price,
        "entry_rule": spec.entry_rule,
        "invalidation_rule": spec.invalidation_rule,
        "stop_loss_pct": spec.stop_loss_pct,
        "take_profit_pct": spec.take_profit_pct,
        "max_holding_days": spec.max_holding_days,
        "exit_time": iso(exit_time),
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "gross_return": gross_return,
        "roundtrip_cost_bps": roundtrip_cost_bps,
        "net_return": net_return,
        "win": "yes" if net_return > 0 else "no",
        "max_adverse_excursion": mae,
        "max_favorable_excursion": mfe,
        "time_to_tp_hours": time_to_tp,
        "time_to_sl_hours": time_to_sl,
        "risk_reward_realized": (mfe / mae) if mae and mae > 0 else np.nan,
        "lower_confidence_sensitivity": spec.lower_confidence_sensitivity,
        "status": "ok",
    }


def build_specs() -> list[TradeSpec]:
    clean = read_csv("clean_research_universe.csv")
    execution = read_csv("execution_features.csv")
    pump = read_csv("pump_fade_features.csv")
    monitoring = read_csv("monitoring_tag_path_features.csv")
    events = read_csv("events.csv")

    event_map = events.set_index("event_id").to_dict("index")
    clean_map = clean.set_index("token_symbol").to_dict("index")
    store = KlineStore()
    specs: list[TradeSpec] = []

    eligible_tokens = set(clean.loc[clean["is_research_eligible"] == "yes", "token_symbol"].astype(str))
    sensitivity_tokens = set(
        clean.loc[
            (clean["is_research_eligible"] != "yes")
            & (~clean["primary_scenario"].isin(["PAIR_REMOVAL_ONLY", "UNKNOWN_MANUAL_REVIEW"]))
            & (~clean["exclusion_reason"].fillna("").str.contains("unresolved_pair_or_symbol|suspicious_fallback_spike")),
            "token_symbol",
        ].astype(str)
    )

    # 1. Spot delisting announcement shock.
    shock = execution[
        (execution["event_type"] == "SPOT_TOKEN_DELISTING_ANNOUNCED")
        & (execution["market_type"] == "spot")
        & (execution["path_data_available_7d"] == "yes")
        & (execution["token_symbol"].astype(str).isin(eligible_tokens | sensitivity_tokens))
    ].copy()
    for _, row in shock.iterrows():
        token = str(row["token_symbol"])
        lower = "no" if token in eligible_tokens else "yes"
        ev_time = pd.to_datetime(row["event_time"], utc=True)
        pair = str(row["symbol_pair"])
        df1h = store.load(pair, "spot", "1h")
        for delay_hours, sub, sl, tp, hold in [
            (1, "immediate_1h_confirmation", 0.18, 0.30, 7),
            (24, "rebound_failure_24h", 0.12, 0.30, 7),
            (24, "rebound_failure_24h_hold30", 0.15, 0.50, 30),
        ]:
            if sub.startswith("rebound_failure") and str(row.get("vwap_reclaim_failure")) != "yes":
                continue
            entry_time, entry_price = nearest_close_after(df1h, ev_time + pd.Timedelta(hours=delay_hours))
            if entry_price is None:
                continue
            specs.append(
                TradeSpec(
                    hypothesis="spot_delisting_announcement_shock",
                    sub_strategy=sub,
                    token_symbol=token,
                    event_id=str(row["event_id"]),
                    event_type=str(row["event_type"]),
                    scenario=str(row["scenario"]),
                    confidence_tier=str(row["confidence_level"]) if lower == "no" else "low_sensitivity",
                    pair=pair,
                    market_type="spot",
                    event_time=ev_time,
                    entry_time=entry_time,
                    entry_price=entry_price,
                    stop_loss_pct=sl,
                    take_profit_pct=tp,
                    max_holding_days=hold,
                    entry_rule=f"short after {delay_hours}h confirmation; rebound variant requires vwap_reclaim_failure=yes",
                    invalidation_rule="stop if price trades above entry by SL pct; conceptual invalidation on sustained baseline reclaim",
                    lower_confidence_sensitivity=lower,
                )
            )

    # 2. Delisting pump fade after pump confirmation.
    pump_candidates = pump[
        (pump["token_symbol"].astype(str).isin(eligible_tokens | sensitivity_tokens))
        & (pump["manual_review_required"].astype(str) != "yes")
    ].copy()
    for _, row in pump_candidates.iterrows():
        token = str(row["token_symbol"])
        c = clean_map.get(token, {})
        lower = "no" if token in eligible_tokens else "yes"
        ev = event_map.get(str(row["event_id"]), {})
        ev_time = pd.to_datetime(row["event_time"], utc=True)
        pair = str(c.get("spot_pair", ""))
        if not pair or pair == "nan":
            continue
        df1h = store.load(pair, "spot", "1h")
        baseline = safe_float(read_csv("pump_analysis.csv").set_index("event_id").loc[str(row["event_id"]), "baseline_price"])
        if baseline is None:
            continue
        pump_time, _pump_price = first_pump_confirmation(df1h, ev_time, baseline, threshold=0.20, max_hours=72)
        entry_time, entry_price = first_failed_breakout_after_pump(df1h, pump_time, baseline, failure_level=0.10, max_hours_after_pump=72)
        if entry_price is None:
            continue
        specs.append(
                TradeSpec(
                    hypothesis="delisting_pump_fade_after_failed_breakout",
                    sub_strategy="pump20_failed_breakout_fade",
                token_symbol=token,
                event_id=str(row["event_id"]),
                event_type=str(ev.get("event_type", "SPOT_TOKEN_DELISTING_ANNOUNCED")),
                scenario=str(row["scenario"]),
                confidence_tier=str(row["confidence_level"]) if lower == "no" else "low_sensitivity",
                pair=pair,
                market_type="spot",
                event_time=ev_time,
                entry_time=entry_time,
                entry_price=entry_price,
                stop_loss_pct=0.20,
                take_profit_pct=0.40,
                max_holding_days=7,
                entry_rule="short after +20% pump confirmation and subsequent 1h close back below baseline +10%",
                invalidation_rule="stop if price trades 20% above failed-breakout entry price",
                lower_confidence_sensitivity=lower,
            )
        )

    # 3. Monitoring Tag delayed-collapse.
    mon = monitoring[
        (monitoring["token_symbol"].astype(str).isin(eligible_tokens | sensitivity_tokens))
        & (monitoring["path_data_available_90d"] == "yes")
    ].copy()
    for _, row in mon.iterrows():
        token = str(row["token_symbol"])
        c = clean_map.get(token, {})
        lower = "no" if token in eligible_tokens else "yes"
        ev_time = pd.to_datetime(row["event_time"], utc=True)
        pair = str(c.get("spot_pair", ""))
        if not pair or pair == "nan":
            continue
        df1h = store.load(pair, "spot", "1h")
        scenario = str(row["scenario"])
        for delay_hours, sub, sl, tp, hold in [
            (1, "tag_immediate_1h", 0.20, 0.30, 30),
            (24, "tag_24h_delay", 0.18, 0.30, 30),
            (24 * 7, "tag_7d_delay", 0.20, 0.45, 90),
        ]:
            entry_time, entry_price = nearest_close_after(df1h, ev_time + pd.Timedelta(hours=delay_hours))
            if entry_price is None:
                continue
            specs.append(
                TradeSpec(
                    hypothesis="monitoring_tag_failed_recovery_delayed_collapse",
                    sub_strategy=sub,
                    token_symbol=token,
                    event_id=str(row["event_id"]),
                    event_type="MONITORING_TAG_ADDED",
                    scenario=scenario,
                    confidence_tier=str(row["confidence_level"]) if lower == "no" else "low_sensitivity",
                    pair=pair,
                    market_type="spot",
                    event_time=ev_time,
                    entry_time=entry_time,
                    entry_price=entry_price,
                    stop_loss_pct=sl,
                    take_profit_pct=tp,
                    max_holding_days=hold,
                    entry_rule=f"short after Monitoring Tag plus {delay_hours}h delay",
                    invalidation_rule="stop by fixed SL; conceptual invalidation on sustained 90/100% pre-tag baseline reclaim",
                    lower_confidence_sensitivity=lower,
                )
            )
        # Failed-recovery trigger: only information available by +7d is used.
        r7 = safe_float(row.get("return_7d_after_tag"))
        failed_trigger = r7 is not None and r7 < 0
        if failed_trigger:
            entry_time, entry_price = nearest_close_after(df1h, ev_time + pd.Timedelta(days=7))
            if entry_price is not None:
                specs.append(
                    TradeSpec(
                        hypothesis="monitoring_tag_failed_recovery_delayed_collapse",
                        sub_strategy="failed_recovery_7d_trigger",
                        token_symbol=token,
                        event_id=str(row["event_id"]),
                        event_type="MONITORING_TAG_ADDED",
                        scenario=scenario,
                        confidence_tier=str(row["confidence_level"]) if lower == "no" else "low_sensitivity",
                        pair=pair,
                        market_type="spot",
                        event_time=ev_time,
                        entry_time=entry_time,
                        entry_price=entry_price,
                        stop_loss_pct=0.18,
                        take_profit_pct=0.45,
                        max_holding_days=90,
                        entry_rule="short at +7d only if 7d return known at trigger time is negative",
                        invalidation_rule="stop by fixed SL; conceptual invalidation on sustained baseline reclaim",
                        lower_confidence_sensitivity=lower,
                    )
                )
    return specs


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    ok = trades[trades["status"] == "ok"].copy()
    groups = [
        ["hypothesis", "sub_strategy", "roundtrip_cost_bps"],
        ["hypothesis", "roundtrip_cost_bps"],
        ["scenario", "roundtrip_cost_bps"],
        ["event_type", "roundtrip_cost_bps"],
        ["confidence_tier", "roundtrip_cost_bps"],
    ]
    rows = []
    for keys in groups:
        for vals, grp in ok.groupby(keys, dropna=False):
            if not isinstance(vals, tuple):
                vals = (vals,)
            ret = pd.to_numeric(grp["net_return"], errors="coerce")
            mae = pd.to_numeric(grp["max_adverse_excursion"], errors="coerce")
            mfe = pd.to_numeric(grp["max_favorable_excursion"], errors="coerce")
            row = {k: v for k, v in zip(keys, vals)}
            row.update(
                {
                    "grouping": "+".join(keys),
                    "number_of_trades": len(grp),
                    "win_rate": float((ret > 0).mean()),
                    "median_return": float(ret.median()),
                    "average_return": float(ret.mean()),
                    "p25_return": float(ret.quantile(0.25)),
                    "p75_return": float(ret.quantile(0.75)),
                    "worst_trade": float(ret.min()),
                    "best_trade": float(ret.max()),
                    "median_max_adverse_excursion": float(mae.median()),
                    "median_max_favorable_excursion": float(mfe.median()),
                    "median_time_to_tp_hours": float(pd.to_numeric(grp["time_to_tp_hours"], errors="coerce").median()) if grp["time_to_tp_hours"].notna().any() else np.nan,
                    "median_time_to_sl_hours": float(pd.to_numeric(grp["time_to_sl_hours"], errors="coerce").median()) if grp["time_to_sl_hours"].notna().any() else np.nan,
                    "expectancy": float(ret.mean()),
                    "median_risk_reward": float(pd.to_numeric(grp["risk_reward_realized"], errors="coerce").median()),
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def write_report(trades: pd.DataFrame, summary: pd.DataFrame) -> None:
    ok = trades[trades["status"] == "ok"].copy()
    report = [
        "# Hypothesis Backtest Report v1",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This is a retrospective rules-based research backtest. It is not a live tradability claim and does not include borrow availability, real order book depth, funding, liquidation dynamics, or venue-specific execution constraints.",
        "",
        "## Assumptions",
        "",
        "- Short PnL is computed as `entry_price / exit_price - 1`.",
        "- Transaction cost/slippage is modeled as round-trip cost with two assumptions: 0 bps and 20 bps.",
        "- Stop/TP use first-touch OHLCV logic; if stop and TP touch in the same candle, stop is assumed first.",
        "- Entries are after event time: +1h, +24h, +7d, or after pump20 confirmation plus failed-breakout close.",
        "- Pair-removal-only and unknown manual-review rows are excluded from clean hypotheses.",
        "- Lower-confidence sensitivity samples are marked but separated by `confidence_tier=low_sensitivity`.",
        "",
        "## Hypothesis Definitions",
        "",
        "### 1. Spot Delisting Announcement Shock",
        "",
        "- Eligible universe: clean/sensitivity spot `SPOT_TOKEN_DELISTING_ANNOUNCED` rows with path data.",
        "- Entry rules: `immediate_1h_confirmation`; `rebound_failure_24h` only when `vwap_reclaim_failure=yes`; 30d variant for rebound failure.",
        "- Stops: 12-18% depending on sub-rule.",
        "- Take profits: 30% for 7d tests; 50% for 30d rebound-failure test.",
        "- Invalidation: fixed SL; conceptual invalidation on sustained baseline reclaim.",
        "",
        "### 2. Delisting Pump-Fade",
        "",
        "- Eligible universe: pump rows with no manual-review pump flag and spot pair available.",
        "- Entry rule: after first post-event candle confirming +20% pump from baseline, then subsequent 1h close back below baseline +10%.",
        "- Stop: 20% above failed-breakout entry.",
        "- Take profit: 40%.",
        "- Holding window: 7d.",
        "",
        "### 3. Monitoring Tag Failed-Recovery Delayed Collapse",
        "",
        "- Eligible universe: Monitoring Tag rows with path data.",
        "- Entry delays: +1h, +24h, +7d.",
        "- Failed-recovery trigger: +7d entry only if the 7d return known at that time is negative.",
        "- Stops: 18-20%.",
        "- Take profits: 30-45%.",
        "- Holding windows: 30d and 90d depending on sub-rule.",
        "",
        "## Overall Results",
        "",
    ]
    top = summary[summary["grouping"] == "hypothesis+sub_strategy+roundtrip_cost_bps"].copy()
    cols = [
        "hypothesis",
        "sub_strategy",
        "roundtrip_cost_bps",
        "number_of_trades",
        "win_rate",
        "median_return",
        "average_return",
        "p25_return",
        "p75_return",
        "worst_trade",
        "best_trade",
        "median_max_adverse_excursion",
        "median_max_favorable_excursion",
        "median_time_to_tp_hours",
        "median_time_to_sl_hours",
        "median_risk_reward",
    ]
    report.append(top[cols].to_markdown(index=False))
    report.extend(
        [
            "",
            "## Results By Scenario",
            "",
            summary[summary["grouping"] == "scenario+roundtrip_cost_bps"][
                ["scenario", "roundtrip_cost_bps", "number_of_trades", "win_rate", "median_return", "average_return", "worst_trade", "best_trade"]
            ].to_markdown(index=False),
            "",
            "## Results By Confidence Tier",
            "",
            summary[summary["grouping"] == "confidence_tier+roundtrip_cost_bps"][
                ["confidence_tier", "roundtrip_cost_bps", "number_of_trades", "win_rate", "median_return", "average_return", "worst_trade", "best_trade"]
            ].to_markdown(index=False),
            "",
            "## Interpretation",
            "",
            "- Treat 0 bps as a clean statistical baseline, not an executable assumption.",
            "- 20 bps is a coarse sensitivity test; small-cap delisting names may require much larger slippage assumptions.",
            "- Pump-fade entries are explicitly after pump confirmation and a subsequent failed-breakout close, reducing look-ahead compared with entering before the squeeze.",
            "- Monitoring Tag delayed-collapse variants test timing sensitivity; the failed-recovery trigger is intentionally delayed and uses only the +7d return known at trigger time.",
            "- Samples remain small after quality filters; results should be bootstrapped and retested with borrow/perp availability before any execution claim.",
        ]
    )
    (DOCS / "hypothesis_backtest_report.md").write_text("\n".join(report) + "\n")


def main() -> None:
    specs = build_specs()
    store = KlineStore()
    rows = []
    for spec in specs:
        for cost in ROUNDTRIP_COST_BPS:
            rows.append(simulate_short_trade(store, spec, cost))
    trades = pd.DataFrame(rows)
    trades.to_csv(PROCESSED / "backtest_trades.csv", index=False)
    trades.to_parquet(PROCESSED / "backtest_trades.parquet", index=False)
    summary = summarize(trades)
    summary.to_csv(PROCESSED / "backtest_summary.csv", index=False)
    summary.to_parquet(PROCESSED / "backtest_summary.parquet", index=False)
    write_report(trades, summary)
    print(
        {
            "trade_rows": len(trades),
            "ok_trade_rows": int((trades["status"] == "ok").sum()) if not trades.empty else 0,
            "summary_rows": len(summary),
            "hypotheses": sorted(trades["hypothesis"].dropna().unique().tolist()) if not trades.empty else [],
            "outputs": [
                str(PROCESSED / "backtest_trades.csv"),
                str(PROCESSED / "backtest_summary.csv"),
                str(DOCS / "hypothesis_backtest_report.md"),
            ],
        }
    )


if __name__ == "__main__":
    main()
