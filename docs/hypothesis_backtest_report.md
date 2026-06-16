# Hypothesis Backtest Report v1

Generated at UTC: 2026-05-27T08:27:07.742811+00:00

This is a retrospective rules-based research backtest. It is not a live tradability claim and does not include borrow availability, real order book depth, funding, liquidation dynamics, or venue-specific execution constraints.

## Assumptions

- Short PnL is computed as `entry_price / exit_price - 1`.
- Transaction cost/slippage is modeled as round-trip cost with two assumptions: 0 bps and 20 bps.
- Stop/TP use first-touch OHLCV logic; if stop and TP touch in the same candle, stop is assumed first.
- Entries are after event time: +1h, +24h, +7d, or after pump20 confirmation plus failed-breakout close.
- Pair-removal-only and unknown manual-review rows are excluded from clean hypotheses.
- Lower-confidence sensitivity samples are marked but separated by `confidence_tier=low_sensitivity`.

## Hypothesis Definitions

### 1. Spot Delisting Announcement Shock

- Eligible universe: clean/sensitivity spot `SPOT_TOKEN_DELISTING_ANNOUNCED` rows with path data.
- Entry rules: `immediate_1h_confirmation`; `rebound_failure_24h` only when `vwap_reclaim_failure=yes`; 30d variant for rebound failure.
- Stops: 12-18% depending on sub-rule.
- Take profits: 30% for 7d tests; 50% for 30d rebound-failure test.
- Invalidation: fixed SL; conceptual invalidation on sustained baseline reclaim.

### 2. Delisting Pump-Fade

- Eligible universe: pump rows with no manual-review pump flag and spot pair available.
- Entry rule: after first post-event candle confirming +20% pump from baseline, then subsequent 1h close back below baseline +10%.
- Stop: 20% above failed-breakout entry.
- Take profit: 40%.
- Holding window: 7d.

### 3. Monitoring Tag Failed-Recovery Delayed Collapse

- Eligible universe: Monitoring Tag rows with path data.
- Entry delays: +1h, +24h, +7d.
- Failed-recovery trigger: +7d entry only if the 7d return known at that time is negative.
- Stops: 18-20%.
- Take profits: 30-45%.
- Holding windows: 30d and 90d depending on sub-rule.

## Overall Results

| hypothesis                                      | sub_strategy                |   roundtrip_cost_bps |   number_of_trades |   win_rate |   median_return |   average_return |   p25_return |   p75_return |   worst_trade |   best_trade |   median_max_adverse_excursion |   median_max_favorable_excursion |   median_time_to_tp_hours |   median_time_to_sl_hours |   median_risk_reward |
|:------------------------------------------------|:----------------------------|---------------------:|-------------------:|-----------:|----------------:|-----------------:|-------------:|-------------:|--------------:|-------------:|-------------------------------:|---------------------------------:|--------------------------:|--------------------------:|---------------------:|
| delisting_pump_fade_after_failed_breakout       | pump20_failed_breakout_fade |                    0 |                 29 |   0.482759 |     -0.0804322  |        0.215877  |    -0.166667 |     0.666667 |     -0.166667 |     0.666667 |                       0.228261 |                         0.732026 |                     113   |                      16.5 |              5.11165 |
| delisting_pump_fade_after_failed_breakout       | pump20_failed_breakout_fade |                   20 |                 29 |   0.482759 |     -0.0824322  |        0.213877  |    -0.168667 |     0.664667 |     -0.168667 |     0.664667 |                       0.228261 |                         0.732026 |                     113   |                      16.5 |              5.11165 |
| monitoring_tag_failed_recovery_delayed_collapse | failed_recovery_7d_trigger  |                    0 |                 86 |   0.290698 |     -0.152542   |        0.102921  |    -0.152542 |     0.389632 |     -0.152542 |     0.818182 |                       0.477701 |                         0.75     |                     606   |                     200   |              2.36643 |
| monitoring_tag_failed_recovery_delayed_collapse | failed_recovery_7d_trigger  |                   20 |                 86 |   0.290698 |     -0.154542   |        0.100921  |    -0.154542 |     0.387632 |     -0.154542 |     0.816182 |                       0.477701 |                         0.75     |                     606   |                     200   |              2.36643 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_24h_delay               |                    0 |                117 |   0.504274 |      0.0118021  |        0.0944302 |    -0.152542 |     0.428571 |     -0.152542 |     0.428571 |                       0.200333 |                         0.376667 |                     172.5 |                     105   |              1.97885 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_24h_delay               |                   20 |                117 |   0.504274 |      0.00980209 |        0.0924302 |    -0.154542 |     0.426571 |     -0.154542 |     0.426571 |                       0.200333 |                         0.376667 |                     172.5 |                     105   |              1.97885 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_7d_delay                |                    0 |                108 |   0.333333 |     -0.166667   |        0.133956  |    -0.166667 |     0.818182 |     -0.166667 |     0.818182 |                       0.453462 |                         0.783095 |                     589   |                     199   |              2.36643 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_7d_delay                |                   20 |                108 |   0.333333 |     -0.168667   |        0.131956  |    -0.168667 |     0.816182 |     -0.168667 |     0.816182 |                       0.453462 |                         0.783095 |                     589   |                     199   |              2.36643 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_immediate_1h            |                    0 |                117 |   0.564103 |      0.0912672  |        0.0965541 |    -0.166667 |     0.428571 |     -0.166667 |     0.428571 |                       0.188174 |                         0.377217 |                     152   |                      93.5 |              2.44697 |
| monitoring_tag_failed_recovery_delayed_collapse | tag_immediate_1h            |                   20 |                117 |   0.564103 |      0.0892672  |        0.0945541 |    -0.168667 |     0.426571 |     -0.168667 |     0.426571 |                       0.188174 |                         0.377217 |                     152   |                      93.5 |              2.44697 |
| spot_delisting_announcement_shock               | immediate_1h_confirmation   |                    0 |                 20 |   0.55     |      0.220928   |        0.146306  |    -0.152542 |     0.428571 |     -0.152542 |     0.428571 |                       0.257823 |                         0.550233 |                      43.5 |                      23   |              1.49414 |
| spot_delisting_announcement_shock               | immediate_1h_confirmation   |                   20 |                 20 |   0.55     |      0.218928   |        0.144306  |    -0.154542 |     0.426571 |     -0.154542 |     0.426571 |                       0.257823 |                         0.550233 |                      43.5 |                      23   |              1.49414 |
| spot_delisting_announcement_shock               | rebound_failure_24h         |                    0 |                 14 |   0.357143 |     -0.107143   |        0.0579352 |    -0.107143 |     0.247039 |     -0.107143 |     0.428571 |                       0.323587 |                         0.535677 |                       9   |                       9.5 |              1.8911  |
| spot_delisting_announcement_shock               | rebound_failure_24h         |                   20 |                 14 |   0.357143 |     -0.109143   |        0.0559352 |    -0.109143 |     0.245039 |     -0.109143 |     0.426571 |                       0.323587 |                         0.535677 |                       9   |                       9.5 |              1.8911  |
| spot_delisting_announcement_shock               | rebound_failure_24h_hold30  |                    0 |                 14 |   0.285714 |     -0.130435   |        0.0628988 |    -0.130435 |     0.169832 |     -0.130435 |     1        |                       0.323587 |                         0.747575 |                     129   |                      14   |              2.51248 |
| spot_delisting_announcement_shock               | rebound_failure_24h_hold30  |                   20 |                 14 |   0.285714 |     -0.132435   |        0.0608988 |    -0.132435 |     0.167832 |     -0.132435 |     0.998    |                       0.323587 |                         0.747575 |                     129   |                      14   |              2.51248 |

## Results By Scenario

| scenario                             |   roundtrip_cost_bps |   number_of_trades |   win_rate |   median_return |   average_return |   worst_trade |   best_trade |
|:-------------------------------------|---------------------:|-------------------:|-----------:|----------------:|-----------------:|--------------:|-------------:|
| DELISTED_WITHOUT_KNOWN_PRIOR_TAG     |                    0 |                 50 |   0.42     |     -0.107143   |        0.102356  |    -0.166667  |    1         |
| DELISTED_WITHOUT_KNOWN_PRIOR_TAG     |                   20 |                 50 |   0.42     |     -0.109143   |        0.100356  |    -0.168667  |    0.998     |
| DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |                    0 |                 74 |   0.418919 |     -0.152542   |        0.0999434 |    -0.166667  |    0.818182  |
| DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |                   20 |                 74 |   0.418919 |     -0.154542   |        0.0979434 |    -0.168667  |    0.816182  |
| IMMEDIATE_DUMP_AFTER_TAG             |                    0 |                 10 |   0.8      |      0.101334   |        0.160808  |    -0.0309859 |    0.422907  |
| IMMEDIATE_DUMP_AFTER_TAG             |                   20 |                 10 |   0.8      |      0.0993344  |        0.158808  |    -0.0329859 |    0.420907  |
| NO_CLEAR_REACTION                    |                    0 |                 36 |   0.444444 |     -0.152542   |        0.0208971 |    -0.166667  |    0.818182  |
| NO_CLEAR_REACTION                    |                   20 |                 36 |   0.444444 |     -0.154542   |        0.0188971 |    -0.168667  |    0.816182  |
| SLOW_BLEED_AFTER_TAG                 |                    0 |                 19 |   0.473684 |     -0.00537634 |        0.141278  |    -0.166667  |    0.818182  |
| SLOW_BLEED_AFTER_TAG                 |                   20 |                 19 |   0.473684 |     -0.00737634 |        0.139278  |    -0.168667  |    0.816182  |
| TAG_REMOVED_AND_RECOVERED            |                    0 |                 27 |   0.518519 |      0.0844875  |        0.0957721 |    -0.166667  |    0.564103  |
| TAG_REMOVED_AND_RECOVERED            |                   20 |                 27 |   0.518519 |      0.0824875  |        0.0937721 |    -0.168667  |    0.562103  |
| TAG_REMOVED_BUT_NOT_RECOVERED        |                    0 |                  7 |   0.428571 |     -0.152542   |        0.14813   |    -0.166667  |    0.818182  |
| TAG_REMOVED_BUT_NOT_RECOVERED        |                   20 |                  7 |   0.428571 |     -0.154542   |        0.14613   |    -0.168667  |    0.816182  |
| TAG_TO_DELISTING_TO_COLLAPSE         |                    0 |                269 |   0.431227 |     -0.152542   |        0.137561  |    -0.166667  |    0.818182  |
| TAG_TO_DELISTING_TO_COLLAPSE         |                   20 |                269 |   0.431227 |     -0.154542   |        0.135561  |    -0.168667  |    0.816182  |
| TEMPORARY_PANIC_THEN_RECOVERY        |                    0 |                 13 |   0.153846 |     -0.152542   |       -0.1264    |    -0.166667  |    0.0731707 |
| TEMPORARY_PANIC_THEN_RECOVERY        |                   20 |                 13 |   0.153846 |     -0.154542   |       -0.1284    |    -0.168667  |    0.0711707 |

## Results By Confidence Tier

| confidence_tier   |   roundtrip_cost_bps |   number_of_trades |   win_rate |   median_return |   average_return |   worst_trade |   best_trade |
|:------------------|---------------------:|-------------------:|-----------:|----------------:|-----------------:|--------------:|-------------:|
| high              |                    0 |                226 |   0.473451 |       -0.09249  |         0.115299 |     -0.166667 |     0.818182 |
| high              |                   20 |                226 |   0.473451 |       -0.09449  |         0.113299 |     -0.168667 |     0.816182 |
| low_sensitivity   |                    0 |                279 |   0.405018 |       -0.152542 |         0.109263 |     -0.166667 |     1        |
| low_sensitivity   |                   20 |                279 |   0.405018 |       -0.154542 |         0.107263 |     -0.168667 |     0.998    |

## Interpretation

- Treat 0 bps as a clean statistical baseline, not an executable assumption.
- 20 bps is a coarse sensitivity test; small-cap delisting names may require much larger slippage assumptions.
- Pump-fade entries are explicitly after pump confirmation and a subsequent failed-breakout close, reducing look-ahead compared with entering before the squeeze.
- Monitoring Tag delayed-collapse variants test timing sensitivity; the failed-recovery trigger is intentionally delayed and uses only the +7d return known at trigger time.
- Samples remain small after quality filters; results should be bootstrapped and retested with borrow/perp availability before any execution claim.
