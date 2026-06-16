#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "derivatives_availability"
DOCS = ROOT / "docs"
WORKLOG = DOCS / "codex" / "worklog.md"
BASE = "https://fapi.binance.com"
COST_BPS = [20, 50, 100, 200, 500]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def parse_ts(value: Any) -> pd.Timestamp:
    return pd.to_datetime(value, utc=True, errors="coerce")


def ms(ts: pd.Timestamp) -> int:
    return int(pd.Timestamp(ts).timestamp() * 1000)


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100 * float(value):.1f}%"


def profit_factor(returns: pd.Series) -> float:
    wins = returns[returns > 0].sum()
    losses = -returns[returns < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


def cache_key(endpoint: str, params: dict[str, Any]) -> str:
    payload = endpoint + "?" + parse.urlencode(sorted((k, str(v)) for k, v in params.items()))
    return hashlib.sha256(payload.encode()).hexdigest()[:24]


def raw_path(endpoint: str, params: dict[str, Any]) -> Path:
    safe_endpoint = endpoint.strip("/").replace("/", "_")
    return RAW / safe_endpoint / f"{cache_key(endpoint, params)}.json"


def request_json(endpoint: str, params: dict[str, Any], *, timeout: int, retries: int, sleep_s: float, use_cache: bool) -> tuple[Any, dict[str, Any]]:
    RAW.mkdir(parents=True, exist_ok=True)
    path = raw_path(endpoint, params)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "endpoint": endpoint,
        "params": params,
        "cache_path": str(path),
        "cache_hit": False,
        "http_status": None,
        "error": "",
        "requested_at_utc": now_utc(),
    }
    if use_cache and path.exists():
        try:
            payload = json.loads(path.read_text())
            meta.update(payload.get("_meta", {}))
            meta["cache_hit"] = True
            return payload.get("data"), meta
        except Exception as exc:
            meta["error"] = f"cache_read_error:{exc}"

    url = BASE + endpoint + "?" + parse.urlencode(params)
    last_error = ""
    for attempt in range(retries + 1):
        try:
            req = request.Request(url, headers={"User-Agent": "codex-derivatives-availability/1.0"})
            with request.urlopen(req, timeout=timeout) as resp:
                status = int(resp.status)
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            meta["http_status"] = status
            path.write_text(json.dumps({"_meta": meta, "data": data}, ensure_ascii=False))
            time.sleep(sleep_s)
            return data, meta
        except error.HTTPError as exc:
            last_error = f"http_{exc.code}:{exc.reason}"
            meta["http_status"] = exc.code
            if exc.code in {418, 429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(sleep_s * (2 ** attempt))
                continue
            break
        except Exception as exc:
            last_error = f"{type(exc).__name__}:{exc}"
            if attempt < retries:
                time.sleep(sleep_s * (2 ** attempt))
                continue
            break
    meta["error"] = last_error
    path.write_text(json.dumps({"_meta": meta, "data": None}, ensure_ascii=False))
    time.sleep(sleep_s)
    return None, meta


def candidate_rows(limit: int | None = None) -> pd.DataFrame:
    short = read_csv("monitoring_shortability.csv")
    cols = [
        "event_id",
        "token_entity_id",
        "token_symbol",
        "spot_symbol",
        "futures_symbol_candidate",
        "entry_time",
        "event_time",
        "feasibility_tier",
        "low_liquidity_flag",
        "gross_return",
        "net_return_20bps",
        "net_return_50bps",
        "net_return_100bps",
        "net_return_200bps",
        "net_return_500bps",
        "max_adverse_excursion",
        "max_favorable_excursion",
    ]
    out = short[cols].copy()
    out["entry_dt"] = pd.to_datetime(out["entry_time"], utc=True, errors="coerce")
    out = out.sort_values(["entry_dt", "token_symbol"]).reset_index(drop=True)
    if limit:
        out = out.head(limit)
    return out


def load_existing() -> pd.DataFrame:
    path = PROCESSED / "derivatives_availability.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def append_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path = PROCESSED / "derivatives_availability.csv"
    new = pd.DataFrame(rows)
    if path.exists():
        old = pd.read_csv(path)
        out = pd.concat([old, new], ignore_index=True)
        out = out.drop_duplicates(["event_id", "token_symbol", "futures_symbol", "entry_time"], keep="last")
    else:
        out = new
    out.to_csv(path, index=False)
    out.to_parquet(PROCESSED / "derivatives_availability.parquet", index=False)


def query_symbol(symbol: str, entry_time: pd.Timestamp, args: argparse.Namespace) -> dict[str, Any]:
    start = entry_time - pd.Timedelta(hours=args.window_hours)
    end = entry_time + pd.Timedelta(hours=args.window_hours)
    params = {
        "symbol": symbol,
        "interval": "1h",
        "startTime": ms(start),
        "endTime": ms(end),
        "limit": 1000,
    }
    klines, k_meta = request_json("/fapi/v1/klines", params, timeout=args.timeout, retries=args.retries, sleep_s=args.sleep, use_cache=args.use_cache)
    kline_rows = len(klines) if isinstance(klines, list) else 0

    funding_params = {
        "symbol": symbol,
        "startTime": ms(start),
        "endTime": ms(end),
        "limit": 1000,
    }
    funding, f_meta = request_json("/fapi/v1/fundingRate", funding_params, timeout=args.timeout, retries=args.retries, sleep_s=args.sleep, use_cache=args.use_cache)
    funding_rows = len(funding) if isinstance(funding, list) else 0

    oi_params = {
        "symbol": symbol,
        "period": "1h",
        "startTime": ms(start),
        "endTime": ms(end),
        "limit": 500,
    }
    oi, oi_meta = request_json("/futures/data/openInterestHist", oi_params, timeout=args.timeout, retries=args.retries, sleep_s=args.sleep, use_cache=args.use_cache)
    oi_rows = len(oi) if isinstance(oi, list) else 0

    errors = [m["error"] for m in [k_meta, f_meta, oi_meta] if m.get("error")]
    http_statuses = [m.get("http_status") for m in [k_meta, f_meta, oi_meta] if m.get("http_status")]
    api_unavailable = any(
        ("URLError" in err)
        or ("Timeout" in err)
        or ("timed out" in err)
        or ("http_418" in err)
        or ("http_429" in err)
        or ("http_5" in err)
        for err in errors
    ) and kline_rows == 0 and funding_rows == 0 and oi_rows == 0
    confirmed = kline_rows > 0 or funding_rows > 0 or oi_rows > 0
    manual_review = (confirmed and kline_rows == 0) or api_unavailable
    status_labels = []
    if confirmed:
        status_labels.append("confirmed_binance_perp")
    if kline_rows > 0:
        status_labels.append("inferred_from_futures_klines")
    if funding_rows > 0:
        status_labels.append("funding_available")
    if oi_rows > 0:
        status_labels.append("oi_available")
    if api_unavailable:
        status_labels.append("api_unavailable")
    if not confirmed and not api_unavailable:
        status_labels.append("no_binance_perp_evidence")
    if manual_review:
        status_labels.append("manual_review_needed")
    return {
        "futures_symbol": symbol,
        "query_start_utc": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "query_end_utc": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kline_rows": kline_rows,
        "funding_rows": funding_rows,
        "open_interest_rows": oi_rows,
        "confirmed_binance_perp": "yes" if confirmed else "no",
        "inferred_from_futures_klines": "yes" if kline_rows > 0 else "no",
        "funding_available": "yes" if funding_rows > 0 else "no",
        "oi_available": "yes" if oi_rows > 0 else "no",
        "api_unavailable": "yes" if api_unavailable else "no",
        "no_binance_perp_evidence": "yes" if not confirmed and not api_unavailable else "no",
        "manual_review_needed": "yes" if manual_review else "no",
        "availability_status": ";".join(status_labels),
        "http_statuses": ";".join(str(x) for x in http_statuses),
        "api_errors": ";".join(errors),
        "kline_cache_path": k_meta.get("cache_path", ""),
        "funding_cache_path": f_meta.get("cache_path", ""),
        "open_interest_cache_path": oi_meta.get("cache_path", ""),
        "cache_hit_all": "yes" if k_meta.get("cache_hit") and f_meta.get("cache_hit") and oi_meta.get("cache_hit") else "no",
    }


def collect(args: argparse.Namespace) -> pd.DataFrame:
    rows = candidate_rows(args.limit)
    existing = load_existing()
    done = set()
    if args.resume and not existing.empty:
        done = set(zip(existing["event_id"].astype(str), existing["token_symbol"].astype(str), existing["futures_symbol"].astype(str), existing["entry_time"].astype(str)))

    collected: list[dict[str, Any]] = []
    request_count = 0
    skipped = 0
    for _, row in rows.iterrows():
        entry_time = parse_ts(row["entry_time"])
        if pd.isna(entry_time):
            continue
        symbols = [s.strip() for s in str(row["futures_symbol_candidate"]).split(",") if s.strip() and s.strip() != "nan"]
        for symbol in symbols:
            key = (str(row["event_id"]), str(row["token_symbol"]), symbol, str(row["entry_time"]))
            if key in done:
                skipped += 1
                continue
            result = query_symbol(symbol, entry_time, args)
            request_count += 3
            result.update(
                {
                    "event_id": row["event_id"],
                    "token_entity_id": row["token_entity_id"],
                    "token_symbol": row["token_symbol"],
                    "spot_symbol": row["spot_symbol"],
                    "entry_time": row["entry_time"],
                    "event_time": row["event_time"],
                    "feasibility_tier": row["feasibility_tier"],
                    "low_liquidity_flag": row["low_liquidity_flag"],
                    "gross_return": row["gross_return"],
                    "net_return_20bps": row["net_return_20bps"],
                    "net_return_50bps": row["net_return_50bps"],
                    "net_return_100bps": row["net_return_100bps"],
                    "net_return_200bps": row["net_return_200bps"],
                    "net_return_500bps": row["net_return_500bps"],
                    "max_adverse_excursion": row["max_adverse_excursion"],
                    "max_favorable_excursion": row["max_favorable_excursion"],
                    "collected_at_utc": now_utc(),
                }
            )
            collected.append(result)
            if len(collected) >= args.flush_every:
                append_rows(collected)
                collected = []
    append_rows(collected)
    out = load_existing()
    log_work(request_count, skipped, out)
    return out


def log_work(request_count: int, skipped: int, out: pd.DataFrame) -> None:
    WORKLOG.parent.mkdir(parents=True, exist_ok=True)
    confirmed = int(out["confirmed_binance_perp"].eq("yes").sum()) if not out.empty else 0
    api_unavailable = int(out["api_unavailable"].eq("yes").sum()) if not out.empty else 0
    text = [
        "",
        f"## {now_utc()} - Derivatives availability collector",
        "- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation candidate symbols",
        f"- output_rows={len(out)}",
        f"- new_api_request_attempts={request_count}",
        f"- skipped_existing_rows={skipped}",
        f"- confirmed_symbol_rows={confirmed}",
        f"- api_unavailable_rows={api_unavailable}",
        "- outputs=data/processed/derivatives_availability.csv,data/processed/derivatives_availability.parquet,docs/derivatives_availability_quality_report.md,data/processed/monitoring_strategy_tradeable_subset_summary.csv",
    ]
    with WORKLOG.open("a") as f:
        f.write("\n".join(text) + "\n")


def best_per_trade(availability: pd.DataFrame) -> pd.DataFrame:
    if availability.empty:
        return pd.DataFrame()
    score = (
        availability["confirmed_binance_perp"].eq("yes").astype(int) * 4
        + availability["inferred_from_futures_klines"].eq("yes").astype(int) * 3
        + availability["funding_available"].eq("yes").astype(int) * 2
        + availability["oi_available"].eq("yes").astype(int) * 2
        - availability["api_unavailable"].eq("yes").astype(int)
    )
    work = availability.copy()
    work["_score"] = score
    work = work.sort_values(["event_id", "token_symbol", "entry_time", "_score"], ascending=[True, True, True, False])
    return work.drop_duplicates(["event_id", "token_symbol", "entry_time"], keep="first").drop(columns=["_score"])


def summarize_tradeable(availability: pd.DataFrame) -> pd.DataFrame:
    best = best_per_trade(availability)
    if best.empty:
        summary = pd.DataFrame()
        summary.to_csv(PROCESSED / "monitoring_strategy_tradeable_subset_summary.csv", index=False)
        return summary

    views = [
        ("confirmed_or_inferred_shortable", best["confirmed_binance_perp"].eq("yes")),
        ("inferred_from_futures_klines", best["inferred_from_futures_klines"].eq("yes")),
        ("funding_available", best["funding_available"].eq("yes")),
        ("oi_available", best["oi_available"].eq("yes")),
        ("no_binance_perp_evidence", best["no_binance_perp_evidence"].eq("yes")),
        ("api_unavailable", best["api_unavailable"].eq("yes")),
        ("manual_review_needed", best["manual_review_needed"].eq("yes")),
        ("medium_feasibility_plus_confirmed_or_inferred_shortable", best["feasibility_tier"].isin(["high", "medium"]) & best["confirmed_binance_perp"].eq("yes")),
    ]
    rows = []
    for view, mask in views:
        sub = best[mask].copy()
        for cost in COST_BPS:
            ret = pd.to_numeric(sub[f"net_return_{cost}bps"], errors="coerce").dropna()
            mae = pd.to_numeric(sub["max_adverse_excursion"], errors="coerce")
            mfe = pd.to_numeric(sub["max_favorable_excursion"], errors="coerce")
            rows.append(
                {
                    "view": view,
                    "cost_bps": cost,
                    "n_trades": int(len(ret)),
                    "win_rate": float((ret > 0).mean()) if len(ret) else np.nan,
                    "median_return": float(ret.median()) if len(ret) else np.nan,
                    "average_return": float(ret.mean()) if len(ret) else np.nan,
                    "p25_return": float(ret.quantile(0.25)) if len(ret) else np.nan,
                    "p75_return": float(ret.quantile(0.75)) if len(ret) else np.nan,
                    "worst_trade": float(ret.min()) if len(ret) else np.nan,
                    "best_trade": float(ret.max()) if len(ret) else np.nan,
                    "median_mae": float(mae.median()) if mae.notna().any() else np.nan,
                    "median_mfe": float(mfe.median()) if mfe.notna().any() else np.nan,
                    "profit_factor": profit_factor(ret) if len(ret) else np.nan,
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(PROCESSED / "monitoring_strategy_tradeable_subset_summary.csv", index=False)
    return summary


def write_report(availability: pd.DataFrame, summary: pd.DataFrame) -> None:
    if availability.empty:
        report = "# Derivatives Availability Quality Report\n\nNo rows collected yet.\n"
        (DOCS / "derivatives_availability_quality_report.md").write_text(report)
        return
    best = best_per_trade(availability)
    status_counts = availability["availability_status"].value_counts(dropna=False)
    best_counts = {
        "candidate_trades_with_any_result": len(best),
        "confirmed_binance_perp": int(best["confirmed_binance_perp"].eq("yes").sum()),
        "inferred_from_futures_klines": int(best["inferred_from_futures_klines"].eq("yes").sum()),
        "funding_available": int(best["funding_available"].eq("yes").sum()),
        "oi_available": int(best["oi_available"].eq("yes").sum()),
        "no_binance_perp_evidence": int(best["no_binance_perp_evidence"].eq("yes").sum()),
        "api_unavailable": int(best["api_unavailable"].eq("yes").sum()),
        "manual_review_needed": int(best["manual_review_needed"].eq("yes").sum()),
    }
    display = summary[summary["cost_bps"] == 100].copy() if not summary.empty else pd.DataFrame()
    if not display.empty:
        for col in ["win_rate", "median_return", "average_return", "p25_return", "p75_return", "worst_trade", "best_trade", "median_mae", "median_mfe"]:
            display[col] = display[col].map(pct)

    unresolved = best[
        best["confirmed_binance_perp"].ne("yes")
    ][["token_symbol", "entry_time", "futures_symbol", "availability_status", "api_errors"]].head(80)

    report = [
        "# Derivatives Availability Quality Report",
        "",
        f"Generated at UTC: {now_utc()}",
        "",
        "Scope: Binance USD-M derivatives availability for Monitoring Tag candidate trades.",
        "",
        "Current exchangeInfo is not used as historical proof. Evidence comes from historical futures klines, funding, and open-interest API responses around `entry_time`.",
        "",
        "## Coverage",
        "",
    ]
    report.extend(f"- {k}: {v}" for k, v in best_counts.items())
    report.extend(
        [
            "",
            "## Raw Symbol-Level Status Counts",
            "",
            status_counts.to_markdown(),
            "",
            "## Tradeable Subset Metrics at 100 bps",
            "",
            display.to_markdown(index=False) if not display.empty else "No summary rows.",
            "",
            "## Unresolved / Manual Review Queue",
            "",
            unresolved.to_markdown(index=False) if not unresolved.empty else "No unresolved rows.",
            "",
            "## Notes",
            "",
            "- `confirmed_binance_perp=yes` means at least one of futures klines, funding, or open-interest rows was found around entry.",
            "- `inferred_from_futures_klines=yes` is the strongest free public evidence in this collector.",
            "- `api_unavailable=yes` means API errors or limitations prevented a clean conclusion.",
            "- Empty responses without API errors are kept as `no_binance_perp_evidence`, not proof that no contract existed.",
        ]
    )
    (DOCS / "derivatives_availability_quality_report.md").write_text("\n".join(report))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--window-hours", type=int, default=48)
    parser.add_argument("--flush-every", type=int, default=10)
    args = parser.parse_args()

    availability = collect(args)
    summary = summarize_tradeable(availability)
    write_report(availability, summary)
    print(
        {
            "availability_rows": int(len(availability)),
            "unique_candidate_trades": int(best_per_trade(availability).shape[0]) if not availability.empty else 0,
            "confirmed_best_trades": int(best_per_trade(availability)["confirmed_binance_perp"].eq("yes").sum()) if not availability.empty else 0,
            "output": str(PROCESSED / "derivatives_availability.csv"),
            "report": str(DOCS / "derivatives_availability_quality_report.md"),
        }
    )


if __name__ == "__main__":
    main()
