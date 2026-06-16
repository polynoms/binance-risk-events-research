# Bottom/Rebound Merge Report

- bottom_analysis: files=8, rows=147, schema_ok=True, duplicates_removed=0, exclusions_removed=2, output=bottom_analysis_risk.csv
- rebound_analysis: files=8, rows=147, schema_ok=True, duplicates_removed=0, exclusions_removed=2, output=rebound_analysis_risk.csv
- tradable_bottom_signals: files=8, rows=84, schema_ok=True, duplicates_removed=0, exclusions_removed=0, output=tradable_bottom_signals_risk.csv
- signal_quality: files=8, rows=84, schema_ok=True, duplicates_removed=0, exclusions_removed=0, output=signal_quality_risk.csv
- bottom_rebound_scenarios: files=8, rows=147, schema_ok=True, duplicates_removed=0, exclusions_removed=2, output=bottom_rebound_scenarios_risk.csv
- epic_like_cases: files=8, rows=13, schema_ok=True, duplicates_removed=0, exclusions_removed=0, output=epic_like_cases_risk.csv
- bottom_rebound_case_comparison: files=8, rows=147, schema_ok=True, duplicates_removed=0, exclusions_removed=2, output=bottom_rebound_case_comparison_risk.csv

## Risk QA

- token_risk_entities: 147
- CML_present: False
- REMOVE_present: False
- FORTH_present: True
- TRU_present: True

### Scenario Distribution
| primary_bottom_rebound_scenario   |   count |
|:----------------------------------|--------:|
| MANUAL_REVIEW_REQUIRED            |      82 |
| NO_CLEAR_BOTTOM_REBOUND_PATTERN   |      20 |
| DELISTING_DEATH_SPIRAL            |      13 |
| EPIC_LIKE_REBOUND                 |      12 |
| SLOW_BLEED_THEN_SQUEEZE           |       9 |
| DEAD_CAT_BOUNCE                   |       6 |
| NO_BOTTOM_CONTINUED_BLEED         |       5 |

### Anchor Distribution
| anchor_event_type              |   count |
|:-------------------------------|--------:|
| MONITORING_TAG_ADDED           |     118 |
| SPOT_TOKEN_DELISTING_ANNOUNCED |      26 |
| MONITORING_TAG_REMOVED         |       3 |
- absolute_bottoms: 140
- tradable_signals: 84
- failed_signals: 40

### Tradeability Tier Distribution
| tradeability_tier   |   count |
|:--------------------|--------:|
| Manual Review       |      35 |
| C                   |      27 |
| B                   |      16 |
| A                   |       6 |

### EPIC-Like Candidates
| token_symbol   |   epic_similarity_score | manual_review_required   | notes                                                |
|:---------------|------------------------:|:-------------------------|:-----------------------------------------------------|
| ALPACA         |                    1    | no                       | nan                                                  |
| AST            |                    1    | no                       | nan                                                  |
| BAKE           |                    1    | no                       | nan                                                  |
| CTXC           |                    1    | no                       | nan                                                  |
| EPIC           |                    0.75 | yes                      | manual_case_study=false;epic_evaluated_by_same_rules |
| FLOW           |                    0.8  | no                       | nan                                                  |
| GHST           |                    1    | no                       | nan                                                  |
| KEY            |                    0.8  | no                       | nan                                                  |
| MOB            |                    1    | no                       | nan                                                  |
| PDA            |                    0.8  | no                       | nan                                                  |
| PORTAL         |                    0.8  | no                       | nan                                                  |
| STPT           |                    1    | no                       | nan                                                  |
| UNFI           |                    1    | no                       | nan                                                  |
- weak_rebound_90d_lt20: 55
- strong_rebound_without_causal_signal_90d: 22
