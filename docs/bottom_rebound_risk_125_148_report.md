# Bottom/Rebound Full Report

## Run Filters

- risk_only: True
- control_only: False
- event_types: ['MONITORING_TAG_ADDED', 'MONITORING_TAG_REMOVED', 'SPOT_TOKEN_DELISTING_ANNOUNCED', 'VOTE_TO_DELIST_RESULT', 'VOTE_TO_DELIST_STARTED']
- start_index: 125
- end_index: 148

## All Anchors

- tokens_requested: 22
- tokens_processed: 22
- anchor_events: {'MONITORING_TAG_ADDED': 19, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 3}
- missing_1h_path: ['VAI']
- absolute_bottoms_found: 21
- tradable_signals_found: 10
- signal_quality_rows: 10
- epic_like_rows: 1
- manual_review_count: 10

## Token-Risk Relevant Anchors Only

- token_risk_tokens_processed: 22
- token_risk_anchor_events: {'MONITORING_TAG_ADDED': 19, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 3}
- token_risk_missing_1h_path: ['VAI']
- token_risk_absolute_bottoms_found: 21
- token_risk_tradable_signals_found: 10
- token_risk_epic_like_rows: 1
- token_risk_manual_review_count: 10

Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.
