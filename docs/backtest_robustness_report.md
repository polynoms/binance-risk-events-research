# Backtest Robustness Report v1

Generated at UTC: 2026-05-27T08:36:50.684053+00:00

This is diagnostic robustness validation only. It does not optimize rules, add filters, or claim live tradability.

## Scope

- Base trade rows at source costs: 1010
- Expanded cost-view rows: 2020
- Cost views: 0, 20, 50, 100 bps roundtrip.
- Time splits: 2023H2, 2024H1, 2024H2, 2025H1, 2025H2, 2026YTD.
- De-clustering: first trade per hypothesis/sub-strategy/token/day/cost and first trade per event family.

## Robustness Verdicts

| hypothesis_family                 | sub_strategy                |   n_trades_20bps |   median_return_20bps |   average_return_20bps |   profit_factor_20bps |   avg_ex_top5_20bps |   declustered_avg_20bps | robustness_verdict   |
|:----------------------------------|:----------------------------|-----------------:|----------------------:|-----------------------:|----------------------:|--------------------:|------------------------:|:---------------------|
| monitoring_tag                    | tag_immediate_1h            |              117 |            0.0892672  |              0.0945541 |               2.2995  |          0.0635244  |               0.0945541 | robust_candidate     |
| monitoring_tag                    | tag_24h_delay               |              117 |            0.00980209 |              0.0924302 |               2.32411 |          0.0743685  |               0.0924302 | robust_candidate     |
| spot_delisting_announcement_shock | rebound_failure_24h_hold30  |               14 |           -0.132435   |              0.0608988 |               1.70362 |         -0.0111859  |               0.0608988 | small_sample         |
| spot_delisting_announcement_shock | rebound_failure_24h         |               14 |           -0.109143   |              0.0559352 |               1.89118 |         -0.0451475  |               0.0559352 | small_sample         |
| pump_fade                         | pump20_failed_breakout_fade |               29 |           -0.0824322  |              0.213877  |               3.53807 |          0.180485   |               0.213877  | tail_dependent       |
| spot_delisting_announcement_shock | immediate_1h_confirmation   |               20 |            0.218928   |              0.144306  |               3.07503 |         -0.13796    |               0.144306  | tail_dependent       |
| monitoring_tag                    | tag_7d_delay                |              108 |           -0.168667   |              0.131956  |               2.20806 |          0.00413373 |               0.131956  | tail_dependent       |
| monitoring_tag                    | failed_recovery_7d_trigger  |               86 |           -0.154542   |              0.100921  |               1.93327 |         -0.0150674  |               0.100921  | tail_dependent       |

## Cost Sensitivity

| sample_type   | hypothesis_family                 | sub_strategy                |   robust_cost_bps |   n_trades |   win_rate |   median_return |   average_return |   profit_factor |   median_mae |   median_mfe |
|:--------------|:----------------------------------|:----------------------------|------------------:|-----------:|-----------:|----------------:|-----------------:|----------------:|-------------:|-------------:|
| raw           | monitoring_tag                    | failed_recovery_7d_trigger  |                 0 |         86 |   0.290698 |     -0.152542   |        0.102921  |         1.96442 |     0.477701 |     0.75     |
| raw           | monitoring_tag                    | failed_recovery_7d_trigger  |                20 |         86 |   0.290698 |     -0.154542   |        0.100921  |         1.93327 |     0.477701 |     0.75     |
| raw           | monitoring_tag                    | failed_recovery_7d_trigger  |                50 |         86 |   0.290698 |     -0.157542   |        0.0979209 |         1.88805 |     0.477701 |     0.75     |
| raw           | monitoring_tag                    | failed_recovery_7d_trigger  |               100 |         86 |   0.290698 |     -0.162542   |        0.0929209 |         1.81645 |     0.477701 |     0.75     |
| raw           | monitoring_tag                    | tag_24h_delay               |                 0 |        117 |   0.504274 |      0.0118021  |        0.0944302 |         2.37225 |     0.200333 |     0.376667 |
| raw           | monitoring_tag                    | tag_24h_delay               |                20 |        117 |   0.504274 |      0.00980209 |        0.0924302 |         2.32411 |     0.200333 |     0.376667 |
| raw           | monitoring_tag                    | tag_24h_delay               |                50 |        117 |   0.504274 |      0.00680209 |        0.0894302 |         2.25441 |     0.200333 |     0.376667 |
| raw           | monitoring_tag                    | tag_24h_delay               |               100 |        117 |   0.504274 |      0.00180209 |        0.0844302 |         2.14449 |     0.200333 |     0.376667 |
| raw           | monitoring_tag                    | tag_7d_delay                |                 0 |        108 |   0.333333 |     -0.166667   |        0.133956  |         2.24153 |     0.453462 |     0.783095 |
| raw           | monitoring_tag                    | tag_7d_delay                |                20 |        108 |   0.333333 |     -0.168667   |        0.131956  |         2.20806 |     0.453462 |     0.783095 |
| raw           | monitoring_tag                    | tag_7d_delay                |                50 |        108 |   0.333333 |     -0.171667   |        0.128956  |         2.15937 |     0.453462 |     0.783095 |
| raw           | monitoring_tag                    | tag_7d_delay                |               100 |        108 |   0.333333 |     -0.176667   |        0.123956  |         2.08199 |     0.453462 |     0.783095 |
| raw           | monitoring_tag                    | tag_immediate_1h            |                 0 |        117 |   0.564103 |      0.0912672  |        0.0965541 |         2.34307 |     0.188174 |     0.377217 |
| raw           | monitoring_tag                    | tag_immediate_1h            |                20 |        117 |   0.564103 |      0.0892672  |        0.0945541 |         2.2995  |     0.188174 |     0.377217 |
| raw           | monitoring_tag                    | tag_immediate_1h            |                50 |        117 |   0.564103 |      0.0862672  |        0.0915541 |         2.23605 |     0.188174 |     0.377217 |
| raw           | monitoring_tag                    | tag_immediate_1h            |               100 |        117 |   0.564103 |      0.0812672  |        0.0865541 |         2.13515 |     0.188174 |     0.377217 |
| raw           | pump_fade                         | pump20_failed_breakout_fade |                 0 |         29 |   0.482759 |     -0.0804322  |        0.215877  |         3.59364 |     0.228261 |     0.732026 |
| raw           | pump_fade                         | pump20_failed_breakout_fade |                20 |         29 |   0.482759 |     -0.0824322  |        0.213877  |         3.53807 |     0.228261 |     0.732026 |
| raw           | pump_fade                         | pump20_failed_breakout_fade |                50 |         29 |   0.482759 |     -0.0854322  |        0.210877  |         3.45722 |     0.228261 |     0.732026 |
| raw           | pump_fade                         | pump20_failed_breakout_fade |               100 |         29 |   0.482759 |     -0.0904322  |        0.205877  |         3.32878 |     0.228261 |     0.732026 |
| raw           | spot_delisting_announcement_shock | immediate_1h_confirmation   |                 0 |         20 |   0.55     |      0.220928   |        0.146306  |         3.13137 |     0.257823 |     0.550233 |
| raw           | spot_delisting_announcement_shock | immediate_1h_confirmation   |                20 |         20 |   0.55     |      0.218928   |        0.144306  |         3.07503 |     0.257823 |     0.550233 |
| raw           | spot_delisting_announcement_shock | immediate_1h_confirmation   |                50 |         20 |   0.55     |      0.215928   |        0.141306  |         2.9932  |     0.257823 |     0.550233 |
| raw           | spot_delisting_announcement_shock | immediate_1h_confirmation   |               100 |         20 |   0.55     |      0.210928   |        0.136306  |         2.86353 |     0.257823 |     0.550233 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h         |                 0 |         14 |   0.357143 |     -0.107143   |        0.0579352 |         1.94235 |     0.323587 |     0.535677 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h         |                20 |         14 |   0.357143 |     -0.109143   |        0.0559352 |         1.89118 |     0.323587 |     0.535677 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h         |                50 |         14 |   0.357143 |     -0.112143   |        0.0529352 |         1.81824 |     0.323587 |     0.535677 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h         |               100 |         14 |   0.357143 |     -0.117143   |        0.0479352 |         1.70588 |     0.323587 |     0.535677 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                 0 |         14 |   0.285714 |     -0.130435   |        0.0628988 |         1.73892 |     0.323587 |     0.747575 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                20 |         14 |   0.285714 |     -0.132435   |        0.0608988 |         1.70362 |     0.323587 |     0.747575 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                50 |         14 |   0.285714 |     -0.135435   |        0.0578988 |         1.65279 |     0.323587 |     0.747575 |
| raw           | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |               100 |         14 |   0.285714 |     -0.140435   |        0.0528988 |         1.57333 |     0.323587 |     0.747575 |
| declustered   | monitoring_tag                    | failed_recovery_7d_trigger  |                 0 |         86 |   0.290698 |     -0.152542   |        0.102921  |         1.96442 |     0.477701 |     0.75     |
| declustered   | monitoring_tag                    | failed_recovery_7d_trigger  |                20 |         86 |   0.290698 |     -0.154542   |        0.100921  |         1.93327 |     0.477701 |     0.75     |
| declustered   | monitoring_tag                    | failed_recovery_7d_trigger  |                50 |         86 |   0.290698 |     -0.157542   |        0.0979209 |         1.88805 |     0.477701 |     0.75     |
| declustered   | monitoring_tag                    | failed_recovery_7d_trigger  |               100 |         86 |   0.290698 |     -0.162542   |        0.0929209 |         1.81645 |     0.477701 |     0.75     |
| declustered   | monitoring_tag                    | tag_24h_delay               |                 0 |        117 |   0.504274 |      0.0118021  |        0.0944302 |         2.37225 |     0.200333 |     0.376667 |
| declustered   | monitoring_tag                    | tag_24h_delay               |                20 |        117 |   0.504274 |      0.00980209 |        0.0924302 |         2.32411 |     0.200333 |     0.376667 |
| declustered   | monitoring_tag                    | tag_24h_delay               |                50 |        117 |   0.504274 |      0.00680209 |        0.0894302 |         2.25441 |     0.200333 |     0.376667 |
| declustered   | monitoring_tag                    | tag_24h_delay               |               100 |        117 |   0.504274 |      0.00180209 |        0.0844302 |         2.14449 |     0.200333 |     0.376667 |
| declustered   | monitoring_tag                    | tag_7d_delay                |                 0 |        108 |   0.333333 |     -0.166667   |        0.133956  |         2.24153 |     0.453462 |     0.783095 |
| declustered   | monitoring_tag                    | tag_7d_delay                |                20 |        108 |   0.333333 |     -0.168667   |        0.131956  |         2.20806 |     0.453462 |     0.783095 |
| declustered   | monitoring_tag                    | tag_7d_delay                |                50 |        108 |   0.333333 |     -0.171667   |        0.128956  |         2.15937 |     0.453462 |     0.783095 |
| declustered   | monitoring_tag                    | tag_7d_delay                |               100 |        108 |   0.333333 |     -0.176667   |        0.123956  |         2.08199 |     0.453462 |     0.783095 |
| declustered   | monitoring_tag                    | tag_immediate_1h            |                 0 |        117 |   0.564103 |      0.0912672  |        0.0965541 |         2.34307 |     0.188174 |     0.377217 |
| declustered   | monitoring_tag                    | tag_immediate_1h            |                20 |        117 |   0.564103 |      0.0892672  |        0.0945541 |         2.2995  |     0.188174 |     0.377217 |
| declustered   | monitoring_tag                    | tag_immediate_1h            |                50 |        117 |   0.564103 |      0.0862672  |        0.0915541 |         2.23605 |     0.188174 |     0.377217 |
| declustered   | monitoring_tag                    | tag_immediate_1h            |               100 |        117 |   0.564103 |      0.0812672  |        0.0865541 |         2.13515 |     0.188174 |     0.377217 |
| declustered   | pump_fade                         | pump20_failed_breakout_fade |                 0 |         29 |   0.482759 |     -0.0804322  |        0.215877  |         3.59364 |     0.228261 |     0.732026 |
| declustered   | pump_fade                         | pump20_failed_breakout_fade |                20 |         29 |   0.482759 |     -0.0824322  |        0.213877  |         3.53807 |     0.228261 |     0.732026 |
| declustered   | pump_fade                         | pump20_failed_breakout_fade |                50 |         29 |   0.482759 |     -0.0854322  |        0.210877  |         3.45722 |     0.228261 |     0.732026 |
| declustered   | pump_fade                         | pump20_failed_breakout_fade |               100 |         29 |   0.482759 |     -0.0904322  |        0.205877  |         3.32878 |     0.228261 |     0.732026 |
| declustered   | spot_delisting_announcement_shock | immediate_1h_confirmation   |                 0 |         20 |   0.55     |      0.220928   |        0.146306  |         3.13137 |     0.257823 |     0.550233 |
| declustered   | spot_delisting_announcement_shock | immediate_1h_confirmation   |                20 |         20 |   0.55     |      0.218928   |        0.144306  |         3.07503 |     0.257823 |     0.550233 |
| declustered   | spot_delisting_announcement_shock | immediate_1h_confirmation   |                50 |         20 |   0.55     |      0.215928   |        0.141306  |         2.9932  |     0.257823 |     0.550233 |
| declustered   | spot_delisting_announcement_shock | immediate_1h_confirmation   |               100 |         20 |   0.55     |      0.210928   |        0.136306  |         2.86353 |     0.257823 |     0.550233 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h         |                 0 |         14 |   0.357143 |     -0.107143   |        0.0579352 |         1.94235 |     0.323587 |     0.535677 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h         |                20 |         14 |   0.357143 |     -0.109143   |        0.0559352 |         1.89118 |     0.323587 |     0.535677 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h         |                50 |         14 |   0.357143 |     -0.112143   |        0.0529352 |         1.81824 |     0.323587 |     0.535677 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h         |               100 |         14 |   0.357143 |     -0.117143   |        0.0479352 |         1.70588 |     0.323587 |     0.535677 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                 0 |         14 |   0.285714 |     -0.130435   |        0.0628988 |         1.73892 |     0.323587 |     0.747575 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                20 |         14 |   0.285714 |     -0.132435   |        0.0608988 |         1.70362 |     0.323587 |     0.747575 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |                50 |         14 |   0.285714 |     -0.135435   |        0.0578988 |         1.65279 |     0.323587 |     0.747575 |
| declustered   | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |               100 |         14 |   0.285714 |     -0.140435   |        0.0528988 |         1.57333 |     0.323587 |     0.747575 |

## Outlier Sensitivity At 20 bps

| sample_type           | hypothesis_family                 | sub_strategy                |   n_trades |   median_return |   average_return |   profit_factor |
|:----------------------|:----------------------------------|:----------------------------|-----------:|----------------:|-----------------:|----------------:|
| full_sample           | monitoring_tag                    | failed_recovery_7d_trigger  |         86 |     -0.154542   |       0.100921   |      1.93327    |
| full_sample           | monitoring_tag                    | tag_24h_delay               |        117 |      0.00980209 |       0.0924302  |      2.32411    |
| full_sample           | monitoring_tag                    | tag_7d_delay                |        108 |     -0.168667   |       0.131956   |      2.20806    |
| full_sample           | monitoring_tag                    | tag_immediate_1h            |        117 |      0.0892672  |       0.0945541  |      2.2995     |
| full_sample           | pump_fade                         | pump20_failed_breakout_fade |         29 |     -0.0824322  |       0.213877   |      3.53807    |
| full_sample           | spot_delisting_announcement_shock | immediate_1h_confirmation   |         20 |      0.218928   |       0.144306   |      3.07503    |
| full_sample           | spot_delisting_announcement_shock | rebound_failure_24h         |         14 |     -0.109143   |       0.0559352  |      1.89118    |
| full_sample           | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |         14 |     -0.132435   |       0.0608988  |      1.70362    |
| excluding_best_trade  | monitoring_tag                    | failed_recovery_7d_trigger  |         85 |     -0.154542   |       0.0925061  |      1.84551    |
| excluding_best_trade  | monitoring_tag                    | tag_24h_delay               |        116 |      0.00195741 |       0.0895497  |      2.27188    |
| excluding_best_trade  | monitoring_tag                    | tag_7d_delay                |        107 |     -0.168667   |       0.125561   |      2.13888    |
| excluding_best_trade  | monitoring_tag                    | tag_immediate_1h            |        116 |      0.080219   |       0.0916918  |      2.24939    |
| excluding_best_trade  | pump_fade                         | pump20_failed_breakout_fade |         28 |     -0.125549   |       0.197778   |      3.26608    |
| excluding_best_trade  | spot_delisting_announcement_shock | immediate_1h_confirmation   |         19 |      0.011284   |       0.12945    |      2.76834    |
| excluding_best_trade  | spot_delisting_announcement_shock | rebound_failure_24h         |         13 |     -0.109143   |       0.0274247  |      1.40573    |
| excluding_best_trade  | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |         13 |     -0.132435   |      -0.0111859  |      0.879991   |
| excluding_top_5pct    | monitoring_tag                    | failed_recovery_7d_trigger  |         74 |     -0.154542   |      -0.0150674  |      0.880106   |
| excluding_top_5pct    | monitoring_tag                    | tag_24h_delay               |        111 |     -0.0119889  |       0.0743685  |      2.01074    |
| excluding_top_5pct    | monitoring_tag                    | tag_7d_delay                |         91 |     -0.168667   |       0.00413373 |      1.03189    |
| excluding_top_5pct    | monitoring_tag                    | tag_immediate_1h            |        107 |      0.0249414  |       0.0635244  |      1.79842    |
| excluding_top_5pct    | pump_fade                         | pump20_failed_breakout_fade |         27 |     -0.168667   |       0.180485   |      2.9941     |
| excluding_top_5pct    | spot_delisting_announcement_shock | immediate_1h_confirmation   |         10 |     -0.154542   |      -0.13796    |      0.00811282 |
| excluding_top_5pct    | spot_delisting_announcement_shock | rebound_failure_24h         |         11 |     -0.109143   |      -0.0451475  |      0.43483    |
| excluding_top_5pct    | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |         13 |     -0.132435   |      -0.0111859  |      0.879991   |
| excluding_worst_trade | monitoring_tag                    | failed_recovery_7d_trigger  |         85 |     -0.154542   |       0.103926   |      1.96594    |
| excluding_worst_trade | monitoring_tag                    | tag_24h_delay               |        116 |      0.0241516  |       0.0945593  |      2.36894    |
| excluding_worst_trade | monitoring_tag                    | tag_7d_delay                |        107 |     -0.168667   |       0.134766   |      2.24009    |
| excluding_worst_trade | monitoring_tag                    | tag_immediate_1h            |        116 |      0.0900052  |       0.0968232  |      2.34597    |
| excluding_worst_trade | pump_fade                         | pump20_failed_breakout_fade |         28 |      0.130198   |       0.227539   |      3.80036    |
| excluding_worst_trade | spot_delisting_announcement_shock | immediate_1h_confirmation   |         19 |      0.426571   |       0.160035   |      3.45941    |
| excluding_worst_trade | spot_delisting_announcement_shock | rebound_failure_24h         |         13 |     -0.109143   |       0.0686335  |      2.15939    |
| excluding_worst_trade | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |         13 |     -0.132435   |       0.0757706  |      1.91266    |
| excluding_bottom_5pct | monitoring_tag                    | failed_recovery_7d_trigger  |         64 |     -0.154542   |       0.188736   |      3.04736    |
| excluding_bottom_5pct | monitoring_tag                    | tag_24h_delay               |        102 |      0.0935688  |       0.12875    |      3.24521    |
| excluding_bottom_5pct | monitoring_tag                    | tag_7d_delay                |        101 |     -0.168667   |       0.152791   |      2.45363    |
| excluding_bottom_5pct | monitoring_tag                    | tag_immediate_1h            |        106 |      0.117853   |       0.121869   |      2.94029    |
| excluding_bottom_5pct | pump_fade                         | pump20_failed_breakout_fade |         15 |      0.664667   |       0.570918   |    104.889      |
| excluding_bottom_5pct | spot_delisting_announcement_shock | immediate_1h_confirmation   |         16 |      0.426571   |       0.219018   |      5.53505    |
| excluding_bottom_5pct | spot_delisting_announcement_shock | rebound_failure_24h         |          6 |      0.362802   |       0.276039   |    298.353      |
| excluding_bottom_5pct | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          5 |      0.299033   |       0.408899   |    104.249      |

## Time Split At 20 bps

| time_split   | hypothesis_family                 | sub_strategy                |   n_trades |   median_return |   average_return |   profit_factor |
|:-------------|:----------------------------------|:----------------------------|-----------:|----------------:|-----------------:|----------------:|
| 2023H2       | monitoring_tag                    | failed_recovery_7d_trigger  |          4 |     -0.154542   |       -0.154542  |        0        |
| 2023H2       | monitoring_tag                    | tag_24h_delay               |          4 |     -0.154542   |       -0.128038  |        0        |
| 2023H2       | monitoring_tag                    | tag_7d_delay                |          4 |     -0.168667   |       -0.168667  |        0        |
| 2023H2       | monitoring_tag                    | tag_immediate_1h            |          4 |     -0.0788272  |       -0.0588944 |        0.301647 |
| 2023H2       | pump_fade                         | pump20_failed_breakout_fade |          2 |      0.248      |        0.248     |        3.94071  |
| 2023H2       | spot_delisting_announcement_shock | immediate_1h_confirmation   |          3 |      0.426571   |        0.232867  |        5.52045  |
| 2023H2       | spot_delisting_announcement_shock | rebound_failure_24h         |          3 |      0.426571   |        0.384059  |      nan        |
| 2023H2       | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          3 |      0.299033   |        0.234496  |        6.31195  |
| 2024H1       | monitoring_tag                    | failed_recovery_7d_trigger  |         10 |      0.0666319  |        0.277982  |        4.59749  |
| 2024H1       | monitoring_tag                    | tag_24h_delay               |         13 |      0.170297   |        0.141915  |        4.78137  |
| 2024H1       | monitoring_tag                    | tag_7d_delay                |         13 |     -0.107846   |        0.185306  |        3.10659  |
| 2024H1       | monitoring_tag                    | tag_immediate_1h            |         13 |      0.192399   |        0.191807  |        6.97715  |
| 2024H1       | spot_delisting_announcement_shock | immediate_1h_confirmation   |          4 |      0.136015   |        0.136015  |        2.76022  |
| 2024H1       | spot_delisting_announcement_shock | rebound_failure_24h         |          3 |      0.0830575  |        0.133495  |        4.66937  |
| 2024H1       | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          3 |      0.230376   |        0.365314  |        9.27533  |
| 2024H2       | monitoring_tag                    | failed_recovery_7d_trigger  |         15 |     -0.154542   |       -0.125193  |        0.132045 |
| 2024H2       | monitoring_tag                    | tag_24h_delay               |         16 |      0.200462   |        0.166754  |        4.45286  |
| 2024H2       | monitoring_tag                    | tag_7d_delay                |         16 |     -0.168667   |       -0.140269  |        0.112922 |
| 2024H2       | monitoring_tag                    | tag_immediate_1h            |         16 |      0.426571   |        0.241507  |        8.63659  |
| 2024H2       | pump_fade                         | pump20_failed_breakout_fade |          4 |      0.555442   |        0.401721  |       10.527    |
| 2024H2       | spot_delisting_announcement_shock | immediate_1h_confirmation   |          8 |      0.218928   |        0.156743  |        3.70464  |
| 2024H2       | spot_delisting_announcement_shock | rebound_failure_24h         |          5 |     -0.109143   |       -0.0884283 |        0        |
| 2024H2       | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          5 |     -0.132435   |       -0.109908  |        0        |
| 2025H1       | monitoring_tag                    | failed_recovery_7d_trigger  |         31 |     -0.154542   |        0.181712  |        2.8225   |
| 2025H1       | monitoring_tag                    | tag_24h_delay               |         34 |      0.35616    |        0.148964  |        3.0483   |
| 2025H1       | monitoring_tag                    | tag_7d_delay                |         34 |     -0.168667   |        0.20042   |        2.92385  |
| 2025H1       | monitoring_tag                    | tag_immediate_1h            |         34 |     -0.168667   |        0.0665503 |        1.70607  |
| 2025H1       | pump_fade                         | pump20_failed_breakout_fade |         14 |      0.0870805  |        0.216523  |        3.56746  |
| 2025H1       | spot_delisting_announcement_shock | immediate_1h_confirmation   |          4 |      0.136015   |        0.136015  |        2.76022  |
| 2025H1       | spot_delisting_announcement_shock | rebound_failure_24h         |          2 |     -0.109143   |       -0.109143  |        0        |
| 2025H1       | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          2 |     -0.132435   |       -0.132435  |        0        |
| 2025H2       | monitoring_tag                    | failed_recovery_7d_trigger  |          6 |     -0.154542   |        0.0284633 |        1.26461  |
| 2025H2       | monitoring_tag                    | tag_24h_delay               |         10 |     -0.154542   |       -0.018521  |        0.828794 |
| 2025H2       | monitoring_tag                    | tag_7d_delay                |         10 |     -0.168667   |        0.0424465 |        1.35141  |
| 2025H2       | monitoring_tag                    | tag_immediate_1h            |         10 |     -0.168667   |        0.0190032 |        1.18778  |
| 2025H2       | pump_fade                         | pump20_failed_breakout_fade |          4 |      0.291117   |        0.269559  |        5.29406  |
| 2025H2       | spot_delisting_announcement_shock | immediate_1h_confirmation   |          1 |     -0.154542   |       -0.154542  |        0        |
| 2025H2       | spot_delisting_announcement_shock | rebound_failure_24h         |          1 |     -0.109143   |       -0.109143  |        0        |
| 2025H2       | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          1 |     -0.132435   |       -0.132435  |        0        |
| 2026YTD      | monitoring_tag                    | failed_recovery_7d_trigger  |         20 |     -0.154542   |        0.12958   |        2.28996  |
| 2026YTD      | monitoring_tag                    | tag_24h_delay               |         40 |     -0.00968262 |        0.0483491 |        1.68097  |
| 2026YTD      | monitoring_tag                    | tag_7d_delay                |         31 |     -0.168667   |        0.242661  |        3.78749  |
| 2026YTD      | monitoring_tag                    | tag_immediate_1h            |         40 |      0.0671412  |        0.0622014 |        1.81952  |
| 2026YTD      | pump_fade                         | pump20_failed_breakout_fade |          5 |     -0.168667   |       -0.002     |        0.985178 |

## Confidence Tier At 20 bps

| confidence_bucket   | hypothesis_family                 | sub_strategy                |   n_trades |   median_return |   average_return |   profit_factor |
|:--------------------|:----------------------------------|:----------------------------|-----------:|----------------:|-----------------:|----------------:|
| clean               | monitoring_tag                    | failed_recovery_7d_trigger  |         37 |      -0.154542  |        0.125258  |         2.24954 |
| clean               | monitoring_tag                    | tag_24h_delay               |         55 |       0.0719927 |        0.109269  |         2.89825 |
| clean               | monitoring_tag                    | tag_7d_delay                |         48 |      -0.168667  |        0.137511  |         2.34292 |
| clean               | monitoring_tag                    | tag_immediate_1h            |         55 |       0.0631118 |        0.0703    |         1.93669 |
| clean               | pump_fade                         | pump20_failed_breakout_fade |         10 |       0.503747  |        0.299149  |         5.43403 |
| clean               | spot_delisting_announcement_shock | immediate_1h_confirmation   |          9 |      -0.154542  |        0.0391622 |         1.38011 |
| clean               | spot_delisting_announcement_shock | rebound_failure_24h         |          6 |      -0.0130427 |        0.0802056 |         2.46974 |
| clean               | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          6 |       0.0489706 |        0.111499  |         2.68383 |
| low_sensitivity     | monitoring_tag                    | failed_recovery_7d_trigger  |         49 |      -0.154542  |        0.0825436 |         1.72345 |
| low_sensitivity     | monitoring_tag                    | tag_24h_delay               |         62 |      -0.154542  |        0.0774926 |         1.96067 |
| low_sensitivity     | monitoring_tag                    | tag_7d_delay                |         60 |      -0.168667  |        0.127512  |         2.11174 |
| low_sensitivity     | monitoring_tag                    | tag_immediate_1h            |         62 |       0.133806  |        0.11607   |         2.641   |
| low_sensitivity     | pump_fade                         | pump20_failed_breakout_fade |         19 |      -0.168667  |        0.168997  |         2.81502 |
| low_sensitivity     | spot_delisting_announcement_shock | immediate_1h_confirmation   |         11 |       0.426571  |        0.230332  |         6.46486 |
| low_sensitivity     | spot_delisting_announcement_shock | rebound_failure_24h         |          8 |      -0.109143  |        0.0377323 |         1.54756 |
| low_sensitivity     | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |          8 |      -0.132435  |        0.0229487 |         1.22543 |

## Holding Window Diagnostic At 20 bps

| holding_window_bucket   | hypothesis_family                 | sub_strategy                |   n_trades |   median_return |   average_return |   profit_factor |
|:------------------------|:----------------------------------|:----------------------------|-----------:|----------------:|-----------------:|----------------:|
| 30d                     | monitoring_tag                    | tag_24h_delay               |        117 |      0.00980209 |        0.0924302 |         2.32411 |
| 30d                     | monitoring_tag                    | tag_immediate_1h            |        117 |      0.0892672  |        0.0945541 |         2.2995  |
| 30d                     | spot_delisting_announcement_shock | rebound_failure_24h_hold30  |         14 |     -0.132435   |        0.0608988 |         1.70362 |
| 7d                      | pump_fade                         | pump20_failed_breakout_fade |         29 |     -0.0824322  |        0.213877  |         3.53807 |
| 7d                      | spot_delisting_announcement_shock | immediate_1h_confirmation   |         20 |      0.218928   |        0.144306  |         3.07503 |
| 7d                      | spot_delisting_announcement_shock | rebound_failure_24h         |         14 |     -0.109143   |        0.0559352 |         1.89118 |
| 90d                     | monitoring_tag                    | failed_recovery_7d_trigger  |         86 |     -0.154542   |        0.100921  |         1.93327 |
| 90d                     | monitoring_tag                    | tag_7d_delay                |        108 |     -0.168667   |        0.131956  |         2.20806 |

## Interpretation Guide

- `robust_candidate`: positive median, positive average, survives top-5% removal and de-clustering.
- `tail_dependent`: positive average but weak/negative median or weak after top-tail removal.
- `fragile_positive`: average positive but needs more validation across regime/cost/cluster splits.
- `small_sample`: too few trades for a reliable conclusion.
- `not_robust`: weak after basic robustness checks.

## Caveats

- De-clustering is approximate and event-family based; it reduces but does not eliminate dependence.
- Cost sensitivity is still simplified; stressed delisting liquidity can exceed 100 bps effective cost.
- Holding-window sensitivity is diagnostic by rule bucket, not a full re-optimization.
- No borrow, funding, liquidation, or order-book feasibility is included.
