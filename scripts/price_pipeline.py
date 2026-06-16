#!/usr/bin/env python3
from __future__ import annotations

import csv
import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import ccxt


SPOT_BASE = "https://api.binance.com"
FUTURES_BASE = "https://fapi.binance.com"
QUOTE_PRIORITY = ["USDT", "USDC", "FDUSD"]
TIMEFRAMES = ["1d", "1h", "15m"]
SAMPLE_TOKENS = ["CVX", "ZEC", "AERGO", "BADGER", "A2Z", "AKRO", "BTS", "ALCX", "1000CHEEMS", "APT", "0G"]
ALT_BENCHMARK_SYMBOLS = ["BNB", "SOL", "XRP", "DOGE", "ADA", "AVAX", "DOT", "LINK", "LTC", "TRX"]
COINGECKO_IDS = {
    "AERGO": "aergo",
    "BADGER": "badger-dao",
    "AKRO": "akropolis",
    "BTS": "bitshares",
}
CCXT_EXCHANGES = ["kucoin", "gateio", "mexc", "bitget", "okx", "bybit"]
FALLBACK_QUOTES = ["USDT", "USDC", "USD"]
WINDOWS = {
    "-30d": -30 * 24,
    "-14d": -14 * 24,
    "-7d": -7 * 24,
    "-3d": -3 * 24,
    "-1d": -24,
    "-24h": -24,
    "-4h": -4,
    "-1h": -1,
    "+1h": 1,
    "+4h": 4,
    "+12h": 12,
    "+24h": 24,
    "+3d": 3 * 24,
    "+7d": 7 * 24,
    "+14d": 14 * 24,
    "+30d": 30 * 24,
    "+60d": 60 * 24,
    "+90d": 90 * 24,
}
METRICS = {
    "api_requests_spot": 0,
    "api_requests_futures": 0,
    "api_429_count": 0,
    "kline_cache_hits": 0,
    "kline_downloads": 0,
    "fallback_requests": 0,
    "fallback_points_used": 0,
    "fallback_429_count": 0,
    "fallback_provider_errors": 0,
    "ccxt_exchanges_checked": 0,
    "ccxt_ohlcv_requests": 0,
    "ccxt_points_used": 0,
}


OUTPUTS = {
    "sample": {
        "resolution": "data/processed/price_sample_resolution.csv",
        "price_windows": "data/processed/price_windows_sample.csv",
        "price_windows_parquet": "data/processed/price_windows_sample.parquet",
        "recovery": "data/processed/recovery_analysis_sample.csv",
        "pump": "data/processed/pump_analysis_sample.csv",
        "fallback_quality": "data/processed/fallback_data_quality_sample.csv",
    },
    "full": {
        "resolution": "data/processed/price_resolution.csv",
        "price_windows": "data/processed/price_windows.csv",
        "price_windows_parquet": "data/processed/price_windows.parquet",
        "recovery": "data/processed/recovery_analysis.csv",
        "pump": "data/processed/pump_analysis.csv",
        "fallback_quality": "data/processed/fallback_data_quality.csv",
    },
}

SCHEMAS = {
    "pump": [
        "event_id",
        "token_entity_id",
        "token_symbol",
        "anchor_event_type",
        "baseline_price",
        "max_return_1h",
        "max_return_4h",
        "max_return_24h",
        "max_return_3d",
        "max_return_7d",
        "max_return_until_effective_delisting",
        "max_return_price_source",
        "max_return_exchange",
        "volume_zscore",
        "post_pump_drawdown",
        "pump20_flag",
        "pump_and_dump_flag",
        "low_liquidity_pump_flag",
        "fallback_used",
        "manual_review_required",
    ],
}


def outputs_for(mode: str, output_suffix: str, output_dir: str) -> dict[str, str]:
    outputs = dict(OUTPUTS[mode])
    if output_dir:
        base = Path(output_dir)
        return {
            "resolution": str(base / "price_resolution.csv"),
            "price_windows": str(base / "price_windows.csv"),
            "price_windows_parquet": str(base / "price_windows.parquet"),
            "recovery": str(base / "recovery_analysis.csv"),
            "pump": str(base / "pump_analysis.csv"),
            "fallback_quality": str(base / "fallback_data_quality.csv"),
        }
    if output_suffix:
        normalized = output_suffix if output_suffix.startswith("_") else f"_{output_suffix}"
        stemmed = {}
        for key, value in outputs.items():
            path = Path(value)
            if path.suffix == ".parquet":
                stemmed[key] = str(path.with_name(f"{path.stem}{normalized}.parquet"))
            else:
                stemmed[key] = str(path.with_name(f"{path.stem}{normalized}{path.suffix}"))
        return stemmed
    return outputs


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def get_json(url: str, retries: int = 5, sleep_s: float = 0.5):
    req = urllib.request.Request(url, headers={"User-Agent": "binance-risk-retro-v1"})
    last = None
    for attempt in range(retries + 1):
        try:
            if "fapi.binance.com" in url:
                METRICS["api_requests_futures"] += 1
            else:
                METRICS["api_requests_spot"] += 1
            with urllib.request.urlopen(req, timeout=30) as resp:
                out = json.loads(resp.read().decode("utf-8"))
            time.sleep(sleep_s)
            return out
        except HTTPError as exc:
            if exc.code == 429:
                METRICS["api_429_count"] += 1
            last = exc
            time.sleep(min(20, 2**attempt))
        except Exception as exc:
            last = exc
            time.sleep(min(20, 2**attempt))
    raise last


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fieldnames or (list(rows[0].keys()) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def append_worklog(lines: list[str]) -> None:
    with Path("docs/codex/worklog.md").open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def coingecko_market_chart(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    cg_id = COINGECKO_IDS.get(symbol)
    if not cg_id:
        return pd.DataFrame()
    raw_dir = Path("data/raw/fallback_prices/coingecko") / symbol
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{ms(start)}_{ms(end)}.json"
    if raw_path.exists():
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
    else:
        query = urllib.parse.urlencode({"vs_currency": "usd", "from": int(start.timestamp()), "to": int(end.timestamp())})
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart/range?{query}"
        try:
            payload = get_json(url, sleep_s=8.0, retries=2)
        except HTTPError as exc:
            if exc.code == 429:
                METRICS["fallback_429_count"] += 1
            else:
                METRICS["fallback_provider_errors"] += 1
            return pd.DataFrame()
        except URLError:
            METRICS["fallback_provider_errors"] += 1
            return pd.DataFrame()
        raw_path.write_text(json.dumps(payload), encoding="utf-8")
        METRICS["fallback_requests"] += 1
    prices = payload.get("prices", [])
    if not prices:
        return pd.DataFrame()
    df = pd.DataFrame(prices, columns=["open_time", "close"])
    df["open_datetime_utc"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["volume"] = 0.0
    df["quote_volume"] = 0.0
    return df


def ccxt_exchange(exchange_id: str):
    cls = getattr(ccxt, exchange_id)
    return cls({"enableRateLimit": True, "timeout": 30000})


def ccxt_fallback_ohlcv(symbol: str, start: datetime, end: datetime) -> tuple[pd.DataFrame, str, str]:
    candidates = []
    for exchange_id in CCXT_EXCHANGES:
        METRICS["ccxt_exchanges_checked"] += 1
        raw_dir = Path("data/raw/fallback_prices/ccxt") / exchange_id / symbol
        raw_dir.mkdir(parents=True, exist_ok=True)
        meta_path = raw_dir / "markets.json"
        try:
            ex = ccxt_exchange(exchange_id)
            if meta_path.exists():
                markets = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                markets = ex.load_markets()
                meta_path.write_text(json.dumps(markets, default=str), encoding="utf-8")
            for quote in FALLBACK_QUOTES:
                market_symbol = f"{symbol}/{quote}"
                if market_symbol not in markets:
                    continue
                raw_path = raw_dir / f"{market_symbol.replace('/', '_')}_1d_{ms(start)}_{ms(end)}.json"
                if raw_path.exists():
                    data = json.loads(raw_path.read_text(encoding="utf-8"))
                else:
                    since = ms(start)
                    data = []
                    for _ in range(20):
                        chunk = ex.fetch_ohlcv(market_symbol, timeframe="1d", since=since, limit=1000)
                        METRICS["ccxt_ohlcv_requests"] += 1
                        if not chunk:
                            break
                        data.extend(chunk)
                        since = int(chunk[-1][0]) + 24 * 60 * 60 * 1000
                        if since > ms(end) or len(chunk) < 1000:
                            break
                    raw_path.write_text(json.dumps(data), encoding="utf-8")
                if not data:
                    continue
                df = pd.DataFrame(data, columns=["open_time", "open", "high", "low", "close", "volume"])
                df["open_datetime_utc"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
                for c in ["open", "high", "low", "close", "volume"]:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
                df = df[(df["open_datetime_utc"] >= pd.Timestamp(start)) & (df["open_datetime_utc"] <= pd.Timestamp(end))]
                if df.empty:
                    continue
                df["quote_volume"] = df["close"] * df["volume"]
                score = (len(df), float(df["quote_volume"].fillna(0).sum()))
                candidates.append((score, df, exchange_id, market_symbol))
        except Exception:
            METRICS["fallback_provider_errors"] += 1
            continue
    if not candidates:
        return pd.DataFrame(), "", ""
    candidates.sort(key=lambda x: x[0], reverse=True)
    _, df, exchange_id, market_symbol = candidates[0]
    return df, f"ccxt_{exchange_id}", market_symbol


@dataclass
class ResolvedPair:
    symbol: str
    pair: str
    market_type: str
    status: str
    missing: bool
    notes: str = ""


def load_events() -> tuple[list[dict], list[dict]]:
    events = list(csv.DictReader(open("data/processed/events.csv", encoding="utf-8")))
    lifecycle = list(csv.DictReader(open("data/processed/token_lifecycle.csv", encoding="utf-8")))
    return events, lifecycle


def exchange_info(base: str, raw_name: str) -> dict:
    path = Path(f"data/raw/klines/{raw_name}_exchange_info.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    payload = get_json(f"{base}/api/v3/exchangeInfo" if raw_name == "spot" else f"{base}/fapi/v1/exchangeInfo")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def resolve_spot(symbol: str, spot_info: dict) -> ResolvedPair:
    by_symbol = {s["symbol"]: s for s in spot_info.get("symbols", [])}
    for quote in QUOTE_PRIORITY:
        pair = f"{symbol}{quote}"
        if pair in by_symbol:
            return ResolvedPair(symbol, pair, "spot", by_symbol[pair].get("status", ""), False)
    return ResolvedPair(symbol, "", "spot", "", True, "no_usdt_usdc_fdusd_pair_in_exchange_info")


def resolve_futures(symbol: str, futures_info: dict) -> ResolvedPair:
    by_symbol = {s["symbol"]: s for s in futures_info.get("symbols", [])}
    for quote in ["USDT", "USDC", "BUSD"]:
        pair = f"{symbol}{quote}"
        if pair in by_symbol:
            notes = "normal_contract_sunset_or_migration_review" if quote == "BUSD" else ""
            return ResolvedPair(symbol, pair, "futures", by_symbol[pair].get("status", ""), False, notes)
    return ResolvedPair(symbol, "", "futures", "", True, "no_usdm_pair_in_exchange_info")


def exact_futures_contract(symbol: str, events: list[dict], futures_info: dict) -> ResolvedPair | None:
    suffixes = ("USDT", "USDC", "BUSD", "USD")
    for event in events:
        if event["event_type"] != "FUTURES_CONTRACT_DELISTING_ANNOUNCED":
            continue
        title = event["announcement_title"]
        matches = []
        for token in title.replace(",", " ").split():
            clean = "".join(ch for ch in token if ch.isalnum())
            if any(clean.endswith(s) for s in suffixes) and clean.startswith(symbol):
                matches.append(clean)
        if not matches:
            continue
        pair = matches[0]
        subtype = "normal_contract_sunset_or_migration_review" if pair.endswith("BUSD") else "risk_relevant_or_contract_specific_review"
        return ResolvedPair(symbol, pair, "futures", "historical_or_current", False, subtype)
    return None


def fetch_klines(pair: str, interval: str, start: datetime, end: datetime, market: str) -> pd.DataFrame:
    if not pair:
        return pd.DataFrame()
    raw_dir = Path("data/raw/klines") / market / pair
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{interval}_{ms(start)}_{ms(end)}_paged.json"
    if raw_path.exists():
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        METRICS["kline_cache_hits"] += 1
    else:
        base = SPOT_BASE if market == "spot" else FUTURES_BASE
        endpoint = "/api/v3/klines" if market == "spot" else "/fapi/v1/klines"
        data = []
        cursor = ms(start)
        end_ms = ms(end)
        while cursor < end_ms:
            query = urllib.parse.urlencode({"symbol": pair, "interval": interval, "startTime": cursor, "endTime": end_ms, "limit": 1000})
            chunk = get_json(f"{base}{endpoint}?{query}")
            if not chunk:
                break
            data.extend(chunk)
            last_open = int(chunk[-1][0])
            next_cursor = last_open + 1
            if next_cursor <= cursor:
                break
            cursor = next_cursor
            if len(chunk) < 1000:
                break
        raw_path.write_text(json.dumps(data), encoding="utf-8")
        METRICS["kline_downloads"] += 1
    if not data:
        return pd.DataFrame()
    cols = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades", "taker_base", "taker_quote", "ignore"]
    df = pd.DataFrame(data, columns=cols[: len(data[0])])
    for c in ["open", "high", "low", "close", "volume", "quote_volume"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_datetime_utc"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def closest_close(df: pd.DataFrame, target: datetime) -> float | None:
    if df.empty:
        return None
    t = pd.Timestamp(target)
    before = df[df["open_datetime_utc"] <= t]
    if before.empty:
        return None
    # Do not carry a stale final Binance candle across long post-delisting
    # windows. Missing after the last available candle should stay missing.
    last_time = before.iloc[-1]["open_datetime_utc"]
    if t - last_time > pd.Timedelta(hours=48):
        return None
    return float(before.iloc[-1]["close"])


def row_price(df: pd.DataFrame, target: datetime) -> tuple[float | None, str]:
    price = closest_close(df, target)
    return price, "binance" if price is not None else "missing"


def closest_fallback_close(df: pd.DataFrame, target: datetime) -> float | None:
    price = closest_close(df, target)
    if price is not None:
        METRICS["fallback_points_used"] += 1
    return price


def baselines(daily: pd.DataFrame, event_dt: datetime) -> dict:
    if daily.empty:
        return {k: math.nan for k in ["baseline_vwap_7d", "baseline_median_close_7d", "baseline_close_1d", "baseline_median_close_30d"]}
    t = pd.Timestamp(event_dt)
    pre7 = daily[(daily["open_datetime_utc"] < t) & (daily["open_datetime_utc"] >= t - pd.Timedelta(days=7))]
    pre30 = daily[(daily["open_datetime_utc"] < t) & (daily["open_datetime_utc"] >= t - pd.Timedelta(days=30))]
    close_1d = closest_close(daily, event_dt - timedelta(days=1))
    vwap = (pre7["close"] * pre7["volume"]).sum() / pre7["volume"].sum() if not pre7.empty and pre7["volume"].sum() else math.nan
    return {
        "baseline_vwap_7d": vwap,
        "baseline_median_close_7d": float(pre7["close"].median()) if not pre7.empty else math.nan,
        "baseline_close_1d": close_1d if close_1d is not None else math.nan,
        "baseline_median_close_30d": float(pre30["close"].median()) if not pre30.empty else math.nan,
    }


def pct(a: float | None, b: float | None) -> float:
    if a is None or b is None or not b or math.isnan(b):
        return math.nan
    return a / b - 1


def event_windows(
    event: dict,
    pair: ResolvedPair,
    daily: pd.DataFrame,
    hourly: pd.DataFrame,
    btc: pd.DataFrame,
    eth: pd.DataFrame,
    fallback: pd.DataFrame,
    fallback_source: str,
    alt_hourly: dict[str, pd.DataFrame],
) -> list[dict]:
    event_dt = dt(event["publication_datetime_utc"])
    base = baselines(daily, event_dt)
    event_price = closest_close(hourly if not hourly.empty else daily, event_dt)
    event_price_source = "binance" if event_price is not None else "missing"
    if event_price is None and not fallback.empty:
        event_price = closest_fallback_close(fallback, event_dt)
        event_price_source = fallback_source if event_price is not None else "missing"
    rows = []
    for label, hours in WINDOWS.items():
        target = event_dt + timedelta(hours=hours)
        df = hourly if abs(hours) <= 24 else daily
        price = closest_close(df, target)
        price_source = "binance"
        if price is None and not fallback.empty:
            price = closest_fallback_close(fallback, target)
            price_source = fallback_source if price is not None else "missing"
        elif price is None:
            price_source = "missing"
        btc_ret = pct(closest_close(btc, target), closest_close(btc, event_dt))
        eth_ret = pct(closest_close(eth, target), closest_close(eth, event_dt))
        alt_rets = []
        for alt_symbol, alt_df in alt_hourly.items():
            if alt_symbol == event["token_symbol"]:
                continue
            ret = pct(closest_close(alt_df, target), closest_close(alt_df, event_dt))
            if not math.isnan(ret):
                alt_rets.append(ret)
        alt_ret = sum(alt_rets) / len(alt_rets) if len(alt_rets) >= 5 else math.nan
        raw = pct(price, event_price)
        missing_reason = ""
        if price is None or event_price is None:
            if not pair.pair:
                missing_reason = "unresolved_pair_or_symbol"
            elif event["event_type"] == "SPOT_TOKEN_DELISTING_ANNOUNCED" and hours > 24:
                missing_reason = "expected_post_delisting_missing;fallback_provider_unavailable"
            else:
                missing_reason = "true_data_gap"
        if math.isnan(btc_ret) or math.isnan(eth_ret) or math.isnan(alt_ret):
            missing_reason = (missing_reason + ";benchmark_gap").strip(";")
        rows.append(
            {
                "event_id": event["event_id"],
                "token_entity_id": event["token_entity_id"],
                "token_symbol": event["token_symbol"],
                "event_type": event["event_type"],
                "symbol_pair": pair.pair,
                "market_type": pair.market_type,
                "price_source": "binance_" + pair.market_type if pair.pair else "missing",
                "window_price_source": price_source,
                "event_price_source": event_price_source,
                "window": label,
                "publication_datetime_utc": event["publication_datetime_utc"],
                **base,
                "event_price": event_price if event_price is not None else math.nan,
                "window_price": price if price is not None else math.nan,
                "raw_return": raw,
                "btc_adjusted_return": raw - btc_ret if not math.isnan(raw) and not math.isnan(btc_ret) else math.nan,
                "eth_adjusted_return": raw - eth_ret if not math.isnan(raw) and not math.isnan(eth_ret) else math.nan,
                "alt_benchmark_adjusted_return": raw - alt_ret if not math.isnan(raw) and not math.isnan(alt_ret) else math.nan,
                "alt_benchmark_constituents": len(alt_rets),
                "missing_price_flag": "yes" if price is None or event_price is None else "no",
                "missing_price_reason": missing_reason,
                "benchmark_gap": "yes" if math.isnan(btc_ret) or math.isnan(eth_ret) or math.isnan(alt_ret) else "no",
            }
        )
    return rows


def recovery_row(symbol: str, anchor_event: dict, daily: pd.DataFrame, fallback: pd.DataFrame) -> dict:
    event_dt = dt(anchor_event["publication_datetime_utc"])
    base = baselines(daily, event_dt)
    baseline = base["baseline_vwap_7d"] if not math.isnan(base["baseline_vwap_7d"]) else base["baseline_median_close_7d"]
    if daily.empty or "open_datetime_utc" not in daily.columns:
        return {
            "token_symbol": symbol,
            "anchor_event_id": anchor_event["event_id"],
            "anchor_event_type": anchor_event["event_type"],
            "baseline_price": baseline,
            "recovery_90_touch": "unknown",
            "recovery_100_touch": "unknown",
            "recovery_90_sustained": "unknown",
            "recovery_100_sustained": "unknown",
            "never_recovered": "unknown",
            "missing_price_flag": "yes",
            "fallback_used": "yes" if not fallback.empty else "no",
        }
    post = daily[(daily["open_datetime_utc"] >= pd.Timestamp(event_dt)) & (daily["open_datetime_utc"] <= pd.Timestamp(event_dt + timedelta(days=90)))]
    if not fallback.empty:
        fpost = fallback[(fallback["open_datetime_utc"] >= pd.Timestamp(event_dt)) & (fallback["open_datetime_utc"] <= pd.Timestamp(event_dt + timedelta(days=90)))]
        if not fpost.empty:
            post = pd.concat([post, fpost], ignore_index=True).sort_values("open_datetime_utc")
    if post.empty or math.isnan(baseline):
        return {"token_symbol": symbol, "anchor_event_id": anchor_event["event_id"], "never_recovered": "unknown", "missing_price_flag": "yes"}
    closes = post["close"].tolist()
    def sustained(level: float) -> bool:
        streak = 0
        for c in closes:
            streak = streak + 1 if c >= level else 0
            if streak >= 3:
                return True
        return False
    return {
        "token_symbol": symbol,
        "anchor_event_id": anchor_event["event_id"],
        "anchor_event_type": anchor_event["event_type"],
        "baseline_price": baseline,
        "recovery_90_touch": "yes" if post["high"].max() >= 0.9 * baseline else "no",
        "recovery_100_touch": "yes" if post["high"].max() >= baseline else "no",
        "recovery_90_sustained": "yes" if sustained(0.9 * baseline) else "no",
        "recovery_100_sustained": "yes" if sustained(baseline) else "no",
        "never_recovered": "yes" if post["high"].max() < 0.9 * baseline else "no",
        "missing_price_flag": "no",
        "fallback_used": "yes" if not fallback.empty else "no",
    }


def volume_zscore_around(daily: pd.DataFrame, event_dt: datetime) -> float:
    if daily.empty or "quote_volume" not in daily:
        return math.nan
    t = pd.Timestamp(event_dt)
    pre = daily[(daily["open_datetime_utc"] < t) & (daily["open_datetime_utc"] >= t - pd.Timedelta(days=30))]
    cur = daily[daily["open_datetime_utc"] >= t].head(1)
    if pre.empty or cur.empty:
        return math.nan
    std = pre["quote_volume"].std()
    if not std or math.isnan(std):
        return math.nan
    return float((cur.iloc[0]["quote_volume"] - pre["quote_volume"].mean()) / std)


def pump_analysis_rows(events: list[dict], price_rows: list[dict], daily_by_symbol: dict[str, pd.DataFrame], fallback_by_symbol: dict[str, pd.DataFrame]) -> list[dict]:
    out = []
    by_event: dict[str, list[dict]] = {}
    for row in price_rows:
        by_event.setdefault(row["event_id"], []).append(row)
    wanted = {"SPOT_TOKEN_DELISTING_ANNOUNCED"}
    for event in events:
        if event["event_type"] not in wanted:
            continue
        rows = by_event.get(event["event_id"], [])
        if not rows:
            continue
        symbol = event["token_symbol"]
        event_dt = dt(event["publication_datetime_utc"])
        baseline = rows[0].get("baseline_vwap_7d", math.nan)
        by_window = {r["window"]: r for r in rows}
        horizons = {
            "1h": "+1h",
            "4h": "+4h",
            "24h": "+24h",
            "3d": "+3d",
            "7d": "+7d",
        }
        returns = {name: by_window.get(label, {}).get("raw_return", math.nan) for name, label in horizons.items()}
        until_rows = [r for r in rows if r["window"] in {"+1h", "+4h", "+12h", "+24h", "+3d", "+7d", "+14d", "+30d", "+60d", "+90d"}]
        valid_returns = [r for r in until_rows if not pd.isna(r.get("raw_return", math.nan))]
        max_row = max(valid_returns, key=lambda r: r["raw_return"]) if valid_returns else {}
        max_return = max_row.get("raw_return", math.nan)
        min_after = min((r["raw_return"] for r in valid_returns), default=math.nan)
        drawdown = min_after - max_return if not pd.isna(max_return) and not pd.isna(min_after) else math.nan
        fallback_used = any(str(r.get("window_price_source", "")).startswith("ccxt_") for r in rows)
        fallback_df = fallback_by_symbol.get(symbol, pd.DataFrame())
        fallback_quote_volume = float(fallback_df["quote_volume"].fillna(0).sum()) if not fallback_df.empty and "quote_volume" in fallback_df else math.nan
        low_liq = fallback_used and (pd.isna(fallback_quote_volume) or fallback_quote_volume < 100000)
        suspicious = fallback_used and not pd.isna(max_return) and max_return >= 1.0
        pump20 = bool(not pd.isna(max_return) and max_return >= 0.20)
        pump_and_dump = bool(pump20 and not pd.isna(drawdown) and drawdown <= -0.30)
        out.append(
            {
                "event_id": event["event_id"],
                "token_entity_id": event["token_entity_id"],
                "token_symbol": symbol,
                "anchor_event_type": event["event_type"],
                "baseline_price": baseline,
                "max_return_1h": returns["1h"],
                "max_return_4h": returns["4h"],
                "max_return_24h": returns["24h"],
                "max_return_3d": returns["3d"],
                "max_return_7d": returns["7d"],
                "max_return_until_effective_delisting": max_return,
                "max_return_price_source": max_row.get("window_price_source", ""),
                "max_return_exchange": max_row.get("window_price_source", "").replace("ccxt_", "") if str(max_row.get("window_price_source", "")).startswith("ccxt_") else "binance",
                "volume_zscore": volume_zscore_around(daily_by_symbol.get(symbol, pd.DataFrame()), event_dt),
                "post_pump_drawdown": drawdown,
                "pump20_flag": "yes" if pump20 else "no",
                "pump_and_dump_flag": "yes" if pump_and_dump and not low_liq else "no",
                "low_liquidity_pump_flag": "yes" if low_liq else "no",
                "fallback_used": "yes" if fallback_used else "no",
                "manual_review_required": "yes" if low_liq or suspicious else "no",
            }
        )
    return out


def fallback_quality_rows(resolution_rows: list[dict], price_rows: list[dict], fallback_by_symbol: dict[str, pd.DataFrame]) -> list[dict]:
    out = []
    missing_by_symbol: dict[str, list[str]] = {}
    for row in price_rows:
        if row.get("missing_price_reason"):
            missing_by_symbol.setdefault(row["token_symbol"], []).append(row["missing_price_reason"])
    for row in resolution_rows:
        symbol = row["token_symbol"]
        fallback_df = fallback_by_symbol.get(symbol, pd.DataFrame())
        quote_volume = float(fallback_df["quote_volume"].fillna(0).sum()) if not fallback_df.empty and "quote_volume" in fallback_df else math.nan
        fallback_rows = len(fallback_df)
        low_liq = fallback_rows > 0 and (pd.isna(quote_volume) or quote_volume < 100000)
        sym_price = [r for r in price_rows if r["token_symbol"] == symbol]
        fallback_returns = [r.get("raw_return", math.nan) for r in sym_price if str(r.get("window_price_source", "")).startswith("ccxt_")]
        suspicious = any((not pd.isna(x) and abs(x) >= 1.0) for x in fallback_returns)
        reasons = ";".join(sorted(set(";".join(missing_by_symbol.get(symbol, [])).split(";")) - {""}))
        out.append(
            {
                "token_symbol": symbol,
                "fallback_provider_unavailable": "yes" if "fallback_provider_unavailable" in reasons else "no",
                "true_data_gap": "yes" if "true_data_gap" in reasons else "no",
                "expected_post_delisting_missing": "yes" if "expected_post_delisting_missing" in reasons else "no",
                "low_liquidity_fallback": "yes" if low_liq else "no",
                "suspicious_fallback_spike": "yes" if suspicious else "no",
                "fallback_exchange": row.get("fallback_provider", ""),
                "fallback_pair": row.get("fallback_market", ""),
                "fallback_rows_count": fallback_rows,
                "fallback_quote_volume": quote_volume,
                "reason": reasons,
                "notes": "manual_review_recommended" if low_liq or suspicious else "",
            }
        )
    return out


def selected_lifecycle(lifecycle: list[dict], mode: str, tokens: list[str] | None) -> list[dict]:
    by_symbol = {r["token_symbol"]: r for r in lifecycle if r.get("token_symbol")}
    if tokens:
        return [by_symbol[s] for s in tokens if s in by_symbol]
    if mode == "sample":
        return [by_symbol[s] for s in SAMPLE_TOKENS if s in by_symbol]
    return [r for r in lifecycle if r.get("token_symbol") and r["final_outcome"] != "unknown"]


def selected_events_for_symbols(events: list[dict], symbols: set[str], mode: str) -> list[dict]:
    out = []
    for event in events:
        symbol = event["token_symbol"]
        if symbol not in symbols:
            continue
        if mode == "sample":
            if event["event_type"] == "SPOT_PAIR_REMOVED" and symbol != "0G":
                continue
            if event["event_type"] != "SPOT_PAIR_REMOVED" and symbol == "0G":
                continue
        out.append(event)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Binance risk-event price analysis tables.")
    parser.add_argument("--mode", choices=["sample", "full"], default="sample")
    parser.add_argument("--tokens", default="", help="Optional comma-separated token symbols.")
    parser.add_argument("--resume", action="store_true", help="Use existing cached raw data where available.")
    parser.add_argument("--rate-limit", type=float, default=0.5, help="Nominal sleep between direct HTTP requests.")
    parser.add_argument("--skip-fallback", action="store_true", help="Disable CCXT/CoinGecko fallback layer.")
    parser.add_argument("--max-tokens", type=int, default=0, help="Process at most this many lifecycle entities after filtering.")
    parser.add_argument("--start-index", type=int, default=0, help="Start offset within filtered lifecycle entities.")
    parser.add_argument("--end-index", type=int, default=0, help="End offset within filtered lifecycle entities.")
    parser.add_argument("--output-suffix", default="", help="Suffix for output files, e.g. batch_000_025.")
    parser.add_argument("--output-dir", default="", help="Directory for output files. Overrides --output-suffix.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tokens = [x.strip().upper() for x in args.tokens.split(",") if x.strip()] or None
    events, lifecycle = load_events()
    run_lc = selected_lifecycle(lifecycle, args.mode, tokens)
    if args.end_index:
        run_lc = run_lc[args.start_index : args.end_index]
    elif args.start_index:
        run_lc = run_lc[args.start_index :]
    if args.max_tokens:
        run_lc = run_lc[: args.max_tokens]
    lc_by_symbol = {r["token_symbol"]: r for r in lifecycle}
    sample_symbols = [r["token_symbol"] for r in run_lc]
    spot_info = exchange_info(SPOT_BASE, "spot")
    futures_info = exchange_info(FUTURES_BASE, "futures")
    spot_res = {s: resolve_spot(s, spot_info) for s in sample_symbols}
    fut_res = {s: resolve_futures(s, futures_info) for s in sample_symbols}

    sample_events = selected_events_for_symbols(events, set(sample_symbols), args.mode)

    btc = fetch_klines("BTCUSDT", "1h", datetime(2023, 7, 1, tzinfo=timezone.utc), datetime(2026, 5, 26, 23, 59, tzinfo=timezone.utc), "spot")
    eth = fetch_klines("ETHUSDT", "1h", datetime(2023, 7, 1, tzinfo=timezone.utc), datetime(2026, 5, 26, 23, 59, tzinfo=timezone.utc), "spot")
    alt_hourly = {}
    for alt in ALT_BENCHMARK_SYMBOLS:
        rp = resolve_spot(alt, spot_info)
        if not rp.missing:
            alt_hourly[alt] = fetch_klines(rp.pair, "1h", datetime(2023, 7, 1, tzinfo=timezone.utc), datetime(2026, 5, 26, 23, 59, tzinfo=timezone.utc), "spot")
    price_rows = []
    recovery_rows = []
    pump_rows = []
    resolution_rows = []
    kline_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    daily_by_symbol: dict[str, pd.DataFrame] = {}
    fallback_by_symbol: dict[str, pd.DataFrame] = {}

    for idx, symbol in enumerate(sample_symbols, start=1):
        print(f"[{idx}/{len(sample_symbols)}] {symbol}", flush=True)
        lc = lc_by_symbol[symbol]
        sym_events = [e for e in sample_events if e["token_symbol"] == symbol]
        exact_fut = exact_futures_contract(symbol, sym_events, futures_info)
        pair = (exact_fut or fut_res[symbol]) if lc["final_outcome"] == "futures_only_delisting" else spot_res[symbol]
        resolution_rows.append(
            {
                "token_symbol": symbol,
                "final_outcome": lc["final_outcome"],
                "spot_pair": spot_res[symbol].pair,
                "spot_missing": "yes" if spot_res[symbol].missing else "no",
                "futures_pair": fut_res[symbol].pair,
                "futures_missing": "yes" if fut_res[symbol].missing else "no",
                "exact_futures_contract": exact_fut.pair if exact_fut else "",
                "futures_class": exact_fut.notes if exact_fut else fut_res[symbol].notes,
                "fallback_required": "yes" if spot_res[symbol].missing and lc["final_outcome"] != "futures_only_delisting" else "no",
            }
        )
        if not sym_events:
            continue
        first_event = min(dt(e["publication_datetime_utc"]) for e in sym_events)
        start = first_event - timedelta(days=35)
        end = min(datetime(2026, 5, 26, 23, 59, tzinfo=timezone.utc), max(dt(e["publication_datetime_utc"]) for e in sym_events) + timedelta(days=95))
        intraday_start = min(dt(e["publication_datetime_utc"]) for e in sym_events) - timedelta(days=1)
        intraday_end = min(datetime(2026, 5, 26, 23, 59, tzinfo=timezone.utc), max(dt(e["publication_datetime_utc"]) for e in sym_events) + timedelta(days=1))
        market = pair.market_type
        for tf in TIMEFRAMES:
            tf_start, tf_end = (intraday_start, intraday_end) if tf == "15m" else (start, end)
            kline_cache[(symbol, market, tf)] = fetch_klines(pair.pair, tf, tf_start, tf_end, market)
        daily = kline_cache[(symbol, market, "1d")]
        hourly = kline_cache[(symbol, market, "1h")]
        daily_by_symbol[symbol] = daily
        fallback = pd.DataFrame()
        fallback_source = ""
        fallback_market = ""
        if not args.skip_fallback and lc["final_outcome"] in {"delisted_after_tag", "delisted_without_known_tag"}:
            fallback, fallback_source, fallback_market = ccxt_fallback_ohlcv(symbol, start, end)
            if fallback.empty:
                fallback = coingecko_market_chart(symbol, start, end)
                fallback_source = "fallback_coingecko" if not fallback.empty else ""
                fallback_market = "coingecko_usd" if not fallback.empty else ""
            if not fallback.empty:
                METRICS["ccxt_points_used"] += len(fallback) if fallback_source.startswith("ccxt_") else 0
        fallback_by_symbol[symbol] = fallback
        for event in sym_events:
            price_rows.extend(event_windows(event, pair, daily, hourly, btc, eth, fallback, fallback_source, alt_hourly))
        if fallback_source:
            resolution_rows[-1]["fallback_provider"] = fallback_source
            resolution_rows[-1]["fallback_market"] = fallback_market
            resolution_rows[-1]["fallback_required"] = "yes"
        else:
            resolution_rows[-1]["fallback_provider"] = ""
            resolution_rows[-1]["fallback_market"] = ""
        if lc["final_outcome"] != "spot_pair_removed_only":
            anchor = next((e for e in sym_events if e["event_type"] in {"MONITORING_TAG_ADDED", "SPOT_TOKEN_DELISTING_ANNOUNCED"}), sym_events[0])
            recovery_rows.append(recovery_row(symbol, anchor, daily, fallback))

    pump_rows = pump_analysis_rows(sample_events, price_rows, daily_by_symbol, fallback_by_symbol)
    fallback_quality = fallback_quality_rows(resolution_rows, price_rows, fallback_by_symbol)

    outputs = outputs_for(args.mode, args.output_suffix, args.output_dir)
    write_csv(Path(outputs["resolution"]), resolution_rows)
    write_csv(Path(outputs["price_windows"]), price_rows)
    write_csv(Path(outputs["recovery"]), recovery_rows)
    write_csv(Path(outputs["pump"]), pump_rows, SCHEMAS["pump"])
    write_csv(Path(outputs["fallback_quality"]), fallback_quality)
    pd.DataFrame(price_rows).to_parquet(outputs["price_windows_parquet"], index=False)
    append_worklog(
        [
            f"\n## {now_utc()} - Price collection {args.mode}",
            f"- token_entity_id={len(sample_symbols)}",
            f"- events_covered={len(sample_events)}",
            f"- tokens_filter={','.join(tokens) if tokens else ''}",
            f"- skip_fallback={args.skip_fallback}",
            "- sources=Binance Spot API, Binance USD-M Futures API",
            f"- outputs={','.join(outputs.values())}",
        ]
    )
    print(
        json.dumps(
            {
                "mode": args.mode,
                "token_entity_id": len(sample_symbols),
                "events_covered": len(sample_events),
                "spot_pairs_resolved": sum(1 for r in resolution_rows if r["spot_missing"] == "no"),
                "spot_pairs_missing": sum(1 for r in resolution_rows if r["spot_missing"] == "yes"),
                "futures_pairs_resolved": sum(1 for r in resolution_rows if r["futures_missing"] == "no"),
                "fallback_required": sum(1 for r in resolution_rows if r["fallback_required"] == "yes"),
                "fallback_points_used": METRICS["fallback_points_used"],
                "price_window_rows": len(price_rows),
                "missing_price_rows": sum(1 for r in price_rows if r["missing_price_flag"] == "yes"),
                "benchmark_gap_rows": sum(1 for r in price_rows if r["benchmark_gap"] == "yes"),
                "pump_rows": len(pump_rows),
                "fallback_quality_rows": len(fallback_quality),
                **METRICS,
                "outputs": outputs,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
