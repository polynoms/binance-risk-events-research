#!/usr/bin/env python3
"""Merge bottom/rebound batch CSV outputs with schema checks."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = [
    "bottom_analysis",
    "rebound_analysis",
    "tradable_bottom_signals",
    "signal_quality",
    "bottom_rebound_scenarios",
    "epic_like_cases",
    "bottom_rebound_case_comparison",
]
TOKEN_EXCLUSIONS = ROOT / "config/manual_token_exclusions.yaml"


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


def files_for_table(table: str, scope: str | None, batch_dir: Path) -> list[Path]:
    if scope == "risk":
        processed = ROOT / "data/processed"
        return sorted(
            [
                *processed.glob(f"{table}_risk_[0-9]*_[0-9]*.csv"),
                *processed.glob(f"{table}_risk_gap_*.csv"),
            ]
        )
    return sorted(batch_dir.glob(f"**/{table}_*.csv"))


def dedupe_columns(table: str, merged: pd.DataFrame) -> list[str]:
    if table in {"bottom_analysis", "rebound_analysis", "bottom_rebound_scenarios"}:
        return [c for c in ["token_entity_id", "anchor_event_id", "anchor_event_type"] if c in merged.columns]
    if table in {"tradable_bottom_signals", "signal_quality"}:
        return [c for c in ["token_entity_id", "anchor_event_id", "signal_timestamp_utc", "signal_type"] if c in merged.columns]
    if table == "bottom_rebound_case_comparison":
        return [c for c in ["token_symbol"] if c in merged.columns]
    return [c for c in ["token_entity_id", "anchor_event_id"] if c in merged.columns]


def filter_exclusions(df: pd.DataFrame, excluded: set[str]) -> tuple[pd.DataFrame, int]:
    if not excluded or "token_symbol" not in df.columns:
        return df, 0
    mask = df["token_symbol"].astype(str).str.upper().isin(excluded)
    removed = int(mask.sum())
    return df[~mask].copy(), removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-dir", default="data/processed/bottom_rebound_batches")
    parser.add_argument("--out-dir", default="data/processed")
    parser.add_argument("--scope", choices=["risk"], help="Merge flat risk batch files from data/processed.")
    args = parser.parse_args()

    batch_dir = ROOT / args.batch_dir
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report = []
    excluded = load_excluded_symbols()
    merged_frames: dict[str, pd.DataFrame] = {}

    for table in TABLES:
        files = files_for_table(table, args.scope, batch_dir)
        if not files:
            report.append(f"- {table}: no batch files")
            continue
        frames = []
        schemas = {}
        for fp in files:
            df = pd.read_csv(fp)
            frames.append(df)
            schemas[str(fp)] = tuple(df.columns)
        first_schema = next(iter(schemas.values()))
        schema_ok = all(cols == first_schema for cols in schemas.values())
        merged = pd.concat(frames, ignore_index=True)
        merged, exclusions_removed = filter_exclusions(merged, excluded if args.scope == "risk" else set())
        dedupe_cols = dedupe_columns(table, merged)
        duplicates = int(merged.duplicated(subset=dedupe_cols).sum()) if dedupe_cols else 0
        if dedupe_cols:
            merged = merged.drop_duplicates(subset=dedupe_cols, keep="last")
        output_name = f"{table}_{args.scope}.csv" if args.scope else f"{table}.csv"
        merged.to_csv(out_dir / output_name, index=False)
        merged_frames[table] = merged
        report.append(
            f"- {table}: files={len(files)}, rows={len(merged)}, schema_ok={schema_ok}, duplicates_removed={duplicates}, exclusions_removed={exclusions_removed}, output={output_name}"
        )

    report_name = f"bottom_rebound_{args.scope}_merged_qa.md" if args.scope else "bottom_rebound_merge_report.md"
    extra = []
    if args.scope == "risk":
        scenarios = merged_frames.get("bottom_rebound_scenarios", pd.DataFrame())
        bottom = merged_frames.get("bottom_analysis", pd.DataFrame())
        signals = merged_frames.get("tradable_bottom_signals", pd.DataFrame())
        quality = merged_frames.get("signal_quality", pd.DataFrame())
        epic = merged_frames.get("epic_like_cases", pd.DataFrame())
        rebound = merged_frames.get("rebound_analysis", pd.DataFrame())
        if not scenarios.empty:
            extra.extend(
                [
                    "",
                    "## Risk QA",
                    "",
                    f"- token_risk_entities: {scenarios['token_symbol'].nunique() if 'token_symbol' in scenarios.columns else len(scenarios)}",
                    f"- CML_present: {bool('token_symbol' in scenarios.columns and scenarios['token_symbol'].astype(str).str.upper().eq('CML').any())}",
                    f"- REMOVE_present: {bool('token_symbol' in scenarios.columns and scenarios['token_symbol'].astype(str).str.upper().eq('REMOVE').any())}",
                    f"- FORTH_present: {bool('token_symbol' in scenarios.columns and scenarios['token_symbol'].astype(str).str.upper().eq('FORTH').any())}",
                    f"- TRU_present: {bool('token_symbol' in scenarios.columns and scenarios['token_symbol'].astype(str).str.upper().eq('TRU').any())}",
                    "",
                    "### Scenario Distribution",
                    scenarios["primary_bottom_rebound_scenario"].value_counts(dropna=False).to_markdown()
                    if "primary_bottom_rebound_scenario" in scenarios.columns
                    else "missing scenario column",
                ]
            )
        if not bottom.empty:
            extra.extend(
                [
                    "",
                    "### Anchor Distribution",
                    bottom["anchor_event_type"].value_counts(dropna=False).to_markdown()
                    if "anchor_event_type" in bottom.columns
                    else "missing anchor column",
                    f"- absolute_bottoms: {int(bottom['low_price'].notna().sum()) if 'low_price' in bottom.columns else 'unknown'}",
                ]
            )
        if not signals.empty:
            extra.append(f"- tradable_signals: {len(signals)}")
            if "signal_failed_stop" in signals.columns:
                extra.append(f"- failed_signals: {int(signals['signal_failed_stop'].eq('yes').sum())}")
        if not quality.empty and "tradeability_tier" in quality.columns:
            extra.extend(["", "### Tradeability Tier Distribution", quality["tradeability_tier"].value_counts(dropna=False).to_markdown()])
        if not epic.empty:
            cols = [c for c in ["token_symbol", "epic_similarity_score", "manual_review_required", "notes"] if c in epic.columns]
            extra.extend(["", "### EPIC-Like Candidates", epic[cols].to_markdown(index=False)])
        if not rebound.empty and not scenarios.empty and {"token_symbol", "max_rebound_90d"}.issubset(rebound.columns):
            max90 = pd.to_numeric(rebound["max_rebound_90d"], errors="coerce")
            extra.append(f"- weak_rebound_90d_lt20: {int((max90.fillna(0) < 0.2).sum())}")
            sc_by_symbol = scenarios.set_index("token_symbol") if "token_symbol" in scenarios.columns else pd.DataFrame()
            strong_no_signal = 0
            if not sc_by_symbol.empty and "tradable_signal_found" in sc_by_symbol.columns:
                for _, row in rebound.iterrows():
                    sym = row.get("token_symbol")
                    val = pd.to_numeric(pd.Series([row.get("max_rebound_90d")]), errors="coerce").iloc[0]
                    if pd.notna(val) and val >= 0.5 and sym in sc_by_symbol.index and sc_by_symbol.loc[sym, "tradable_signal_found"] != "yes":
                        strong_no_signal += 1
            extra.append(f"- strong_rebound_without_causal_signal_90d: {strong_no_signal}")
    (out_dir / report_name).write_text("# Bottom/Rebound Merge Report\n\n" + "\n".join(report + extra) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
