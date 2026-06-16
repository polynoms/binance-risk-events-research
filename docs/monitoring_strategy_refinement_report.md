# Monitoring Strategy Refinement v1

Generated at UTC: 2026-05-27T09:55:52.457849+00:00

Scope: Monitoring Tag immediate / 24h refinement only. Spot delisting and pump-fade hypotheses are intentionally untouched.

This is a focused research diagnostic, not a live tradability claim. It does not model borrow availability, funding, forced buy-ins, live order book depth, or venue-specific execution constraints.

## Method

- Base trades come from `backtest_trades.csv` Monitoring Tag rows only.
- Entry rules are limited to immediate +1h, 24h delay, and an interpretable 24h failed-recovery trigger. 7d variants are reported as diagnostics only.
- Cost sensitivity is recomputed at 0/20/50/100 bps from gross returns.
- Outlier sensitivity is reported as excluding top 5% for samples with n >= 20.
- Results with n < 20 are flagged low confidence.
- Filters are tested separately plus a small number of simple combinations; no global optimization grid is used.

## Recommendation

Recommended next candidate rule: `immediate_1h_confirmation + negative_1h_confirmation`. It has n=89, median=7.1%, average=8.9%, PF=2.20, and positive ex-top5 average.

## Priority Variants at 20 bps

| execution_variant           | filter_group       | filter_name                        | entry_feasible_filter   |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | median_mae   | median_mfe   |   profit_factor | average_return_ex_top5   | low_confidence_flag   |
|:----------------------------|:-------------------|:-----------------------------------|:------------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:-------------|:-------------|----------------:|:-------------------------|:----------------------|
| 24h_delay                   | volatility         | high_post_tag_volatility           | no                      |         37 | 51.4%      | 33.3%           | 14.1%            | -15.5%       | 42.7%        | 33.3%        | 68.1%        |         2.87998 | 12.5%                    | no                    |
| immediate_1h_confirmation   | scenario           | scenario_tag_not_recovered         | no                      |         36 | 69.4%      | 32.3%           | 18.8%            | -16.9%       | 42.7%        | 9.4%         | 65.6%        |         4.6502  | 13.1%                    | no                    |
| 24h_delay                   | scenario           | scenario_tag_not_recovered         | no                      |         36 | 63.9%      | 25.9%           | 17.2%            | -15.5%       | 42.7%        | 14.8%        | 50.8%        |         4.07534 | -5.6%                    | no                    |
| immediate_1h_confirmation   | path_behavior      | no_sustained_reclaim_above_entry   | no                      |         68 | 83.8%      | 23.7%           | 22.3%            | 8.5%         | 42.7%        | 7.9%         | 56.7%        |         9.17875 | 19.2%                    | no                    |
| immediate_1h_confirmation   | path_behavior      | high_mfe_mae_asymmetry             | no                      |         77 | 80.5%      | 23.4%           | 20.7%            | 6.3%         | 42.7%        | 8.7%         | 55.1%        |         7.30073 | 17.4%                    | no                    |
| 24h_delay                   | path_behavior      | high_mfe_mae_asymmetry             | no                      |         71 | 71.8%      | 20.6%           | 18.7%            | -2.9%        | 42.7%        | 8.6%         | 60.2%        |         5.93859 | 16.9%                    | no                    |
| 24h_failed_recovery_trigger | scenario           | scenario_tag_not_recovered         | no                      |         29 | 65.5%      | 18.4%           | 17.3%            | -15.5%       | 42.7%        | 12.4%        | 49.7%        |         4.25431 | -6.3%                    | no                    |
| 24h_failed_recovery_trigger | path_behavior      | high_mfe_mae_asymmetry             | no                      |         52 | 71.2%      | 18.2%           | 18.2%            | -6.3%        | 42.7%        | 9.4%         | 57.4%        |         5.62237 | 16.2%                    | no                    |
| 24h_delay                   | path_behavior      | no_sustained_reclaim_above_entry   | no                      |         68 | 66.2%      | 18.2%           | 17.1%            | -15.5%       | 42.7%        | 9.4%         | 45.2%        |         5.02002 | -0.8%                    | no                    |
| immediate_1h_confirmation   | simple_combo       | combo_clean_negative_1h_no_reclaim | no                      |         22 | 77.3%      | 14.2%           | 17.2%            | 2.3%         | 42.7%        | 7.8%         | 51.7%        |         5.4772  | 11.5%                    | no                    |
| 24h_failed_recovery_trigger | scenario           | scenario_tag_followed_by_delisting | no                      |         60 | 53.3%      | 13.2%           | 12.4%            | -15.5%       | 42.7%        | 19.9%        | 47.2%        |         2.7614  | 9.6%                     | no                    |
| immediate_1h_confirmation   | path_behavior      | failed_rebound_24h                 | yes                     |         54 | 63.0%      | 11.8%           | 12.2%            | -16.9%       | 42.7%        | 17.9%        | 38.8%        |         2.95314 | 9.1%                     | no                    |
| 24h_failed_recovery_trigger | path_behavior      | no_sustained_reclaim_above_entry   | no                      |         59 | 62.7%      | 10.9%           | 15.4%            | -15.5%       | 42.7%        | 10.1%        | 42.8%        |         4.31374 | -2.1%                    | no                    |
| immediate_1h_confirmation   | data_quality_combo | clean_no_gap_no_fallback           | yes                     |         27 | 55.6%      | 10.7%           | 7.1%             | -16.9%       | 24.6%        | 18.6%        | 32.5%        |         1.94372 | -1.0%                    | no                    |
| immediate_1h_confirmation   | data_quality       | exclude_fallback_only_paths        | yes                     |         68 | 61.8%      | 10.3%           | 10.2%            | -16.9%       | 42.7%        | 17.6%        | 32.2%        |         2.58167 | -1.5%                    | no                    |
| immediate_1h_confirmation   | volatility         | avoid_extreme_initial_wick         | no                      |        106 | 58.5%      | 9.5%            | 9.9%             | -16.9%       | 42.7%        | 17.9%        | 36.5%        |         2.43705 | 7.3%                     | no                    |
| immediate_1h_confirmation   | data_quality       | exclude_true_data_gap_heavy        | yes                     |        101 | 56.4%      | 9.1%            | 10.3%            | -16.9%       | 42.7%        | 20.2%        | 43.0%        |         2.42206 | 6.8%                     | no                    |
| immediate_1h_confirmation   | path_behavior      | early_lower_low_after_tag          | no                      |         82 | 57.3%      | 9.0%            | 10.4%            | -16.9%       | 42.7%        | 20.2%        | 44.0%        |         2.44503 | 6.9%                     | no                    |
| immediate_1h_confirmation   | base               | base_all_monitoring                | yes                     |        117 | 56.4%      | 8.9%            | 9.5%             | -16.9%       | 42.7%        | 18.8%        | 37.7%        |         2.2995  | 6.4%                     | no                    |
| 24h_delay                   | simple_combo       | combo_clean_negative_1h_no_reclaim | no                      |         22 | 68.2%      | 8.2%            | 15.3%            | -2.8%        | 42.7%        | 8.6%         | 38.4%        |         5.12337 | -0.3%                    | no                    |
| 24h_failed_recovery_trigger | simple_combo       | combo_clean_negative_1h_no_reclaim | no                      |         20 | 65.0%      | 7.6%            | 13.7%            | -6.3%        | 42.7%        | 8.6%         | 38.4%        |         4.34971 | -1.9%                    | no                    |
| 24h_failed_recovery_trigger | data_quality       | exclude_true_data_gap_heavy        | yes                     |         68 | 52.9%      | 7.6%            | 11.1%            | -15.5%       | 42.7%        | 19.0%        | 42.7%        |         2.65434 | 8.6%                     | no                    |
| 24h_failed_recovery_trigger | path_behavior      | early_lower_low_after_tag          | no                      |         67 | 52.2%      | 7.2%            | 11.0%            | -15.5%       | 42.7%        | 18.3%        | 42.7%        |         2.72809 | 9.0%                     | no                    |
| 24h_delay                   | data_quality       | clean_only                         | yes                     |         55 | 56.4%      | 7.2%            | 10.9%            | -15.5%       | 42.7%        | 15.8%        | 33.8%        |         2.89825 | -3.3%                    | no                    |

## Diagnostic 7d Variants at 20 bps

| execution_variant             | filter_group   | filter_name                        | entry_feasible_filter   |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | median_mae   | median_mfe   |   profit_factor | average_return_ex_top5   | low_confidence_flag   |
|:------------------------------|:---------------|:-----------------------------------|:------------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:-------------|:-------------|----------------:|:-------------------------|:----------------------|
| 7d_delay_diagnostic           | path_behavior  | high_mfe_mae_asymmetry             | no                      |         64 | 56.2%      | 35.9%           | 33.6%            | -16.9%       | 81.6%        | 18.6%        | 230.3%       |         5.76682 | 16.3%                    | no                    |
| 7d_failed_recovery_diagnostic | path_behavior  | high_mfe_mae_asymmetry             | no                      |         49 | 51.0%      | 25.8%           | 29.1%            | -15.5%       | 81.6%        | 20.6%        | 326.1%       |         4.84737 | 12.1%                    | no                    |
| 7d_failed_recovery_diagnostic | scenario       | scenario_tag_not_recovered         | no                      |         32 | 40.6%      | -15.5%          | 22.7%            | -15.5%       | 81.6%        | 33.3%        | 123.1%       |         3.58843 | 3.1%                     | no                    |
| 7d_failed_recovery_diagnostic | path_behavior  | no_sustained_reclaim_above_entry   | no                      |         59 | 37.3%      | -15.5%          | 17.7%            | -15.5%       | 81.6%        | 37.4%        | 78.9%        |         2.87238 | 4.7%                     | no                    |
| 7d_failed_recovery_diagnostic | volatility     | high_post_tag_volatility           | no                      |         35 | 31.4%      | -15.5%          | 15.4%            | -15.5%       | 81.6%        | 58.7%        | 150.7%       |         2.50663 | 1.7%                     | no                    |
| 7d_failed_recovery_diagnostic | path_behavior  | failed_rebound_24h                 | yes                     |         38 | 34.2%      | -15.5%          | 14.2%            | -15.5%       | 71.7%        | 39.9%        | 78.0%        |         2.44257 | -1.0%                    | no                    |
| 7d_failed_recovery_diagnostic | simple_combo   | combo_delisting_path_negative_1h   | no                      |         54 | 29.6%      | -15.5%          | 13.2%            | -15.5%       | 81.6%        | 40.3%        | 124.3%       |         2.24533 | -2.3%                    | no                    |
| 7d_failed_recovery_diagnostic | volatility     | avoid_extreme_initial_wick         | no                      |         75 | 32.0%      | -15.5%          | 12.5%            | -15.5%       | 61.0%        | 45.0%        | 70.4%        |         2.21331 | -0.6%                    | no                    |
| 7d_failed_recovery_diagnostic | data_quality   | clean_only                         | yes                     |         37 | 35.1%      | -15.5%          | 12.5%            | -15.5%       | 42.1%        | 42.8%        | 52.5%        |         2.24954 | 1.7%                     | no                    |
| 7d_failed_recovery_diagnostic | scenario       | scenario_tag_followed_by_delisting | no                      |         70 | 30.0%      | -15.5%          | 12.1%            | -15.5%       | 77.6%        | 45.8%        | 118.9%       |         2.13856 | -2.3%                    | no                    |
| 7d_failed_recovery_diagnostic | path_behavior  | early_lower_low_after_tag          | no                      |         65 | 29.2%      | -15.5%          | 10.8%            | -15.5%       | 42.1%        | 45.7%        | 121.8%       |         2.00857 | -2.0%                    | no                    |
| 7d_failed_recovery_diagnostic | data_quality   | exclude_benchmark_gap_heavy        | yes                     |         85 | 29.4%      | -15.5%          | 10.4%            | -15.5%       | 42.1%        | 46.6%        | 78.9%        |         1.96594 | -1.3%                    | no                    |

## Candidate Ranking

| execution_variant           | filter_group   | filter_name                 | entry_feasible_filter   |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | median_mae   | median_mfe   |   profit_factor | average_return_ex_top5   | low_confidence_flag   |
|:----------------------------|:---------------|:----------------------------|:------------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:-------------|:-------------|----------------:|:-------------------------|:----------------------|
| immediate_1h_confirmation   | path_behavior  | negative_1h_confirmation    | yes                     |         89 | 56.2%      | 7.1%            | 8.9%             | -16.9%       | 42.7%        | 21.3%        | 38.3%        |         2.19979 | 5.5%                     | no                    |
| 24h_delay                   | path_behavior  | negative_1h_confirmation    | yes                     |         89 | 50.6%      | 1.0%            | 9.1%             | -15.5%       | 42.7%        | 22.5%        | 38.3%        |         2.28885 | 7.1%                     | no                    |
| 24h_failed_recovery_trigger | path_behavior  | negative_1h_confirmation    | yes                     |         64 | 51.6%      | 4.1%            | 9.8%             | -15.5%       | 42.7%        | 19.0%        | 42.7%        |         2.46101 | 7.6%                     | no                    |
| immediate_1h_confirmation   | data_quality   | exclude_benchmark_gap_heavy | yes                     |        110 | 53.6%      | 5.9%            | 9.2%             | -16.9%       | 42.7%        | 21.6%        | 41.2%        |         2.18637 | 5.8%                     | no                    |
| immediate_1h_confirmation   | data_quality   | exclude_true_data_gap_heavy | yes                     |        101 | 56.4%      | 9.1%            | 10.3%            | -16.9%       | 42.7%        | 20.2%        | 43.0%        |         2.42206 | 6.8%                     | no                    |
| 24h_delay                   | data_quality   | exclude_true_data_gap_heavy | yes                     |        101 | 51.5%      | 3.9%            | 10.4%            | -15.5%       | 42.7%        | 20.4%        | 42.7%        |         2.48987 | 8.4%                     | no                    |
| 24h_failed_recovery_trigger | data_quality   | exclude_benchmark_gap_heavy | yes                     |         74 | 51.4%      | 5.5%            | 10.5%            | -15.5%       | 42.7%        | 19.7%        | 42.7%        |         2.50267 | 8.2%                     | no                    |
| 24h_failed_recovery_trigger | data_quality   | exclude_true_data_gap_heavy | yes                     |         68 | 52.9%      | 7.6%            | 11.1%            | -15.5%       | 42.7%        | 19.0%        | 42.7%        |         2.65434 | 8.6%                     | no                    |
| immediate_1h_confirmation   | data_quality   | clean_only                  | yes                     |         55 | 54.5%      | 6.3%            | 7.0%             | -16.9%       | 29.6%        | 13.2%        | 36.3%        |         1.93669 | 3.5%                     | no                    |
| 24h_failed_recovery_trigger | data_quality   | clean_only                  | yes                     |         29 | 55.2%      | 4.4%            | 10.1%            | -15.5%       | 42.7%        | 10.1%        | 33.9%        |         2.83071 | 7.7%                     | no                    |
| immediate_1h_confirmation   | data_quality   | exclude_fallback_only_paths | yes                     |         68 | 61.8%      | 10.3%           | 10.2%            | -16.9%       | 42.7%        | 17.6%        | 32.2%        |         2.58167 | -1.5%                    | no                    |
| 24h_delay                   | data_quality   | clean_only                  | yes                     |         55 | 56.4%      | 7.2%            | 10.9%            | -15.5%       | 42.7%        | 15.8%        | 33.8%        |         2.89825 | -3.3%                    | no                    |

## Cost Sensitivity Snapshot

| execution_variant           | filter_name                        |   cost_bps |   n_trades | median_return   | average_return   |   profit_factor | low_confidence_flag   |
|:----------------------------|:-----------------------------------|-----------:|-----------:|:----------------|:-----------------|----------------:|:----------------------|
| 24h_delay                   | base_all_monitoring                |          0 |        117 | 1.2%            | 9.4%             |         2.37225 | no                    |
| 24h_delay                   | base_all_monitoring                |         20 |        117 | 1.0%            | 9.2%             |         2.32411 | no                    |
| 24h_delay                   | base_all_monitoring                |         50 |        117 | 0.7%            | 8.9%             |         2.25441 | no                    |
| 24h_delay                   | base_all_monitoring                |        100 |        117 | 0.2%            | 8.4%             |         2.14449 | no                    |
| 24h_delay                   | clean_only                         |          0 |         55 | 7.4%            | 11.1%            |         2.96275 | no                    |
| 24h_delay                   | clean_only                         |         20 |         55 | 7.2%            | 10.9%            |         2.89825 | no                    |
| 24h_delay                   | clean_only                         |         50 |         55 | 6.9%            | 10.6%            |         2.80508 | no                    |
| 24h_delay                   | clean_only                         |        100 |         55 | 6.4%            | 10.1%            |         2.65868 | no                    |
| 24h_delay                   | combo_clean_negative_1h_no_reclaim |          0 |         22 | 8.4%            | 15.5%            |         5.24995 | no                    |
| 24h_delay                   | combo_clean_negative_1h_no_reclaim |         20 |         22 | 8.2%            | 15.3%            |         5.12337 | no                    |
| 24h_delay                   | combo_clean_negative_1h_no_reclaim |         50 |         22 | 7.9%            | 15.0%            |         4.94143 | no                    |
| 24h_delay                   | combo_clean_negative_1h_no_reclaim |        100 |         22 | 7.4%            | 14.5%            |         4.65763 | no                    |
| 24h_failed_recovery_trigger | base_all_monitoring                |          0 |         79 | 4.6%            | 10.4%            |         2.59437 | no                    |
| 24h_failed_recovery_trigger | base_all_monitoring                |         20 |         79 | 4.4%            | 10.2%            |         2.54075 | no                    |
| 24h_failed_recovery_trigger | base_all_monitoring                |         50 |         79 | 4.1%            | 9.9%             |         2.4632  | no                    |
| 24h_failed_recovery_trigger | base_all_monitoring                |        100 |         79 | 3.6%            | 9.4%             |         2.34107 | no                    |
| 24h_failed_recovery_trigger | clean_only                         |          0 |         29 | 4.6%            | 10.3%            |         2.89796 | no                    |
| 24h_failed_recovery_trigger | clean_only                         |         20 |         29 | 4.4%            | 10.1%            |         2.83071 | no                    |
| 24h_failed_recovery_trigger | clean_only                         |         50 |         29 | 4.1%            | 9.8%             |         2.73385 | no                    |
| 24h_failed_recovery_trigger | clean_only                         |        100 |         29 | 3.6%            | 9.3%             |         2.58229 | no                    |
| 24h_failed_recovery_trigger | combo_clean_negative_1h_no_reclaim |          0 |         20 | 7.8%            | 13.9%            |         4.45783 | no                    |
| 24h_failed_recovery_trigger | combo_clean_negative_1h_no_reclaim |         20 |         20 | 7.6%            | 13.7%            |         4.34971 | no                    |
| 24h_failed_recovery_trigger | combo_clean_negative_1h_no_reclaim |         50 |         20 | 7.3%            | 13.4%            |         4.19429 | no                    |
| 24h_failed_recovery_trigger | combo_clean_negative_1h_no_reclaim |        100 |         20 | 6.8%            | 12.9%            |         3.95187 | no                    |
| immediate_1h_confirmation   | base_all_monitoring                |          0 |        117 | 9.1%            | 9.7%             |         2.34307 | no                    |
| immediate_1h_confirmation   | base_all_monitoring                |         20 |        117 | 8.9%            | 9.5%             |         2.2995  | no                    |
| immediate_1h_confirmation   | base_all_monitoring                |         50 |        117 | 8.6%            | 9.2%             |         2.23605 | no                    |
| immediate_1h_confirmation   | base_all_monitoring                |        100 |        117 | 8.1%            | 8.7%             |         2.13515 | no                    |
| immediate_1h_confirmation   | clean_only                         |          0 |         55 | 6.5%            | 7.2%             |         1.97515 | no                    |
| immediate_1h_confirmation   | clean_only                         |         20 |         55 | 6.3%            | 7.0%             |         1.93669 | no                    |
| immediate_1h_confirmation   | clean_only                         |         50 |         55 | 6.0%            | 6.7%             |         1.88071 | no                    |
| immediate_1h_confirmation   | clean_only                         |        100 |         55 | 5.5%            | 6.2%             |         1.79173 | no                    |
| immediate_1h_confirmation   | combo_clean_negative_1h_no_reclaim |          0 |         22 | 14.4%           | 17.4%            |         5.58372 | no                    |
| immediate_1h_confirmation   | combo_clean_negative_1h_no_reclaim |         20 |         22 | 14.2%           | 17.2%            |         5.4772  | no                    |
| immediate_1h_confirmation   | combo_clean_negative_1h_no_reclaim |         50 |         22 | 13.9%           | 16.9%            |         5.32206 | no                    |
| immediate_1h_confirmation   | combo_clean_negative_1h_no_reclaim |        100 |         22 | 13.4%           | 16.4%            |         5.07521 | no                    |

## Interpretation

- Prefer candidates with positive median return, positive average return after excluding top 5%, profit factor above 1, and median MFE greater than median MAE.
- A high average with negative median is treated as tail-dependent rather than robust.
- Clean-only filters are especially important because low-sensitivity rows can include fallback-heavy or gap-heavy paths.
- Scenario filters such as tag followed by delisting are informative but can be partly ex-post; use them for archetype research, not direct entry rules unless their components are observable at entry time.

## Next Step

Backtest only the recommended candidate and one conservative baseline with explicit live-feasibility assumptions: borrow availability, market impact, maximum borrow cost, and no-entry rules during exchange maintenance or abnormal gaps.
