# Monitoring Live Feasibility v1

Generated at UTC: 2026-05-27T10:41:27.613530+00:00

Scope: only the recommended Monitoring Tag candidate rule: `immediate_1h_confirmation + negative_1h_confirmation`.

This is not a live tradability claim. It separates the historical market signal from execution feasibility proxies. The biggest unresolved blocker is true borrow/shortability data.

## Candidate Universe

- Candidate trades: 89
- Feasibility tiers: high=0, medium=55, low=34
- Low liquidity flags: 22
- Extreme first-hour wick/gap flags: 5
- Abnormal candle gap flags: 8
- Fallback-only path flags: 0
- Futures/perp proxy available around event: 0
- Borrow availability unknown: 89
- Event clustered with another risk event within +/-7d: 4

## Metrics by Feasibility View at 100 bps

| view                           |   cost_bps |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | worst_trade   | best_trade   | median_mae   | median_mfe   |   profit_factor |
|:-------------------------------|-----------:|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:--------------|:-------------|:-------------|:-------------|----------------:|
| all_candidate_trades           |        100 |         89 | 56.2%      | 6.3%            | 8.1%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 21.3%        | 38.3%        |         2.04212 |
| high_medium_feasibility        |        100 |         55 | 65.5%      | 13.7%           | 12.5%            | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 13.4%        | 38.2%        |         3.04693 |
| high_feasibility_only          |        100 |          0 | NA         | NA              | NA               | NA           | NA           | NA            | NA           | NA           | NA           |       nan       |
| excluding_low_liquidity        |        100 |         67 | 61.2%      | 10.5%           | 10.9%            | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 18.1%        | 43.0%        |         2.59479 |
| excluding_extreme_wick_gap     |        100 |         77 | 58.4%      | 8.3%            | 8.7%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 20.2%        | 36.3%        |         2.18968 |
| excluding_unknown_shortability |        100 |          0 | NA         | NA              | NA               | NA           | NA           | NA            | NA           | NA           | NA           |       nan       |

## Cost Sensitivity Snapshot

| view                    |   cost_bps |   n_trades | win_rate   | median_return   | average_return   |   profit_factor |
|:------------------------|-----------:|-----------:|:-----------|:----------------|:-----------------|----------------:|
| all_candidate_trades    |         20 |         89 | 56.2%      | 7.1%            | 8.9%             |         2.19979 |
| all_candidate_trades    |         50 |         89 | 56.2%      | 6.8%            | 8.6%             |         2.13894 |
| all_candidate_trades    |        100 |         89 | 56.2%      | 6.3%            | 8.1%             |         2.04212 |
| all_candidate_trades    |        200 |         89 | 53.9%      | 5.3%            | 7.1%             |         1.86286 |
| all_candidate_trades    |        500 |         89 | 51.7%      | 2.3%            | 4.1%             |         1.42376 |
| high_medium_feasibility |         20 |         55 | 65.5%      | 14.5%           | 13.3%            |         3.28131 |
| high_medium_feasibility |         50 |         55 | 65.5%      | 14.2%           | 13.0%            |         3.19086 |
| high_medium_feasibility |        100 |         55 | 65.5%      | 13.7%           | 12.5%            |         3.04693 |
| high_medium_feasibility |        200 |         55 | 63.6%      | 12.7%           | 11.5%            |         2.77869 |
| high_medium_feasibility |        500 |         55 | 61.8%      | 9.7%            | 8.5%             |         2.1245  |

## Interpretation

- The historical signal remains separate from execution feasibility. A trade can have good retrospective return and still be untradeable if borrow, depth, or spread is unavailable.
- `high` feasibility requires strong quote volume, stable candles, no low-liquidity flags, and a futures/perp proxy around the event. This is only a proxy for shortability, not proof of borrow availability.
- `medium` usually means market path is usable but shortability is unknown or volume is only moderate.
- `low` means at least one hard execution issue appears: low liquidity, fallback-only path, abnormal gap, missing path, or extreme wick/gap.
- Excluding unknown shortability is intentionally strict and may leave too few trades if futures proxy coverage is incomplete.

## Additional Data Required Before Live Claims

- Historical order book snapshots or bid/ask spreads around event and entry.
- Borrow availability and borrow fee history for spot margin shorts.
- Perp listing status at event time, funding rate, open interest, and liquidation intensity.
- Venue-specific max order size, market impact estimates, and maintenance/outage flags.
- Cross-venue liquidity if Binance spot is deteriorating after the tag.
