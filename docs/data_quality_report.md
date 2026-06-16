# Data Quality Report v1

Generated at UTC: 2026-05-27T01:08:20.943070+00:00

## Coverage

- Events: 1277
- Lifecycle rows: 544
- Price-resolution rows: 529
- Price-window rows: 22050
- Recovery rows: 270
- Pump rows: 110
- Manual-review events: 12

## Event Distribution

- `SPOT_PAIR_REMOVED`: 824
- `MONITORING_TAG_ADDED`: 124
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 110
- `FUTURES_CONTRACT_DELISTING_ANNOUNCED`: 93
- `SEED_TAG_ADDED`: 69
- `SEED_TAG_REMOVED`: 23
- `VOTE_TO_DELIST_RESULT`: 15
- `MONITORING_TAG_REMOVED`: 11
- `VOTE_TO_DELIST_STARTED`: 8

## Missing And Fallback

- Missing price rows: 2340
- Benchmark gap rows: 392
- Fallback-provider-unavailable tokens: 70
- True-data-gap tokens: 226
- Expected post-delisting missing tokens: 70
- Suspicious fallback spike cases: 4
- Low-liquidity fallback cases: 0

## Missing Reason Breakdown

- `true_data_gap`: 1557
- `true_data_gap;benchmark_gap`: 345
- `unresolved_pair_or_symbol`: 212
- `expected_post_delisting_missing;fallback_provider_unavailable`: 181
- `expected_post_delisting_missing;fallback_provider_unavailable;benchmark_gap`: 41
- `unresolved_pair_or_symbol;benchmark_gap`: 4

## Manual Review Candidates

- Event rows marked manual review remain in `manual_review_events.csv`.
- Scenario rows marked manual review remain in `scenario_classification.csv`.
- Known parser artefact candidates include unresolved symbols such as `REMOVE` and non-standard announcement-derived symbols.
