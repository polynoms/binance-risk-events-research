# Derivatives Data Acquisition Plan

Generated at UTC: 2026-05-27.

Scope: fill the shortability gap for the Monitoring Tag candidate rule `immediate_1h_confirmation + negative_1h_confirmation`.

This is data acquisition, not strategy optimization. The objective is to determine whether each historical candidate could plausibly have been shorted around `entry_time`.

## Why This Layer Is Needed

The current research stack shows a Monitoring Tag market signal in spot OHLCV, but live execution is not proven. A short trade requires either:

- an available derivatives instrument, preferably a USD-M perpetual contract, or
- spot margin borrow availability and sufficient borrow capacity.

The current `futures_exchangeInfo` snapshot is not historical proof. It only describes Binance futures metadata at the snapshot time. It cannot prove that a symbol was available at a 2023, 2024, 2025, or early-2026 entry timestamp.

## Required Evidence

For each candidate trade, we need timestamp-local evidence around `entry_time`.

### 1. Futures / Perp Listing Status

Required fields:

- candidate token
- candidate futures symbol, e.g. `TOKENUSDT`, `TOKENBUSD`
- entry timestamp UTC
- evidence that the futures contract existed around entry
- evidence that the contract was not already delisted before entry
- confidence level

Best evidence:

- historical USD-M futures klines around entry
- funding rate records around entry
- open interest records around entry
- official listing/delisting announcements where publication/effective windows bracket entry

Not sufficient:

- current exchangeInfo listing
- current status such as `TRADING` or `SETTLING`

### 2. Futures OHLCV Around Entry

Use Binance USD-M futures historical klines around entry, ideally:

- `1h` klines from `entry_time - 48h` to `entry_time + 48h`
- optional `15m` klines if needed later

If non-empty klines are returned for the candidate futures symbol around entry, classify as strong evidence that the futures contract existed and could be traded at least at the market-data level.

### 3. Funding Rate Around Entry

Use Binance USD-M funding-rate endpoint around entry.

Funding records are useful because perpetual contracts have periodic funding. Funding availability around entry increases confidence that the contract was an active perp. Missing funding does not necessarily prove no perp, because API history can be incomplete or symbol history may be unavailable.

### 4. Open Interest Around Entry

Use Binance futures open-interest history if available for the historical window.

Open interest data is useful for execution feasibility:

- non-zero OI suggests real short/long capacity existed
- rapidly collapsing OI around risk events may imply poor execution or forced exits

If the public API only supports limited lookback, mark `oi_api_unavailable_or_limited` instead of treating missing OI as no contract.

### 5. Announcement Linkage

Use `events.csv` for official futures delisting announcements:

- If a futures delisting announcement window covers `entry_time`, this can infer that the contract existed before effective delisting.
- If the delisting effective date is before `entry_time`, mark the candidate as blocked for that contract.
- If only a future delisting announcement appears after entry, do not treat that as proof at entry.

### 6. Cross-Exchange Coverage

For v1, the minimal collector focuses on Binance USD-M futures. If Binance evidence is missing, later layers can query:

- OKX swaps
- Bybit USDT perpetuals
- Gate futures
- MEXC futures
- other CCXT venues

Cross-exchange coverage should be stored separately because execution venue, liquidity, fees, and funding mechanics differ from Binance.

## Output Classification

Each candidate should receive one or more typed statuses:

- `confirmed_binance_perp`: direct evidence from Binance futures OHLCV/funding/OI around entry
- `inferred_from_futures_klines`: klines exist around entry, even if funding/OI is missing
- `funding_available`: funding records exist around entry
- `oi_available`: open interest records exist around entry
- `no_binance_perp_evidence`: no local or API evidence found
- `api_unavailable`: API error, timeout, rate limit, or endpoint limitation prevented a conclusion
- `manual_review_needed`: conflicting evidence, symbol ambiguity, BUSD sunset, rebrand, redenomination, or announcement ambiguity

## Data Quality Rules

- Preserve unknowns explicitly.
- Do not overwrite raw cache without keeping request metadata.
- Do not fail the full run on one symbol.
- Use retry/backoff and per-request timeout.
- Write incremental outputs so resume can continue.
- Log request URL, parameters, timestamp, HTTP status, and row count.
- Do not use current exchangeInfo as historical proof.

## Minimal Collector Scope

The first collector should:

1. Read `monitoring_shortability.csv`.
2. Expand candidate futures symbols from `futures_symbol_candidate`.
3. For each symbol and entry:
   - query USD-M futures `1h` klines around entry
   - query funding rate around entry
   - query open interest history around entry if endpoint allows
4. Cache raw responses under `data/raw/derivatives_availability/`.
5. Write `data/processed/derivatives_availability.csv` incrementally.
6. Write `docs/derivatives_availability_quality_report.md`.
7. Recompute `data/processed/monitoring_strategy_tradeable_subset_summary.csv` for confirmed/inferred shortable subsets.

## Expected Outcomes

Possible outcomes:

- Enough confirmed/inferred Binance perp evidence exists: the Monitoring Tag candidate can move to execution simulation with derivatives costs.
- Most rows remain unknown: the market signal remains interesting, but live shortability is unproven.
- Best historical returns are mostly not shortable: the strategy thesis weakens materially.

No outcome should be interpreted as live tradability without borrow/perp availability, spreads, funding, and order book depth.
