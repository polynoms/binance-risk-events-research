#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
THRESHOLDS = ROOT / "config" / "research_thresholds.yaml"


def yn(value: Any) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


def median_number(series: pd.Series) -> float | None:
    vals = pd.to_numeric(series, errors="coerce").dropna()
    if vals.empty:
        return None
    return float(vals.median())


def read_csv(name: str) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def event_window_map(price_windows: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    out: dict[tuple[str, str], pd.Series] = {}
    for _, row in price_windows.iterrows():
        out[(str(row["event_id"]), str(row["window"]))] = row
    return out


def pick_anchor_event(events: pd.DataFrame, token: str, event_types: list[str]) -> pd.Series | None:
    rows = events[(events["token_symbol"].astype(str) == token) & (events["event_type"].isin(event_types))].copy()
    if rows.empty:
        return None
    rows["publication_datetime_utc_sort"] = pd.to_datetime(rows["publication_datetime_utc"], errors="coerce", utc=True)
    rows = rows.sort_values(["publication_datetime_utc_sort", "event_type"], na_position="last")
    return rows.iloc[0]


def get_window_return(wmap: dict[tuple[str, str], pd.Series], event_id: str, window: str, col: str) -> float | None:
    row = wmap.get((event_id, window))
    if row is None:
        return None
    value = pd.to_numeric(row.get(col), errors="coerce")
    if pd.isna(value):
        return None
    return float(value)


def classify() -> tuple[pd.DataFrame, pd.DataFrame]:
    with THRESHOLDS.open() as f:
        thresholds = yaml.safe_load(f)

    dump_raw = float(thresholds["dump"]["immediate_24h_raw_return"])
    dump_adj = float(thresholds["dump"]["immediate_24h_market_adjusted_return"])
    pre_weak_24h = float(thresholds["pre_announcement"]["weakness_24h_market_adjusted_return"])
    pre_dump_4h = float(thresholds["pre_announcement"]["dump_4h_market_adjusted_return"])

    lifecycle = read_csv("token_lifecycle.csv")
    events = read_csv("events.csv")
    price_windows = read_csv("price_windows.csv")
    recovery = read_csv("recovery_analysis.csv")
    pump = read_csv("pump_analysis.csv")
    fallback_quality = read_csv("fallback_data_quality.csv")

    wmap = event_window_map(price_windows)
    recovery_by_token = {str(r["token_symbol"]): r for _, r in recovery.iterrows()}
    fallback_by_token = {str(r["token_symbol"]): r for _, r in fallback_quality.iterrows()}
    pump_by_token = {
        str(token): rows.copy()
        for token, rows in pump.groupby(pump["token_symbol"].astype(str), dropna=False)
    }

    rows: list[dict[str, Any]] = []
    for _, life in lifecycle.iterrows():
        token = str(life["token_symbol"])
        final_outcome = str(life.get("final_outcome", "unknown"))
        manual_review = yn(life.get("manual_review_required", "no"))
        secondary_flags: list[str] = []
        anchor = None

        if final_outcome == "spot_pair_removed_only":
            primary = "PAIR_REMOVAL_ONLY"
            anchor = pick_anchor_event(events, token, ["SPOT_PAIR_REMOVED"])
        elif final_outcome == "futures_only_delisting":
            primary = "FUTURES_ONLY_DELISTING"
            anchor = pick_anchor_event(events, token, ["FUTURES_CONTRACT_DELISTING_ANNOUNCED"])
        elif final_outcome == "seed_tag_only":
            primary = "SEED_TAG_ONLY"
            anchor = pick_anchor_event(events, token, ["SEED_TAG_ADDED"])
        elif final_outcome == "tag_removed":
            anchor = pick_anchor_event(events, token, ["MONITORING_TAG_ADDED", "SEED_TAG_ADDED"])
            rec = recovery_by_token.get(token)
            if rec is not None and (yn(rec.get("recovery_90_sustained")) or yn(rec.get("recovery_100_sustained"))):
                primary = "TAG_REMOVED_AND_RECOVERED"
            else:
                primary = "TAG_REMOVED_BUT_NOT_RECOVERED"
        elif final_outcome == "delisted_without_known_tag":
            primary = "DELISTED_WITHOUT_KNOWN_PRIOR_TAG"
            anchor = pick_anchor_event(events, token, ["SPOT_TOKEN_DELISTING_ANNOUNCED"])
        elif final_outcome == "delisted_after_tag":
            anchor = pick_anchor_event(events, token, ["MONITORING_TAG_ADDED"])
            ptoken = pump_by_token.get(token)
            has_pump_dump = False if ptoken is None else any(ptoken["pump_and_dump_flag"].astype(str) == "yes")
            delist_anchor = pick_anchor_event(events, token, ["SPOT_TOKEN_DELISTING_ANNOUNCED"])
            if has_pump_dump:
                primary = "DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP"
                secondary_flags.append("TAG_TO_DELISTING")
            else:
                primary = "TAG_TO_DELISTING_TO_COLLAPSE"
            if delist_anchor is not None and anchor is None:
                anchor = delist_anchor
        elif final_outcome == "still_tagged":
            anchor = pick_anchor_event(events, token, ["MONITORING_TAG_ADDED"])
            if anchor is None:
                primary = "NO_CLEAR_REACTION"
            else:
                event_id = str(anchor["event_id"])
                r24 = get_window_return(wmap, event_id, "+24h", "raw_return")
                a24 = get_window_return(wmap, event_id, "+24h", "alt_benchmark_adjusted_return")
                a30 = get_window_return(wmap, event_id, "+30d", "alt_benchmark_adjusted_return")
                a90 = get_window_return(wmap, event_id, "+90d", "alt_benchmark_adjusted_return")
                rec = recovery_by_token.get(token)
                if (r24 is not None and r24 <= dump_raw) or (a24 is not None and a24 <= dump_adj):
                    if rec is not None and (yn(rec.get("recovery_90_sustained")) or yn(rec.get("recovery_100_sustained"))):
                        primary = "TEMPORARY_PANIC_THEN_RECOVERY"
                    else:
                        primary = "IMMEDIATE_DUMP_AFTER_TAG"
                elif ((a30 is not None and a30 < 0) or (a90 is not None and a90 < 0)):
                    primary = "SLOW_BLEED_AFTER_TAG"
                else:
                    primary = "NO_CLEAR_REACTION"
        else:
            primary = "UNKNOWN_MANUAL_REVIEW"
            manual_review = True
            anchor = pick_anchor_event(events, token, list(events["event_type"].dropna().unique()))

        anchor_event_id = str(anchor["event_id"]) if anchor is not None else ""
        anchor_event_type = str(anchor["event_type"]) if anchor is not None else ""

        if anchor_event_id:
            pre_24h = get_window_return(wmap, anchor_event_id, "-24h", "alt_benchmark_adjusted_return")
            pre_4h = get_window_return(wmap, anchor_event_id, "-4h", "alt_benchmark_adjusted_return")
            if pre_24h is not None and pre_24h <= pre_weak_24h:
                secondary_flags.append("PRICE_MOVED_BEFORE_OFFICIAL_ANNOUNCEMENT")
                secondary_flags.append("PRE_ANNOUNCEMENT_WEAKNESS")
            if pre_4h is not None and pre_4h <= pre_dump_4h:
                secondary_flags.append("PRICE_MOVED_BEFORE_OFFICIAL_ANNOUNCEMENT")
                secondary_flags.append("PRE_ANNOUNCEMENT_DUMP")

        rec = recovery_by_token.get(token)
        ptoken = pump_by_token.get(token)
        fq = fallback_by_token.get(token)
        if rec is not None and yn(rec.get("fallback_used")):
            secondary_flags.append("FALLBACK_PRICE_USED")
        if fq is not None and yn(fq.get("fallback_provider_unavailable")):
            secondary_flags.append("FALLBACK_PROVIDER_UNAVAILABLE")
        if fq is not None and yn(fq.get("suspicious_fallback_spike")):
            secondary_flags.append("SUSPICIOUS_FALLBACK_SPIKE")
            manual_review = True
        if ptoken is not None and any(ptoken["manual_review_required"].astype(str) == "yes"):
            manual_review = True
            secondary_flags.append("PUMP_MANUAL_REVIEW")

        def metric(window: str, col: str) -> float | None:
            if not anchor_event_id:
                return None
            return get_window_return(wmap, anchor_event_id, window, col)

        rows.append(
            {
                "token_entity_id": life["token_entity_id"],
                "token_symbol": token,
                "final_outcome": final_outcome,
                "primary_scenario": primary,
                "secondary_flags": ";".join(sorted(set(secondary_flags))),
                "anchor_event_id": anchor_event_id,
                "anchor_event_type": anchor_event_type,
                "return_1h": metric("+1h", "raw_return"),
                "return_24h": metric("+24h", "raw_return"),
                "return_7d": metric("+7d", "raw_return"),
                "return_30d": metric("+30d", "raw_return"),
                "return_90d": metric("+90d", "raw_return"),
                "alt_adj_return_24h": metric("+24h", "alt_benchmark_adjusted_return"),
                "alt_adj_return_30d": metric("+30d", "alt_benchmark_adjusted_return"),
                "alt_adj_return_90d": metric("+90d", "alt_benchmark_adjusted_return"),
                "recovery_90_sustained": rec.get("recovery_90_sustained") if rec is not None else "",
                "recovery_100_sustained": rec.get("recovery_100_sustained") if rec is not None else "",
                "never_recovered": rec.get("never_recovered") if rec is not None else "",
                "pump20_flag": "yes" if ptoken is not None and any(ptoken["pump20_flag"].astype(str) == "yes") else "no",
                "pump_and_dump_flag": "yes" if ptoken is not None and any(ptoken["pump_and_dump_flag"].astype(str) == "yes") else "no",
                "fallback_used": "yes" if rec is not None and yn(rec.get("fallback_used")) else "no",
                "manual_review_required": "yes" if manual_review else "no",
            }
        )

    scenarios = pd.DataFrame(rows)
    scenarios.to_csv(PROCESSED / "scenario_classification.csv", index=False)
    scenarios.to_parquet(PROCESSED / "scenario_classification.parquet", index=False)

    grouped = []
    total = len(scenarios)
    for scenario, grp in scenarios.groupby("primary_scenario", dropna=False):
        grouped.append(
            {
                "primary_scenario": scenario,
                "number_of_tokens": len(grp),
                "share_of_sample": len(grp) / total if total else 0,
                "median_return_1h": median_number(grp["return_1h"]),
                "median_return_24h": median_number(grp["return_24h"]),
                "median_return_7d": median_number(grp["return_7d"]),
                "median_return_30d": median_number(grp["return_30d"]),
                "median_return_90d": median_number(grp["return_90d"]),
                "recovery_90_sustained_rate": (grp["recovery_90_sustained"].astype(str) == "yes").mean(),
                "recovery_100_sustained_rate": (grp["recovery_100_sustained"].astype(str) == "yes").mean(),
                "pump20_rate": (grp["pump20_flag"].astype(str) == "yes").mean(),
                "pump_and_dump_rate": (grp["pump_and_dump_flag"].astype(str) == "yes").mean(),
                "manual_review_count": int((grp["manual_review_required"].astype(str) == "yes").sum()),
                "example_tokens": ", ".join(grp["token_symbol"].head(8).astype(str)),
            }
        )
    summary = pd.DataFrame(grouped).sort_values("number_of_tokens", ascending=False)
    summary.to_csv(PROCESSED / "scenario_summary.csv", index=False)
    summary.to_parquet(PROCESSED / "scenario_summary.parquet", index=False)
    return scenarios, summary


def write_reports(scenarios: pd.DataFrame, summary: pd.DataFrame) -> None:
    events = read_csv("events.csv")
    lifecycle = read_csv("token_lifecycle.csv")
    price_windows = read_csv("price_windows.csv")
    recovery = read_csv("recovery_analysis.csv")
    pump = read_csv("pump_analysis.csv")
    fallback_quality = read_csv("fallback_data_quality.csv")
    manual_events = read_csv("manual_review_events.csv")

    def b(s: pd.Series) -> pd.Series:
        return s.astype(str).str.lower().isin(["true", "1", "yes"])

    missing = b(price_windows["missing_price_flag"])
    benchmark_gap = b(price_windows["benchmark_gap"])
    event_counts = events["event_type"].value_counts().to_dict()
    outcome_counts = lifecycle["final_outcome"].value_counts().to_dict()
    scenario_counts = scenarios["primary_scenario"].value_counts().to_dict()

    dq = [
        "# Data Quality Report v1",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Coverage",
        "",
        f"- Events: {len(events)}",
        f"- Lifecycle rows: {len(lifecycle)}",
        f"- Price-resolution rows: {len(read_csv('price_resolution.csv'))}",
        f"- Price-window rows: {len(price_windows)}",
        f"- Recovery rows: {len(recovery)}",
        f"- Pump rows: {len(pump)}",
        f"- Manual-review events: {len(manual_events)}",
        "",
        "## Event Distribution",
        "",
    ]
    for k, v in event_counts.items():
        dq.append(f"- `{k}`: {v}")
    dq.extend(
        [
            "",
            "## Missing And Fallback",
            "",
            f"- Missing price rows: {int(missing.sum())}",
            f"- Benchmark gap rows: {int(benchmark_gap.sum())}",
            f"- Fallback-provider-unavailable tokens: {int(b(fallback_quality['fallback_provider_unavailable']).sum())}",
            f"- True-data-gap tokens: {int(b(fallback_quality['true_data_gap']).sum())}",
            f"- Expected post-delisting missing tokens: {int(b(fallback_quality['expected_post_delisting_missing']).sum())}",
            f"- Suspicious fallback spike cases: {int(b(fallback_quality['suspicious_fallback_spike']).sum())}",
            f"- Low-liquidity fallback cases: {int(b(fallback_quality['low_liquidity_fallback']).sum())}",
            "",
            "## Missing Reason Breakdown",
            "",
        ]
    )
    for k, v in price_windows.loc[missing, "missing_price_reason"].fillna("").value_counts().items():
        dq.append(f"- `{k}`: {v}")
    dq.extend(
        [
            "",
            "## Manual Review Candidates",
            "",
            "- Event rows marked manual review remain in `manual_review_events.csv`.",
            "- Scenario rows marked manual review remain in `scenario_classification.csv`.",
            "- Known parser artefact candidates include unresolved symbols such as `REMOVE` and non-standard announcement-derived symbols.",
        ]
    )
    (DOCS / "data_quality_report.md").write_text("\n".join(dq) + "\n")

    report = [
        "# Retrospective Report v1",
        "",
        "## Executive Summary",
        "",
        "V1 собрал официальный корпус Binance risk-events, lifecycle layer и price layer с батчевой загрузкой OHLCV/fallback. Это не инвестиционная рекомендация и не прогноз делистинга; результат предназначен для ретроспективной карты сценариев.",
        "",
        f"- Всего событий: {len(events)}.",
        f"- Lifecycle entities: {len(lifecycle)}.",
        f"- Price-layer entities: {len(read_csv('price_resolution.csv'))}; 15 lifecycle rows с `unknown` outcome не вошли в price universe.",
        f"- Pump20 cases после delisting-announcement: {int((pump['pump20_flag'].astype(str) == 'yes').sum())}.",
        f"- Pump-and-dump cases: {int((pump['pump_and_dump_flag'].astype(str) == 'yes').sum())}.",
        f"- Manual-review scenario rows: {int((scenarios['manual_review_required'].astype(str) == 'yes').sum())}.",
        "",
        "## Data Coverage",
        "",
    ]
    for k, v in event_counts.items():
        report.append(f"- `{k}`: {v}")
    report.extend(["", "## Lifecycle Outcomes", ""])
    for k, v in outcome_counts.items():
        report.append(f"- `{k}`: {v}")
    report.extend(["", "## Scenario Map", ""])
    report.append(summary.to_markdown(index=False))
    report.extend(
        [
            "",
            "## Monitoring Tag Analysis",
            "",
            "Monitoring Tag не трактуется как гарантированный делистинг. Для tagged lifecycle сценарии разделены на immediate dump, slow bleed, temporary recovery, tag removal и tag-to-delisting. Recovery считается отдельно как sustained close logic, поэтому одиночные wicks не засчитываются как настоящее восстановление.",
            "",
            "## Tag Removal Analysis",
            "",
            "Tag removal cases классифицируются отдельно: `TAG_REMOVED_AND_RECOVERED` требует sustained recovery к pre-tag baseline, а `TAG_REMOVED_BUT_NOT_RECOVERED` сохраняет случаи, где bounce не стал устойчивым восстановлением.",
            "",
            "## Delisting Announcement Analysis",
            "",
            "Delisting announcement rows анализируются через `pump_analysis.csv`. Pump-and-dump требует pump20 flag, сильный subsequent drawdown и отсутствие sustained recovery. Fallback prices явно отделены от Binance через `price_source`/exchange.",
            "",
            "## Futures Delisting Analysis",
            "",
            "Futures-only rows сохранены отдельно как `FUTURES_ONLY_DELISTING`; normal BUSD sunset/migration cases не смешиваются со spot token delisting.",
            "",
            "## Pair Removal Control Group",
            "",
            "`SPOT_PAIR_REMOVED` остаётся control class. Эти события классифицируются как `PAIR_REMOVAL_ONLY` и не становятся token delisting outcome.",
            "",
            "## Pre-Announcement Behavior",
            "",
            "Pre-announcement weakness/dump сохраняется как secondary flag, если движение до official publication проходит locked thresholds. Это не доказывает leak или причинность.",
            "",
            "## Caveats And Limitations",
            "",
            "- Public fallback providers неполны; CoinGecko public API был ненадёжен в текущем окружении, поэтому v1 использует CCXT/CEX fallback.",
            "- Низкая ликвидность и suspicious fallback spikes требуют manual review.",
            "- Ticker reuse, rebrand, redenomination и non-standard symbols остаются источником residual risk.",
            "- Market-adjusted returns зависят от v1 equal-weight Binance USDT alt benchmark, без historical universe snapshots.",
            "- Нельзя смешивать spot delisting, futures delisting и pair removal.",
            "",
            "## Implications For Future Monitoring",
            "",
            "Для будущего мониторинга стоит отслеживать tag status, transition to Vote-to-Delist, volume collapse, market-adjusted underperformance, distance from pre-tag baseline, recovery failure, abnormal delisting-announcement volume, fallback-source anomalies и time since tag. Это диагностические признаки, не торговые рекомендации.",
        ]
    )
    (DOCS / "retrospective_report.md").write_text("\n".join(report) + "\n")


def main() -> None:
    scenarios, summary = classify()
    write_reports(scenarios, summary)
    print(
        {
            "scenario_rows": len(scenarios),
            "scenario_summary_rows": len(summary),
            "scenario_distribution": scenarios["primary_scenario"].value_counts().to_dict(),
            "manual_review_scenarios": int((scenarios["manual_review_required"].astype(str) == "yes").sum()),
            "outputs": [
                str(PROCESSED / "scenario_classification.csv"),
                str(PROCESSED / "scenario_classification.parquet"),
                str(PROCESSED / "scenario_summary.csv"),
                str(PROCESSED / "scenario_summary.parquet"),
                str(DOCS / "data_quality_report.md"),
                str(DOCS / "retrospective_report.md"),
            ],
        }
    )


if __name__ == "__main__":
    main()
