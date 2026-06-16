# Bottom/Rebound Batch QA: 000_025

Full bottom/rebound run was not started. This QA covers only lifecycle slice `0:25`.

## Batch Summary

- token_entity_id processed: 20
- anchor events processed: 20
- requested lifecycle slice size: 25
- anchor event distribution:
  - `SPOT_PAIR_REMOVED`: 17
  - `MONITORING_TAG_ADDED`: 3
- absolute bottoms found: 19
- tradable signals found: 17
- signal quality rows: 17
- manual review scenarios: 7
- missing 1h path: `AI`
- 15m path: not required by the main batch; optional 15m cache exists for token-risk candidates `A2Z`, `ACA`, `AERGO`

## Scenario Distribution

- `NO_CLEAR_BOTTOM_REBOUND_PATTERN`: 11
- `MANUAL_REVIEW_REQUIRED`: 5
- `EPIC_LIKE_REBOUND`: 2
- `SLOW_BLEED_THEN_SQUEEZE`: 1
- `DEAD_CAT_BOUNCE`: 1

Important: the two raw `EPIC_LIKE_REBOUND` cases in this batch are control/pair-removal cases, not token-risk Monitoring Tag cases.

## Tradeability Tier Distribution

- `C`: 9
- `Manual Review`: 7
- `B`: 1
- `A`: 0

## Token-Risk Subset

The non-control token-risk anchors in this batch are:

- `A2Z`
- `ACA`
- `AERGO`

Their anchors are `MONITORING_TAG_ADDED`. The rest of the processed rows are mostly `SPOT_PAIR_REMOVED` controls and must not be used as token-risk short/rebound evidence.

## Counts Requested For Batch QA

- EPIC-like candidates:
  - raw: 2
  - token-risk relevant: 0
- continued bleed / death spiral:
  - raw: 0
- weak rebound:
  - raw: 2
- strong rebound without causal signal:
  - raw, using 90d rebound >= 50%: 3
  - token-risk relevant: 1 (`AERGO`)
- failed signals:
  - raw: 6
- cases requiring 15m refinement:
  - raw candidates: 18
  - token-risk candidates: 3 (`A2Z`, `ACA`, `AERGO`)

## Top Candidates For Optional 15m Refinement

Token-risk candidates:

- `A2Z`: manual-review signal, failed stop, low quote volume at low.
- `ACA`: manual-review signal, failed stop, low quote volume at low.
- `AERGO`: strong rebound without causal signal, low quote volume at low, manual review.

Control-only candidates exist in the raw batch, but they should remain outside token-risk conclusions.

## Batch Files Created

- `data/processed/bottom_analysis_000_025.csv`
- `data/processed/rebound_analysis_000_025.csv`
- `data/processed/tradable_bottom_signals_000_025.csv`
- `data/processed/signal_quality_000_025.csv`
- `data/processed/bottom_rebound_scenarios_000_025.csv`
- `data/processed/epic_like_cases_000_025.csv`
- `data/processed/bottom_rebound_case_comparison_000_025.csv`
- `docs/bottom_rebound_000_025_report.md`

## Notes

This batch is useful as a pipeline/integration test, but it is not representative analytically because it is dominated by `SPOT_PAIR_REMOVED` controls.
