# Bottom/Rebound Full Report

## Run Filters

- risk_only: True
- control_only: False
- event_types: ['MONITORING_TAG_ADDED', 'MONITORING_TAG_REMOVED', 'SPOT_TOKEN_DELISTING_ANNOUNCED', 'VOTE_TO_DELIST_RESULT', 'VOTE_TO_DELIST_STARTED']
- start_index: 0
- end_index: 25

## All Anchors

- tokens_requested: 25
- tokens_processed: 25
- anchor_events: {'MONITORING_TAG_ADDED': 21, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 3, 'VOTE_TO_DELIST_STARTED': 1}
- missing_1h_path: ['CML']
- absolute_bottoms_found: 24
- tradable_signals_found: 17
- signal_quality_rows: 17
- epic_like_rows: 3
- manual_review_count: 16

## Token-Risk Relevant Anchors Only

- token_risk_tokens_processed: 25
- token_risk_anchor_events: {'MONITORING_TAG_ADDED': 21, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 3, 'VOTE_TO_DELIST_STARTED': 1}
- token_risk_missing_1h_path: ['CML']
- token_risk_absolute_bottoms_found: 24
- token_risk_tradable_signals_found: 17
- token_risk_epic_like_rows: 3
- token_risk_manual_review_count: 16

Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.
