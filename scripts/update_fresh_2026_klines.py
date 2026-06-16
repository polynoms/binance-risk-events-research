#!/usr/bin/env python3
"""Incrementally update local Binance spot kline cache for fresh 2026 sample tokens."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/klines/spot"
TOKENS = ["EPIC", "HEI", "ALCX", "COOKIE", "TLM"]


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def fetch(pair: str, interval: str, start: datetime, end: datetime, rate_limit: float) -> list[list]:
    endpoint = "https://api.binance.com/api/v3/klines"
    cursor = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    rows: list[list] = []
    while cursor <= end_ms:
        query = urllib.parse.urlencode(
            {"symbol": pair, "interval": interval, "startTime": cursor, "endTime": end_ms, "limit": 1000}
        )
        url = f"{endpoint}?{query}"
        with urllib.request.urlopen(url, timeout=20) as response:
            batch = json.load(response)
        if not batch:
            break
        rows.extend(batch)
        next_cursor = int(batch[-1][0]) + 1
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        time.sleep(rate_limit)
        if len(batch) < 1000:
            break
    rows = sorted({int(r[0]): r for r in rows}.values(), key=lambda r: int(r[0]))
    return rows


def write_cache(pair: str, interval: str, start: datetime, end: datetime, rows: list[list]) -> Path:
    out_dir = RAW / pair
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"{interval}_{int(start.timestamp() * 1000)}_{int(end.timestamp() * 1000)}_paged.json"
    out = out_dir / name
    out.write_text(json.dumps(rows, separators=(",", ":")), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", default=",".join(TOKENS))
    parser.add_argument("--end", default="2026-06-08T23:59:59Z")
    parser.add_argument("--rate-limit", type=float, default=0.15)
    args = parser.parse_args()

    tokens = [t.strip().upper() for t in args.tokens.split(",") if t.strip()]
    end = parse_dt(args.end)
    starts = {
        "1h": parse_dt("2026-05-22T00:00:00Z"),
        "1d": parse_dt("2026-05-22T00:00:00Z"),
        "15m": parse_dt("2026-05-21T00:00:00Z"),
    }
    summary = []
    for token in tokens:
        pair = f"{token}USDT"
        for interval, start in starts.items():
            rows = fetch(pair, interval, start, end, args.rate_limit)
            path = write_cache(pair, interval, start, end, rows)
            summary.append({"pair": pair, "interval": interval, "rows": len(rows), "path": str(path)})
            print(summary[-1])
    print({"updated": len(summary), "tokens": tokens, "end": end.isoformat()})


if __name__ == "__main__":
    main()
