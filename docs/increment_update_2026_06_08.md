# Increment Update - 2026-06-08

Period scanned: `2026-05-27T00:00:00Z` to `2026-06-08T23:59:59Z`.

Primary source: Binance official announcements.

## Announcement Collection

- Candidate pages: 2
- Selected pages: 2
- Detail pages downloaded: 2
- Parsed events from automatic collector: 10
- Manual-review events from automatic collector: 0

Automatic extraction found:

- `SPOT_PAIR_REMOVED`: 7
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 3

Manual correction:

- Added missing one-letter token `D` from official Binance announcement:
  `Binance Will Delist COS, D, HIGH, MBOX on 2026-06-19`.
- Reason: parser missed one-letter symbol `D`.
- Classification: `SPOT_TOKEN_DELISTING_ANNOUNCED`, token-level event.
- Confidence: `0.96`.

Final updated `events.csv`:

- Rows: 1288
- Date range: `2023-07-27T09:45:03Z` to `2026-06-05T07:00:07Z`

## New Events

### Spot Pair Removal - Control Class

Announcement:
`Notice of Removal of Spot Trading Pairs - 2026-06-05`

Publication:
`2026-06-02T05:15:00Z`

Tokens:

- AXL
- CRV
- EGLD
- OPN
- POL
- QTUM
- SKY

Classification:

- `SPOT_PAIR_REMOVED`
- Pair-level only
- Not token-level delisting

### Spot Token Delisting

Announcement:
`Binance Will Delist COS, D, HIGH, MBOX on 2026-06-19`

Publication:
`2026-06-05T07:00:07Z`

Effective spot delisting:
`2026-06-19T03:00:00Z`

Tokens:

- COS
- D
- HIGH
- MBOX

Lifecycle impact:

- COS: `delisted_after_tag`
- HIGH: `delisted_after_tag`
- MBOX: `delisted_after_tag`
- D: `delisted_without_known_tag`

## Lifecycle Update

Updated `token_lifecycle.csv`:

- Rows: 548
- `delisted_after_tag`: 88
- `delisted_without_known_tag`: 26
- `still_tagged`: 24
- `spot_pair_removed_only`: 262
- Pair-removal invariant passed: `SPOT_PAIR_REMOVED` did not become final token delisting.

## Incremental Price Run

Scope:

- COS
- D
- HIGH
- MBOX

Output directory:

`data/processed/increment_2026_06_08/`

Price pipeline results:

- Token entities: 4
- Events covered: 15
- Spot pairs resolved: 4
- Spot pairs missing: 0
- Futures pairs resolved: 4
- Price-window rows: 270
- Missing price rows: 76
- Benchmark-gap rows: 76
- Pump rows: 4
- Fallback quality rows: 4
- Binance spot API requests: 268
- Binance API 429: 0
- Kline cache hits: 18
- Kline downloads: 6

Important limitation:

The delisting effective time is in the future (`2026-06-19T03:00:00Z`), so post-effective delisting fallback windows are expected to be incomplete until after that date.

## Direct Binance Delisting Reaction

Because the full price pipeline produced missing event windows for the fresh delisting announcement, a direct Binance 1h-kline reaction file was generated:

`data/processed/increment_2026_06_08/new_delisting_reaction_direct_binance.csv`

Event anchor:

`2026-06-05T07:00:07Z`

Returns from event 1h open:

| Token | +1h | +4h | +24h | +3d | Current | Max pump | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|
| COS | -14.50% | -27.69% | -31.54% | -29.82% | -27.69% | 0.00% | -34.08% |
| D | -15.35% | -28.26% | -35.47% | -21.51% | -29.53% | 0.12% | -38.72% |
| HIGH | -12.63% | -20.00% | -24.21% | -21.05% | -18.95% | 10.53% | -27.37% |
| MBOX | -20.54% | -25.00% | -35.71% | -39.29% | -36.61% | 14.29% | -41.96% |

## Caveats

- No new `MONITORING_TAG_ADDED` announcements were found in the scanned period.
- No new `MONITORING_TAG_REMOVED` announcements were found in the scanned period.
- Fresh delisting event windows should be recomputed after `2026-06-19T03:00:00Z`.
- The direct reaction table is a tactical supplement, not a replacement for the full price pipeline.
