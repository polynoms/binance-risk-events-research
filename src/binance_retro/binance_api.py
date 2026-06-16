from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path
from typing import Any


BASE = "https://www.binance.com"


def get_json(url: str, timeout: int = 30, sleep_s: float = 5.0, retries: int = 8) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; binance-risk-retro-v1)",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read().decode("utf-8")
            break
        except HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            time.sleep(min(60, 2 ** attempt))
    if sleep_s:
        time.sleep(sleep_s)
    return json.loads(payload)


def list_articles(catalog_id: int, page_no: int, page_size: int = 50) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {
            "type": 1,
            "catalogId": catalog_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }
    )
    return get_json(f"{BASE}/bapi/composite/v1/public/cms/article/list/query?{query}")


def article_detail(article_code: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"articleCode": article_code})
    return get_json(f"{BASE}/bapi/composite/v1/public/cms/article/detail/query?{query}")


def write_raw_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
