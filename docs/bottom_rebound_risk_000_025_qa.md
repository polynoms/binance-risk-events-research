# Bottom/Rebound Risk Batch QA: risk_000_025

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over lifecycle risk universe slice `0:25`.

## Summary

- token-risk entities processed: 25
- anchor events: 25
- absolute bottoms: 24
- tradable signals: 17
- manual review scenarios: 16
- missing 1h path: CML

## Anchor Event Types

- `MONITORING_TAG_ADDED`: 21
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 3
- `VOTE_TO_DELIST_STARTED`: 1

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 16
- `EPIC_LIKE_REBOUND`: 3
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 3
- `DELISTING_DEATH_SPIRAL`: 2
- `SLOW_BLEED_THEN_SQUEEZE`: 1

## Tradeability Tiers

- `Manual Review`: 8
- `B`: 5
- `C`: 2
- `A`: 2

## Required Counts

- Monitoring Tag anchors: 21
- Spot Delisting anchors: 3
- Vote-to-Delist anchors: 1
- EPIC-like candidates: 3
- continued bleed / death spiral: 2
- weak rebound, max 90d < 20%: 8
- strong rebound without causal signal, max 90d >= 50%: 4
- failed signals: 5
- signal manual review: 8

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   |   notes |
|:---------------|------------------------:|:-------------------------|--------:|
| ALPACA         |                       1 | no                       |     nan |
| AST            |                       1 | no                       |     nan |
| BAKE           |                       1 | no                       |     nan |

## Top Candidates For Optional 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                   |   risk_reward_7d |
|:---------------|:--------------------------------|:--------------|:--------|:-----------------------------------------|-----------------:|
| A2Z            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.144   | manual_review;failed_signal              |        18.1459   |
| ACA            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;failed_signal              |         0.530786 |
| AERGO          | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound               |       nan        |
| AKRO           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |
| ALCX           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |
| ALPACA         | EPIC_LIKE_REBOUND               | C             | 0.742   | high_rebound                             |        16.4184   |
| AMB            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |
| ARDR           | MANUAL_REVIEW_REQUIRED          | B             | 0.795   | B-tier;manual_review;high_rebound        |         3.33243  |
| AST            | EPIC_LIKE_REBOUND               | Manual Review | 0.0     | high_rebound;failed_signal               |         0.673077 |
| ATA            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal |         0        |
| BADGER         | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |
| BAKE           | EPIC_LIKE_REBOUND               | A             | 0.923   | A-tier;high_rebound                      |        20.4965   |
| BAL            | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound                             |         0.619489 |
| BETA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound               |       nan        |
| BIFI           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.741   | manual_review;high_rebound               |         1.29699  |
| BLZ            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | B             | 0.787   | B-tier                                   |         1.73651  |
| BOND           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound               |       nan        |
| BSW            | MANUAL_REVIEW_REQUIRED          | A             | 0.923   | A-tier;manual_review;high_rebound        |         9.51186  |
| BTS            | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                             |       nan        |
| CHESS          | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |
| CLV            | MANUAL_REVIEW_REQUIRED          | B             | 0.764   | B-tier;manual_review;high_rebound        |        57.9642   |
| CML            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            |       nan        |

## Batch Files

- `data/processed/bottom_analysis_risk_000_025.csv`
- `data/processed/rebound_analysis_risk_000_025.csv`
- `data/processed/tradable_bottom_signals_risk_000_025.csv`
- `data/processed/signal_quality_risk_000_025.csv`
- `data/processed/bottom_rebound_scenarios_risk_000_025.csv`
- `data/processed/epic_like_cases_risk_000_025.csv`
- `data/processed/bottom_rebound_case_comparison_risk_000_025.csv`
- `docs/bottom_rebound_risk_000_025_report.md`
