# Monitoring Perp Subset Diagnostics

Generated at UTC: 2026-05-27T12:02:25.873410+00:00

Scope: diagnostics only for Monitoring Tag `immediate_1h_confirmation + negative_1h_confirmation`. No new optimized strategy is introduced.

## Main Distribution Comparison at 100 bps

| comparison_group                          |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | avg_ex_top5   | avg_ex_bottom5   |   profit_factor | median_mae   | median_mfe   |   median_quote_volume_24h | median_return_1h   | low_liquidity_rate   | abnormal_gap_rate   | extreme_wick_gap_rate   | clustered_rate   | funding_available_rate   | oi_available_rate   |
|:------------------------------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:--------------|:-----------------|----------------:|:-------------|:-------------|--------------------------:|:-------------------|:---------------------|:--------------------|:------------------------|:-----------------|:-------------------------|:--------------------|
| A_full_confirmed_or_inferred_binance_perp |         52 | 48.1%      | -17.7%          | 5.2%             | -17.7%       | 41.9%        | 1.3%          | 7.6%             |         1.56527 | 26.9%        | 38.8%        |               3.04882e+06 | -2.0%              | 30.8%                | 9.6%                | 3.8%                    | 7.7%             | 98.1%                    | 13.5%               |
| B_medium_feasibility_confirmed_shortable  |         30 | 56.7%      | 11.0%           | 9.8%             | -17.7%       | 41.9%        | 6.2%          | 12.8%            |         2.27366 | 12.8%        | 37.0%        |               4.62315e+06 | -1.9%              | 0.0%                 | 0.0%                | 0.0%                    | 6.7%             | 100.0%                   | 20.0%               |
| C_no_binance_perp_evidence                |         37 | 67.6%      | 10.5%           | 12.1%            | -17.7%       | 41.9%        | 9.5%          | 15.7%            |         3.11505 | 18.1%        | 38.2%        |               2.25411e+06 | -3.4%              | 16.2%                | 8.1%                | 8.1%                    | 0.0%             | 0.0%                     | 0.0%                |

## Feasibility Split

| comparison_group                          | feasibility_tier   |   n_trades | win_rate   | median_return   | average_return   | median_mae   | median_mfe   |   median_quote_volume_24h | low_liquidity_rate   | abnormal_gap_rate   |
|:------------------------------------------|:-------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|--------------------------:|:---------------------|:--------------------|
| A_full_confirmed_or_inferred_binance_perp | low                |         22 | 36.4%      | -17.7%          | -1.0%            | 34.8%        | 44.5%        |          935920           | 72.7%                | 22.7%               |
| A_full_confirmed_or_inferred_binance_perp | medium             |         30 | 56.7%      | 11.0%           | 9.8%             | 12.8%        | 37.0%        |               4.62315e+06 | 0.0%                 | 0.0%                |
| B_medium_feasibility_confirmed_shortable  | medium             |         30 | 56.7%      | 11.0%           | 9.8%             | 12.8%        | 37.0%        |               4.62315e+06 | 0.0%                 | 0.0%                |
| C_no_binance_perp_evidence                | low                |         12 | 50.0%      | -5.7%           | 4.5%             | 26.1%        | 45.2%        |               1.54653e+06 | 50.0%                | 25.0%               |
| C_no_binance_perp_evidence                | medium             |         25 | 76.0%      | 16.3%           | 15.8%            | 17.3%        | 38.2%        |               2.39167e+06 | 0.0%                 | 0.0%                |

## Scenario Split

| comparison_group                          | primary_scenario                     |   n_trades | win_rate   | median_return   | average_return   | median_mae   | median_mfe   | low_liquidity_rate   |
|:------------------------------------------|:-------------------------------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:---------------------|
| A_full_confirmed_or_inferred_binance_perp | TAG_TO_DELISTING_TO_COLLAPSE         |         25 | 40.0%      | -17.7%          | 4.5%             | 24.5%        | 50.6%        | 32.0%                |
| A_full_confirmed_or_inferred_binance_perp | NO_CLEAR_REACTION                    |          8 | 50.0%      | -2.5%           | 1.3%             | 20.2%        | 18.8%        | 50.0%                |
| A_full_confirmed_or_inferred_binance_perp | DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |          7 | 57.1%      | 0.7%            | 10.5%            | 29.8%        | 57.6%        | 28.6%                |
| A_full_confirmed_or_inferred_binance_perp | TAG_REMOVED_AND_RECOVERED            |          4 | 75.0%      | 25.9%           | 19.0%            | 24.0%        | 43.5%        | 25.0%                |
| A_full_confirmed_or_inferred_binance_perp | IMMEDIATE_DUMP_AFTER_TAG             |          3 | 100.0%     | 22.6%           | 18.7%            | 1.5%         | 26.4%        | 0.0%                 |
| A_full_confirmed_or_inferred_binance_perp | SLOW_BLEED_AFTER_TAG                 |          2 | 50.0%      | -3.1%           | -3.1%            | 30.3%        | 22.5%        | 0.0%                 |
| A_full_confirmed_or_inferred_binance_perp | TEMPORARY_PANIC_THEN_RECOVERY        |          2 | 0.0%       | -17.7%          | -17.7%           | 44.4%        | 48.1%        | 50.0%                |
| A_full_confirmed_or_inferred_binance_perp | TAG_REMOVED_BUT_NOT_RECOVERED        |          1 | 0.0%       | -17.7%          | -17.7%           | 33.3%        | 52.9%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | TAG_TO_DELISTING_TO_COLLAPSE         |         12 | 41.7%      | -17.7%          | 7.1%             | 20.7%        | 41.8%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |          4 | 75.0%      | 41.9%           | 27.0%            | 21.1%        | 121.3%       | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | NO_CLEAR_REACTION                    |          4 | 75.0%      | 17.6%           | 12.6%            | 6.2%         | 22.2%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | IMMEDIATE_DUMP_AFTER_TAG             |          3 | 100.0%     | 22.6%           | 18.7%            | 1.5%         | 26.4%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | TAG_REMOVED_AND_RECOVERED            |          3 | 66.7%      | 9.9%            | 11.4%            | 13.2%        | 32.3%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | SLOW_BLEED_AFTER_TAG                 |          2 | 50.0%      | -3.1%           | -3.1%            | 30.3%        | 22.5%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | TAG_REMOVED_BUT_NOT_RECOVERED        |          1 | 0.0%       | -17.7%          | -17.7%           | 33.3%        | 52.9%        | 0.0%                 |
| B_medium_feasibility_confirmed_shortable  | TEMPORARY_PANIC_THEN_RECOVERY        |          1 | 0.0%       | -17.7%          | -17.7%           | 54.0%        | 51.5%        | 0.0%                 |
| C_no_binance_perp_evidence                | TAG_TO_DELISTING_TO_COLLAPSE         |         26 | 65.4%      | 11.0%           | 12.1%            | 19.5%        | 43.7%        | 7.7%                 |
| C_no_binance_perp_evidence                | DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |          5 | 80.0%      | 41.9%           | 25.3%            | 11.5%        | 68.6%        | 0.0%                 |
| C_no_binance_perp_evidence                | TEMPORARY_PANIC_THEN_RECOVERY        |          2 | 50.0%      | -5.7%           | -5.7%            | 167.5%       | 13.0%        | 100.0%               |
| C_no_binance_perp_evidence                | IMMEDIATE_DUMP_AFTER_TAG             |          1 | 100.0%     | 4.0%            | 4.0%             | 8.2%         | 15.4%        | 0.0%                 |
| C_no_binance_perp_evidence                | NO_CLEAR_REACTION                    |          1 | 0.0%       | -17.7%          | -17.7%           | 66.3%        | 54.1%        | 100.0%               |
| C_no_binance_perp_evidence                | SLOW_BLEED_AFTER_TAG                 |          1 | 100.0%     | 21.7%           | 21.7%            | 0.5%         | 36.3%        | 100.0%               |
| C_no_binance_perp_evidence                | TAG_REMOVED_AND_RECOVERED            |          1 | 100.0%     | 10.5%           | 10.5%            | 2.8%         | 13.8%        | 0.0%                 |

## Time Split

| comparison_group                          | event_half   |   n_trades | win_rate   | median_return   | average_return   | median_mae   | median_mfe   | funding_available_rate   |
|:------------------------------------------|:-------------|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:-------------------------|
| A_full_confirmed_or_inferred_binance_perp | 2024H1       |          5 | 60.0%      | 9.9%            | 11.7%            | 4.2%         | 32.3%        | 100.0%                   |
| A_full_confirmed_or_inferred_binance_perp | 2024H2       |          5 | 60.0%      | 0.7%            | 9.8%             | 20.2%        | 37.7%        | 100.0%                   |
| A_full_confirmed_or_inferred_binance_perp | 2025H1       |         17 | 35.3%      | -17.7%          | 1.0%             | 44.1%        | 50.9%        | 100.0%                   |
| A_full_confirmed_or_inferred_binance_perp | 2025H2       |          1 | 0.0%       | -17.7%          | -17.7%           | 32.7%        | 35.6%        | 100.0%                   |
| A_full_confirmed_or_inferred_binance_perp | 2026YTD      |         24 | 54.2%      | 11.0%           | 6.8%             | 19.0%        | 35.4%        | 95.8%                    |
| B_medium_feasibility_confirmed_shortable  | 2024H1       |          4 | 75.0%      | 25.9%           | 19.0%            | 3.8%         | 49.4%        | 100.0%                   |
| B_medium_feasibility_confirmed_shortable  | 2024H2       |          3 | 33.3%      | -17.7%          | 2.2%             | 20.2%        | 30.5%        | 100.0%                   |
| B_medium_feasibility_confirmed_shortable  | 2025H1       |         11 | 36.4%      | -17.7%          | 4.0%             | 36.4%        | 51.5%        | 100.0%                   |
| B_medium_feasibility_confirmed_shortable  | 2025H2       |          1 | 0.0%       | -17.7%          | -17.7%           | 32.7%        | 35.6%        | 100.0%                   |
| B_medium_feasibility_confirmed_shortable  | 2026YTD      |         11 | 81.8%      | 21.2%           | 16.7%            | 2.4%         | 26.4%        | 100.0%                   |
| C_no_binance_perp_evidence                | 2023H2       |          3 | 66.7%      | 0.3%            | -3.0%            | 13.4%        | 25.1%        | 0.0%                     |
| C_no_binance_perp_evidence                | 2024H1       |          6 | 100.0%     | 20.6%           | 24.6%            | 6.3%         | 32.7%        | 0.0%                     |
| C_no_binance_perp_evidence                | 2024H2       |         10 | 90.0%      | 41.9%           | 30.7%            | 20.0%        | 51.4%        | 0.0%                     |
| C_no_binance_perp_evidence                | 2025H1       |          9 | 33.3%      | -17.7%          | -1.6%            | 30.3%        | 470.9%       | 0.0%                     |
| C_no_binance_perp_evidence                | 2025H2       |          2 | 50.0%      | -2.0%           | -2.0%            | 44.5%        | 23.2%        | 0.0%                     |
| C_no_binance_perp_evidence                | 2026YTD      |          7 | 57.1%      | 4.0%            | 3.0%             | 8.2%         | 36.3%        | 0.0%                     |

## What Kills The Full Confirmed Perp Subset

- The full confirmed/inferred Binance perp subset is dragged down mainly by low-feasibility names: confirmed shortable but poor liquidity/gap/wick profile.
- Confirmed/inferred subset size is 52; the medium-feasibility core is 30, while low-feasibility confirmed rows are 22.
- Median 100 bps return: confirmed full -17.7%, medium-feasibility confirmed 11.0%, no-perp-evidence 10.5%.
- The no-perp-evidence group has stronger spot returns but remains an execution question, not a tradable Binance-perp result.
- OI availability is sparse and should be treated as a data-coverage marker, not a validated filter yet.

## Candidate Filters For Future Testing

- Liquidity floor candidate: exclude `low_liquidity_flag=yes`; this is entry-time observable via recent spot volume.
- Wick/gap exclusion: exclude `extreme_first_hour_wick_gap=yes` and `abnormal_candle_gap=yes`; these are available by confirmation time.
- Feasibility tier filter: require `feasibility_tier in {medium, high}` before treating Binance-perp subset as executable.
- Funding/OI availability: funding confirms perp existence, but OI coverage is too sparse for a robust filter in v1.
- Avoid using `scenario` as an entry filter unless decomposed into observable features; scenario labels are mostly ex-post diagnostics.

## Caveats

- This report uses 100 bps cost view for diagnostics.
- Derivatives availability is based on public Binance futures klines/funding/OI API results around entry.
- Some symbols may have venue-specific execution constraints not captured by OHLCV.
- No-perp-evidence rows can still be shortable via borrow or other venues, but that is not proven here.
- Candidate filters are hypotheses for later testing, not optimized rules.
