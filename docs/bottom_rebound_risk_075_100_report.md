# Bottom/Rebound Full Report

## Run Filters

- risk_only: True
- control_only: False
- event_types: ['MONITORING_TAG_ADDED', 'MONITORING_TAG_REMOVED', 'SPOT_TOKEN_DELISTING_ANNOUNCED', 'VOTE_TO_DELIST_RESULT', 'VOTE_TO_DELIST_STARTED']
- start_index: 75
- end_index: 100

## All Anchors

- tokens_requested: 25
- tokens_processed: 25
- anchor_events: {'MONITORING_TAG_ADDED': 18, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 7}
- missing_1h_path: ['NON']
- absolute_bottoms_found: 24
- tradable_signals_found: 12
- signal_quality_rows: 12
- epic_like_rows: 3
- manual_review_count: 13

## Token-Risk Relevant Anchors Only

- token_risk_tokens_processed: 25
- token_risk_anchor_events: {'MONITORING_TAG_ADDED': 18, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 7}
- token_risk_missing_1h_path: ['NON']
- token_risk_absolute_bottoms_found: 24
- token_risk_tradable_signals_found: 12
- token_risk_epic_like_rows: 3
- token_risk_manual_review_count: 13

Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.
