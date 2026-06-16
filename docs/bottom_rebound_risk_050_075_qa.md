# Bottom/Rebound Risk Batch QA: risk_050_075

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over risk universe slice `50:75` after excluding non-token artifacts such as `CML`.

## Summary

- token-risk entities processed: 25
- anchor events: 25
- absolute bottoms: 24
- tradable signals: 17
- manual review scenarios: 13
- missing price/path issues: IDRT

## Anchor Event Types

- `MONITORING_TAG_ADDED`: 20
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 5

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 13
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 6
- `EPIC_LIKE_REBOUND`: 2
- `SLOW_BLEED_THEN_SQUEEZE`: 2
- `DEAD_CAT_BOUNCE`: 1
- `DELISTING_DEATH_SPIRAL`: 1

## Tradeability Tiers

- `Manual Review`: 9
- `B`: 4
- `C`: 4

## Required Counts

- Monitoring Tag anchors: 20
- Spot Delisting anchors: 5
- Vote-to-Delist anchors: 0
- EPIC-like candidates: 2
- continued bleed / death spiral: 1
- weak rebound, max 90d < 20%: 7
- strong rebound without causal signal, max 90d >= 50%: 5
- failed signals: 10
- signal manual review: 9

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   |   notes |
|:---------------|------------------------:|:-------------------------|--------:|
| GHST           |                     1   | no                       |     nan |
| KEY            |                     0.8 | no                       |     nan |

## Top Candidates For Optional 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                          |        rr7d |
|:---------------|:--------------------------------|:--------------|:--------|:------------------------------------------------|------------:|
| FUN            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.013   | manual_review                                   |   0.551522  |
| GFT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan         |
| GHST           | EPIC_LIKE_REBOUND               | B             | 0.752   | B-tier;high_rebound                             |   4.31818   |
| GPS            | MANUAL_REVIEW_REQUIRED          | B             | 0.832   | B-tier;manual_review;high_rebound;failed_signal |   2.65237   |
| GTC            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      | nan         |
| HARD           | SLOW_BLEED_THEN_SQUEEZE         | B             | 0.85    | B-tier;high_rebound                             |   1.78523   |
| HEI            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      | nan         |
| HFT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan         |
| HIFI           | MANUAL_REVIEW_REQUIRED          | C             | 0.707   | manual_review;high_rebound;failed_signal        |   0.562874  |
| HIGH           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    | nan         |
| HOOK           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |   1.59672   |
| IDEX           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    | nan         |
| IDRT           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan         |
| IRIS           | MANUAL_REVIEW_REQUIRED          | C             | 0.577   | manual_review;high_rebound;failed_signal        |   0.541114  |
| KDA            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | Manual Review | 0.402   | failed_signal                                   |   0.977343  |
| KEY            | EPIC_LIKE_REBOUND               | C             | 0.72    | high_rebound;failed_signal                      |   0.598484  |
| KMD            | MANUAL_REVIEW_REQUIRED          | C             | 0.488   | manual_review;failed_signal                     |   0.0128535 |
| KP3R           | DEAD_CAT_BOUNCE                 |               |         | high_rebound                                    | nan         |
| LINA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan         |
| LOOM           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan         |
| LTO            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | B             | 0.732   | B-tier;failed_signal                            |   4.36644   |
| MBL            | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound                                    |   0.723213  |

## Batch Files

- `data/processed/bottom_analysis_risk_050_075.csv`
- `data/processed/rebound_analysis_risk_050_075.csv`
- `data/processed/tradable_bottom_signals_risk_050_075.csv`
- `data/processed/signal_quality_risk_050_075.csv`
- `data/processed/bottom_rebound_scenarios_risk_050_075.csv`
- `data/processed/epic_like_cases_risk_050_075.csv`
- `data/processed/bottom_rebound_case_comparison_risk_050_075.csv`
- `docs/bottom_rebound_risk_050_075_report.md`
