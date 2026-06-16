#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from binance_retro.binance_api import article_detail, list_articles, write_raw_json
from binance_retro.parsing import parse_article, utc_from_ms


CATALOGS = {
    48: "New Cryptocurrency Listing",
    49: "Latest Binance News",
    161: "Delisting",
}

KEYWORDS = (
    "monitoring tag",
    "seed tag",
    "vote to delist",
    "will delist",
    "notice of removal of spot trading pairs",
    "futures will delist",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_bound(value: str, *, is_end: bool = False) -> datetime:
    if "T" in value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    suffix = "T23:59:59+00:00" if is_end else "T00:00:00+00:00"
    return datetime.fromisoformat(value + suffix).astimezone(timezone.utc)


def in_range(ms: int, start: str, end: str) -> bool:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return parse_bound(start) <= dt <= parse_bound(end, is_end=True)


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


def append_worklog(lines: list[str]) -> None:
    path = Path("docs/codex/worklog.md")
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def collect_index(start: str, end: str, max_pages: int) -> list[dict]:
    articles_by_code: dict[str, dict] = {}
    search_lines = [f"\n## {now_utc()} - Announcement index collection"]
    for catalog_id, catalog_name in CATALOGS.items():
        pages = 0
        found = 0
        for page_no in range(1, max_pages + 1):
            payload = list_articles(catalog_id, page_no)
            raw_path = Path(f"data/raw/binance_announcements/index/catalog_{catalog_id}_page_{page_no}.json")
            write_raw_json(raw_path, payload)
            catalogs = payload.get("data", {}).get("catalogs", [])
            if not catalogs:
                break
            articles = catalogs[0].get("articles", [])
            if not articles:
                break
            pages += 1
            stop_after_page = False
            for item in articles:
                release_ms = item.get("releaseDate")
                if not release_ms:
                    continue
                dt = datetime.fromtimestamp(release_ms / 1000, tz=timezone.utc)
                if dt < parse_bound(start):
                    stop_after_page = True
                if in_range(release_ms, start, end):
                    title = item.get("title", "")
                    if any(k in title.lower() for k in KEYWORDS):
                        item = dict(item)
                        item["catalogId"] = catalog_id
                        item["catalogName"] = catalog_name
                        articles_by_code[item["code"]] = item
                        found += 1
            if stop_after_page:
                break
        search_lines.append(
            f"- catalogId={catalog_id} ({catalog_name}); pages_scanned={pages}; keyword_hits={found}; endpoint=/bapi/composite/v1/public/cms/article/list/query"
        )
    append_worklog(search_lines)
    return sorted(articles_by_code.values(), key=lambda x: x.get("releaseDate", 0))


def choose_validation_sample(index: list[dict]) -> list[dict]:
    buckets = {
        "monitoring": lambda t: "monitoring tag" in t and ("extend the monitoring tag" in t or "remove the monitoring tag" in t),
        "monitoring_removed": lambda t: "remove the monitoring tag" in t,
        "spot_delist": lambda t: "will delist" in t and "futures" not in t and "margin" not in t,
        "futures_delist": lambda t: "futures will delist" in t or ("usdⓢ-m" in t and "delist" in t),
        "pair_removal": lambda t: "notice of removal of spot trading pairs" in t,
        "seed": lambda t: "seed tag" in t,
    }
    selected = []
    seen = set()
    for _, pred in buckets.items():
        for item in index:
            title = item.get("title", "").lower()
            if pred(title) and item["code"] not in seen:
                selected.append(item)
                seen.add(item["code"])
                break
    spot_delist_count = sum(
        1
        for item in selected
        if "will delist" in item.get("title", "").lower()
        and "futures" not in item.get("title", "").lower()
        and "margin" not in item.get("title", "").lower()
    )
    for item in index:
        if spot_delist_count >= 2:
            break
        title = item.get("title", "").lower()
        if "will delist" in title and "futures" not in title and "margin" not in title and item["code"] not in seen:
            selected.append(item)
            seen.add(item["code"])
            spot_delist_count += 1
    for item in index:
        if len(selected) >= 10:
            break
        if item["code"] not in seen:
            selected.append(item)
            seen.add(item["code"])
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2023-07-26")
    parser.add_argument("--end", default="2026-05-26T23:59:59Z")
    parser.add_argument("--max-pages", type=int, default=120)
    parser.add_argument("--validation-sample", action="store_true")
    parser.add_argument("--use-existing-index", action="store_true")
    args = parser.parse_args()

    collected_at = now_utc()
    index_path = Path("data/raw/binance_announcements/index_hits.json")
    if args.use_existing_index and index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        append_worklog([f"\n## {collected_at} - Reused cached announcement index", f"- cached_candidates={len(index)}", f"- source={index_path}"])
    else:
        index = collect_index(args.start, args.end, args.max_pages)
    Path("data/raw/binance_announcements").mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    selected = choose_validation_sample(index) if args.validation_sample else index
    rows: list[dict] = []
    details_ok = 0
    detail_cache_hits = 0
    detail_downloaded = 0
    manual = 0
    for item in selected:
        detail_path = Path(f"data/raw/binance_announcements/detail/{item['code']}.json")
        if detail_path.exists():
            detail = json.loads(detail_path.read_text(encoding="utf-8"))
            detail_cache_hits += 1
        else:
            detail = article_detail(item["code"])
            write_raw_json(detail_path, detail)
            detail_downloaded += 1
        if detail.get("success"):
            if not detail.get("data", {}).get("releaseDate") and item.get("releaseDate"):
                detail["data"]["releaseDate"] = item["releaseDate"]
                write_raw_json(detail_path, detail)
            details_ok += 1
            events, text = parse_article(detail, collected_at)
            Path(f"data/raw/binance_announcements/text/{item['code']}.txt").parent.mkdir(parents=True, exist_ok=True)
            Path(f"data/raw/binance_announcements/text/{item['code']}.txt").write_text(text, encoding="utf-8")
            rows.extend(events)
    # Dedup by URL + event_type + token_symbol.
    dedup = {}
    for row in rows:
        key = (row["announcement_url"], row["event_type"], row["token_symbol"])
        dedup[key] = row
    rows = list(dedup.values())
    manual = sum(1 for r in rows if r.get("manual_review_required") == "yes")

    out = Path("data/processed/events_validation.csv" if args.validation_sample else "data/processed/events.csv")
    write_csv(out, rows)
    append_worklog(
        [
            f"\n## {collected_at} - {'Validation sample' if args.validation_sample else 'Full event parse'}",
            f"- candidate_pages={len(index)}",
            f"- selected_pages={len(selected)}",
            f"- detail_cache_hits={detail_cache_hits}",
            f"- detail_downloaded={detail_downloaded}",
            f"- successfully_parsed_pages={details_ok}",
            f"- parsed_events={len(rows)}",
            f"- manual_review_events={manual}",
            f"- output={out}",
        ]
    )
    print(
        json.dumps(
            {
                "output": str(out),
                "candidate_pages": len(index),
                "selected_pages": len(selected),
                "detail_cache_hits": detail_cache_hits,
                "detail_downloaded": detail_downloaded,
                "successfully_parsed_pages": details_ok,
                "parsed_events": len(rows),
                "manual_review_events": manual,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
