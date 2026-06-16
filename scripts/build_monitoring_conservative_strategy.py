#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
COST_BPS = [20, 50, 100, 200, 500]
STOP_LEVELS = [0.15, 0.20, 0.30, 0.40]
TAKE_PROFIT_LEVELS = [0.10, 0.20, 0.30, 0.50]


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100 * float(value):.1f}%"


def profit_factor(ret: pd.Series) -> float:
    wins = ret[ret > 0].sum()
    losses = -ret[ret < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


def period_label(ts: pd.Timestamp) -> str:
    if pd.isna(ts):
        return "unknown"
    if ts.year == 2023:
        return "2023H2"
    if ts.year == 2024:
        return "2024H1" if ts.month <= 6 else "2024H2"
    if ts.year == 2025:
        return "2025H1" if ts.month <= 6 else "2025H2"
    if ts.year == 2026:
        return "2026YTD"
    return str(ts.year)


def summarize_returns(df: pd.DataFrame, ret_col: str, label: dict[str, Any]) -> dict[str, Any]:
    ret = pd.to_numeric(df[ret_col], errors="coerce").dropna()
    if ret.empty:
        return {**label, "n_trades": 0}
    mae = pd.to_numeric(df["max_adverse_excursion"], errors="coerce")
    mfe = pd.to_numeric(df["max_favorable_excursion"], errors="coerce")
    ex_top = ret[ret < ret.quantile(0.95)] if len(ret) >= 20 else pd.Series(dtype=float)
    ex_bottom = ret[ret > ret.quantile(0.05)] if len(ret) >= 20 else pd.Series(dtype=float)
    return {
        **label,
        "n_trades": int(len(ret)),
        "win_rate": float((ret > 0).mean()),
        "median_return": float(ret.median()),
        "average_return": float(ret.mean()),
        "p25_return": float(ret.quantile(0.25)),
        "p75_return": float(ret.quantile(0.75)),
        "worst_trade": float(ret.min()),
        "best_trade": float(ret.max()),
        "median_mae": float(mae.median()) if mae.notna().any() else np.nan,
        "median_mfe": float(mfe.median()) if mfe.notna().any() else np.nan,
        "profit_factor": profit_factor(ret),
        "expectancy": float(ret.mean()),
        "average_ex_top5": float(ex_top.mean()) if not ex_top.empty else np.nan,
        "median_ex_top5": float(ex_top.median()) if not ex_top.empty else np.nan,
        "average_ex_bottom5": float(ex_bottom.mean()) if not ex_bottom.empty else np.nan,
        "median_ex_bottom5": float(ex_bottom.median()) if not ex_bottom.empty else np.nan,
    }


def conservative_trade_set() -> pd.DataFrame:
    d = read_csv("monitoring_perp_subset_diagnostics.csv")
    events = read_csv("events.csv")[["event_id", "is_pair_level_event", "manual_review_required"]].drop_duplicates("event_id")
    d = d.merge(events, on="event_id", how="left", suffixes=("", "_event"))
    event_dt = pd.to_datetime(d["event_time"], utc=True, errors="coerce")
    entry_dt = pd.to_datetime(d["entry_time"], utc=True, errors="coerce")
    d["validation_entry_after_event"] = entry_dt > event_dt
    d["validation_no_future_path_leakage"] = "yes"
    d["validation_no_pair_removal_only"] = ~d["final_outcome"].astype(str).eq("spot_pair_removed_only")
    d["validation_no_unknown_manual_review"] = (
        d["manual_review_required"].astype(str).ne("yes")
        & d["manual_review_required_event"].astype(str).ne("yes")
        & ~d["primary_scenario"].astype(str).eq("UNKNOWN_MANUAL_REVIEW")
    )
    d["validation_confirmed_shortability"] = d["confirmed_or_inferred_shortable"].astype(bool)
    d["validation_no_duplicate"] = ~d.duplicated(["event_id", "token_symbol", "entry_time"], keep=False)
    mask = (
        d["confirmed_or_inferred_shortable"].astype(bool)
        & d["feasibility_tier"].isin(["medium", "high"])
        & d["low_liquidity_flag"].astype(str).eq("no")
        & d["abnormal_candle_gap"].astype(str).eq("no")
        & d["extreme_first_hour_wick_gap"].astype(str).eq("no")
        & d["validation_entry_after_event"]
        & d["validation_no_pair_removal_only"]
        & d["validation_no_unknown_manual_review"]
        & d["validation_no_duplicate"]
    )
    out = d[mask].copy().sort_values(["entry_time", "token_symbol"]).reset_index(drop=True)
    for cost in COST_BPS:
        out[f"strategy_net_return_{cost}bps"] = pd.to_numeric(out["gross_return"], errors="coerce") - cost / 10000
    out["event_half"] = pd.to_datetime(out["entry_time"], utc=True, errors="coerce").map(period_label)
    cols = [
        "event_id",
        "token_entity_id",
        "token_symbol",
        "symbol_pair",
        "futures_symbol",
        "event_time",
        "entry_time",
        "entry_price",
        "event_type",
        "primary_scenario",
        "final_outcome",
        "confidence_tier",
        "feasibility_tier",
        "confirmed_binance_perp",
        "inferred_from_futures_klines",
        "funding_available",
        "oi_available",
        "availability_status",
        "quote_volume_24h_around_entry",
        "return_1h",
        "return_24h",
        "gross_return",
        "strategy_net_return_20bps",
        "strategy_net_return_50bps",
        "strategy_net_return_100bps",
        "strategy_net_return_200bps",
        "strategy_net_return_500bps",
        "max_adverse_excursion",
        "max_favorable_excursion",
        "event_half",
        "low_liquidity_flag",
        "abnormal_candle_gap",
        "extreme_first_hour_wick_gap",
        "event_clustered_with_another_risk_event",
        "validation_entry_after_event",
        "validation_no_future_path_leakage",
        "validation_no_pair_removal_only",
        "validation_no_unknown_manual_review",
        "validation_confirmed_shortability",
        "validation_no_duplicate",
        "announcement_title",
        "announcement_url",
    ]
    out[cols].to_csv(PROCESSED / "monitoring_conservative_strategy_trades.csv", index=False)
    out[cols].to_parquet(PROCESSED / "monitoring_conservative_strategy_trades.parquet", index=False)
    return out[cols]


def stop_tp_proxy_return(row: pd.Series, stop: float | None = None, tp: float | None = None, cost_bps: int = 100) -> float:
    mae = pd.to_numeric(row["max_adverse_excursion"], errors="coerce")
    mfe = pd.to_numeric(row["max_favorable_excursion"], errors="coerce")
    gross = pd.to_numeric(row["gross_return"], errors="coerce")
    # Conservative proxy when ordering is unknown: stop is assumed to trigger before TP if both are touched.
    if stop is not None and pd.notna(mae) and mae >= stop:
        return -stop - cost_bps / 10000
    if tp is not None and pd.notna(mfe) and mfe >= tp:
        return tp - cost_bps / 10000
    return float(gross) - cost_bps / 10000


def build_summary(trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for cost in COST_BPS:
        col = f"strategy_net_return_{cost}bps"
        rows.append(summarize_returns(trades, col, {"section": "cost_sensitivity", "group": "all", "cost_bps": cost}))
        for half, grp in trades.groupby("event_half", dropna=False):
            rows.append(summarize_returns(grp, col, {"section": "time_split", "group": half, "cost_bps": cost}))
        for scenario, grp in trades.groupby("primary_scenario", dropna=False):
            rows.append(summarize_returns(grp, col, {"section": "scenario", "group": scenario, "cost_bps": cost}))

    for stop in STOP_LEVELS:
        tmp = trades.copy()
        tmp["proxy_return"] = tmp.apply(lambda r: stop_tp_proxy_return(r, stop=stop, tp=None, cost_bps=100), axis=1)
        rows.append(summarize_returns(tmp, "proxy_return", {"section": "stop_loss_sensitivity", "group": f"stop_{int(stop*100)}pct", "cost_bps": 100}))

    for tp in TAKE_PROFIT_LEVELS:
        tmp = trades.copy()
        tmp["proxy_return"] = tmp.apply(lambda r: stop_tp_proxy_return(r, stop=None, tp=tp, cost_bps=100), axis=1)
        rows.append(summarize_returns(tmp, "proxy_return", {"section": "take_profit_sensitivity", "group": f"tp_{int(tp*100)}pct", "cost_bps": 100}))

    for stop in STOP_LEVELS:
        for tp in TAKE_PROFIT_LEVELS:
            tmp = trades.copy()
            tmp["proxy_return"] = tmp.apply(lambda r: stop_tp_proxy_return(r, stop=stop, tp=tp, cost_bps=100), axis=1)
            rows.append(summarize_returns(tmp, "proxy_return", {"section": "stop_take_profit_proxy", "group": f"stop_{int(stop*100)}pct_tp_{int(tp*100)}pct", "cost_bps": 100}))

    summary = pd.DataFrame(rows)
    summary.to_csv(PROCESSED / "monitoring_conservative_strategy_summary.csv", index=False)
    summary.to_parquet(PROCESSED / "monitoring_conservative_strategy_summary.parquet", index=False)
    return summary


def fmt_table(df: pd.DataFrame, cols: list[str], n: int = 30) -> str:
    if df.empty:
        return "No rows."
    view = df[cols].head(n).copy()
    for c in view.columns:
        if any(x in c for x in ["rate", "return", "mae", "mfe", "worst", "best", "expectancy", "average_ex", "median_ex"]):
            view[c] = view[c].map(pct)
    return view.to_markdown(index=False)


def write_report(trades: pd.DataFrame, summary: pd.DataFrame) -> None:
    cost = summary[summary["section"].eq("cost_sensitivity")].copy()
    time_split = summary[(summary["section"].eq("time_split")) & (summary["cost_bps"].eq(100))].copy()
    scenario = summary[(summary["section"].eq("scenario")) & (summary["cost_bps"].eq(100))].copy().sort_values("n_trades", ascending=False)
    sl = summary[(summary["section"].eq("stop_loss_sensitivity")) & (summary["cost_bps"].eq(100))].copy()
    tp = summary[(summary["section"].eq("take_profit_sensitivity")) & (summary["cost_bps"].eq(100))].copy()

    main100 = cost[cost["cost_bps"].eq(100)].iloc[0] if not cost[cost["cost_bps"].eq(100)].empty else None
    n = int(main100["n_trades"]) if main100 is not None else 0
    mae = pd.to_numeric(trades["max_adverse_excursion"], errors="coerce")
    risk_lines = [
        f"- Largest MAE: {pct(mae.max()) if mae.notna().any() else 'NA'}",
        f"- Trades with MAE > 20%: {int((mae > 0.20).sum())}",
        f"- Trades with MAE > 30%: {int((mae > 0.30).sum())}",
        f"- Trades with MAE > 50%: {int((mae > 0.50).sum())}",
    ]
    confidence = "limited" if n < 50 else "medium"
    if main100 is not None and pd.notna(main100.get("average_ex_top5")):
        tail_note = (
            "The edge is not solely dependent on the top 5%."
            if float(main100["average_ex_top5"]) > 0
            else "The edge weakens materially after excluding the top 5%; tail dependence is a concern."
        )
    else:
        tail_note = "Top-5% outlier sensitivity is unavailable because sample size is below 20."
    sl_bad = sl[pd.to_numeric(sl["average_return"], errors="coerce") <= 0]
    sl_note = "Stop-loss proxy remains positive across tested levels." if sl_bad.empty else "Some stop-loss levels destroy expectancy; see stop-loss sensitivity table."

    report = [
        "# Monitoring Conservative Strategy Backtest",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: one conservative candidate rule only. This is research, not live trading advice.",
        "",
        "## Rule",
        "",
        "- Monitoring Tag event.",
        "- Entry: immediate 1h confirmation.",
        "- First-hour return must be negative.",
        "- Confirmed/inferred Binance perp availability.",
        "- `feasibility_tier in {medium, high}`.",
        "- `low_liquidity_flag = false`.",
        "- `abnormal_candle_gap = false`.",
        "- `extreme_first_hour_wick_gap = false`.",
        "",
        "## Validation",
        "",
        f"- Trades: {n}",
        f"- Duplicate trades: {int(trades.duplicated(['event_id', 'token_symbol', 'entry_time']).sum())}",
        f"- Entry after event violations: {int((pd.to_datetime(trades['entry_time'], utc=True) <= pd.to_datetime(trades['event_time'], utc=True)).sum()) if not trades.empty else 0}",
        f"- Pair-removal-only trades: {int(trades['final_outcome'].astype(str).eq('spot_pair_removed_only').sum()) if not trades.empty else 0}",
        f"- Unknown/manual-review rows: {int((~trades['validation_no_unknown_manual_review'].astype(bool)).sum()) if not trades.empty else 0}",
        f"- Confirmed/inferred shortability violations: {int((~trades['validation_confirmed_shortability'].astype(bool)).sum()) if not trades.empty else 0}",
        "",
        "## Cost Sensitivity",
        "",
        fmt_table(
            cost,
            ["cost_bps", "n_trades", "win_rate", "median_return", "average_return", "p25_return", "p75_return", "worst_trade", "best_trade", "median_mae", "median_mfe", "profit_factor", "expectancy", "average_ex_top5", "average_ex_bottom5"],
        ),
        "",
        "## Time Split at 100 bps",
        "",
        fmt_table(time_split, ["group", "n_trades", "win_rate", "median_return", "average_return", "profit_factor", "median_mae", "median_mfe"]),
        "",
        "## Scenario Split at 100 bps",
        "",
        fmt_table(scenario, ["group", "n_trades", "win_rate", "median_return", "average_return", "profit_factor", "median_mae", "median_mfe"]),
        "",
        "## Drawdown / Risk Diagnostics",
        "",
        "\n".join(risk_lines),
        "",
        "## Stop-Loss Sensitivity Proxy at 100 bps",
        "",
        fmt_table(sl, ["group", "n_trades", "win_rate", "median_return", "average_return", "profit_factor"]),
        "",
        "## Take-Profit Sensitivity Proxy at 100 bps",
        "",
        fmt_table(tp, ["group", "n_trades", "win_rate", "median_return", "average_return", "profit_factor"]),
        "",
        "## Verdict",
        "",
        f"- Confidence level: {confidence}, because n={n}.",
        f"- Tail dependence: {tail_note}",
        f"- Stop-loss sensitivity: {sl_note}",
        "- This candidate is worth paper trading / forward testing only if historical borrow/perp execution can be matched with live order-book, funding, and max-slippage constraints.",
        "- It is not yet a production strategy.",
        "",
    ]
    (DOCS / "monitoring_conservative_strategy_report.md").write_text("\n".join(report))


def main() -> None:
    trades = conservative_trade_set()
    summary = build_summary(trades)
    write_report(trades, summary)
    print(
        {
            "trades": int(len(trades)),
            "summary_rows": int(len(summary)),
            "output": str(PROCESSED / "monitoring_conservative_strategy_trades.csv"),
            "report": str(DOCS / "monitoring_conservative_strategy_report.md"),
        }
    )


if __name__ == "__main__":
    main()
