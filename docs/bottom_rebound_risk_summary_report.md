# Bottom/Rebound Risk Summary Report

Full monolithic bottom/rebound run was not started. This report summarizes merged risk-only batches plus gap backfills.

## Coverage

- expected risk universe after exclusions: 147
- merged token-risk entities: 147
- coverage ok: True
- FORTH gap backfill included: True
- TRU gap backfill included: True
- CML excluded: True
- REMOVE excluded: True

## Duplicate Checks

- bottom duplicates: 0
- rebound duplicates: 0
- scenario duplicates: 0
- signal duplicates: 0

## Anchor Event Distribution

| anchor_event_type              |   count |
|:-------------------------------|--------:|
| MONITORING_TAG_ADDED           |     118 |
| SPOT_TOKEN_DELISTING_ANNOUNCED |      26 |
| MONITORING_TAG_REMOVED         |       3 |

## Scenario Distribution

| primary_bottom_rebound_scenario   |   count |
|:----------------------------------|--------:|
| MANUAL_REVIEW_REQUIRED            |      82 |
| NO_CLEAR_BOTTOM_REBOUND_PATTERN   |      20 |
| DELISTING_DEATH_SPIRAL            |      13 |
| EPIC_LIKE_REBOUND                 |      12 |
| SLOW_BLEED_THEN_SQUEEZE           |       9 |
| DEAD_CAT_BOUNCE                   |       6 |
| NO_BOTTOM_CONTINUED_BLEED         |       5 |

## Signal Quality

- absolute bottoms: 140
- tradable signals: 84
- failed signals: 40

### Tradeability Tier Distribution

| tradeability_tier   |   count |
|:--------------------|--------:|
| Manual Review       |      35 |
| C                   |      27 |
| B                   |      16 |
| A                   |       6 |

## Rebound Classes

- EPIC-like candidates: 13
- continued bleed / death spiral: 18
- weak rebound, max 90d < 20%: 55
- strong rebound without causal signal, max 90d >= 50%: 22

## EPIC-Like Candidates

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

## Manual Review / Data Quality

- manual_review scenarios: 82

### Missing Path / Parser Issues

| token_symbol   | anchor_event_type              | notes                                 |
|:---------------|:-------------------------------|:--------------------------------------|
| D              | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path_or_no_post_event_data |
| IDRT           | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path                       |
| NON            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path                       |
| SNM            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path                       |
| SRM            | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path                       |
| TORN           | SPOT_TOKEN_DELISTING_ANNOUNCED | missing_1h_path                       |
| VAI            | MONITORING_TAG_ADDED           | missing_1h_path                       |

### Manual Review Reason Counts

| reason                                |   count |
|:--------------------------------------|--------:|
| low_quote_volume_at_low               |      69 |
| low_liquidity_wick                    |      29 |
| short_post_event_history              |      10 |
| missing_bottom_or_path                |       7 |
| missing_1h_path                       |       6 |
| missing_1h_path_or_no_post_event_data |       1 |

## Top Candidates For Later 15m Refinement

| token_symbol   | scenario                        | tier          | score   | reason                                          |   risk_reward_7d |
|:---------------|:--------------------------------|:--------------|:--------|:------------------------------------------------|-----------------:|
| MOB            | EPIC_LIKE_REBOUND               | A             | 0.963   | A-tier;high_rebound;EPIC-like                   |       19.1317    |
| THE            | MANUAL_REVIEW_REQUIRED          | A             | 0.963   | A-tier;manual_review;high_rebound               |        5.44202   |
| CTXC           | EPIC_LIKE_REBOUND               | B             | 0.947   | B-tier;high_rebound;EPIC-like                   |        4.85155   |
| BAKE           | EPIC_LIKE_REBOUND               | A             | 0.923   | A-tier;high_rebound;EPIC-like                   |       20.4965    |
| BSW            | MANUAL_REVIEW_REQUIRED          | A             | 0.923   | A-tier;manual_review;high_rebound               |        9.51186   |
| UNFI           | EPIC_LIKE_REBOUND               | B             | 0.874   | B-tier;high_rebound;EPIC-like                   |        2.52036   |
| EPIC           | MANUAL_REVIEW_REQUIRED          | B             | 0.872   | B-tier;manual_review;high_rebound;EPIC-like     |       10.4032    |
| PORTAL         | EPIC_LIKE_REBOUND               | A             | 0.853   | A-tier;high_rebound;failed_signal;EPIC-like     |        3.55987   |
| HARD           | SLOW_BLEED_THEN_SQUEEZE         | B             | 0.85    | B-tier;high_rebound                             |        1.78523   |
| GPS            | MANUAL_REVIEW_REQUIRED          | B             | 0.832   | B-tier;manual_review;high_rebound;failed_signal |        2.65237   |
| CREAM          | MANUAL_REVIEW_REQUIRED          | B             | 0.812   | B-tier;manual_review;high_rebound               |        2.76633   |
| ARDR           | MANUAL_REVIEW_REQUIRED          | B             | 0.795   | B-tier;manual_review;high_rebound               |        3.33243   |
| BLZ            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | B             | 0.787   | B-tier                                          |        1.73651   |
| SUN            | DEAD_CAT_BOUNCE                 | B             | 0.786   | B-tier;high_rebound                             |       15.3749    |
| CLV            | MANUAL_REVIEW_REQUIRED          | B             | 0.764   | B-tier;manual_review;high_rebound               |       57.9642    |
| PYTH           | MANUAL_REVIEW_REQUIRED          | C             | 0.763   | manual_review;high_rebound                      |        1.32545   |
| GHST           | EPIC_LIKE_REBOUND               | B             | 0.752   | B-tier;high_rebound;EPIC-like                   |        4.31818   |
| STPT           | EPIC_LIKE_REBOUND               | C             | 0.743   | high_rebound;failed_signal;EPIC-like            |        0.871178  |
| ALPACA         | EPIC_LIKE_REBOUND               | C             | 0.742   | high_rebound;EPIC-like                          |       16.4184    |
| BIFI           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.741   | manual_review;high_rebound                      |        1.29699   |
| LTO            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | B             | 0.732   | B-tier;failed_signal                            |        4.36644   |
| WAVES          | DELISTING_DEATH_SPIRAL          | C             | 0.727   | failed_signal                                   |        0.89634   |
| KEY            | EPIC_LIKE_REBOUND               | C             | 0.72    | high_rebound;failed_signal;EPIC-like            |        0.598484  |
| POLS           | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.715   | high_rebound                                    |        0.19694   |
| HIFI           | MANUAL_REVIEW_REQUIRED          | C             | 0.707   | manual_review;high_rebound;failed_signal        |        0.562874  |
| COS            | MANUAL_REVIEW_REQUIRED          | C             | 0.703   | manual_review;high_rebound                      |        1.47051   |
| FLM            | MANUAL_REVIEW_REQUIRED          | C             | 0.7     | manual_review;high_rebound;failed_signal        |       20.1133    |
| DEGO           | MANUAL_REVIEW_REQUIRED          | C             | 0.696   | manual_review;failed_signal                     |        1.17662   |
| MOVE           | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.689   | high_rebound;failed_signal                      |        0.266709  |
| VGX            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | C             | 0.682   | failed_signal                                   |        0.15024   |
| EPX            | MANUAL_REVIEW_REQUIRED          | C             | 0.681   | manual_review;high_rebound;failed_signal        |        0.533431  |
| VITE           | MANUAL_REVIEW_REQUIRED          | B             | 0.681   | B-tier;manual_review;high_rebound;failed_signal |        1.87572   |
| TROY           | DELISTING_DEATH_SPIRAL          | C             | 0.673   | failed_signal                                   |        0         |
| NKN            | MANUAL_REVIEW_REQUIRED          | C             | 0.66    | manual_review;high_rebound;failed_signal        |       49.4118    |
| REN            | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.614   | high_rebound                                    |        0.318975  |
| FOR            | MANUAL_REVIEW_REQUIRED          | C             | 0.597   | manual_review;high_rebound;failed_signal        |        0.695389  |
| FLOW           | EPIC_LIKE_REBOUND               | C             | 0.589   | high_rebound;EPIC-like                          |        0.803963  |
| IRIS           | MANUAL_REVIEW_REQUIRED          | C             | 0.577   | manual_review;high_rebound;failed_signal        |        0.541114  |
| ZEN            | SLOW_BLEED_THEN_SQUEEZE         | C             | 0.558   | high_rebound;failed_signal                      |        0.437459  |
| KMD            | MANUAL_REVIEW_REQUIRED          | C             | 0.488   | manual_review;failed_signal                     |        0.0128535 |
| KDA            | NO_CLEAR_BOTTOM_REBOUND_PATTERN | Manual Review | 0.402   | failed_signal                                   |        0.977343  |
| PDA            | EPIC_LIKE_REBOUND               | Manual Review | 0.371   | high_rebound;failed_signal;EPIC-like            |        4.18113   |
| REI            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.284   | manual_review;high_rebound                      |        1.87232   |
| UFT            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.226   | manual_review;failed_signal                     |        0.948196  |
| SXP            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.18    | manual_review                                   |       16.0681    |
| A2Z            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.144   | manual_review;failed_signal                     |       18.1459    |
| DENT           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.144   | manual_review;high_rebound;failed_signal        |        0.104895  |
| COOKIE         | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.089   | manual_review;failed_signal                     |        3.18471   |
| XEM            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.078   | manual_review;high_rebound                      |        2.70554   |
| VOXEL          | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.07    | manual_review;high_rebound;failed_signal        |      106.329     |
| FUN            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.013   | manual_review                                   |        0.551522  |
| NULS           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.003   | manual_review                                   |        0.340615  |
| ACA            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;failed_signal                     |        0.530786  |
| AST            | EPIC_LIKE_REBOUND               | Manual Review | 0.0     | high_rebound;failed_signal;EPIC-like            |        0.673077  |
| ATA            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |        0         |
| BAL            | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound                                    |        0.619489  |
| FIS            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |        0.108588  |
| HOOK           | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |        1.59672   |
| MBL            | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound                                    |        0.723213  |
| MDT            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |        0.168729  |
| SNT            | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound                                    |        0.381994  |
| STMX           | SLOW_BLEED_THEN_SQUEEZE         | Manual Review | 0.0     | high_rebound;failed_signal                      |        0.138355  |
| SYS            | MANUAL_REVIEW_REQUIRED          | Manual Review | 0.0     | manual_review;high_rebound;failed_signal        |        0.576721  |
| AERGO          | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| AKRO           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| ALCX           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| AMB            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| BADGER         | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| BETA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| BOND           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| BTS            | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    |      nan         |
| CHESS          | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| CVX            | DEAD_CAT_BOUNCE                 |               |         | high_rebound                                    |      nan         |
| D              | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| DATA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| DF             | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| DODO           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| FARM           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| FIO            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| FIRO           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    |      nan         |
| GFT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| GTC            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| HEI            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| HFT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| HIGH           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    |      nan         |
| IDEX           | NO_CLEAR_BOTTOM_REBOUND_PATTERN |               |         | high_rebound                                    |      nan         |
| IDRT           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| KP3R           | DEAD_CAT_BOUNCE                 |               |         | high_rebound                                    |      nan         |
| LINA           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| LOOM           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| MDX            | DEAD_CAT_BOUNCE                 |               |         | high_rebound                                    |      nan         |
| MLN            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| NFP            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| NOM            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| NON            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| NTRN           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| OAX            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| OXT            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
| PERP           | MANUAL_REVIEW_REQUIRED          |               |         | manual_review;high_rebound                      |      nan         |
| PHB            | MANUAL_REVIEW_REQUIRED          |               |         | manual_review                                   |      nan         |
