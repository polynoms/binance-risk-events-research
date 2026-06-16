#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events_csv")
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.events_csv, encoding="utf-8")))
    errors: list[str] = []
    warnings: list[str] = []

    for row in rows:
        if row["event_type"] == "SPOT_PAIR_REMOVED":
            if row["is_token_level_event"] != "no":
                errors.append(f"SPOT_PAIR_REMOVED marked token-level: {row['event_id']}")
            if row["is_pair_level_event"] != "yes":
                errors.append(f"SPOT_PAIR_REMOVED not marked pair-level: {row['event_id']}")
            if row["token_remains_tradable_on_binance"] != "yes":
                errors.append(f"SPOT_PAIR_REMOVED does not preserve tradable flag: {row['event_id']}")
        if row["event_type"] == "SPOT_TOKEN_DELISTING_ANNOUNCED" and row["is_pair_level_event"] == "yes":
            errors.append(f"Token delisting marked pair-level: {row['event_id']}")

    event_counts = Counter(r["event_type"] for r in rows)
    if event_counts["MONITORING_TAG_REMOVED"] == 0:
        warnings.append("No MONITORING_TAG_REMOVED event in sample.")

    report = {
        "events_csv": args.events_csv,
        "rows": len(rows),
        "event_type_counts": dict(event_counts),
        "manual_review_events": sum(r["manual_review_required"] == "yes" for r in rows),
        "errors": errors,
        "warnings": warnings,
    }
    out = Path(args.events_csv).with_suffix(".validation.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

