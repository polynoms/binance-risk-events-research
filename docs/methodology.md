# Methodology v1

This methodology is locked before the full historical collection run. Thresholds are stored in `config/research_thresholds.yaml` and should not be changed retroactively to fit observed results.

## Scope

The study covers Binance Global official events from `2023-07-26` through `2026-05-26`.

Primary announcement source is Binance English Support announcements at `binance.com/en/support/announcement`. Translated or mirrored official Binance pages are fallback only when an English original is unavailable.

Primary price source is Binance Spot OHLCV. Binance USD-M Futures OHLCV, funding, and open interest are used for futures-only events when available. If Binance Spot price becomes unavailable after delisting, v1 fallback uses public CCXT CEX data first because CoinGecko public API was rate-limited/unavailable in the current environment. CoinGecko remains optional, and DEX/on-chain data is deferred. Fallback prices must be marked with `price_source` and exchange.

## Event Types

- `MONITORING_TAG_ADDED`: Binance announces that the Monitoring Tag is added to a token.
- `MONITORING_TAG_REMOVED`: Binance announces that the Monitoring Tag is removed from a token.
- `SEED_TAG_ADDED`: Binance announces that the Seed Tag is added to a token.
- `SEED_TAG_REMOVED`: Binance announces that the Seed Tag is removed from a token.
- `VOTE_TO_DELIST_STARTED`: official Binance Vote to Delist campaign starts.
- `VOTE_TO_DELIST_RESULT`: official Binance Vote to Delist result is published.
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: Binance announces removal of spot trading for the token or all relevant spot pairs for the token.
- `FUTURES_CONTRACT_DELISTING_ANNOUNCED`: Binance announces USD-M futures contract delisting, settlement, or removal. COIN-M is included only if it is a risk/delisting event, not normal delivery expiry.
- `SPOT_PAIR_REMOVED`: Binance removes one or more spot pairs while the token remains tradable on other Binance spot pairs.

Spot pair removal is not token delisting. It is a control class.

## Ambiguity Policy

Clean classification is more important than completeness. Any case is marked `manual_review_required = true` if:

- `confidence_score < 0.75`;
- token-level vs pair-level status is unclear;
- tag type is unclear;
- effective datetime is unclear or conflicting;
- rebrand, token swap, redenomination, or ticker reuse may affect identity;
- price source is uncertain;
- announcement text is not an English original and no English original is found.

## Baselines

The event timestamp price is not the main baseline. For each event:

- `baseline_vwap_7d`: VWAP over the 7 days before the event.
- `baseline_median_close_7d`: median daily close over the 7 days before the event.
- `baseline_close_1d`: daily close one day before the event.
- `baseline_median_close_30d`: sensitivity baseline.

Recovery after Monitoring Tag or later delisting announcement uses pre-tag baseline when a prior tag exists. If there was no known tag, recovery uses pre-delisting-announcement baseline.

## Returns

For each event window, compute:

- raw return;
- BTC-adjusted return;
- ETH-adjusted return;
- equal-weight Binance USDT altcoin benchmark-adjusted return, excluding the studied token.

The v1 altcoin benchmark uses available Binance Spot USDT candles. Historical universe snapshots are deferred to v2.

## Windows

Pre-event windows:

- `-30d`, `-14d`, `-7d`, `-3d`, `-1d`, `-24h`, `-4h`, `-1h`

Post-event windows:

- `+1h`, `+4h`, `+12h`, `+24h`, `+3d`, `+7d`, `+14d`, `+30d`, `+60d`, `+90d`

For delisting announcements, also compute max pump, max drawdown, and final Binance trading price until effective delisting time when available.

## Recovery Logic

- `recovery_90_touch`: price traded at or above 90% of baseline at least once.
- `recovery_100_touch`: price traded at or above 100% of baseline at least once.
- `recovery_90_sustained`: at least 3 consecutive daily closes above 90% of baseline.
- `recovery_100_sustained`: at least 3 consecutive daily closes above 100% of baseline.

Single wicks are touch events only, never sustained recovery.

## Pump Logic

After delisting announcement:

- pump exists if max return is at least 20% and volume z-score is at least 2.0;
- pump-and-dump requires a sharp post-announcement rise, abnormal volume, subsequent drawdown of at least 30% from the post-announcement high, and no sustained recovery.

## Scenario Classification

Each token lifecycle receives one `primary_scenario` and optional `secondary_flags`.

Primary scenarios:

- `IMMEDIATE_DUMP_AFTER_TAG`
- `SLOW_BLEED_AFTER_TAG`
- `TEMPORARY_PANIC_THEN_RECOVERY`
- `TAG_REMOVED_AND_RECOVERED`
- `TAG_REMOVED_BUT_NOT_RECOVERED`
- `TAG_TO_DELISTING_TO_COLLAPSE`
- `DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP`
- `DELISTING_ANNOUNCEMENT_PUMP_WITH_PARTIAL_RECOVERY`
- `NO_CLEAR_REACTION`
- `PRICE_MOVED_BEFORE_OFFICIAL_ANNOUNCEMENT`
- `DELISTED_WITHOUT_KNOWN_PRIOR_TAG`
- `PAIR_REMOVAL_ONLY`

If pre-announcement movement coexists with a stronger lifecycle scenario, it is stored as a secondary flag.

## Exclusions From Core Scenario Metrics

The raw dataset includes stablecoins, wrapped assets, leveraged tokens, fan tokens, BETH/WBETH-like assets, and redenominated/rebranded assets. These may be excluded from aggregate scenario metrics when they distort interpretation, with exclusions listed in the report.

## Limitations

The study is retrospective and descriptive. It does not prove leaks, causality, or provide investment recommendations. Market regime, survivorship bias, low liquidity, fallback price differences, ticker reuse, and incomplete public data are material limitations.
