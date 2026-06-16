# Execution Feature Quality Report

Generated at UTC: 2026-05-27T07:01:16.537576+00:00

## Universe

- Total lifecycle/scenario rows: 544
- Research eligible rows: 115
- Excluded or flagged rows: 429

## Exclusion Reasons

- `pair_removal_control_only`: 259
- `true_data_gap_heavy`: 78
- `fallback_provider_unavailable`: 70
- `no_resolved_binance_pair`: 26
- `manual_review_required`: 21
- `unknown_manual_review`: 15
- `unresolved_pair_or_symbol`: 9
- `benchmark_gap_heavy`: 4
- `suspicious_fallback_spike`: 4

## Feature Coverage

- Execution feature rows: 269
- Execution rows with 24h path data: 197
- Execution rows with 7d path data: 197
- Pump fade rows: 110
- Monitoring Tag path rows: 124
- Monitoring rows with 90d path data: 119

## Duplicate Checks

- clean universe duplicate token_entity_id: 0
- execution duplicate event/token: 0
- pump fade duplicate event/token: 0
- monitoring duplicate event/token: 0

## Data Quality Notes

- `PAIR_REMOVAL_ONLY` is retained in clean universe as excluded/control, not used as token-risk short signal.
- Path features use locally cached Binance 15m/1h/1d klines only. Fallback-only path reconstruction is not attempted in v1.
- Missing/fallback-heavy rows remain present with lower confidence rather than being silently dropped.
