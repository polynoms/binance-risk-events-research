# Bottom/Rebound Full Report

## Run Filters

- risk_only: True
- control_only: False
- event_types: ['MONITORING_TAG_ADDED', 'MONITORING_TAG_REMOVED', 'SPOT_TOKEN_DELISTING_ANNOUNCED', 'VOTE_TO_DELIST_RESULT', 'VOTE_TO_DELIST_STARTED']
- start_index: 0
- end_index: None

## All Anchors

- tokens_requested: 1
- tokens_processed: 1
- anchor_events: {'MONITORING_TAG_ADDED': 1}
- missing_1h_path: []
- absolute_bottoms_found: 1
- tradable_signals_found: 0
- signal_quality_rows: 0
- epic_like_rows: 0
- manual_review_count: 1

## Token-Risk Relevant Anchors Only

- token_risk_tokens_processed: 1
- token_risk_anchor_events: {'MONITORING_TAG_ADDED': 1}
- token_risk_missing_1h_path: []
- token_risk_absolute_bottoms_found: 1
- token_risk_tradable_signals_found: 0
- token_risk_epic_like_rows: 0
- token_risk_manual_review_count: 1

Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.
