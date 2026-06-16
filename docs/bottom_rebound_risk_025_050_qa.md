# Bottom/Rebound Risk Batch QA: risk_025_050

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over lifecycle risk universe slice `25:50`.

## Summary

- token-risk entities processed: 25
- anchor events: 25
- absolute bottoms: 24
- tradable signals: 16
- manual review scenarios: 16
- missing 1h path: D

## Anchor Event Types

- `MONITORING_TAG_ADDED`: 21
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 4

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 16
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 3
- `EPIC_LIKE_REBOUND`: 2
- `DELISTING_DEATH_SPIRAL`: 2
- `DEAD_CAT_BOUNCE`: 1
- `NO_BOTTOM_CONTINUED_BLEED`: 1

## Tradeability Tiers

- `C`: 7
- `Manual Review`: 5
- `B`: 3
- `A`: 1

## Required Counts

- Monitoring Tag anchors: 21
- Spot Delisting anchors: 4
- Vote-to-Delist anchors: 0
- EPIC-like candidates: 3
- continued bleed / death spiral: 3
- weak rebound, max 90d < 20%: 9
- strong rebound without causal signal, max 90d >= 50%: 2
- failed signals: 8
- signal manual review: 5

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   | notes                                                |
|:---------------|------------------------:|:-------------------------|:-----------------------------------------------------|
| CTXC           |                    1    | no                       | nan                                                  |
| EPIC           |                    0.75 | yes                      | manual_case_study=false;epic_evaluated_by_same_rules |
| FLOW           |                    0.8  | no                       | nan                                                  |

## Top Candidates For Optional 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                   |       rr7d |
|:---------------|:--------------------------------|:--------------|:--------|:-----------------------------------------|-----------:|
| COOKIE         | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.089   | manual_review;failed_signal              |   3.18471  |
| COS            | MANUAL_REVIEW_REQUIRED          | C             | 0.703   | manual_review;high_rebound               |   1.47051  |
| CREAM          | MANUAL_REVIEW_REQUIRED          | B             | 0.812   | B-tier;manual_review;high_rebound        |   2.76633  |
| CTXC           | EPIC_LIKE_REBOUND               | B             | 0.947   | B-tier;high_rebound                      |   4.85155  |
| CVX            | DEAD_CAT_BOUNCE                 |               |         | high_rebound                             | nan        |
| D              | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| DATA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| DEGO           | MANUAL_REVIEW_REQUIRED          | C             | 0.696   | manual_review;failed_signal              |   1.17662  |
| DENT           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.144   | manual_review;high_rebound;failed_signal |   0.104895 |
| DF             | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| DODO           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| EPIC           | MANUAL_REVIEW_REQUIRED          | B             | 0.872   | B-tier;manual_review;high_rebound        |  10.4032   |
| EPX            | MANUAL_REVIEW_REQUIRED          | C             | 0.681   | manual_review;high_rebound;failed_signal |   0.533431 |
| FARM           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| FIO            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| FIRO           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                             | nan        |
| FIS            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal |   0.108588 |
| FLM            | MANUAL_REVIEW_REQUIRED          | C             | 0.7     | manual_review;high_rebound;failed_signal |  20.1133   |
| FLOW           | EPIC_LIKE_REBOUND               | C             | 0.589   | high_rebound                             |   0.803963 |
| FOR            | MANUAL_REVIEW_REQUIRED          | C             | 0.597   | manual_review;high_rebound;failed_signal |   0.695389 |

## Batch Files

- `data/processed/bottom_analysis_risk_025_050.csv`
- `data/processed/rebound_analysis_risk_025_050.csv`
- `data/processed/tradable_bottom_signals_risk_025_050.csv`
- `data/processed/signal_quality_risk_025_050.csv`
- `data/processed/bottom_rebound_scenarios_risk_025_050.csv`
- `data/processed/epic_like_cases_risk_025_050.csv`
- `data/processed/bottom_rebound_case_comparison_risk_025_050.csv`
- `docs/bottom_rebound_risk_025_050_report.md`
