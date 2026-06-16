# Bottom/Rebound Risk Batch QA: risk_100_125

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over risk universe slice `100:125`.

## Summary

- processed: 25
- anchor events: 25
- Monitoring Tag anchors: 18
- Spot Delisting anchors: 4
- Vote-to-Delist anchors: 0
- absolute bottoms: 21
- tradable signals: 12
- manual review scenarios: 15
- signal manual review: 5
- missing path / parser issues: REMOVE, SNM, SRM, TORN

## Anchor Distribution

- `MONITORING_TAG_ADDED`: 18
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 4
- `MONITORING_TAG_REMOVED`: 3

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 15
- `SLOW_BLEED_THEN_SQUEEZE`: 3
- `DEAD_CAT_BOUNCE`: 2
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 2
- `DELISTING_DEATH_SPIRAL`: 2
- `EPIC_LIKE_REBOUND`: 1

## Tradeability Tier Distribution

- `C`: 5
- `Manual Review`: 5
- `B`: 1
- `A`: 1

## Requested Counts

- EPIC-like candidates: 1
- continued bleed / death spiral: 2
- weak rebound, max 90d < 20%: 12
- strong rebound without causal signal, max 90d >= 50%: 2
- failed signals: 4

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   |   notes |
|:---------------|------------------------:|:-------------------------|--------:|
| STPT           |                       1 | no                       |     nan |

## Missing Path / Parser Issues

| token_symbol   | anchor_event_type              | notes           |
|:---------------|:-------------------------------|:----------------|
| REMOVE         | MONITORING_TAG_ADDED           | missing_1h_path |
| SNM            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path |
| SRM            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path |
| TORN           | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path |

## Top Candidates For Later 15m Refinement

| token_symbol   | scenario                | tier          | score   | reason                                   |       rr7d |
|:---------------|:------------------------|:--------------|:--------|:-----------------------------------------|-----------:|
| PYTH           | MANUAL_REVIEW_REQUIRED  | C             | 0.763   | manual_review;high_rebound               |   1.32545  |
| QI             | MANUAL_REVIEW_REQUIRED  |               |         | manual_review;high_rebound               | nan        |
| QUICK          | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| RDNT           | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| REEF           | DEAD_CAT_BOUNCE         |               |         | high_rebound                             | nan        |
| REI            | MANUAL_REVIEW_REQUIRED  | Manual Review | 0.284   | manual_review;high_rebound               |   1.87232  |
| REMOVE         | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| REN            | SLOW_BLEED_THEN_SQUEEZE | C             | 0.614   | high_rebound                             |   0.318975 |
| SNM            | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| SNT            | SLOW_BLEED_THEN_SQUEEZE | Manual Review | 0.0     | high_rebound                             |   0.381994 |
| SRM            | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| STMX           | SLOW_BLEED_THEN_SQUEEZE | Manual Review | 0.0     | high_rebound;failed_signal               |   0.138355 |
| STORJ          | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| STPT           | EPIC_LIKE_REBOUND       | C             | 0.743   | high_rebound;failed_signal               |   0.871178 |
| SUN            | DEAD_CAT_BOUNCE         | B             | 0.786   | B-tier;high_rebound                      |  15.3749   |
| SXP            | MANUAL_REVIEW_REQUIRED  | Manual Review | 0.18    | manual_review                            |  16.0681   |
| SYN            | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| SYS            | MANUAL_REVIEW_REQUIRED  | Manual Review | 0.0     | manual_review;high_rebound;failed_signal |   0.576721 |
| THE            | MANUAL_REVIEW_REQUIRED  | A             | 0.963   | A-tier;manual_review;high_rebound        |   5.44202  |
| TLM            | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| TORN           | MANUAL_REVIEW_REQUIRED  |               |         | manual_review                            | nan        |
| TROY           | DELISTING_DEATH_SPIRAL  | C             | 0.673   | failed_signal                            |   0        |

## Files

- `data/processed/bottom_analysis_risk_100_125.csv`
- `data/processed/rebound_analysis_risk_100_125.csv`
- `data/processed/tradable_bottom_signals_risk_100_125.csv`
- `data/processed/signal_quality_risk_100_125.csv`
- `data/processed/bottom_rebound_scenarios_risk_100_125.csv`
- `data/processed/epic_like_cases_risk_100_125.csv`
- `data/processed/bottom_rebound_case_comparison_risk_100_125.csv`
- `docs/bottom_rebound_risk_100_125_report.md`
