# Bottom/Rebound Risk Batch QA: risk_125_148

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over risk universe slice `125:148` after excluding `CML` and `REMOVE` parser artifacts.

## Summary

- processed: 22
- anchor events: 22
- Monitoring Tag anchors: 19
- Spot Delisting anchors: 3
- Monitoring Tag Removed anchors: 0
- Vote-to-Delist anchors: 0
- absolute bottoms: 21
- tradable signals: 10
- manual review scenarios: 10
- signal manual review: 3
- missing path / parser issues: VAI

## Anchor Distribution

- `MONITORING_TAG_ADDED`: 19
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 3

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 10
- `DELISTING_DEATH_SPIRAL`: 5
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 4
- `EPIC_LIKE_REBOUND`: 1
- `DEAD_CAT_BOUNCE`: 1
- `SLOW_BLEED_THEN_SQUEEZE`: 1

## Tradeability Tier Distribution

- `C`: 5
- `Manual Review`: 3
- `B`: 2

## Requested Counts

- EPIC-like candidates: 1
- continued bleed / death spiral: 5
- weak rebound, max 90d < 20%: 8
- strong rebound without causal signal, max 90d >= 50%: 5
- failed signals: 7

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   |   notes |
|:---------------|------------------------:|:-------------------------|--------:|
| UNFI           |                       1 | no                       |     nan |

## Missing Path / Parser Issues

| token_symbol   | anchor_event_type    | notes           |
|:---------------|:---------------------|:----------------|
| VAI            | MONITORING_TAG_ADDED | missing_1h_path |

## Top Candidates For Later 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                          |       rr7d |
|:---------------|:--------------------------------|:--------------|:--------|:------------------------------------------------|-----------:|
| UFT            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.226   | manual_review;failed_signal                     |   0.948196 |
| UNFI           | EPIC_LIKE_REBOUND               | B             | 0.874   | B-tier;high_rebound                             |   2.52036  |
| VAI            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan        |
| VELODROME      | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan        |
| VGX            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | C             | 0.682   | failed_signal                                   |   0.15024  |
| VIC            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      | nan        |
| VITE           | MANUAL_REVIEW_REQUIRED          | B             | 0.681   | B-tier;manual_review;high_rebound;failed_signal |   1.87572  |
| VOXEL          | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.07    | manual_review;high_rebound;failed_signal        | 106.329    |
| WAN            | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    | nan        |
| WAVES          | DELISTING_DEATH_SPIRAL          | C             | 0.727   | failed_signal                                   |   0.89634  |
| WIF            | DEAD_CAT_BOUNCE                 |               |         | high_rebound                                    | nan        |
| WNXM           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      | nan        |
| WRX            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan        |
| XEM            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.078   | manual_review;high_rebound                      |   2.70554  |
| YFII           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   | nan        |
| ZEC            | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    | nan        |
| ZEN            | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.558   | high_rebound;failed_signal                      |   0.437459 |

## Files

- `data/processed/bottom_analysis_risk_125_148.csv`
- `data/processed/rebound_analysis_risk_125_148.csv`
- `data/processed/tradable_bottom_signals_risk_125_148.csv`
- `data/processed/signal_quality_risk_125_148.csv`
- `data/processed/bottom_rebound_scenarios_risk_125_148.csv`
- `data/processed/epic_like_cases_risk_125_148.csv`
- `data/processed/bottom_rebound_case_comparison_risk_125_148.csv`
- `docs/bottom_rebound_risk_125_148_report.md`
