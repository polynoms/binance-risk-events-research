# Bottom/Rebound 15m Refinement: Risk Top Candidates

Full monolithic bottom/rebound run was not started. Control-only was not run. This is selected-candidate 15m QA only.

## Scope

Candidates requested/covered: `MOB, THE, CTXC, BAKE, BSW, UNFI, EPIC, PORTAL, HARD, GPS, CREAM, ARDR, SUN, CLV, GHST, STPT, ALPACA, AST, FLOW, KEY, PDA`.

Input signals: `data/processed/tradable_bottom_signals_risk.csv`  
Output: `data/processed/signal_15m_refinement_risk_top.csv`

## Summary

- candidates covered: 21
- rows produced: 37
- unique candidates in output: 21
- candidates without existing 1h signal / no 15m entry: 7
- clean 15m confirmations: 10
- downgraded / review-caution rows: 28
- stop failed rows: 8
- wick/range risk rows: 8
- single-candle artifact rows: 2
- low-liquidity at entry, quote volume < 25k: 11
- below v4 signal-liquidity threshold, quote volume < 100k: 19

## A/B Tier After 15m

- A-tier rows checked: 5
- A-tier clean after 15m: 3
- B-tier rows checked: 10
- B-tier clean after 15m: 3

### A/B Rows

| token_symbol   | signal_type                 | tradeability_tier   |   final_tradeability_score | refined_15m_entry_time    |   liquidity_at_15m_entry |   refined_rr_7d |   refined_mfe_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | refinement_notes                                          | status_after_15m        |
|:---------------|:----------------------------|:--------------------|---------------------------:|:--------------------------|-------------------------:|----------------:|-----------------:|:--------------|:-----------------|:------------------------------|:----------------------------------------------------------|:------------------------|
| THE            | HIGHER_LOW_BREAKOUT         | A                   |                      0.963 | 2025-07-14T04:00:00+00:00 |                285965    |         8.6078  |         1.09511  | no            | no               | no                            | nan                                                       | confirmed_high_quality  |
| CTXC           | HIGHER_LOW_BREAKOUT         | B                   |                      0.947 | 2024-07-09T13:00:00+00:00 |                 21340.8  |         4.13584 |         0.469466 | no            | yes              | no                            | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity | wick_or_artifact_review |
| CTXC           | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |                      0.808 | 2024-07-09T04:00:00+00:00 |                  4092.79 |         4.76334 |         0.488786 | no            | no               | no                            | low_15m_entry_liquidity                                   | low_liquidity_review    |
| BAKE           | CAPITULATION_RECLAIM        | A                   |                      0.923 | 2025-09-09T19:00:00+00:00 |                 62493.3  |        66.4493  |         5.22507  | no            | no               | no                            | nan                                                       | confirmed_high_quality  |
| BAKE           | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |                      0.913 | 2025-07-16T16:00:00+00:00 |                 42330.8  |         2.69896 |         0.258564 | no            | no               | no                            | nan                                                       | clean_but_weaker_rr     |
| BSW            | HIGHER_LOW_BREAKOUT         | A                   |                      0.923 | 2025-04-19T09:00:00+00:00 |                 60517    |         7.71693 |         2.61446  | no            | yes              | no                            | 15m_entry_has_wick_or_large_range                         | wick_or_artifact_review |
| BSW            | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |                      0.761 | 2025-04-10T11:00:00+00:00 |                 17382    |         2.83505 |         0.234043 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity | failed_or_trap          |
| UNFI           | CAPITULATION_RECLAIM        | B                   |                      0.874 | 2024-04-13T21:00:00+00:00 |                480173    |         4.0283  |         0.466403 | no            | yes              | no                            | 15m_entry_has_wick_or_large_range                         | wick_or_artifact_review |
| EPIC           | HIGHER_LOW_BREAKOUT         | B                   |                      0.872 | 2026-06-01T05:00:00+00:00 |                 23332.8  |         7.61105 |         2.14504  | no            | no               | no                            | low_15m_entry_liquidity                                   | low_liquidity_review    |
| PORTAL         | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |                      0.853 | 2025-05-16T09:00:00+00:00 |                 83956.2  |         5.15284 |         0.596965 | no            | no               | no                            | nan                                                       | confirmed_high_quality  |
| HARD           | HIGHER_LOW_BREAKOUT         | B                   |                      0.85  | 2024-08-25T12:00:00+00:00 |                 83645.4  |         6.6117  |         0.859454 | no            | no               | no                            | nan                                                       | confirmed_high_quality  |
| GPS            | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |                      0.832 | 2025-03-14T15:00:00+00:00 |                264391    |         2.65237 |         0.267806 | yes           | no               | no                            | nan                                                       | failed_or_trap          |
| ARDR           | HIGHER_LOW_BREAKOUT         | B                   |                      0.795 | 2025-04-15T09:00:00+00:00 |                136989    |        10.1536  |         1.8865   | no            | no               | no                            | nan                                                       | confirmed_high_quality  |
| SUN            | HIGHER_LOW_BREAKOUT         | B                   |                      0.786 | 2024-08-13T17:00:00+00:00 |                  6786.12 |        16.712   |         0.677704 | no            | no               | no                            | low_15m_entry_liquidity                                   | low_liquidity_review    |
| CLV            | HIGHER_LOW_BREAKOUT         | B                   |                      0.764 | 2024-11-09T20:00:00+00:00 |                  6462.76 |        62.806   |         5.46698  | no            | no               | no                            | low_15m_entry_liquidity                                   | low_liquidity_review    |

## EPIC-Like Candidates After 15m

- total EPIC-like in merged risk dataset: 13
- EPIC-like candidates covered here: 13
- EPIC-like confirmed / clean enough after 15m: 2
- EPIC-like invalid/downgraded after 15m: 11

| token_symbol   | signal_type                 | tradeability_tier   |   liquidity_at_15m_entry |   refined_rr_7d |   refined_mfe_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | refinement_notes                                                      | status_after_15m        |
|:---------------|:----------------------------|:--------------------|-------------------------:|----------------:|-----------------:|:--------------|:-----------------|:------------------------------|:----------------------------------------------------------------------|:------------------------|
| BAKE           | CAPITULATION_RECLAIM        | A                   |          62493.3         |       66.4493   |        5.22507   | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| PORTAL         | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |          83956.2         |        5.15284  |        0.596965  | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| UNFI           | HIGHER_LOW_BREAKOUT         | C                   |          85674.2         |        0.799067 |        0.122659  | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| ALPACA         | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         204413           |        0.698422 |        0.188092  | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| EPIC           | HIGHER_LOW_BREAKOUT         | B                   |          23332.8         |        7.61105  |        2.14504   | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| CTXC           | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |           4092.79        |        4.76334  |        0.488786  | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| PDA            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           9353.69        |        4.67364  |        0.295     | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity             | failed_or_trap          |
| GHST           | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           3772.49        |        0.888889 |        0.0390244 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |          53936.8         |        0.705882 |        0.0812641 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| KEY            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |              6.90671e+06 |        0.407565 |        0.0770126 | no            | yes              | yes                           | 15m_entry_has_wick_or_large_range;next_3_15m_candles_failed_to_extend | wick_or_artifact_review |
| FLOW           | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |          20347.7         |        0.258398 |        0.0215054 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| MOB            | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         117712           |        0.222469 |        0.0212202 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| STPT           | NO_EXISTING_SIGNAL_15M_QA   | nan                 |            nan           |      nan        |      nan         | nan           | nan              | nan                           | missing_15m_entry_after_signal                                        | no_15m_or_no_1h_signal  |

## Best Tradable Rebound Candidates After 15m

| token_symbol   | signal_type                 | tradeability_tier   |   liquidity_at_15m_entry |   refined_rr_7d |   refined_mfe_7d |   refined_mae_before_mfe | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | status_after_15m       |
|:---------------|:----------------------------|:--------------------|-------------------------:|----------------:|-----------------:|-------------------------:|:--------------|:-----------------|:------------------------------|:-----------------------|
| BAKE           | CAPITULATION_RECLAIM        | A                   |                  62493.3 |        66.4493  |         5.22507  |             -0.002849    | no            | no               | no                            | confirmed_high_quality |
| ARDR           | HIGHER_LOW_BREAKOUT         | B                   |                 136989   |        10.1536  |         1.8865   |             -0.00476776  | no            | no               | no                            | confirmed_high_quality |
| THE            | HIGHER_LOW_BREAKOUT         | A                   |                 285965   |         8.6078  |         1.09511  |             -0.000997672 | no            | no               | no                            | confirmed_high_quality |
| HARD           | HIGHER_LOW_BREAKOUT         | B                   |                  83645.4 |         6.6117  |         0.859454 |             -0.00606673  | no            | no               | no                            | confirmed_high_quality |
| PORTAL         | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |                  83956.2 |         5.15284 |         0.596965 |             -0.00168634  | no            | no               | no                            | confirmed_high_quality |

## Rebound Exists But Not Tradable / Not Clean Under 15m QA

| token_symbol   | signal_type                 | tradeability_tier   |   liquidity_at_15m_entry |   refined_rr_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | refinement_notes                                                      | status_after_15m        |
|:---------------|:----------------------------|:--------------------|-------------------------:|----------------:|:--------------|:-----------------|:------------------------------|:----------------------------------------------------------------------|:------------------------|
| UNFI           | HIGHER_LOW_BREAKOUT         | C                   |          85674.2         |        0.799067 | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| ALPACA         | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         204413           |        0.698422 | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| EPIC           | HIGHER_LOW_BREAKOUT         | B                   |          23332.8         |        7.61105  | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| CTXC           | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |           4092.79        |        4.76334  | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| PDA            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           9353.69        |        4.67364  | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity             | failed_or_trap          |
| GHST           | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           3772.49        |        0.888889 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |          53936.8         |        0.705882 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| KEY            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |              6.90671e+06 |        0.407565 | no            | yes              | yes                           | 15m_entry_has_wick_or_large_range;next_3_15m_candles_failed_to_extend | wick_or_artifact_review |
| FLOW           | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |          20347.7         |        0.258398 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| MOB            | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         117712           |        0.222469 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| STPT           | NO_EXISTING_SIGNAL_15M_QA   | nan                 |            nan           |      nan        | nan           | nan              | nan                           | missing_15m_entry_after_signal                                        | no_15m_or_no_1h_signal  |

## Failed / Trap Cases

| token_symbol   | signal_type                 | tradeability_tier   |   liquidity_at_15m_entry |   refined_rr_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | false_breakout_warning_flag   | refinement_notes                                                      | status_after_15m        |
|:---------------|:----------------------------|:--------------------|-------------------------:|----------------:|:--------------|:-----------------|:------------------------------|:------------------------------|:----------------------------------------------------------------------|:------------------------|
| MOB            | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         117712           |        0.222469 | yes           | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| BSW            | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |          17382           |        2.83505  | yes           | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity             | failed_or_trap          |
| UNFI           | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |         109302           |        0.462517 | yes           | no               | no                            | yes                           | nan                                                                   | failed_or_trap          |
| PORTAL         | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |          83956.2         |        5.15284  | no            | no               | no                            | yes                           | nan                                                                   | confirmed_high_quality  |
| GPS            | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |         264391           |        2.65237  | yes           | no               | no                            | yes                           | nan                                                                   | failed_or_trap          |
| GHST           | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           3772.49        |        0.888889 | yes           | no               | no                            | yes                           | low_15m_entry_liquidity                                               | failed_or_trap          |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |          53936.8         |        0.705882 | yes           | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| FLOW           | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |          20347.7         |        0.258398 | yes           | no               | no                            | yes                           | low_15m_entry_liquidity                                               | failed_or_trap          |
| KEY            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |              6.90671e+06 |        0.407565 | no            | yes              | yes                           | yes                           | 15m_entry_has_wick_or_large_range;next_3_15m_candles_failed_to_extend | wick_or_artifact_review |
| PDA            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |           9353.69        |        4.67364  | yes           | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity             | failed_or_trap          |

## Candidate-Level Best Status

| token_symbol   | signal_type                 | tradeability_tier   |   final_tradeability_score |   liquidity_at_15m_entry |   refined_rr_7d |   refined_mfe_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | refinement_notes                                                      | status_after_15m        |
|:---------------|:----------------------------|:--------------------|---------------------------:|-------------------------:|----------------:|-----------------:|:--------------|:-----------------|:------------------------------|:----------------------------------------------------------------------|:------------------------|
| BAKE           | CAPITULATION_RECLAIM        | A                   |                      0.923 |          62493.3         |       66.4493   |        5.22507   | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| ARDR           | HIGHER_LOW_BREAKOUT         | B                   |                      0.795 |         136989           |       10.1536   |        1.8865    | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| THE            | HIGHER_LOW_BREAKOUT         | A                   |                      0.963 |         285965           |        8.6078   |        1.09511   | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| HARD           | HIGHER_LOW_BREAKOUT         | B                   |                      0.85  |          83645.4         |        6.6117   |        0.859454  | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| PORTAL         | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |                      0.853 |          83956.2         |        5.15284  |        0.596965  | no            | no               | no                            | nan                                                                   | confirmed_high_quality  |
| GPS            | HIGHER_LOW_BREAKOUT         | Manual Review       |                      0     |          25294.8         |        1.45421  |        0.241026  | no            | no               | no                            | nan                                                                   | clean_but_weaker_rr     |
| UNFI           | HIGHER_LOW_BREAKOUT         | C                   |                      0.779 |          85674.2         |        0.799067 |        0.122659  | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| ALPACA         | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |                      0.742 |         204413           |        0.698422 |        0.188092  | no            | no               | no                            | nan                                                                   | downgraded_or_unclear   |
| CLV            | HIGHER_LOW_BREAKOUT         | B                   |                      0.764 |           6462.76        |       62.806    |        5.46698   | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| SUN            | HIGHER_LOW_BREAKOUT         | B                   |                      0.786 |           6786.12        |       16.712    |        0.677704  | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| BSW            | HIGHER_LOW_BREAKOUT         | A                   |                      0.923 |          60517           |        7.71693  |        2.61446   | no            | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | wick_or_artifact_review |
| EPIC           | HIGHER_LOW_BREAKOUT         | B                   |                      0.872 |          23332.8         |        7.61105  |        2.14504   | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| CTXC           | SLOW_BLEED_SQUEEZE_BREAKOUT | A                   |                      0.808 |           4092.79        |        4.76334  |        0.488786  | no            | no               | no                            | low_15m_entry_liquidity                                               | low_liquidity_review    |
| PDA            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |                      0.037 |           9353.69        |        4.67364  |        0.295     | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity             | failed_or_trap          |
| GHST           | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |                      0     |           3772.49        |        0.888889 |        0.0390244 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |                      0     |          53936.8         |        0.705882 |        0.0812641 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| KEY            | SLOW_BLEED_SQUEEZE_BREAKOUT | Manual Review       |                      0.459 |              6.90671e+06 |        0.407565 |        0.0770126 | no            | yes              | yes                           | 15m_entry_has_wick_or_large_range;next_3_15m_candles_failed_to_extend | wick_or_artifact_review |
| FLOW           | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |                      0.589 |          20347.7         |        0.258398 |        0.0215054 | yes           | no               | no                            | low_15m_entry_liquidity                                               | failed_or_trap          |
| MOB            | SLOW_BLEED_SQUEEZE_BREAKOUT | C                   |                      0.561 |         117712           |        0.222469 |        0.0212202 | yes           | yes              | no                            | 15m_entry_has_wick_or_large_range                                     | failed_or_trap          |
| CREAM          | NO_EXISTING_SIGNAL_15M_QA   | nan                 |                    nan     |            nan           |      nan        |      nan         | nan           | nan              | nan                           | missing_15m_entry_after_signal                                        | no_15m_or_no_1h_signal  |
| STPT           | NO_EXISTING_SIGNAL_15M_QA   | nan                 |                    nan     |            nan           |      nan        |      nan         | nan           | nan              | nan                           | missing_15m_entry_after_signal                                        | no_15m_or_no_1h_signal  |

## Notes

- `clean_15m` requires: 15m entry exists, stop not failed, no wick/range risk, no single-candle artifact, and 15m entry quote volume >= 25k.
- This does not prove live tradability. It only reduces obvious 1h artifacts and flags liquidity/wick/trap risks.
- Cases below 100k quote volume at 15m entry still carry execution-size caveats even if not hard-rejected.
