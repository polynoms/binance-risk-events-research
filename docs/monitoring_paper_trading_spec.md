# Monitoring Tag Conservative Paper Trading Spec v1

Generated at UTC: 2026-05-27.

This document defines a paper-trading protocol for research and forward testing only. It is not a live trading instruction, not investment advice, and not a claim of guaranteed profitability.

## Strategy Summary

Strategy name: `monitoring_tag_conservative_short_v1`

Research basis:

- Event-driven short-side candidate derived from Binance Monitoring Tag announcements.
- Uses post-announcement weakness confirmation.
- Requires Binance perp shortability evidence and conservative execution feasibility filters.
- Risk control v1 uses fixed stop-loss and take-profit, no trailing.

## Signal Definition

Eligible event:

- Binance Global official announcement.
- Event type: `MONITORING_TAG_ADDED`.
- Source must be official Binance announcement/support page.
- Timestamp must be normalized to UTC.

Entry signal:

1. Detect a new Monitoring Tag announcement.
2. Identify affected token symbols.
3. Wait for 1h confirmation after announcement time.
4. Compute 1h return from event reference price to the first eligible 1h confirmation close.
5. Enter paper short only if 1h return is negative.

Do not enter before the announcement timestamp. Do not enter on rumors, social posts, unofficial polls, or translated pages unless the English original is unavailable and manual review approves the event.

## Required Data Sources

Minimum required:

- Binance official announcements.
- Binance spot OHLCV for the token's primary USD-like pair.
- Binance USD-M futures klines around entry.
- Binance funding rate history around entry if available.
- 1h candles for entry confirmation and risk-control simulation.

Strongly recommended:

- Binance USD-M futures exchange/listing metadata with historical timestamp validity.
- Funding rate and open interest around entry.
- Bid/ask spread or order book snapshots around entry.
- Mark price and index price for perp execution quality.
- Exchange status / maintenance data.

Current exchangeInfo snapshot must not be used as historical proof for past availability.

## Eligibility Checks

All checks must pass:

- `event_type = MONITORING_TAG_ADDED`.
- 1h return after event is negative.
- Confirmed or inferred Binance perp availability around entry.
- `feasibility_tier in {medium, high}`.
- `low_liquidity_flag = false`.
- `abnormal_candle_gap = false`.
- `extreme_first_hour_wick_gap = false`.
- No pair-removal-only lifecycle.
- No unknown/manual-review event classification.
- No unresolved token symbol or ambiguous rebrand/swap case.
- Entry time is strictly after event time.

## Exclusion Rules

Exclude:

- `SPOT_PAIR_REMOVED` control events.
- `UNKNOWN_MANUAL_REVIEW`.
- Events where token-level vs pair-level classification is ambiguous.
- Events with unresolved symbol mapping.
- Events with no Binance perp evidence and no borrow evidence.
- Events with low liquidity, abnormal candle gap, or extreme first-hour wick/gap.
- Events during exchange outage, maintenance, suspended trading, or materially incomplete market data.
- Events where the token has a rebrand, redenomination, swap, or migration that prevents clean price continuity.

## Event De-Duplication

Deduplicate by:

- `announcement_url`
- `event_type`
- `token_symbol`
- `publication_datetime_utc`

If multiple Monitoring Tag announcements refer to the same token within a short window, use only the first valid `MONITORING_TAG_ADDED` event unless a later announcement clearly represents a new lifecycle state.

## Entry Timing

Entry is paper-recorded at the first eligible 1h close after the event confirmation window.

Reference:

- `event_time = publication_datetime_utc`
- `confirmation_time = first 1h close after event_time + 1h`
- `entry_time = confirmation_time`

If the required candle is missing, mark the signal as `missed_data_gap` and do not paper-enter.

## Position Sizing

Use fixed risk per paper trade, not fixed notional.

Suggested paper risk:

- Conservative: `0.25%` of paper account equity per trade.
- Aggressive research setting: `0.50%` of paper account equity per trade.

With a 15% stop distance:

```text
position_notional = account_equity * risk_fraction / 0.15
```

Examples:

- `0.25%` risk: position notional is about `1.67%` of account equity.
- `0.50%` risk: position notional is about `3.33%` of account equity.

Do not size by notional blindly. A token with higher slippage, wider spreads, or uncertain funding should receive lower size or be excluded from paper execution quality scoring.

## Risk Rules

Risk profile v1:

- Stop-loss: `15%` adverse move from entry.
- Take-profit: `30%` favorable move from entry.
- Max holding period: `30d`.
- Trailing stop: none.
- Round-trip cost/slippage tracked separately.

For a short:

```text
stop_price = entry_price * 1.15
take_profit_price = entry_price * 0.70
```

## Exit Rules

Exit on the first of:

1. Stop-loss touched.
2. Take-profit touched.
3. Max holding period reached.
4. Manual invalidation condition triggered.
5. Trading venue suspends the instrument before normal exit.

Same-candle ambiguity:

- If stop-loss and take-profit are both touched in the same candle, paper accounting assumes stop-loss is hit first.
- This is intentionally conservative.

## Manual Override Conditions

Manual review can block or invalidate a paper trade if:

- Binance announcement parsing is ambiguous.
- Token identity is ambiguous due to ticker reuse, swap, migration, or redenomination.
- Perp availability is not verifiable.
- Funding, open interest, or order book data is clearly broken.
- Spreads or slippage are too large for realistic execution.
- Token is suspended, halted, or settlement-only.
- Risk event overlaps with another event that changes the thesis materially.

Every manual override must include a reason and timestamp.

## Required Paper Trade Fields

Every paper trade must record:

- `paper_trade_id`
- `event_id`
- `announcement_url`
- `token_symbol`
- `spot_symbol`
- `futures_symbol`
- `event_time_utc`
- `confirmation_time_utc`
- `entry_time_utc`
- `entry_price`
- `one_hour_return`
- `eligibility_passed`
- `exclusion_reason`
- `shortability_status`
- `feasibility_tier`
- `quote_volume_24h`
- `funding_rate_at_entry`
- `open_interest_at_entry`
- `spread_bps_at_entry`
- `paper_account_equity`
- `risk_fraction`
- `position_notional`
- `stop_price`
- `take_profit_price`
- `max_exit_time_utc`
- `exit_time_utc`
- `exit_price`
- `exit_reason`
- `gross_return`
- `fees_bps`
- `slippage_bps`
- `funding_pnl`
- `net_return`
- `realized_r_multiple`
- `missed_fill_flag`
- `manual_override_flag`
- `manual_override_reason`
- `notes`

## Daily Monitoring Routine

Daily routine:

1. Check open paper trades for SL/TP/max-hold exits.
2. Record funding accrual.
3. Record open interest and volume changes.
4. Record spread/slippage estimates.
5. Check for new Binance risk announcements.
6. Check if any token has tag removal, delisting announcement, futures delisting, or trading suspension.
7. Update missed-fill and no-short-available cases.
8. Record all data gaps explicitly.

## Failure Modes

Main failure modes:

- Signal exists in spot data but no short instrument is available.
- Perp exists but liquidity is too poor.
- Funding cost overwhelms expected edge.
- First-hour negative confirmation is a delayed reaction and entry is too late.
- Stop-loss is hit frequently due to post-tag squeezes.
- Announcement parsing misses tokens or misclassifies pair removals.
- Token migration/rebrand breaks price continuity.
- Backtest overstates fill quality because it uses candles rather than order book.
- Market regime changes reduce signal reliability.

## Forward Test Evaluation

Minimum before judgment:

- At least `20` paper trades, or
- `3-6 months` of forward observation, whichever gives better coverage.

Track separately:

- Signal quality.
- Execution quality.
- Shortability availability.
- Funding drag.
- Slippage.
- Missed fills.
- No-short-available cases.
- False positives.
- Manual-review blocks.

## Strategy Invalidation Conditions

The strategy should be reconsidered or paused if:

- Confirmed shortable sample has negative median return after costs over a meaningful forward sample.
- Realized slippage/funding consistently exceeds assumptions.
- Stop-loss hit rate is materially higher than expected.
- Most valid signals are not shortable.
- Paper fills are frequently unrealistic versus observed order book.
- Event parser produces repeated false positives.
- Binance changes Monitoring Tag mechanics or announcement format.

Signal quality and execution quality must be evaluated separately.
