#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


EVENT_ORDER = [
    "MONITORING_TAG_ADDED",
    "MONITORING_TAG_REMOVED",
    "SEED_TAG_ADDED",
    "SEED_TAG_REMOVED",
    "VOTE_TO_DELIST_STARTED",
    "VOTE_TO_DELIST_RESULT",
    "SPOT_TOKEN_DELISTING_ANNOUNCED",
    "FUTURES_CONTRACT_DELISTING_ANNOUNCED",
]


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def days_between(start: str, end: str) -> str:
    a, b = parse_dt(start), parse_dt(end)
    if not a or not b:
        return ""
    return str((b - a).days)


def first_dt(rows: list[dict], event_type: str) -> str:
    vals = sorted(r["publication_datetime_utc"] for r in rows if r["event_type"] == event_type and r["publication_datetime_utc"])
    return vals[0] if vals else ""


def first_dt_after(rows: list[dict], event_type: str, after: str) -> str:
    after_dt = parse_dt(after)
    vals = []
    for r in rows:
        if r["event_type"] != event_type or not r["publication_datetime_utc"]:
            continue
        current = parse_dt(r["publication_datetime_utc"])
        if current and (not after_dt or current >= after_dt):
            vals.append(r["publication_datetime_utc"])
    return sorted(vals)[0] if vals else ""


def first_effective_dt(rows: list[dict], event_type: str) -> str:
    vals = sorted(r["effective_datetime_utc"] for r in rows if r["event_type"] == event_type and r["effective_datetime_utc"])
    return vals[0] if vals else ""


def any_event(rows: list[dict], event_type: str) -> bool:
    return any(r["event_type"] == event_type for r in rows)


def safe_symbol(row: dict) -> str:
    return row.get("token_symbol", "").strip()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def final_outcome(rows: list[dict]) -> str:
    has_monitoring = any_event(rows, "MONITORING_TAG_ADDED")
    has_monitoring_removed = any_event(rows, "MONITORING_TAG_REMOVED")
    has_seed = any_event(rows, "SEED_TAG_ADDED")
    has_spot_delist = any_event(rows, "SPOT_TOKEN_DELISTING_ANNOUNCED")
    has_futures = any_event(rows, "FUTURES_CONTRACT_DELISTING_ANNOUNCED")
    has_token_level = any(r["is_token_level_event"] == "yes" for r in rows if r["event_type"] != "SPOT_PAIR_REMOVED")
    has_manual = any(r["manual_review_required"] == "yes" for r in rows)

    if has_spot_delist and has_monitoring:
        return "delisted_after_tag"
    if has_spot_delist and not has_monitoring:
        return "delisted_without_known_tag"
    if has_monitoring_removed:
        return "tag_removed"
    if has_monitoring:
        return "still_tagged"
    if has_futures and not has_spot_delist and not has_token_level:
        return "futures_only_delisting"
    if has_futures and not has_spot_delist and not has_monitoring and not has_seed:
        return "futures_only_delisting"
    if has_seed and not has_spot_delist and not has_monitoring:
        return "seed_tag_only"
    if all(r["event_type"] == "SPOT_PAIR_REMOVED" for r in rows):
        return "spot_pair_removed_only"
    if has_manual:
        return "unknown"
    return "unknown"


def scenario_stub(outcome: str) -> str:
    mapping = {
        "delisted_after_tag": "TAG_TO_DELISTING_TO_COLLAPSE",
        "delisted_without_known_tag": "DELISTED_WITHOUT_KNOWN_PRIOR_TAG",
        "tag_removed": "TAG_REMOVED_PENDING_PRICE_ANALYSIS",
        "still_tagged": "PENDING_PRICE_ANALYSIS",
        "futures_only_delisting": "FUTURES_ONLY_DELISTING",
        "spot_pair_removed_only": "PAIR_REMOVAL_ONLY",
        "seed_tag_only": "SEED_TAG_ONLY",
    }
    return mapping.get(outcome, "UNKNOWN")


def build_lifecycle(events: list[dict]) -> list[dict]:
    by_token: dict[str, list[dict]] = defaultdict(list)
    for row in events:
        symbol = safe_symbol(row)
        if not symbol:
            continue
        # Pair-removal rows are retained for control-class lifecycle only, never
        # as token delisting evidence.
        entity_id = row.get("token_entity_id") or symbol
        by_token[entity_id].append(row)

    out = []
    for entity_id, rows in sorted(by_token.items()):
        rows = sorted(rows, key=lambda r: (r.get("publication_datetime_utc", ""), EVENT_ORDER.index(r["event_type"]) if r["event_type"] in EVENT_ORDER else 99))
        representative = next((r for r in rows if r["event_type"] != "SPOT_PAIR_REMOVED"), rows[0])
        first_monitoring = first_dt(rows, "MONITORING_TAG_ADDED")
        first_seed = first_dt(rows, "SEED_TAG_ADDED")
        monitoring_removed = first_dt_after(rows, "MONITORING_TAG_REMOVED", first_monitoring)
        seed_removed = first_dt_after(rows, "SEED_TAG_REMOVED", first_seed)
        delist = first_dt(rows, "SPOT_TOKEN_DELISTING_ANNOUNCED")
        effective_delist = first_effective_dt(rows, "SPOT_TOKEN_DELISTING_ANNOUNCED")
        vote_start = first_dt(rows, "VOTE_TO_DELIST_STARTED")
        vote_result = first_dt(rows, "VOTE_TO_DELIST_RESULT")
        outcome = final_outcome(rows)
        manual = any(r["manual_review_required"] == "yes" for r in rows)
        notes = []
        if any(r["event_type"] == "SPOT_PAIR_REMOVED" for r in rows) and not delist:
            notes.append("pair_removal_observed_but_not_token_delisting")
        if any(r["manual_review_required"] == "yes" and not safe_symbol(r) for r in rows):
            notes.append("incomplete_symbol_extraction")
        if any("COIN-M" in r["announcement_title"] and r["event_type"] == "FUTURES_CONTRACT_DELISTING_ANNOUNCED" for r in rows):
            notes.append("coin_m_futures_review")
        out.append(
            {
                "token_entity_id": entity_id,
                "token_symbol": representative.get("token_symbol", entity_id),
                "token_name": representative.get("token_name", ""),
                "first_monitoring_tag_datetime_utc": first_monitoring,
                "first_seed_tag_datetime_utc": first_seed,
                "vote_to_delist_datetime_utc": vote_start,
                "vote_to_delist_result": "published" if vote_result else "",
                "monitoring_tag_removed_datetime_utc": monitoring_removed,
                "seed_tag_removed_datetime_utc": seed_removed,
                "delisting_announcement_datetime_utc": delist,
                "effective_delisting_datetime_utc": effective_delist,
                "was_delisted_after_tag": "yes" if delist and first_monitoring else "no",
                "was_delisted_without_known_prior_tag": "yes" if delist and not first_monitoring else "no",
                "days_from_monitoring_tag_to_delisting": days_between(first_monitoring, delist),
                "days_from_monitoring_tag_to_tag_removal": days_between(first_monitoring, monitoring_removed),
                "final_outcome": outcome,
                "primary_scenario_stub": scenario_stub(outcome),
                "event_count": str(len(rows)),
                "has_pair_removal_control_event": "yes" if any(r["event_type"] == "SPOT_PAIR_REMOVED" for r in rows) else "no",
                "manual_review_required": "yes" if manual else "no",
                "entity_notes": ";".join(notes),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", default="data/processed/events.csv")
    parser.add_argument("--out", default="data/processed/token_lifecycle.csv")
    parser.add_argument("--manual-out", default="data/processed/manual_review_events.csv")
    args = parser.parse_args()

    events = list(csv.DictReader(open(args.events, encoding="utf-8")))
    lifecycle = build_lifecycle(events)
    manual_rows = [r for r in events if r["manual_review_required"] == "yes"]

    write_csv(Path(args.out), lifecycle)
    write_csv(Path(args.manual_out), manual_rows)

    bad_pair_delist = [
        r
        for r in lifecycle
        if r["final_outcome"] in {"delisted_after_tag", "delisted_without_known_tag"}
        and not r["delisting_announcement_datetime_utc"]
    ]
    print(
        {
            "lifecycle_rows": len(lifecycle),
            "manual_review_events": len(manual_rows),
            "bad_pair_delist_lifecycle_rows": len(bad_pair_delist),
            "out": args.out,
            "manual_out": args.manual_out,
        }
    )
    if bad_pair_delist:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
