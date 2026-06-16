# Bottom/Rebound Risk Batch QA: risk_075_100

Full monolithic bottom/rebound run was not started. This batch uses `--risk-only` over risk universe slice `75:100`.

## Summary

- processed: 25
- anchor events: 25
- Monitoring Tag anchors: 18
- Spot Delisting anchors: 7
- Vote-to-Delist anchors: 0
- absolute bottoms: 24
- tradable signals: 12
- manual review scenarios: 13
- signal manual review: 5
- missing path / parser issues: NON

## Anchor Distribution

- `MONITORING_TAG_ADDED`: 18
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 7

## Scenario Distribution

- `MANUAL_REVIEW_REQUIRED`: 13
- `NO_BOTTOM_CONTINUED_BLEED`: 4
- `EPIC_LIKE_REBOUND`: 3
- `SLOW_BLEED_THEN_SQUEEZE`: 2
- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 2
- `DEAD_CAT_BOUNCE`: 1

## Tradeability Tier Distribution

- `Manual Review`: 5
- `C`: 4
- `A`: 2
- `B`: 1

## Requested Counts

- EPIC-like candidates: 3
- continued bleed / death spiral: 4
- weak rebound, max 90d < 20%: 11
- strong rebound without causal signal, max 90d >= 50%: 4
- failed signals: 6

## EPIC-Like Candidates

| token_symbol   |   epic_similarity_score | manual_review_required   |   notes |
|:---------------|------------------------:|:-------------------------|--------:|
| MOB            |                     1   | no                       |     nan |
| PDA            |                     0.8 | no                       |     nan |
| PORTAL         |                     0.8 | no                       |     nan |

## Missing Path / Parser Issues

| token_symbol   | anchor_event_type              | notes           |
|:---------------|:-------------------------------|:----------------|
| NON            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path |

## Top Candidates For Later 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                   |       rr7d |
|:---------------|:--------------------------------|:--------------|:--------|:-----------------------------------------|-----------:|
| MDT            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal |   0.168729 |
| MDX            | DEAD_CAT_BOUNCE                 |               |         | high_rebound                             | nan        |
| MLN            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| MOB            | EPIC_LIKE_REBOUND               | A             | 0.963   | A-tier;high_rebound                      |  19.1317   |
| MOVE           | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.689   | high_rebound;failed_signal               |   0.266709 |
| NFP            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| NKN            | MANUAL_REVIEW_REQUIRED          | C             | 0.66    | manual_review;high_rebound;failed_signal |  49.4118   |
| NOM            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| NON            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| NTRN           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| NULS           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.003   | manual_review                            |   0.340615 |
| OAX            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| OXT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| PDA            | EPIC_LIKE_REBOUND               | Manual Review | 0.371   | high_rebound;failed_signal               |   4.18113  |
| PERP           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound               | nan        |
| PHB            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                            | nan        |
| POLS           | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.715   | high_rebound                             |   0.19694  |
| POND           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound               | nan        |
| PORTAL         | EPIC_LIKE_REBOUND               | A             | 0.853   | A-tier;high_rebound;failed_signal        |   3.55987  |
| PROS           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                             | nan        |

## Files

- `data/processed/bottom_analysis_risk_075_100.csv`
- `data/processed/rebound_analysis_risk_075_100.csv`
- `data/processed/tradable_bottom_signals_risk_075_100.csv`
- `data/processed/signal_quality_risk_075_100.csv`
- `data/processed/bottom_rebound_scenarios_risk_075_100.csv`
- `data/processed/epic_like_cases_risk_075_100.csv`
- `data/processed/bottom_rebound_case_comparison_risk_075_100.csv`
- `docs/bottom_rebound_risk_075_100_report.md`
