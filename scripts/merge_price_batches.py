#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd


TABLES = {
    "resolution": "price_resolution.csv",
    "price_windows": "price_windows.csv",
    "recovery": "recovery_analysis.csv",
    "pump": "pump_analysis.csv",
    "fallback_quality": "fallback_data_quality.csv",
}

FINAL = {
    "resolution": "data/processed/price_resolution.csv",
    "price_windows": "data/processed/price_windows.csv",
    "price_windows_parquet": "data/processed/price_windows.parquet",
    "recovery": "data/processed/recovery_analysis.csv",
    "pump": "data/processed/pump_analysis.csv",
    "fallback_quality": "data/processed/fallback_data_quality.csv",
}

UNIQUE_KEYS = {
    "resolution": ["token_symbol"],
    "price_windows": ["event_id", "token_symbol", "symbol_pair", "market_type", "window"],
    "recovery": ["token_symbol", "anchor_event_id"],
    "pump": ["event_id", "token_symbol"],
    "fallback_quality": ["token_symbol"],
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def collect_batch_dirs(args: argparse.Namespace) -> list[Path]:
    dirs: list[Path] = []
    if args.batch_dir:
        dirs.extend(sorted(Path(args.batch_dir).glob("*")))
    if args.inputs:
        dirs.extend(Path(x) for x in args.inputs)
    return [d for d in dirs if d.is_dir()]


def validate_schema(table: str, frames: list[tuple[Path, pd.DataFrame]]) -> list[str]:
    errors = []
    schemas = [(path, tuple(df.columns)) for path, df in frames if not df.empty]
    if not schemas:
        return errors
    expected = schemas[0][1]
    for path, schema in schemas[1:]:
        if schema != expected:
            errors.append(f"{table}: schema mismatch in {path}")
    return errors


def validate_unique(table: str, df: pd.DataFrame) -> list[str]:
    keys = UNIQUE_KEYS[table]
    missing = [k for k in keys if k not in df.columns]
    if missing:
        return [f"{table}: missing unique key columns {missing}"]
    dupes = df[df.duplicated(keys, keep=False)]
    if not dupes.empty:
        return [f"{table}: duplicate rows for keys {keys}: {len(dupes)} rows"]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge batch-safe price pipeline outputs.")
    parser.add_argument("--batch-dir", default="", help="Parent directory containing batch output dirs.")
    parser.add_argument("--inputs", nargs="*", default=[], help="Explicit batch output directories.")
    parser.add_argument("--out-dir", default="data/processed", help="Canonical output directory.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    batch_dirs = collect_batch_dirs(args)
    if not batch_dirs:
        raise SystemExit("No batch directories found.")

    report = {
        "batch_dirs": [str(d) for d in batch_dirs],
        "tables": {},
        "errors": [],
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for table, filename in TABLES.items():
        frames: list[tuple[Path, pd.DataFrame]] = []
        for batch_dir in batch_dirs:
            path = batch_dir / filename
            df = read_csv(path)
            frames.append((path, df))
        report["errors"].extend(validate_schema(table, frames))
        with_schema = [df.assign(_batch=str(path.parent)) for path, df in frames if len(df.columns) > 0]
        merged = pd.concat(with_schema, ignore_index=True) if with_schema else pd.DataFrame()
        batch_counts = {str(path.parent): int(len(df)) for path, df in frames}
        report["tables"][table] = {
            "rows": int(len(merged)),
            "batch_counts": batch_counts,
            "columns": list(merged.columns),
        }
        if "_batch" in merged.columns:
            merged_without_batch = merged.drop(columns=["_batch"])
        else:
            merged_without_batch = merged
        report["errors"].extend(validate_unique(table, merged_without_batch))
        if not args.dry_run:
            output_path = out_dir / TABLES[table]
            merged_without_batch.to_csv(output_path, index=False)
            if table == "price_windows":
                merged_without_batch.to_parquet(out_dir / "price_windows.parquet", index=False)

    report_path = out_dir / "price_batch_merge_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
