# Market Structure Research Framework v1

This document converts the Binance risk-event retrospective dataset into research hypotheses for risk-event driven crypto trading analysis. It is descriptive research, not trading advice. Event labels can be lagging symptoms of prior degradation, and the dataset has survivorship, liquidity, fallback, and missing-data limitations.

## Dataset Anchor

- Period: 2023-07-26 to 2026-05-26.
- Events: 1,277.
- Lifecycle entities: 544.
- Price-layer entities: 529.
- Price windows: 22,050.
- Recovery rows: 270.
- Pump rows: 110.
- Scenario rows: 544.
- Manual-review scenarios: 21.

## Core Scenario Map

| Scenario | Tokens | Interpretation |
|---|---:|---|
| `PAIR_REMOVAL_ONLY` | 259 | Control class; not token delisting. |
| `TAG_TO_DELISTING_TO_COLLAPSE` | 66 | Monitoring/related risk marker followed by spot delisting and sustained weakness. |
| `FUTURES_ONLY_DELISTING` | 62 | Futures-specific mechanics; separate from spot token delisting. |
| `SEED_TAG_ONLY` | 61 | Higher-risk listing cohort, not Monitoring Tag. |
| `DELISTED_WITHOUT_KNOWN_PRIOR_TAG` | 25 | Delisting appears without known prior tag in corpus. |
| `DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP` | 19 | Announcement-period pump followed by failed hold/drawdown. |
| `UNKNOWN_MANUAL_REVIEW` | 15 | Ambiguous lifecycle or parser/source issue. |
| `TAG_REMOVED_AND_RECOVERED` | 7 | Tag removal plus sustained recovery. |
| `TAG_REMOVED_BUT_NOT_RECOVERED` | 3 | Tag removed but price did not sustain recovery. |

## Main Empirical Patterns

### 1. Monitoring Tag Has A Persistent Left-Tail Drift

For `MONITORING_TAG_ADDED`, alt-benchmark-adjusted median returns:

- +1h: -1.5%
- +4h: -3.1%
- +24h: -5.9%
- +7d: -11.9%
- +30d: -20.9%
- +90d: -33.9%

Negative-share stays high across windows: 82.5% at +24h, 75.2% at +30d, 78.3% at +90d.

Hypothesis: the tag is often a public confirmation of an already weak market-structure regime. It is not mechanically causal, but it identifies a population with persistent underperformance and weak rebound quality.

Confidence: medium-high. Sample size is good for +1h/+24h/+7d, smaller at +90d due missing/fallback.

### 2. Spot Delisting Announcement Is The Strongest Short-Horizon Shock

For `SPOT_TOKEN_DELISTING_ANNOUNCED`, alt-benchmark-adjusted median returns:

- +1h: -4.8%
- +4h: -8.8%
- +24h: -8.6%
- +7d: -35.8%
- +30d: -46.8%
- +90d: -42.5%

Negative-share is 79.2% at +1h, 81.1% at +4h, 84.9% at +7d, and above 86% at +90d among available rows.

Hypothesis: the announcement window has immediate downside convexity, but entry quality depends heavily on liquidity and borrow/perp availability. Chasing after a large first candle can be fragile because rebounds/pumps exist.

Confidence: high for directionality, medium for tradability because liquidity and borrow constraints are not fully modeled.

### 3. Delisting Pumps Are Real But Usually Unstable

Among 110 spot delisting pump rows:

- Pump20 frequency: 24/110 = 21.8%.
- Pump-and-dump frequency: 23/110 = 20.9%.
- Median max-return windows are still negative through +7d, but the right tail creates squeeze risk.
- Median post-pump drawdown is about -65.6% from post-announcement high.

Hypothesis: post-delisting pumps are often exit-liquidity/squeeze events rather than durable recovery. A short framework should avoid entering directly into abnormal positive-volume impulses unless it has explicit reversion confirmation and stop logic.

Confidence: medium. Four pump rows require manual review; fallback spikes can exaggerate extreme cases.

### 4. Tag-To-Delisting Is Often Delayed

For 85 `delisted_after_tag` cases:

- Median days from Monitoring Tag to delisting: 60.
- 25th percentile: 30 days.
- 75th percentile: 182 days.
- 90th percentile: 280 days.

Hypothesis: the short opportunity is often not just the announcement candle. A delayed-collapse regime exists where deterioration may continue for weeks/months after the tag, especially if recovery attempts fail.

Confidence: medium-high. Timing is from official events, but the causal chain is not proven.

### 5. Tag Removal Is Not A Universal Bullish Reset

Tag removal cases are small:

- `TAG_REMOVED_AND_RECOVERED`: 7.
- `TAG_REMOVED_BUT_NOT_RECOVERED`: 3.
- Monitoring Tag removal median +7d alt-adjusted return: +12.1%, but +30d median: -13.3%.

Hypothesis: tag removal can trigger or coincide with short-term relief, but durable recovery must be validated by sustained closes above pre-tag baseline. A single bounce after removal is not enough.

Confidence: low-medium due small sample.

### 6. Pair Removal Control Group Is Different

For `SPOT_PAIR_REMOVED`, alt-benchmark-adjusted median returns:

- +1h: -0.1%
- +24h: -0.9%
- +7d: -2.2%
- +30d: -6.7%
- +90d: -16.1%

This is weaker than tag/delisting reactions and should not be mixed with token-level delisting.

Hypothesis: pair removal may indicate marginal liquidity decay, but it is not equivalent to existential token risk.

Confidence: high for separation from token delisting.

## Short-Entry Archetypes

### Archetype A: Announcement Shock Short

Trigger universe:

- `SPOT_TOKEN_DELISTING_ANNOUNCED`.
- Exclude pair-removal only.
- Exclude low-confidence/manual-review token-level classification.

Observed pattern:

- Median +1h/+4h/+24h alt-adjusted returns are all materially negative.
- Left tail is large; +7d median alt-adjusted return is around -35.8%.

Research entry idea:

- Avoid entering after a vertical positive pump candle.
- Prefer failed rebound below event VWAP or below pre-event 7d baseline.
- Confirm with abnormal volume plus inability to reclaim 90% of baseline.

Risk controls:

- Invalidation if price sustains above 90% or 100% pre-event baseline for 3 daily closes.
- Hard stop should account for pump20 risk: roughly one in five delisting events had +20% pump behavior.

Confidence: medium-high for event direction; medium for execution.

### Archetype B: Delisting Pump Fade

Trigger universe:

- Delisting announcement with `pump20_flag=yes`.
- Abnormal volume and failure to sustain above baseline.
- Exclude suspicious fallback spike unless manually verified.

Observed pattern:

- 23 pump-and-dump cases.
- Median post-pump drawdown is severe.

Research entry idea:

- Do not short first pump impulse mechanically.
- Wait for break of intraday pump low, VWAP failure, or loss of 90% baseline after pump.
- Require volume exhaustion or failed second push.

Risk controls:

- Invalidate if sustained 90%/100% baseline recovery occurs.
- Manual review required for fallback-driven pumps and low-liquidity symbols.

Confidence: medium. Needs intraday execution-level testing beyond event windows.

### Archetype C: Failed Monitoring-Tag Recovery

Trigger universe:

- `MONITORING_TAG_ADDED`.
- No sustained recovery after initial drawdown.
- 7d/30d alt-adjusted underperformance.

Observed pattern:

- Monitoring Tag +30d median alt-adjusted return: -20.9%.
- +90d median: -33.9%.
- `failed_tag_recovery` screen had median +30d alt-adjusted return near -15.6% and +90d near -39.5%.

Research entry idea:

- Avoid immediate tag-candle chase unless spread/liquidity is acceptable.
- Wait for failed reclaim of pre-tag 7d VWAP/median baseline.
- Enter on lower-high structure after bounce.

Risk controls:

- Invalidate on 3 consecutive daily closes above 90% pre-tag baseline.
- Reduce confidence if benchmark gaps or fallback-provider-unavailable are present.

Confidence: medium-high for population drift, medium for timing.

### Archetype D: Delisted Without Known Prior Tag

Trigger universe:

- `DELISTED_WITHOUT_KNOWN_PRIOR_TAG`.

Observed pattern:

- Median +24h raw return: -12.3%.
- Median +7d raw return: -38.2%.
- Median +90d raw return: -52.7%.
- Pump-and-dump rate: 16%.

Research entry idea:

- Treat as high-shock, low-warning event.
- Post-announcement short setups may exist after first liquidity repricing.

Risk controls:

- Higher uncertainty because absence of known tag may be parser/source limitation or Binance policy path, not necessarily no prior market warning.

Confidence: medium.

## Entry Timing Signals To Research

- Event-time shock: +1h/+4h failure after Monitoring Tag or delisting announcement.
- Failed rebound: price cannot reclaim event VWAP or 90% pre-tag/pre-delisting baseline.
- Market-adjusted underperformance: BTC/ETH/alt-adjusted returns remain negative after +24h/+7d.
- Recovery failure: no `recovery_90_sustained` within 90d.
- Event stacking: multiple risk events or transitions from tag to Vote-to-Delist to delisting.
- Liquidity deterioration proxy: volume/price gaps, missing Binance prices after delisting, fallback-only continuation.

## Stop And Invalidation Concepts

- Baseline invalidation: 3 daily closes above 90% pre-tag baseline for risk-tag shorts.
- Full invalidation: 3 daily closes above 100% baseline.
- Pump invalidation: post-delisting pump holds above 90% baseline rather than reversing.
- Data invalidation: benchmark gap, unresolved symbol, fallback unavailable, or suspicious fallback spike.
- Event invalidation: tag removal followed by sustained recovery.

## Take-Profit Research Targets

- First target: +24h or +7d median move for the specific event/scenario cluster.
- Second target: 30d median underperformance for tag-to-collapse scenarios.
- Tail target: post-delisting final-trading decay, only where Binance/fallback data is reliable.

Avoid one-size targets: pair-removal, futures-only, Monitoring Tag, and spot delisting have materially different distributions.

## Data Quality Guardrails

Never trade/research as clean signal without flags:

- `unresolved_pair_or_symbol`
- `fallback_provider_unavailable`
- `benchmark_gap`
- `true_data_gap`
- `suspicious_fallback_spike`
- `manual_review_required`

Known manual-review symbols include parser/non-standard artefacts such as `REMOVE` and unresolved unknown outcome rows.

## Next Research Tests

1. Build a clean core universe excluding `PAIR_REMOVAL_ONLY`, `UNKNOWN_MANUAL_REVIEW`, stablecoin-like assets, wrapped assets, and unresolved symbols.
2. Compute path features from 1h and 15m candles: max adverse excursion, max favorable excursion, VWAP reclaim failure, and pump duration.
3. Split delisting events into immediate collapse, pump-then-fade, and no-liquidity cases.
4. Compare failed vs recovered Monitoring Tag assets by pre-event drift, event stacking, volume change, and market-adjusted returns.
5. Add borrow/perp availability and funding/open-interest data before calling any setup tradable.
6. Bootstrap scenario medians and tail quantiles to avoid overfitting small clusters.
