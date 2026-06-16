# Bottom/Rebound Full Report

## Run Filters

- risk_only: True
- control_only: False
- event_types: ['MONITORING_TAG_ADDED', 'MONITORING_TAG_REMOVED', 'SPOT_TOKEN_DELISTING_ANNOUNCED', 'VOTE_TO_DELIST_RESULT', 'VOTE_TO_DELIST_STARTED']
- start_index: 50
- end_index: 75

## All Anchors

- tokens_requested: 25
- tokens_processed: 25
- anchor_events: {'MONITORING_TAG_ADDED': 20, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 5}
- missing_1h_path: ['IDRT']
- absolute_bottoms_found: 24
- tradable_signals_found: 17
- signal_quality_rows: 17
- epic_like_rows: 2
- manual_review_count: 13

## Token-Risk Relevant Anchors Only

- token_risk_tokens_processed: 25
- token_risk_anchor_events: {'MONITORING_TAG_ADDED': 20, 'SPOT_TOKEN_DELISTING_ANNOUNCED': 5}
- token_risk_missing_1h_path: ['IDRT']
- token_risk_absolute_bottoms_found: 24
- token_risk_tradable_signals_found: 17
- token_risk_epic_like_rows: 2
- token_risk_manual_review_count: 13

Look-ahead protection: tradable signals are generated only after observed confirmation candles; future lows and future max rebounds are only used for outcome evaluation.
