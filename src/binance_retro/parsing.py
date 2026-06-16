from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


EVENT_TYPES = {
    "MONITORING_TAG_ADDED",
    "MONITORING_TAG_REMOVED",
    "SEED_TAG_ADDED",
    "SEED_TAG_REMOVED",
    "VOTE_TO_DELIST_STARTED",
    "VOTE_TO_DELIST_RESULT",
    "SPOT_TOKEN_DELISTING_ANNOUNCED",
    "FUTURES_CONTRACT_DELISTING_ANNOUNCED",
    "SPOT_PAIR_REMOVED",
}

SYMBOL_RE = re.compile(r"\(([A-Z0-9]{2,15})\)")
PAIR_RE = re.compile(r"\b([A-Z0-9]{2,20})/(USDT|USDC|FDUSD|BTC|ETH|BNB|EUR|TRY|BRL|AUD|BUSD|DAI|TUSD)\b")
COMPACT_PAIR_RE = re.compile(r"\b([A-Z0-9]{2,20})(USDT|USDC|FDUSD|BTC|ETH|BNB|BUSD)\b")
UTC_RE = re.compile(r"20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}\s*\(UTC\)")
SYMBOL_STOPWORDS = {
    "UTC",
    "IBC",
    "API",
    "VIP",
    "USD",
    "CEX",
    "DEX",
    "FAQ",
    "NFT",
    "APR",
    "KYC",
}


@dataclass
class ParsedEvent:
    event_id: str
    token_symbol: str
    token_name: str
    token_entity_id: str
    event_type: str
    announcement_title: str
    announcement_url: str
    publication_datetime_utc: str
    effective_datetime_utc: str
    affected_markets: str
    affected_pairs: str
    token_remains_tradable_on_binance: str
    is_token_level_event: str
    is_pair_level_event: str
    previous_tag_status: str
    new_tag_status: str
    raw_text_hash: str
    source: str
    notes: str
    confidence_score: float
    manual_review_required: str
    parser_version: str
    collected_at_utc: str


def utc_from_ms(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_utc_text(value: str) -> str:
    value = value.replace("(UTC)", "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        except ValueError:
            pass
    return ""


def body_to_text(body: Any) -> str:
    if isinstance(body, str):
        try:
            return body_to_text(json.loads(body))
        except json.JSONDecodeError:
            return body
    if isinstance(body, dict):
        chunks = []
        if "text" in body and isinstance(body["text"], str):
            chunks.append(body["text"])
        cfg = body.get("config")
        if isinstance(cfg, dict) and isinstance(cfg.get("content"), str):
            chunks.append(cfg["content"])
        for key in ("child", "children", "content"):
            value = body.get(key)
            if value is not None:
                chunks.append(body_to_text(value))
        return " ".join(c for c in chunks if c)
    if isinstance(body, list):
        return " ".join(body_to_text(x) for x in body)
    return ""


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def symbol_name_pairs(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for match in SYMBOL_RE.finditer(text):
        symbol = match.group(1)
        if symbol in SYMBOL_STOPWORDS:
            continue
        start = max(0, text.rfind(" ", 0, match.start() - 1))
        phrase = text[max(0, start - 60) : match.start()].strip(" :-,;")
        token_name = phrase.split(".")[-1].split(":")[-1].strip(" ,-;")
        token_name = re.sub(r"^(and|or)\s+", "", token_name, flags=re.I)
        if len(token_name) > 80:
            token_name = ""
        found.append((symbol, token_name))
    dedup = []
    seen = set()
    for symbol, token_name in found:
        if symbol not in seen:
            seen.add(symbol)
            dedup.append((symbol, token_name))
    return dedup


def title_symbol_list(segment: str) -> list[str]:
    segment = re.sub(r"\bon\s+20\d{2}-\d{2}-\d{2}.*$", "", segment, flags=re.I)
    segment = segment.replace("&", ",")
    segment = re.sub(r"\band\b", ",", segment, flags=re.I)
    out = []
    for raw in re.split(r"[,;/]", segment):
        symbol = raw.strip().upper()
        symbol = re.sub(r"[^A-Z0-9].*$", "", symbol)
        if 2 <= len(symbol) <= 15 and symbol not in SYMBOL_STOPWORDS:
            out.append(symbol)
    seen = set()
    return [s for s in out if not (s in seen or seen.add(s))]


def symbols_from_title_for_event(event_type: str, title: str) -> list[tuple[str, str]]:
    if event_type == "MONITORING_TAG_ADDED":
        m = re.search(r"Monitoring Tag to Include (.*?)(?:,?\s+and Remove| and Remove| on 20\d{2}-\d{2}-\d{2}|$)", title, re.I)
        return [(s, "") for s in title_symbol_list(m.group(1))] if m else []
    if event_type == "MONITORING_TAG_REMOVED":
        m = re.search(r"Remove the Monitoring Tag for (.*?)(?:,?\s+and Remove| on 20\d{2}-\d{2}-\d{2}|$)", title, re.I)
        return [(s, "") for s in title_symbol_list(m.group(1))] if m else []
    if event_type == "SEED_TAG_REMOVED":
        m = re.search(r"Remove the Seed Tag for (.*?)(?:,?\s+and Remove| on 20\d{2}-\d{2}-\d{2}|$)", title, re.I)
        return [(s, "") for s in title_symbol_list(m.group(1))] if m else []
    if event_type == "SPOT_TOKEN_DELISTING_ANNOUNCED":
        m = re.search(r"Will Delist (.*?)(?: on 20\d{2}-\d{2}-\d{2}|$)", title, re.I)
        return [(s, "") for s in title_symbol_list(m.group(1))] if m else []
    return []


def affected_pairs(text: str) -> list[str]:
    pairs = {f"{m.group(1)}/{m.group(2)}" for m in PAIR_RE.finditer(text)}
    return sorted(pairs)


def compact_pairs(text: str) -> list[str]:
    pairs = set()
    for m in COMPACT_PAIR_RE.finditer(text):
        base, quote = m.group(1), m.group(2)
        if base not in {"USD", "US"} and len(base) > 1:
            pairs.add(f"{base}/{quote}")
    return sorted(pairs)


def classify_article(title: str, text: str) -> dict[str, Any]:
    lower_title = title.lower()
    lower_text = text.lower()
    markets: set[str] = set()
    event_types: set[str] = set()
    confidence = 0.62
    notes: list[str] = []
    lower_full = f"{lower_title} {lower_text}"

    if "monitoring tag" in lower_title or "monitoring tag" in lower_text:
        markets.update({"spot", "margin"})
        if re.search(r"extend the monitoring tag|added to the monitoring tag|to include", lower_title):
            event_types.add("MONITORING_TAG_ADDED")
            confidence = max(confidence, 0.88)
        if "remove the monitoring tag" in lower_title or "removed from the monitoring tag" in lower_text:
            event_types.add("MONITORING_TAG_REMOVED")
            confidence = max(confidence, 0.88)
    if "seed tag" in lower_title or "seed tag" in lower_text:
        markets.add("spot")
        if "with seed tag applied" in lower_title or "seed tag applied" in lower_text:
            event_types.add("SEED_TAG_ADDED")
            confidence = max(confidence, 0.82)
        if "remove the seed tag" in lower_title or "seed tag removed" in lower_text:
            event_types.add("SEED_TAG_REMOVED")
            confidence = max(confidence, 0.84)
    if "vote to delist" in lower_title or "vote to delist" in lower_text:
        if any(x in lower_title for x in ("result", "results", "concludes", "concluded")):
            event_types.add("VOTE_TO_DELIST_RESULT")
        else:
            event_types.add("VOTE_TO_DELIST_STARTED")
        confidence = max(confidence, 0.82)
    if "futures will delist" in lower_title or ("usdⓢ-m" in lower_title and "delist" in lower_title):
        event_types.add("FUTURES_CONTRACT_DELISTING_ANNOUNCED")
        markets.add("futures")
        confidence = max(confidence, 0.87)
    if "notice of removal of spot trading pairs" in lower_title:
        event_types.add("SPOT_PAIR_REMOVED")
        markets.add("spot")
        confidence = max(confidence, 0.93)
    elif "will delist" in lower_title and "spot trading pairs" in lower_text and "futures" not in lower_title:
        event_types.add("SPOT_TOKEN_DELISTING_ANNOUNCED")
        markets.add("spot")
        confidence = max(confidence, 0.88)

    if "does not affect the availability of the tokens on binance spot" in lower_text:
        notes.append("Official text states pair removal does not affect token availability.")
    token_level_spot_delist_body = (
        "all spot trading pairs" in lower_text
        or "delist and cease trading on all trading pairs for the following tokens" in lower_text
        or "delist and cease trading on all trading pairs for the following token(s)" in lower_text
        or "remove and cease trading on all trading pairs for the following tokens" in lower_text
        or "remove and cease trading on all trading pairs for the following token(s)" in lower_text
    )
    if token_level_spot_delist_body:
        notes.append("Official text references all trading pairs for the affected tokens.")
    if "busd" in lower_full and "futures will delist" in lower_title:
        notes.append("futures_delisting_subtype=normal_bUSD_contract_sunset_or_migration_review")
    elif "futures" in lower_full and "delist" in lower_full:
        notes.append("futures_delisting_subtype=risk_or_contract_specific_review_required")

    return {
        "event_types": sorted(event_types),
        "affected_markets": sorted(markets),
        "confidence": confidence,
        "notes": notes,
    }


def split_symbols_for_event(event_type: str, title: str, text: str) -> list[tuple[str, str]]:
    from_title = symbols_from_title_for_event(event_type, title)
    if from_title:
        return from_title
    if event_type == "SPOT_PAIR_REMOVED":
        pairs = affected_pairs(text)
        return [(p.split("/")[0], "") for p in pairs]
    if event_type == "FUTURES_CONTRACT_DELISTING_ANNOUNCED":
        return [(p.split("/")[0], "") for p in compact_pairs(title + " " + text)]
    return symbol_name_pairs(title + " " + text)


def parse_article(detail: dict[str, Any], collected_at_utc: str) -> tuple[list[dict[str, Any]], str]:
    data = detail["data"]
    title = data.get("title", "")
    code = data.get("code", "")
    url = f"https://www.binance.com/en/support/announcement/detail/{code}"
    text = clean_text(body_to_text(data.get("body", "")))
    full_text = clean_text(f"{title} {text}")
    raw_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
    publication = utc_from_ms(data.get("releaseDate"))
    effective = ""
    effective_match = UTC_RE.search(full_text)
    if effective_match:
        effective = normalize_utc_text(effective_match.group(0))
    meta = classify_article(title, full_text)
    pairs = affected_pairs(full_text)
    events: list[dict[str, Any]] = []

    for event_type in meta["event_types"]:
        symbols = split_symbols_for_event(event_type, title, full_text)
        if not symbols:
            symbols = [("", "")]
        for symbol, token_name in symbols:
            is_pair = event_type == "SPOT_PAIR_REMOVED"
            is_token = event_type not in {"SPOT_PAIR_REMOVED", "FUTURES_CONTRACT_DELISTING_ANNOUNCED"}
            token_remains = "unknown"
            if is_pair:
                token_remains = "yes"
            elif event_type == "SPOT_TOKEN_DELISTING_ANNOUNCED":
                token_remains = "no_after_effective_time"
            event_key = f"{code}:{event_type}:{symbol}"
            confidence = float(meta["confidence"])
            manual = confidence < 0.75 or not symbol
            token_level_spot_delist_body = (
                "all spot trading pairs" in full_text.lower()
                or "delist and cease trading on all trading pairs for the following tokens" in full_text.lower()
                or "delist and cease trading on all trading pairs for the following token(s)" in full_text.lower()
                or "remove and cease trading on all trading pairs for the following tokens" in full_text.lower()
                or "remove and cease trading on all trading pairs for the following token(s)" in full_text.lower()
            )
            if event_type == "SPOT_TOKEN_DELISTING_ANNOUNCED" and not token_level_spot_delist_body:
                manual = True
                confidence = min(confidence, 0.74)
            if event_type == "SPOT_TOKEN_DELISTING_ANNOUNCED" and token_level_spot_delist_body:
                manual = manual and confidence < 0.75
                confidence = max(confidence, 0.91)
            parsed = ParsedEvent(
                event_id=hashlib.sha1(event_key.encode("utf-8")).hexdigest()[:16],
                token_symbol=symbol,
                token_name=token_name,
                token_entity_id=symbol,
                event_type=event_type,
                announcement_title=title,
                announcement_url=url,
                publication_datetime_utc=publication,
                effective_datetime_utc=effective,
                affected_markets=";".join(meta["affected_markets"]),
                affected_pairs=";".join(pairs),
                token_remains_tradable_on_binance=token_remains,
                is_token_level_event="yes" if is_token else "no",
                is_pair_level_event="yes" if is_pair else "no",
                previous_tag_status="",
                new_tag_status=tag_status(event_type),
                raw_text_hash=raw_hash,
                source="binance_official_announcement",
                notes=" ".join(meta["notes"]),
                confidence_score=confidence,
                manual_review_required="yes" if manual else "no",
                parser_version="v1",
                collected_at_utc=collected_at_utc,
            )
            events.append(asdict(parsed))
    return events, text


def tag_status(event_type: str) -> str:
    if event_type == "MONITORING_TAG_ADDED":
        return "monitoring_tag"
    if event_type == "MONITORING_TAG_REMOVED":
        return "none_or_seed_tag_unknown"
    if event_type == "SEED_TAG_ADDED":
        return "seed_tag"
    if event_type == "SEED_TAG_REMOVED":
        return "none_or_monitoring_tag_unknown"
    return ""
