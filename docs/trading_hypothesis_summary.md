# Trading Hypothesis Summary

This is a research summary for short/risk-event hypotheses, not a live tradability claim or investment advice.

## Most Useful Short-Research Event Types

| scenario                             |   n |   median_mfe_24h |   median_mae_24h |   median_mfe_7d |   median_mae_7d |   rebound_rate |   vwap_fail_rate |
|:-------------------------------------|----:|-----------------:|-----------------:|----------------:|----------------:|---------------:|-----------------:|
| SEED_TAG_ONLY                        |   5 |        0.0721311 |        0.0374618 |        0.635    |      0.632029   |       0.2      |         0        |
| DELISTED_WITHOUT_KNOWN_PRIOR_TAG     |   9 |        0.199609  |        0.0851187 |        0.555856 |      0.0507307  |       0.333333 |         0.666667 |
| TAG_REMOVED_BUT_NOT_RECOVERED        |   2 |        0.153639  |        0.127416  |        0.45157  |      0.186049   |       0.5      |         0.5      |
| DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |   5 |        0.151899  |        0.0172543 |        0.384296 |      0.00990248 |       0        |         0.6      |
| TAG_REMOVED_AND_RECOVERED            |   5 |        0.0638439 |        0.0258085 |        0.337838 |      0.0125253  |       0.2      |         0.2      |
| TAG_TO_DELISTING_TO_COLLAPSE         |  19 |        0.104478  |        0.0535714 |        0.26     |      0.0940103  |       0.315789 |         0.368421 |
| FUTURES_ONLY_DELISTING               |  47 |        0.177403  |        0.0776498 |        0.25937  |      0.0779082  |       0.382979 |         0.510638 |
| TEMPORARY_PANIC_THEN_RECOVERY        |   4 |        0.17814   |        0.0545826 |        0.237134 |      0.134042   |       0.75     |         0.75     |
| IMMEDIATE_DUMP_AFTER_TAG             |   3 |        0.145833  |        0.025974  |        0.228798 |      0.0168818  |       0        |         1        |
| SLOW_BLEED_AFTER_TAG                 |   4 |        0.0397668 |        0.0598641 |        0.138047 |      0.161435   |       0.25     |         0.5      |
| NO_CLEAR_REACTION                    |  11 |        0.0819348 |        0.0415755 |        0.110436 |      0.128086   |       0.545455 |         0.363636 |

## Pump-Fade Candidates

- Pump rows: 110.
- Research-eligible pump rows: 33.
- Pump-fade score distribution: n=110, p25=0.100, median=0.100, p75=0.200.
- Post-pump drawdown distribution: n=106, p25=-0.837, median=-0.656, p75=-0.470.

Interpretation: pump-fade research should focus on events where pump20 and pump-and-dump flags are present, but manual-review and suspicious fallback cases should be excluded or separately verified.

## Monitoring Tag Delayed-Collapse Candidates

- Monitoring Tag rows: 124.
- Research-eligible Monitoring rows: 55.
- Delayed-collapse score distribution: n=124, p25=0.200, median=0.350, p75=0.550.
- Max drawdown after tag distribution: n=119, p25=-0.766, median=-0.452, p75=-0.271.

Interpretation: Monitoring Tag looks most useful as a regime filter plus failed-recovery framework, not just as an immediate-candle short signal.

## Noisy Or Not-Yet-Tradeable Areas

- `PAIR_REMOVAL_ONLY`: useful control group, not token delisting signal.
- `UNKNOWN_MANUAL_REVIEW`: not clean enough for signal research without manual review.
- Fallback-provider-unavailable and unresolved-symbol rows: useful for data-quality reports, not clean execution tests.
- Futures-only rows: structurally different mechanics; require funding/open-interest/liquidation features before execution claims.

## Stop-Loss Risk Zones

- Delisting announcements have pump/squeeze risk; stop zones based only on immediate entry candle are statistically dangerous.
- 90%/100% pre-event baseline reclaim remains a practical invalidation concept.
- Pump-fade shorts should avoid entering before failed breakout confirmation because pump20 events exist in about one-fifth of delisting rows.

## Historically Plausible Take-Profit Zones

- Announcement shock shorts: first target around +24h/+7d favorable excursion distributions, not fixed percentage.
- Failed Monitoring Tag recovery: +30d/+90d drift is more relevant than +1h reaction.
- Pump-fade: post-pump drawdown tail is large, but only after excluding suspicious fallback and liquidity artifacts.

## Backtest Priority

1. Spot delisting announcement shock with rebound-failure entry.
2. Delisting pump-fade after failed breakout confirmation.
3. Monitoring Tag failed-recovery delayed-collapse.
4. Delisted-without-known-tag shock response as a separate high-uncertainty class.
5. Futures-only delisting only after adding futures market-structure features.
