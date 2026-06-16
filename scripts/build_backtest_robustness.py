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
COST_BPS = [0, 20, 50, 100]


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def period_label(ts: pd.Timestamp) -> str:
    if pd.isna(ts):
        return "unknown"
    year = ts.year
    if year == 2023:
        return "2023H2"
    if year == 2024:
        return "2024H1" if ts.month <= 6 else "2024H2"
    if year == 2025:
        return "2025H1" if ts.month <= 6 else "2025H2"
    if year == 2026:
        return "2026YTD"
    return str(year)


def profit_factor(returns: pd.Series) -> float:
    wins = returns[returns > 0].sum()
    losses = -returns[returns < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


def metrics(df: pd.DataFrame, label: dict[str, Any]) -> dict[str, Any]:
    ret = pd.to_numeric(df["robust_net_return"], errors="coerce").dropna()
    if ret.empty:
        return {**label, "n_trades": 0}
    mae = pd.to_numeric(df.get("max_adverse_excursion"), errors="coerce")
    mfe = pd.to_numeric(df.get("max_favorable_excursion"), errors="coerce")
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
        "expectancy": float(ret.mean()),
        "profit_factor": profit_factor(ret),
        "median_mae": float(mae.median()) if mae.notna().any() else np.nan,
        "median_mfe": float(mfe.median()) if mfe.notna().any() else np.nan,
    }


def outlier_subset(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if df.empty:
        return df
    ret = pd.to_numeric(df["robust_net_return"], errors="coerce")
    if mode == "full_sample":
        return df
    if len(df) < 3:
        return df.iloc[0:0]
    if mode == "excluding_best_trade":
        return df.drop(index=ret.idxmax()).copy()
    if mode == "excluding_worst_trade":
        return df.drop(index=ret.idxmin()).copy()
    if mode == "excluding_top_5pct":
        cutoff = ret.quantile(0.95)
        return df.loc[ret < cutoff].copy()
    if mode == "excluding_bottom_5pct":
        cutoff = ret.quantile(0.05)
        return df.loc[ret > cutoff].copy()
    raise ValueError(mode)


def decluster(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    work = df.copy()
    work["_event_day"] = pd.to_datetime(work["event_time"], utc=True, errors="coerce").dt.floor("D")
    keys = ["hypothesis", "sub_strategy", "token_symbol", "_event_day", "robust_cost_bps"]
    work = work.sort_values(["event_time", "entry_time"]).drop_duplicates(keys, keep="first")
    family_keys = ["hypothesis", "sub_strategy", "event_id", "robust_cost_bps"]
    work = work.drop_duplicates(family_keys, keep="first")
    return work.drop(columns=["_event_day"], errors="ignore")


def add_cost_views(base: pd.DataFrame) -> pd.DataFrame:
    source = base[base["roundtrip_cost_bps"] == 0].copy()
    rows = []
    for cost in COST_BPS:
        x = source.copy()
        x["robust_cost_bps"] = cost
        x["robust_net_return"] = pd.to_numeric(x["gross_return"], errors="coerce") - cost / 10000
        rows.append(x)
    return pd.concat(rows, ignore_index=True)


def build_summary() -> tuple[pd.DataFrame, pd.DataFrame]:
    trades = read_csv("backtest_trades.csv")
    trades = trades[trades["status"] == "ok"].copy()
    trades["event_dt"] = pd.to_datetime(trades["event_time"], utc=True, errors="coerce")
    trades["time_split"] = trades["event_dt"].map(period_label)
    trades["hypothesis_family"] = trades["hypothesis"].replace(
        {
            "spot_delisting_announcement_shock": "spot_delisting_announcement_shock",
            "monitoring_tag_failed_recovery_delayed_collapse": "monitoring_tag",
            "delisting_pump_fade_after_failed_breakout": "pump_fade",
        }
    )
    trades["confidence_bucket"] = np.where(trades["confidence_tier"].astype(str) == "low_sensitivity", "low_sensitivity", "clean")
    expanded = add_cost_views(trades)

    rows: list[dict[str, Any]] = []

    def add_grouped(frame: pd.DataFrame, group_cols: list[str], test_name: str, sample_type: str) -> None:
        for keys, grp in frame.groupby(group_cols, dropna=False):
            if not isinstance(keys, tuple):
                keys = (keys,)
            label = {"test_name": test_name, "sample_type": sample_type}
            label.update({col: value for col, value in zip(group_cols, keys)})
            rows.append(metrics(grp, label))

    common = ["hypothesis_family", "sub_strategy", "robust_cost_bps"]
    add_grouped(expanded, common, "cost_sensitivity", "raw")
    add_grouped(decluster(expanded), common, "cost_sensitivity", "declustered")
    add_grouped(expanded, ["time_split", *common], "time_split", "raw")
    add_grouped(decluster(expanded), ["time_split", *common], "time_split", "declustered")
    add_grouped(expanded, ["confidence_bucket", *common], "confidence_tier", "raw")
    add_grouped(decluster(expanded), ["confidence_bucket", *common], "confidence_tier", "declustered")
    add_grouped(expanded, ["event_type", *common], "event_type", "raw")
    add_grouped(decluster(expanded), ["event_type", *common], "event_type", "declustered")
    add_grouped(expanded, ["scenario", *common], "scenario", "raw")

    for mode in ["full_sample", "excluding_best_trade", "excluding_top_5pct", "excluding_worst_trade", "excluding_bottom_5pct"]:
        for keys, grp in expanded.groupby(common, dropna=False):
            sub = outlier_subset(grp, mode)
            label = {"test_name": "outlier_sensitivity", "sample_type": mode}
            label.update({col: value for col, value in zip(common, keys)})
            rows.append(metrics(sub, label))

    # Diagnostic holding-window comparison by actual rule max holding windows.
    expanded["holding_window_bucket"] = expanded["max_holding_days"].astype(str) + "d"
    add_grouped(expanded, ["holding_window_bucket", *common], "holding_window_sensitivity", "raw")

    summary = pd.DataFrame(rows)
    summary.to_csv(PROCESSED / "backtest_robustness_summary.csv", index=False)
    summary.to_parquet(PROCESSED / "backtest_robustness_summary.parquet", index=False)
    expanded.to_csv(PROCESSED / "backtest_robustness_trades_expanded.csv", index=False)
    return expanded, summary


def fmt_pct(x: Any) -> str:
    if pd.isna(x):
        return "NA"
    return f"{100 * float(x):.1f}%"


def classify_hypotheses(summary: pd.DataFrame) -> pd.DataFrame:
    base = summary[
        (summary["test_name"] == "cost_sensitivity")
        & (summary["sample_type"] == "raw")
        & (summary["robust_cost_bps"] == 20)
    ].copy()
    out = []
    for _, row in base.iterrows():
        h = row["hypothesis_family"]
        sub = row["sub_strategy"]
        n = int(row["n_trades"])
        median = float(row["median_return"]) if pd.notna(row["median_return"]) else np.nan
        avg = float(row["average_return"]) if pd.notna(row["average_return"]) else np.nan
        pf = float(row["profit_factor"]) if pd.notna(row["profit_factor"]) else np.nan
        outlier = summary[
            (summary["test_name"] == "outlier_sensitivity")
            & (summary["sample_type"] == "excluding_top_5pct")
            & (summary["hypothesis_family"] == h)
            & (summary["sub_strategy"] == sub)
            & (summary["robust_cost_bps"] == 20)
        ]
        top5_avg = float(outlier["average_return"].iloc[0]) if not outlier.empty and pd.notna(outlier["average_return"].iloc[0]) else np.nan
        decl = summary[
            (summary["test_name"] == "cost_sensitivity")
            & (summary["sample_type"] == "declustered")
            & (summary["hypothesis_family"] == h)
            & (summary["sub_strategy"] == sub)
            & (summary["robust_cost_bps"] == 20)
        ]
        decl_avg = float(decl["average_return"].iloc[0]) if not decl.empty and pd.notna(decl["average_return"].iloc[0]) else np.nan
        if n < 20:
            verdict = "small_sample"
        elif median > 0 and avg > 0 and top5_avg > 0 and decl_avg > 0:
            verdict = "robust_candidate"
        elif avg > 0 and (pd.isna(top5_avg) or top5_avg <= 0 or median <= 0):
            verdict = "tail_dependent"
        elif avg > 0 and decl_avg > 0:
            verdict = "fragile_positive"
        else:
            verdict = "not_robust"
        out.append(
            {
                "hypothesis_family": h,
                "sub_strategy": sub,
                "n_trades_20bps": n,
                "median_return_20bps": median,
                "average_return_20bps": avg,
                "profit_factor_20bps": pf,
                "avg_ex_top5_20bps": top5_avg,
                "declustered_avg_20bps": decl_avg,
                "robustness_verdict": verdict,
            }
        )
    return pd.DataFrame(out).sort_values(["robustness_verdict", "average_return_20bps"], ascending=[True, False])


def write_report(expanded: pd.DataFrame, summary: pd.DataFrame) -> None:
    verdicts = classify_hypotheses(summary)
    cost = summary[(summary["test_name"] == "cost_sensitivity") & (summary["sample_type"].isin(["raw", "declustered"]))]
    cost_main = cost[
        [
            "sample_type",
            "hypothesis_family",
            "sub_strategy",
            "robust_cost_bps",
            "n_trades",
            "win_rate",
            "median_return",
            "average_return",
            "profit_factor",
            "median_mae",
            "median_mfe",
        ]
    ]
    outlier = summary[(summary["test_name"] == "outlier_sensitivity") & (summary["robust_cost_bps"] == 20)][
        [
            "sample_type",
            "hypothesis_family",
            "sub_strategy",
            "n_trades",
            "median_return",
            "average_return",
            "profit_factor",
        ]
    ]
    time = summary[(summary["test_name"] == "time_split") & (summary["sample_type"] == "raw") & (summary["robust_cost_bps"] == 20)][
        [
            "time_split",
            "hypothesis_family",
            "sub_strategy",
            "n_trades",
            "median_return",
            "average_return",
            "profit_factor",
        ]
    ]
    conf = summary[(summary["test_name"] == "confidence_tier") & (summary["sample_type"] == "raw") & (summary["robust_cost_bps"] == 20)][
        [
            "confidence_bucket",
            "hypothesis_family",
            "sub_strategy",
            "n_trades",
            "median_return",
            "average_return",
            "profit_factor",
        ]
    ]
    hold = summary[(summary["test_name"] == "holding_window_sensitivity") & (summary["robust_cost_bps"] == 20)][
        [
            "holding_window_bucket",
            "hypothesis_family",
            "sub_strategy",
            "n_trades",
            "median_return",
            "average_return",
            "profit_factor",
        ]
    ]

    report = [
        "# Backtest Robustness Report v1",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This is diagnostic robustness validation only. It does not optimize rules, add filters, or claim live tradability.",
        "",
        "## Scope",
        "",
        f"- Base trade rows at source costs: {len(read_csv('backtest_trades.csv'))}",
        f"- Expanded cost-view rows: {len(expanded)}",
        "- Cost views: 0, 20, 50, 100 bps roundtrip.",
        "- Time splits: 2023H2, 2024H1, 2024H2, 2025H1, 2025H2, 2026YTD.",
        "- De-clustering: first trade per hypothesis/sub-strategy/token/day/cost and first trade per event family.",
        "",
        "## Robustness Verdicts",
        "",
        verdicts.to_markdown(index=False),
        "",
        "## Cost Sensitivity",
        "",
        cost_main.to_markdown(index=False),
        "",
        "## Outlier Sensitivity At 20 bps",
        "",
        outlier.to_markdown(index=False),
        "",
        "## Time Split At 20 bps",
        "",
        time.to_markdown(index=False),
        "",
        "## Confidence Tier At 20 bps",
        "",
        conf.to_markdown(index=False),
        "",
        "## Holding Window Diagnostic At 20 bps",
        "",
        hold.to_markdown(index=False),
        "",
        "## Interpretation Guide",
        "",
        "- `robust_candidate`: positive median, positive average, survives top-5% removal and de-clustering.",
        "- `tail_dependent`: positive average but weak/negative median or weak after top-tail removal.",
        "- `fragile_positive`: average positive but needs more validation across regime/cost/cluster splits.",
        "- `small_sample`: too few trades for a reliable conclusion.",
        "- `not_robust`: weak after basic robustness checks.",
        "",
        "## Caveats",
        "",
        "- De-clustering is approximate and event-family based; it reduces but does not eliminate dependence.",
        "- Cost sensitivity is still simplified; stressed delisting liquidity can exceed 100 bps effective cost.",
        "- Holding-window sensitivity is diagnostic by rule bucket, not a full re-optimization.",
        "- No borrow, funding, liquidation, or order-book feasibility is included.",
    ]
    (DOCS / "backtest_robustness_report.md").write_text("\n".join(report) + "\n")


def main() -> None:
    expanded, summary = build_summary()
    write_report(expanded, summary)
    print(
        {
            "expanded_rows": len(expanded),
            "summary_rows": len(summary),
            "outputs": [
                str(PROCESSED / "backtest_robustness_summary.csv"),
                str(PROCESSED / "backtest_robustness_summary.parquet"),
                str(DOCS / "backtest_robustness_report.md"),
            ],
        }
    )


if __name__ == "__main__":
    main()
