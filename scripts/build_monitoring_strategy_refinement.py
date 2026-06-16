#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
COST_BPS = [0, 20, 50, 100]


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def yn(value: Any) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


def profit_factor(returns: pd.Series) -> float:
    wins = returns[returns > 0].sum()
    losses = -returns[returns < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100 * float(value):.1f}%"


def load_monitoring_base() -> pd.DataFrame:
    trades = read_csv("backtest_trades.csv")
    execution = read_csv("execution_features.csv")
    paths = read_csv("monitoring_tag_path_features.csv")
    universe = read_csv("clean_research_universe.csv")
    scenarios = read_csv("scenario_classification.csv")

    base = trades[
        (trades["hypothesis"] == "monitoring_tag_failed_recovery_delayed_collapse")
        & (trades["status"] == "ok")
        & (trades["roundtrip_cost_bps"] == 0)
        & (trades["sub_strategy"].isin(["tag_immediate_1h", "tag_24h_delay", "tag_7d_delay", "failed_recovery_7d_trigger"]))
    ].copy()

    exec_cols = [
        "event_id",
        "return_1h",
        "return_4h",
        "return_24h",
        "return_7d",
        "return_30d",
        "max_adverse_excursion_24h",
        "max_favorable_excursion_24h",
        "max_adverse_excursion_7d",
        "max_favorable_excursion_7d",
        "vwap_reclaim_failure",
        "sustained_close_above_entry",
        "sustained_close_below_entry",
        "path_data_available_24h",
        "path_data_available_7d",
    ]
    path_cols = [
        "event_id",
        "time_from_tag_to_next_risk_event",
        "time_from_tag_to_delisting",
        "return_7d_after_tag",
        "return_30d_after_tag",
        "return_90d_after_tag",
        "alt_adj_return_30d_after_tag",
        "alt_adj_return_90d_after_tag",
        "max_drawdown_after_tag",
        "recovery_after_tag",
        "failed_recovery_flag",
        "delayed_collapse_candidate_score",
        "path_data_available_90d",
    ]
    universe_cols = [
        "token_symbol",
        "is_research_eligible",
        "exclusion_reason",
        "data_quality_score",
        "benchmark_gap_rate",
        "true_data_gap_rate",
        "fallback_provider",
    ]
    scenario_cols = [
        "token_symbol",
        "final_outcome",
        "primary_scenario",
        "recovery_90_sustained",
        "recovery_100_sustained",
        "never_recovered",
        "manual_review_required",
    ]

    base = base.merge(execution[exec_cols].drop_duplicates("event_id"), on="event_id", how="left")
    base = base.merge(paths[path_cols].drop_duplicates("event_id"), on="event_id", how="left")
    base = base.merge(universe[universe_cols].drop_duplicates("token_symbol"), on="token_symbol", how="left")
    base = base.merge(scenarios[scenario_cols].drop_duplicates("token_symbol"), on="token_symbol", how="left")

    base["confidence_bucket"] = np.where(base["confidence_tier"].astype(str) == "low_sensitivity", "low_sensitivity", "clean")
    base["robust_net_return"] = pd.to_numeric(base["gross_return"], errors="coerce")
    base["event_dt"] = pd.to_datetime(base["event_time"], utc=True, errors="coerce")
    base["entry_dt"] = pd.to_datetime(base["entry_time"], utc=True, errors="coerce")
    base["mfe_mae_ratio"] = pd.to_numeric(base["max_favorable_excursion"], errors="coerce") / pd.to_numeric(
        base["max_adverse_excursion"], errors="coerce"
    ).replace(0, np.nan)
    base["fallback_only_path"] = base["fallback_provider"].notna() & (base["fallback_provider"].astype(str) != "")
    base["benchmark_gap_heavy"] = pd.to_numeric(base["benchmark_gap_rate"], errors="coerce").fillna(0) > 0.10
    base["true_data_gap_heavy"] = pd.to_numeric(base["true_data_gap_rate"], errors="coerce").fillna(0) > 0.10
    base["clean_quality"] = base["is_research_eligible"].astype(str).eq("yes") & base["confidence_bucket"].eq("clean")
    return base


def add_cost_views(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost in COST_BPS:
        x = df.copy()
        x["cost_bps"] = cost
        x["net_return_after_cost"] = pd.to_numeric(x["gross_return"], errors="coerce") - cost / 10000
        rows.append(x)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def summarize(df: pd.DataFrame, label: dict[str, Any]) -> dict[str, Any]:
    ret = pd.to_numeric(df["net_return_after_cost"], errors="coerce").dropna()
    if ret.empty:
        return {
            **label,
            "n_trades": 0,
            "low_confidence_flag": "yes",
        }
    mae = pd.to_numeric(df["max_adverse_excursion"], errors="coerce")
    mfe = pd.to_numeric(df["max_favorable_excursion"], errors="coerce")
    ex_top = ret[ret < ret.quantile(0.95)] if len(ret) >= 20 else pd.Series(dtype=float)
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
        "expectancy": float(ret.mean()),
        "profit_factor": profit_factor(ret),
        "average_return_ex_top5": float(ex_top.mean()) if not ex_top.empty else np.nan,
        "median_return_ex_top5": float(ex_top.median()) if not ex_top.empty else np.nan,
        "low_confidence_flag": "yes" if len(ret) < 20 else "no",
    }


def build_filter_sets(base: pd.DataFrame) -> list[tuple[str, str, bool, Callable[[pd.DataFrame], pd.Series]]]:
    mae24 = pd.to_numeric(base["max_adverse_excursion_24h"], errors="coerce")
    mfe24 = pd.to_numeric(base["max_favorable_excursion_24h"], errors="coerce")
    high_post_vol_threshold = (mae24.fillna(0) + mfe24.fillna(0)).quantile(0.66)
    low_pre_expansion_threshold = (mfe24.fillna(0) + mae24.fillna(0)).quantile(0.50)
    extreme_wick_threshold = mae24.quantile(0.90)

    def all_rows(df: pd.DataFrame) -> pd.Series:
        return pd.Series(True, index=df.index)

    filter_specs: list[tuple[str, str, bool, Callable[[pd.DataFrame], pd.Series]]] = [
        ("base_all_monitoring", "base", True, all_rows),
        ("clean_only", "data_quality", True, lambda df: df["clean_quality"]),
        ("exclude_benchmark_gap_heavy", "data_quality", True, lambda df: ~df["benchmark_gap_heavy"]),
        ("exclude_true_data_gap_heavy", "data_quality", True, lambda df: ~df["true_data_gap_heavy"]),
        ("exclude_fallback_only_paths", "data_quality", True, lambda df: ~df["fallback_only_path"]),
        ("clean_no_gap_no_fallback", "data_quality_combo", True, lambda df: df["clean_quality"] & ~df["benchmark_gap_heavy"] & ~df["true_data_gap_heavy"] & ~df["fallback_only_path"]),
        ("negative_1h_confirmation", "path_behavior", True, lambda df: pd.to_numeric(df["return_1h"], errors="coerce") < 0),
        ("failed_rebound_24h", "path_behavior", True, lambda df: (pd.to_numeric(df["return_24h"], errors="coerce") < 0) & df["vwap_reclaim_failure"].astype(str).eq("yes")),
        ("no_sustained_reclaim_above_entry", "path_behavior", False, lambda df: ~df["sustained_close_above_entry"].astype(str).eq("yes")),
        ("high_mfe_mae_asymmetry", "path_behavior", False, lambda df: pd.to_numeric(df["mfe_mae_ratio"], errors="coerce") >= 1.25),
        ("early_lower_low_after_tag", "path_behavior", False, lambda df: pd.to_numeric(df["max_favorable_excursion_24h"], errors="coerce") >= 0.08),
        ("high_post_tag_volatility", "volatility", False, lambda df: (pd.to_numeric(df["max_adverse_excursion_24h"], errors="coerce").fillna(0) + pd.to_numeric(df["max_favorable_excursion_24h"], errors="coerce").fillna(0)) >= high_post_vol_threshold),
        ("low_pre_then_expansion_proxy", "volatility", False, lambda df: (pd.to_numeric(df["max_adverse_excursion_24h"], errors="coerce").fillna(0) + pd.to_numeric(df["max_favorable_excursion_24h"], errors="coerce").fillna(0)) >= low_pre_expansion_threshold),
        ("avoid_extreme_initial_wick", "volatility", False, lambda df: pd.to_numeric(df["max_adverse_excursion_24h"], errors="coerce").fillna(0) < extreme_wick_threshold),
        ("scenario_monitoring_tag_only", "scenario", False, lambda df: df["scenario"].astype(str).isin(["IMMEDIATE_DUMP_AFTER_TAG", "SLOW_BLEED_AFTER_TAG", "TEMPORARY_PANIC_THEN_RECOVERY", "NO_CLEAR_REACTION"])),
        ("scenario_tag_followed_by_delisting", "scenario", False, lambda df: df["scenario"].astype(str).isin(["TAG_TO_DELISTING_TO_COLLAPSE", "DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP"])),
        ("scenario_tag_removed_recovered", "scenario", False, lambda df: df["scenario"].astype(str).eq("TAG_REMOVED_AND_RECOVERED")),
        ("scenario_tag_not_recovered", "scenario", False, lambda df: df["never_recovered"].astype(str).eq("yes") | ((pd.to_numeric(df["return_30d_after_tag"], errors="coerce") < 0) & (pd.to_numeric(df["return_90d_after_tag"], errors="coerce") < 0))),
        ("combo_clean_negative_1h_no_reclaim", "simple_combo", False, lambda df: df["clean_quality"] & (pd.to_numeric(df["return_1h"], errors="coerce") < 0) & ~df["sustained_close_above_entry"].astype(str).eq("yes")),
        ("combo_clean_failed_24h_no_reclaim", "simple_combo", False, lambda df: df["clean_quality"] & (pd.to_numeric(df["return_24h"], errors="coerce") < 0) & df["vwap_reclaim_failure"].astype(str).eq("yes") & ~df["sustained_close_above_entry"].astype(str).eq("yes")),
        ("combo_delisting_path_negative_1h", "simple_combo", False, lambda df: df["scenario"].astype(str).isin(["TAG_TO_DELISTING_TO_COLLAPSE", "DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP"]) & (pd.to_numeric(df["return_1h"], errors="coerce") < 0)),
    ]
    return filter_specs


def execution_variant_frames(base: pd.DataFrame) -> list[tuple[str, str, pd.DataFrame]]:
    variants = [
        ("immediate_1h_confirmation", "priority", base[base["sub_strategy"] == "tag_immediate_1h"].copy()),
        ("24h_delay", "priority", base[base["sub_strategy"] == "tag_24h_delay"].copy()),
        (
            "24h_failed_recovery_trigger",
            "priority",
            base[
                (base["sub_strategy"] == "tag_24h_delay")
                & (pd.to_numeric(base["return_24h"], errors="coerce") < 0)
                & (
                    base["vwap_reclaim_failure"].astype(str).eq("yes")
                    | ~base["sustained_close_above_entry"].astype(str).eq("yes")
                )
            ].copy(),
        ),
        ("7d_delay_diagnostic", "diagnostic", base[base["sub_strategy"] == "tag_7d_delay"].copy()),
        ("7d_failed_recovery_diagnostic", "diagnostic", base[base["sub_strategy"] == "failed_recovery_7d_trigger"].copy()),
    ]
    return variants


def build_refinement() -> pd.DataFrame:
    base = load_monitoring_base()
    filters = build_filter_sets(base)
    rows: list[dict[str, Any]] = []

    for execution_variant, priority, frame in execution_variant_frames(base):
        if frame.empty:
            continue
        for filter_name, filter_group, entry_feasible_filter, predicate in filters:
            mask = predicate(frame).fillna(False)
            subset = frame[mask].copy()
            if subset.empty:
                rows.append(
                    {
                        "execution_variant": execution_variant,
                        "variant_priority": priority,
                        "filter_group": filter_group,
                        "filter_name": filter_name,
                        "entry_feasible_filter": "yes" if entry_feasible_filter else "no",
                        "cost_bps": 20,
                        "sample_view": "full_sample",
                        "n_trades": 0,
                        "low_confidence_flag": "yes",
                    }
                )
                continue
            costed = add_cost_views(subset)
            for cost, cost_grp in costed.groupby("cost_bps"):
                rows.append(
                    summarize(
                        cost_grp,
                        {
                            "execution_variant": execution_variant,
                            "variant_priority": priority,
                            "filter_group": filter_group,
                            "filter_name": filter_name,
                            "entry_feasible_filter": "yes" if entry_feasible_filter else "no",
                            "cost_bps": int(cost),
                            "sample_view": "full_sample",
                        },
                    )
                )
                if cost == 20:
                    ex = cost_grp.copy()
                    ret = pd.to_numeric(ex["net_return_after_cost"], errors="coerce")
                    if len(ex) >= 20:
                        ex = ex.loc[ret < ret.quantile(0.95)].copy()
                    else:
                        ex = ex.iloc[0:0].copy()
                    rows.append(
                        summarize(
                            ex,
                            {
                                "execution_variant": execution_variant,
                                "variant_priority": priority,
                                "filter_group": filter_group,
                                "filter_name": filter_name,
                                "entry_feasible_filter": "yes" if entry_feasible_filter else "no",
                                "cost_bps": 20,
                                "sample_view": "excluding_top5",
                            },
                        )
                    )
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "monitoring_strategy_refinement.csv", index=False)
    out.to_parquet(PROCESSED / "monitoring_strategy_refinement.parquet", index=False)
    return out


def select_candidate(df: pd.DataFrame) -> pd.DataFrame:
    main = df[
        (df["variant_priority"] == "priority")
        & (df["entry_feasible_filter"] == "yes")
        & ~(df["filter_name"] == "base_all_monitoring")
        & (df["cost_bps"] == 20)
        & (df["sample_view"] == "full_sample")
        & (pd.to_numeric(df["n_trades"], errors="coerce") >= 20)
    ].copy()
    main = main[
        ~(
            main["execution_variant"].eq("immediate_1h_confirmation")
            & main["filter_name"].eq("failed_rebound_24h")
        )
    ].copy()
    ex = df[
        (df["variant_priority"] == "priority")
        & (df["entry_feasible_filter"] == "yes")
        & (df["cost_bps"] == 20)
        & (df["sample_view"] == "excluding_top5")
    ][["execution_variant", "filter_name", "average_return", "median_return"]].rename(
        columns={"average_return": "avg_ex_top5_return_check", "median_return": "median_ex_top5_return_check"}
    )
    main = main.merge(ex, on=["execution_variant", "filter_name"], how="left")
    for col in ["median_return", "average_return", "median_mae", "median_mfe", "profit_factor", "avg_ex_top5_return_check"]:
        main[col] = pd.to_numeric(main[col], errors="coerce")
    main["candidate_score"] = (
        (main["median_return"] > 0).astype(int) * 3
        + (main["average_return"] > 0).astype(int) * 2
        + (main["avg_ex_top5_return_check"] > 0).astype(int) * 2
        + (main["profit_factor"] > 1.2).astype(int)
        + (main["median_mfe"] > main["median_mae"]).astype(int)
        + (main["filter_group"].eq("path_behavior")).astype(int)
        - (main["low_confidence_flag"].eq("yes")).astype(int) * 2
    )
    return main.sort_values(["candidate_score", "n_trades", "median_return"], ascending=[False, False, False])


def write_report(refinement: pd.DataFrame) -> None:
    base20 = refinement[
        (refinement["cost_bps"] == 20)
        & (refinement["sample_view"] == "full_sample")
        & (pd.to_numeric(refinement["n_trades"], errors="coerce") > 0)
    ].copy()
    candidates = select_candidate(refinement)

    def table(df: pd.DataFrame, n: int = 16) -> str:
        cols = [
            "execution_variant",
            "filter_group",
            "filter_name",
            "entry_feasible_filter",
            "n_trades",
            "win_rate",
            "median_return",
            "average_return",
            "p25_return",
            "p75_return",
            "median_mae",
            "median_mfe",
            "profit_factor",
            "average_return_ex_top5",
            "low_confidence_flag",
        ]
        view = df[cols].head(n).copy()
        for c in ["win_rate", "median_return", "average_return", "p25_return", "p75_return", "median_mae", "median_mfe", "average_return_ex_top5"]:
            view[c] = view[c].map(pct)
        return view.to_markdown(index=False)

    priority = base20[base20["variant_priority"] == "priority"].sort_values(
        ["low_confidence_flag", "median_return", "average_return"], ascending=[True, False, False]
    )
    diagnostic = base20[base20["variant_priority"] == "diagnostic"].sort_values(
        ["low_confidence_flag", "median_return", "average_return"], ascending=[True, False, False]
    )
    best = candidates.head(1)
    if best.empty:
        recommendation = "No robust priority candidate found with n >= 20."
    else:
        row = best.iloc[0]
        if row["candidate_score"] >= 7 and row["median_return"] > 0 and row["avg_ex_top5_return_check"] > 0:
            recommendation = (
                f"Recommended next candidate rule: `{row['execution_variant']} + {row['filter_name']}`. "
                f"It has n={int(row['n_trades'])}, median={pct(row['median_return'])}, "
                f"average={pct(row['average_return'])}, PF={row['profit_factor']:.2f}, and positive ex-top5 average."
            )
        else:
            recommendation = (
                "No high-confidence robust rule found yet. The best priority candidate is useful for follow-up diagnostics, "
                "but not strong enough to treat as a tradable rule without further validation."
            )

    cost_view = refinement[
        (refinement["sample_view"] == "full_sample")
        & (refinement["filter_name"].isin(["base_all_monitoring", "clean_only", "combo_clean_negative_1h_no_reclaim", "24h_failed_recovery_trigger"]))
        & (refinement["variant_priority"] == "priority")
    ].copy()
    cost_view = cost_view.sort_values(["execution_variant", "filter_name", "cost_bps"])
    cost_cols = ["execution_variant", "filter_name", "cost_bps", "n_trades", "median_return", "average_return", "profit_factor", "low_confidence_flag"]
    cost_table = cost_view[cost_cols].copy()
    for c in ["median_return", "average_return"]:
        cost_table[c] = cost_table[c].map(pct)

    report = [
        "# Monitoring Strategy Refinement v1",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: Monitoring Tag immediate / 24h refinement only. Spot delisting and pump-fade hypotheses are intentionally untouched.",
        "",
        "This is a focused research diagnostic, not a live tradability claim. It does not model borrow availability, funding, forced buy-ins, live order book depth, or venue-specific execution constraints.",
        "",
        "## Method",
        "",
        "- Base trades come from `backtest_trades.csv` Monitoring Tag rows only.",
        "- Entry rules are limited to immediate +1h, 24h delay, and an interpretable 24h failed-recovery trigger. 7d variants are reported as diagnostics only.",
        "- Cost sensitivity is recomputed at 0/20/50/100 bps from gross returns.",
        "- Outlier sensitivity is reported as excluding top 5% for samples with n >= 20.",
        "- Results with n < 20 are flagged low confidence.",
        "- Filters are tested separately plus a small number of simple combinations; no global optimization grid is used.",
        "",
        "## Recommendation",
        "",
        recommendation,
        "",
        "## Priority Variants at 20 bps",
        "",
        table(priority, 24),
        "",
        "## Diagnostic 7d Variants at 20 bps",
        "",
        table(diagnostic, 12),
        "",
        "## Candidate Ranking",
        "",
        table(candidates, 12) if not candidates.empty else "No candidates with n >= 20.",
        "",
        "## Cost Sensitivity Snapshot",
        "",
        cost_table.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- Prefer candidates with positive median return, positive average return after excluding top 5%, profit factor above 1, and median MFE greater than median MAE.",
        "- A high average with negative median is treated as tail-dependent rather than robust.",
        "- Clean-only filters are especially important because low-sensitivity rows can include fallback-heavy or gap-heavy paths.",
        "- Scenario filters such as tag followed by delisting are informative but can be partly ex-post; use them for archetype research, not direct entry rules unless their components are observable at entry time.",
        "",
        "## Next Step",
        "",
        "Backtest only the recommended candidate and one conservative baseline with explicit live-feasibility assumptions: borrow availability, market impact, maximum borrow cost, and no-entry rules during exchange maintenance or abnormal gaps.",
        "",
    ]
    (DOCS / "monitoring_strategy_refinement_report.md").write_text("\n".join(report))


def main() -> None:
    refinement = build_refinement()
    write_report(refinement)
    print(
        {
            "rows": int(len(refinement)),
            "output_csv": str(PROCESSED / "monitoring_strategy_refinement.csv"),
            "report": str(DOCS / "monitoring_strategy_refinement_report.md"),
        }
    )


if __name__ == "__main__":
    main()
