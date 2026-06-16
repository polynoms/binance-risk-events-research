#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter


rows = list(csv.DictReader(open("data/processed/token_lifecycle.csv", encoding="utf-8")))
events = list(csv.DictReader(open("data/processed/events.csv", encoding="utf-8")))

def count(pred):
    return sum(1 for r in rows if pred(r))

print("unique_token_entity_id", len(rows))
print("with_monitoring_tag", count(lambda r: bool(r["first_monitoring_tag_datetime_utc"])))
print("with_monitoring_tag_removed", count(lambda r: bool(r["monitoring_tag_removed_datetime_utc"])))
print("with_seed_tag", count(lambda r: bool(r["first_seed_tag_datetime_utc"])))
print("with_spot_token_delisting", count(lambda r: bool(r["delisting_announcement_datetime_utc"])))
print("with_futures_only_delisting", count(lambda r: r["final_outcome"] == "futures_only_delisting"))
print("delisted_after_tag", count(lambda r: r["was_delisted_after_tag"] == "yes"))
print("delisted_without_known_prior_tag", count(lambda r: r["was_delisted_without_known_prior_tag"] == "yes"))
print("final_outcome_distribution", dict(Counter(r["final_outcome"] for r in rows)))
print("manual_review_lifecycle", count(lambda r: r["manual_review_required"] == "yes"))
print("bad_pair_final_delisted", count(lambda r: r["final_outcome"] in {"delisted_after_tag","delisted_without_known_tag"} and not r["delisting_announcement_datetime_utc"]))
print("pair_removal_only", count(lambda r: r["final_outcome"] == "spot_pair_removed_only"))

categories = {
    "tag_to_removal": lambda r: r["first_monitoring_tag_datetime_utc"] and r["monitoring_tag_removed_datetime_utc"],
    "tag_to_delist": lambda r: r["first_monitoring_tag_datetime_utc"] and r["delisting_announcement_datetime_utc"],
    "delist_without_tag": lambda r: r["was_delisted_without_known_prior_tag"] == "yes",
    "seed_tag_only": lambda r: r["final_outcome"] == "seed_tag_only",
    "futures_only": lambda r: r["final_outcome"] == "futures_only_delisting",
}

for name, pred in categories.items():
    print(f"\n{name}")
    for r in [x for x in rows if pred(x)][:10]:
        print(
            r["token_symbol"],
            r["final_outcome"],
            "monitoring=", r["first_monitoring_tag_datetime_utc"],
            "removed=", r["monitoring_tag_removed_datetime_utc"],
            "seed=", r["first_seed_tag_datetime_utc"],
            "delist=", r["delisting_announcement_datetime_utc"],
            "notes=", r["entity_notes"],
        )

