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


def best_derivatives_view() -> pd.DataFrame:
    d = read_csv("derivatives_availability.csv")
    score = (
        d["confirmed_binance_perp"].eq("yes").astype(int) * 4
        + d["inferred_from_futures_klines"].eq("yes").astype(int) * 3
        + d["funding_available"].eq("yes").astype(int) * 2
        + d["oi_available"].eq("yes").astype(int) * 2
        - d["api_unavailable"].eq("yes").astype(int)
    )
    d = d.copy()
    d["_deriv_score"] = score
    return d.sort_values(["event_id", "token_symbol", "entry_time", "_deriv_score"], ascending=[True, True, True, False]).drop_duplicates(
        ["event_id", "token_symbol", "entry_time"], keep="first"
    )


def build_diagnostics() -> tuple[pd.DataFrame, pd.DataFrame]:
    live = read_csv("monitoring_live_feasibility.csv")
    execf = read_csv("execution_features.csv")
    scen = read_csv("scenario_classification.csv")
    events = read_csv("events.csv")
    deriv = best_derivatives_view()

    exec_cols = [
        "event_id",
        "return_4h",
        "return_7d",
        "return_30d",
        "max_adverse_excursion_24h",
        "max_favorable_excursion_24h",
        "max_adverse_excursion_7d",
        "max_favorable_excursion_7d",
        "vwap_reclaim_failure",
        "sustained_close_above_entry",
        "sustained_close_below_entry",
    ]
    scen_cols = [
        "token_symbol",
        "primary_scenario",
        "final_outcome",
        "recovery_90_sustained",
        "recovery_100_sustained",
        "never_recovered",
        "pump20_flag",
        "pump_and_dump_flag",
    ]
    event_cols = ["event_id", "announcement_title", "announcement_url", "publication_datetime_utc"]

    df = live.merge(execf[exec_cols].drop_duplicates("event_id"), on="event_id", how="left")
    df = df.merge(scen[scen_cols].drop_duplicates("token_symbol"), on="token_symbol", how="left")
    df = df.merge(events[event_cols].drop_duplicates("event_id"), on="event_id", how="left")
    deriv_cols = [
        "event_id",
        "token_symbol",
        "entry_time",
        "futures_symbol",
        "confirmed_binance_perp",
        "inferred_from_futures_klines",
        "funding_available",
        "oi_available",
        "no_binance_perp_evidence",
        "manual_review_needed",
        "availability_status",
        "kline_rows",
        "funding_rows",
        "open_interest_rows",
    ]
    df = df.merge(deriv[deriv_cols], on=["event_id", "token_symbol", "entry_time"], how="left")
    df["entry_dt"] = pd.to_datetime(df["entry_time"], utc=True, errors="coerce")
    df["event_half"] = df["entry_dt"].map(period_label)
    df["net_return_100bps"] = pd.to_numeric(df["net_return_100bps"], errors="coerce")
    df["confirmed_or_inferred_shortable"] = df["confirmed_binance_perp"].eq("yes")
    df["medium_feasibility_confirmed"] = df["confirmed_or_inferred_shortable"] & df["feasibility_tier"].isin(["high", "medium"])
    df["no_perp_evidence_group"] = df["no_binance_perp_evidence"].eq("yes")
    df["diagnostic_group"] = np.select(
        [
            df["medium_feasibility_confirmed"],
            df["confirmed_or_inferred_shortable"],
            df["no_perp_evidence_group"],
        ],
        [
            "B_medium_feasibility_confirmed_shortable",
            "A_confirmed_or_inferred_binance_perp",
            "C_no_binance_perp_evidence",
        ],
        default="other_or_manual_review",
    )
    df["liquidity_bucket"] = pd.qcut(
        pd.to_numeric(df["quote_volume_24h_around_entry"], errors="coerce").rank(method="first"),
        q=3,
        labels=["low_volume", "mid_volume", "high_volume"],
    )
    df["mae_mfe_ratio"] = pd.to_numeric(df["max_adverse_excursion"], errors="coerce") / pd.to_numeric(
        df["max_favorable_excursion"], errors="coerce"
    ).replace(0, np.nan)
    df["first_hour_return_bucket"] = pd.cut(
        pd.to_numeric(df["return_1h"], errors="coerce"),
        bins=[-np.inf, -0.10, -0.05, -0.02, 0],
        labels=["<=-10%", "-10%..-5%", "-5%..-2%", "-2%..0%"],
    )
    df.to_csv(PROCESSED / "monitoring_perp_subset_diagnostics.csv", index=False)
    df.to_parquet(PROCESSED / "monitoring_perp_subset_diagnostics.parquet", index=False)

    rows: list[dict[str, Any]] = []
    comparison_views = [
        ("A_full_confirmed_or_inferred_binance_perp", df["confirmed_or_inferred_shortable"]),
        ("B_medium_feasibility_confirmed_shortable", df["medium_feasibility_confirmed"]),
        ("C_no_binance_perp_evidence", df["no_perp_evidence_group"]),
    ]
    dimension_sets = [
        ("comparison_group", []),
        ("comparison_group+feasibility_tier", ["feasibility_tier"]),
        ("comparison_group+scenario", ["primary_scenario"]),
        ("comparison_group+event_half", ["event_half"]),
        ("comparison_group+liquidity_bucket", ["liquidity_bucket"]),
        ("comparison_group+funding", ["funding_available"]),
        ("comparison_group+oi", ["oi_available"]),
        ("comparison_group+low_liquidity", ["low_liquidity_flag"]),
        ("comparison_group+abnormal_gap", ["abnormal_candle_gap"]),
        ("comparison_group+wick_gap", ["extreme_first_hour_wick_gap"]),
        ("comparison_group+clustered", ["event_clustered_with_another_risk_event"]),
    ]
    for comparison_group, view_mask in comparison_views:
        view_df = df[view_mask].copy()
        if view_df.empty:
            continue
        for grouping_name, dims in dimension_sets:
            if not dims:
                grouped = [((), view_df)]
            else:
                grouped = view_df.groupby(dims, dropna=False, observed=False)
            for keys, grp in grouped:
                if not isinstance(keys, tuple):
                    keys = (keys,)
                cols = dims
                ret = pd.to_numeric(grp["net_return_100bps"], errors="coerce").dropna()
                if ret.empty:
                    continue
                ex_top = ret[ret < ret.quantile(0.95)] if len(ret) >= 20 else pd.Series(dtype=float)
                ex_bottom = ret[ret > ret.quantile(0.05)] if len(ret) >= 20 else pd.Series(dtype=float)
                row = {"grouping": grouping_name, "comparison_group": comparison_group, **{c: k for c, k in zip(cols, keys)}}
                row.update(
                    {
                        "n_trades": int(len(ret)),
                        "win_rate": float((ret > 0).mean()),
                        "median_return": float(ret.median()),
                        "average_return": float(ret.mean()),
                        "p25_return": float(ret.quantile(0.25)),
                        "p75_return": float(ret.quantile(0.75)),
                        "worst_trade": float(ret.min()),
                        "best_trade": float(ret.max()),
                        "avg_ex_top5": float(ex_top.mean()) if not ex_top.empty else np.nan,
                        "avg_ex_bottom5": float(ex_bottom.mean()) if not ex_bottom.empty else np.nan,
                        "profit_factor": profit_factor(ret),
                        "median_mae": float(pd.to_numeric(grp["max_adverse_excursion"], errors="coerce").median()),
                        "median_mfe": float(pd.to_numeric(grp["max_favorable_excursion"], errors="coerce").median()),
                        "median_quote_volume_24h": float(pd.to_numeric(grp["quote_volume_24h_around_entry"], errors="coerce").median()),
                        "median_return_1h": float(pd.to_numeric(grp["return_1h"], errors="coerce").median()),
                        "low_liquidity_rate": float(grp["low_liquidity_flag"].eq("yes").mean()),
                        "abnormal_gap_rate": float(grp["abnormal_candle_gap"].eq("yes").mean()),
                        "extreme_wick_gap_rate": float(grp["extreme_first_hour_wick_gap"].eq("yes").mean()),
                        "clustered_rate": float(grp["event_clustered_with_another_risk_event"].eq("yes").mean()),
                        "funding_available_rate": float(grp["funding_available"].eq("yes").mean()),
                        "oi_available_rate": float(grp["oi_available"].eq("yes").mean()),
                    }
                )
                rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(PROCESSED / "monitoring_perp_subset_diagnostics_summary.csv", index=False)
    return df, summary


def format_table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
    if df.empty:
        return "No rows."
    view = df[cols].head(n).copy()
    for c in view.columns:
        if any(x in c for x in ["return", "rate", "mae", "mfe", "avg_ex"]) and c not in {"n_trades"}:
            view[c] = view[c].map(pct)
    return view.to_markdown(index=False)


def write_report(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    main = summary[summary["grouping"] == "comparison_group"].copy().sort_values("comparison_group")
    cols = [
        "comparison_group",
        "n_trades",
        "win_rate",
        "median_return",
        "average_return",
        "p25_return",
        "p75_return",
        "avg_ex_top5",
        "avg_ex_bottom5",
        "profit_factor",
        "median_mae",
        "median_mfe",
        "median_quote_volume_24h",
        "median_return_1h",
        "low_liquidity_rate",
        "abnormal_gap_rate",
        "extreme_wick_gap_rate",
        "clustered_rate",
        "funding_available_rate",
        "oi_available_rate",
    ]

    scenario = summary[summary["grouping"] == "comparison_group+scenario"].copy()
    scenario = scenario.sort_values(["comparison_group", "n_trades"], ascending=[True, False])
    half = summary[summary["grouping"] == "comparison_group+event_half"].copy()
    half = half.sort_values(["comparison_group", "event_half"])
    feasibility = summary[summary["grouping"] == "comparison_group+feasibility_tier"].copy()
    feasibility = feasibility.sort_values(["comparison_group", "feasibility_tier"])

    confirmed = df[df["confirmed_or_inferred_shortable"]].copy()
    confirmed_low = confirmed[confirmed["feasibility_tier"].eq("low")]
    confirmed_med = confirmed[confirmed["feasibility_tier"].isin(["high", "medium"])]
    no_perp = df[df["no_perp_evidence_group"]].copy()

    def med(s: pd.Series) -> float:
        return float(pd.to_numeric(s, errors="coerce").median())

    interpretation = [
        "- The full confirmed/inferred Binance perp subset is dragged down mainly by low-feasibility names: confirmed shortable but poor liquidity/gap/wick profile.",
        f"- Confirmed/inferred subset size is {len(confirmed)}; the medium-feasibility core is {len(confirmed_med)}, while low-feasibility confirmed rows are {len(confirmed_low)}.",
        f"- Median 100 bps return: confirmed full {pct(med(confirmed['net_return_100bps'])) if not confirmed.empty else 'NA'}, medium-feasibility confirmed {pct(med(confirmed_med['net_return_100bps'])) if not confirmed_med.empty else 'NA'}, no-perp-evidence {pct(med(no_perp['net_return_100bps'])) if not no_perp.empty else 'NA'}.",
        "- The no-perp-evidence group has stronger spot returns but remains an execution question, not a tradable Binance-perp result.",
        "- OI availability is sparse and should be treated as a data-coverage marker, not a validated filter yet.",
    ]

    candidate_filters = [
        "- Liquidity floor candidate: exclude `low_liquidity_flag=yes`; this is entry-time observable via recent spot volume.",
        "- Wick/gap exclusion: exclude `extreme_first_hour_wick_gap=yes` and `abnormal_candle_gap=yes`; these are available by confirmation time.",
        "- Feasibility tier filter: require `feasibility_tier in {medium, high}` before treating Binance-perp subset as executable.",
        "- Funding/OI availability: funding confirms perp existence, but OI coverage is too sparse for a robust filter in v1.",
        "- Avoid using `scenario` as an entry filter unless decomposed into observable features; scenario labels are mostly ex-post diagnostics.",
    ]

    report = [
        "# Monitoring Perp Subset Diagnostics",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: diagnostics only for Monitoring Tag `immediate_1h_confirmation + negative_1h_confirmation`. No new optimized strategy is introduced.",
        "",
        "## Main Distribution Comparison at 100 bps",
        "",
        format_table(main, cols),
        "",
        "## Feasibility Split",
        "",
        format_table(
            feasibility,
            ["comparison_group", "feasibility_tier", "n_trades", "win_rate", "median_return", "average_return", "median_mae", "median_mfe", "median_quote_volume_24h", "low_liquidity_rate", "abnormal_gap_rate"],
            30,
        ),
        "",
        "## Scenario Split",
        "",
        format_table(
            scenario,
            ["comparison_group", "primary_scenario", "n_trades", "win_rate", "median_return", "average_return", "median_mae", "median_mfe", "low_liquidity_rate"],
            40,
        ),
        "",
        "## Time Split",
        "",
        format_table(
            half,
            ["comparison_group", "event_half", "n_trades", "win_rate", "median_return", "average_return", "median_mae", "median_mfe", "funding_available_rate"],
            40,
        ),
        "",
        "## What Kills The Full Confirmed Perp Subset",
        "",
        "\n".join(interpretation),
        "",
        "## Candidate Filters For Future Testing",
        "",
        "\n".join(candidate_filters),
        "",
        "## Caveats",
        "",
        "- This report uses 100 bps cost view for diagnostics.",
        "- Derivatives availability is based on public Binance futures klines/funding/OI API results around entry.",
        "- Some symbols may have venue-specific execution constraints not captured by OHLCV.",
        "- No-perp-evidence rows can still be shortable via borrow or other venues, but that is not proven here.",
        "- Candidate filters are hypotheses for later testing, not optimized rules.",
        "",
    ]
    (DOCS / "monitoring_perp_subset_diagnostics_report.md").write_text("\n".join(report))


def main() -> None:
    df, summary = build_diagnostics()
    write_report(df, summary)
    print(
        {
            "diagnostic_rows": int(len(df)),
            "summary_rows": int(len(summary)),
            "confirmed_or_inferred": int(df["confirmed_or_inferred_shortable"].sum()),
            "medium_feasibility_confirmed": int(df["medium_feasibility_confirmed"].sum()),
            "no_perp_evidence": int(df["no_perp_evidence_group"].sum()),
            "output": str(PROCESSED / "monitoring_perp_subset_diagnostics.csv"),
            "report": str(DOCS / "monitoring_perp_subset_diagnostics_report.md"),
        }
    )


if __name__ == "__main__":
    main()
