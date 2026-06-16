# Monitoring Conservative Strategy Backtest

Generated at UTC: 2026-05-27T12:08:09.690747+00:00

Scope: one conservative candidate rule only. This is research, not live trading advice.

## Rule

- Monitoring Tag event.
- Entry: immediate 1h confirmation.
- First-hour return must be negative.
- Confirmed/inferred Binance perp availability.
- `feasibility_tier in {medium, high}`.
- `low_liquidity_flag = false`.
- `abnormal_candle_gap = false`.
- `extreme_first_hour_wick_gap = false`.

## Validation

- Trades: 30
- Duplicate trades: 0
- Entry after event violations: 0
- Pair-removal-only trades: 0
- Unknown/manual-review rows: 0
- Confirmed/inferred shortability violations: 0

## Cost Sensitivity

|   cost_bps |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | worst_trade   | best_trade   | median_mae   | median_mfe   |   profit_factor | expectancy   | average_ex_top5   | average_ex_bottom5   |
|-----------:|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:--------------|:-------------|:-------------|:-------------|----------------:|:-------------|:------------------|:---------------------|
|         20 |         30 | 56.7%      | 11.8%           | 10.6%            | -16.9%       | 42.7%        | -16.9%        | 42.7%        | 12.8%        | 37.0%        |         2.44353 | 10.6%        | 7.0%              | 13.6%                |
|         50 |         30 | 56.7%      | 11.5%           | 10.3%            | -17.2%       | 42.4%        | -17.2%        | 42.4%        | 12.8%        | 37.0%        |         2.37797 | 10.3%        | 6.7%              | 13.3%                |
|        100 |         30 | 56.7%      | 11.0%           | 9.8%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 12.8%        | 37.0%        |         2.27366 | 9.8%         | 6.2%              | 12.8%                |
|        200 |         30 | 56.7%      | 10.0%           | 8.8%             | -18.7%       | 40.9%        | -18.7%        | 40.9%        | 12.8%        | 37.0%        |         2.0818  | 8.8%         | 5.2%              | 11.8%                |
|        500 |         30 | 56.7%      | 7.0%            | 5.8%             | -21.7%       | 37.9%        | -21.7%        | 37.9%        | 12.8%        | 37.0%        |         1.61249 | 5.8%         | 2.2%              | 8.8%                 |

## Time Split at 100 bps

| group   |   n_trades | win_rate   | median_return   | average_return   |   profit_factor | median_mae   | median_mfe   |
|:--------|-----------:|:-----------|:----------------|:-----------------|----------------:|:-------------|:-------------|
| 2024H1  |          4 | 75.0%      | 25.9%           | 19.0%            |         5.30032 | 3.8%         | 49.4%        |
| 2024H2  |          3 | 33.3%      | -17.7%          | 2.2%             |         1.18464 | 20.2%        | 30.5%        |
| 2025H1  |         11 | 36.4%      | -17.7%          | 4.0%             |         1.35387 | 36.4%        | 51.5%        |
| 2025H2  |          1 | 0.0%       | -17.7%          | -17.7%           |         0       | 32.7%        | 35.6%        |
| 2026YTD |         11 | 81.8%      | 21.2%           | 16.7%            |         6.20546 | 2.4%         | 26.4%        |

## Scenario Split at 100 bps

| group                                |   n_trades | win_rate   | median_return   | average_return   |   profit_factor | median_mae   | median_mfe   |
|:-------------------------------------|-----------:|:-----------|:----------------|:-----------------|----------------:|:-------------|:-------------|
| TAG_TO_DELISTING_TO_COLLAPSE         |         12 | 41.7%      | -17.7%          | 7.1%             |        1.69234  | 20.7%        | 41.8%        |
| DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |          4 | 75.0%      | 41.9%           | 27.0%            |        7.10782  | 21.1%        | 121.3%       |
| NO_CLEAR_REACTION                    |          4 | 75.0%      | 17.6%           | 12.6%            |        3.84402  | 6.2%         | 22.2%        |
| IMMEDIATE_DUMP_AFTER_TAG             |          3 | 100.0%     | 22.6%           | 18.7%            |      nan        | 1.5%         | 26.4%        |
| TAG_REMOVED_AND_RECOVERED            |          3 | 66.7%      | 9.9%            | 11.4%            |        2.93105  | 13.2%        | 32.3%        |
| SLOW_BLEED_AFTER_TAG                 |          2 | 50.0%      | -3.1%           | -3.1%            |        0.650943 | 30.3%        | 22.5%        |
| TAG_REMOVED_BUT_NOT_RECOVERED        |          1 | 0.0%       | -17.7%          | -17.7%           |        0        | 33.3%        | 52.9%        |
| TEMPORARY_PANIC_THEN_RECOVERY        |          1 | 0.0%       | -17.7%          | -17.7%           |        0        | 54.0%        | 51.5%        |

## Drawdown / Risk Diagnostics

- Largest MAE: 202.8%
- Trades with MAE > 20%: 14
- Trades with MAE > 30%: 11
- Trades with MAE > 50%: 5

## Stop-Loss Sensitivity Proxy at 100 bps

| group      |   n_trades | win_rate   | median_return   | average_return   |   profit_factor |
|:-----------|-----------:|:-----------|:----------------|:-----------------|----------------:|
| stop_15pct |         30 | 53.3%      | 10.2%           | 8.5%             |         2.14432 |
| stop_20pct |         30 | 53.3%      | 10.2%           | 6.2%             |         1.63377 |
| stop_30pct |         30 | 53.3%      | 10.2%           | 2.9%             |         1.2191  |
| stop_40pct |         30 | 53.3%      | 10.2%           | 3.1%             |         1.24009 |

## Take-Profit Sensitivity Proxy at 100 bps

| group    |   n_trades | win_rate   | median_return   | average_return   |   profit_factor |
|:---------|-----------:|:-----------|:----------------|:-----------------|----------------:|
| tp_10pct |         30 | 100.0%     | 9.0%            | 9.0%             |       nan       |
| tp_20pct |         30 | 86.7%      | 19.0%           | 13.9%            |         6.92031 |
| tp_30pct |         30 | 80.0%      | 29.0%           | 17.9%            |         6.07001 |
| tp_50pct |         30 | 66.7%      | 21.9%           | 18.6%            |         4.15172 |

## Verdict

- Confidence level: limited, because n=30.
- Tail dependence: The edge is not solely dependent on the top 5%.
- Stop-loss sensitivity: Stop-loss proxy remains positive across tested levels.
- This candidate is worth paper trading / forward testing only if historical borrow/perp execution can be matched with live order-book, funding, and max-slippage constraints.
- It is not yet a production strategy.
