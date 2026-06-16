# Monitoring Tag Forward Test Checklist

This checklist is for paper trading and research only. Do not use it as live execution instructions.

## Before Starting

- [ ] Confirm strategy version: `monitoring_tag_conservative_short_v1`.
- [ ] Confirm no live orders will be placed.
- [ ] Set paper account equity.
- [ ] Set risk fraction: `0.25%` default or `0.50%` aggressive research setting.
- [ ] Confirm risk rules: `SL 15%`, `TP 30%`, `max hold 30d`, no trailing.
- [ ] Confirm same-candle ambiguity rule: stop before TP.
- [ ] Confirm Binance announcement source parser is working.
- [ ] Confirm event timestamps are UTC.
- [ ] Confirm Binance spot and futures data access.
- [ ] Confirm funding and open interest collection if available.
- [ ] Confirm paper trade log path and schema.

## On New Binance Announcement

- [ ] Verify source is official Binance Global announcement.
- [ ] Verify English original if available.
- [ ] Classify event type.
- [ ] Continue only if `event_type = MONITORING_TAG_ADDED`.
- [ ] Extract all affected token symbols.
- [ ] Deduplicate by URL, event type, token, and publication timestamp.
- [ ] Check token identity for ticker reuse, rebrand, migration, swap, or redenomination.
- [ ] Flag manual review if classification is ambiguous.

## Before Entry

- [ ] Wait for 1h confirmation candle.
- [ ] Compute 1h return from event reference price.
- [ ] Continue only if 1h return is negative.
- [ ] Verify confirmed or inferred Binance perp availability around entry.
- [ ] Verify `feasibility_tier in {medium, high}`.
- [ ] Verify `low_liquidity_flag = false`.
- [ ] Verify `abnormal_candle_gap = false`.
- [ ] Verify `extreme_first_hour_wick_gap = false`.
- [ ] Verify not pair-removal-only.
- [ ] Verify no unresolved manual review.
- [ ] Record spread estimate at entry.
- [ ] Record funding rate at entry if available.
- [ ] Record open interest at entry if available.
- [ ] Record if short/perp is unavailable and mark as no-trade paper observation.

## Paper Entry

- [ ] Create `paper_trade_id`.
- [ ] Record event metadata.
- [ ] Record entry timestamp and entry price.
- [ ] Calculate position notional from risk, not from fixed notional.
- [ ] Calculate stop price: `entry_price * 1.15`.
- [ ] Calculate take-profit price: `entry_price * 0.70`.
- [ ] Calculate max exit timestamp: `entry_time + 30d`.
- [ ] Record estimated fees and slippage assumptions.
- [ ] Record missed-fill flag if entry could not be realistically filled.

## Daily Monitoring

- [ ] Check whether stop-loss was touched.
- [ ] Check whether take-profit was touched.
- [ ] Apply stop-before-TP rule if both touched in same candle.
- [ ] Check max holding period.
- [ ] Update funding accrual.
- [ ] Update spread/slippage estimates.
- [ ] Update open interest and volume if available.
- [ ] Check for tag removal, delisting announcement, futures delisting, or trading suspension.
- [ ] Record any manual override and reason.
- [ ] Record data gaps explicitly.

## Exit Logging

- [ ] Record exit timestamp.
- [ ] Record exit price.
- [ ] Record exit reason: `stop_loss`, `take_profit`, `time_exit`, `manual_exit`, `instrument_unavailable`, or `data_gap`.
- [ ] Record gross return.
- [ ] Record fees in bps.
- [ ] Record slippage in bps.
- [ ] Record funding PnL.
- [ ] Record net return.
- [ ] Record realized R multiple.
- [ ] Record notes.

## Weekly Review

- [ ] Count new signals.
- [ ] Count eligible paper entries.
- [ ] Count skipped signals.
- [ ] Count no-short-available cases.
- [ ] Count manual-review cases.
- [ ] Compare realized slippage vs assumption.
- [ ] Compare funding drag vs assumption.
- [ ] Review missed fills.
- [ ] Review false positives.
- [ ] Review any parser or classification errors.

## Minimum Evaluation Window

- [ ] Do not judge before at least `20` paper trades, unless severe execution failure appears earlier.
- [ ] Also review after `3-6 months`, even if fewer than 20 trades occur.
- [ ] Separate signal quality from execution quality.
- [ ] Separate unavailable-short cases from losing trades.

## Strategy Invalidation Watchlist

Pause or downgrade the strategy if:

- [ ] Confirmed shortable paper trades show negative median return after realistic costs.
- [ ] Stop-loss hit rate is materially worse than research expectation.
- [ ] Funding/slippage consistently consumes the expected edge.
- [ ] Most signals are not shortable.
- [ ] Order book depth is insufficient for planned paper notional.
- [ ] Parser repeatedly misclassifies events.
- [ ] Binance changes Monitoring Tag mechanics or announcement format.
- [ ] Forward behavior diverges sharply from historical risk-event path behavior.

## Required Output After Forward Test

- [ ] Paper trade log.
- [ ] Missed signal log.
- [ ] No-short-available log.
- [ ] Manual review log.
- [ ] Slippage/funding summary.
- [ ] Signal quality summary.
- [ ] Execution quality summary.
- [ ] Recommendation: continue, modify, pause, or discard.
