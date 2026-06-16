# Codex Worklog

## 2026-05-26T00:00:00Z - Research design locked

- Scope: Binance Global official announcements from 2023-07-26 through 2026-05-26.
- Methodology: `docs/methodology.md`.
- Thresholds: `config/research_thresholds.yaml`.
- Collection mode: validation sample first, then best-effort full collection.
- Data quality rule: prefer `manual_review_required` over forced classification.


## 2026-05-26T12:23:04Z - Announcement index collection
- catalogId=48 (New Cryptocurrency Listing); pages_scanned=19; keyword_hits=56; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=49 (Latest Binance News); pages_scanned=28; keyword_hits=26; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=161 (Delisting); pages_scanned=6; keyword_hits=195; endpoint=/bapi/composite/v1/public/cms/article/list/query

## 2026-05-26T12:23:04Z - Validation sample
- candidate_pages=277
- selected_pages=10
- successfully_parsed_pages=10
- parsed_events=34
- manual_review_events=8
- output=data/processed/events_validation.csv

## 2026-05-26T12:26:00Z - Announcement index collection
- catalogId=48 (New Cryptocurrency Listing); pages_scanned=19; keyword_hits=56; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=49 (Latest Binance News); pages_scanned=28; keyword_hits=26; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=161 (Delisting); pages_scanned=6; keyword_hits=195; endpoint=/bapi/composite/v1/public/cms/article/list/query

## 2026-05-26T12:26:00Z - Validation sample
- candidate_pages=277
- selected_pages=10
- successfully_parsed_pages=10
- parsed_events=38
- manual_review_events=3
- output=data/processed/events_validation.csv

## 2026-05-26T12:29:06Z - Announcement index collection
- catalogId=48 (New Cryptocurrency Listing); pages_scanned=19; keyword_hits=56; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=49 (Latest Binance News); pages_scanned=28; keyword_hits=26; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=161 (Delisting); pages_scanned=6; keyword_hits=196; endpoint=/bapi/composite/v1/public/cms/article/list/query

## 2026-05-26T12:29:06Z - Validation sample
- candidate_pages=278
- selected_pages=10
- successfully_parsed_pages=10
- parsed_events=49
- manual_review_events=3
- output=data/processed/events_validation.csv

## 2026-05-26T12:31:08Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T12:41:11Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T12:41:11Z - Validation sample
- candidate_pages=278
- selected_pages=10
- successfully_parsed_pages=10
- parsed_events=53
- manual_review_events=4
- output=data/processed/events_validation.csv

## 2026-05-26T12:49:27Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T12:49:27Z - Validation sample
- candidate_pages=278
- selected_pages=10
- successfully_parsed_pages=10
- parsed_events=53
- manual_review_events=0
- output=data/processed/events_validation.csv

## 2026-05-26T13:18:52Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:29:21Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:30:31Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:34:47Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:34:47Z - Full event parse
- candidate_pages=278
- selected_pages=278
- detail_cache_hits=232
- detail_downloaded=46
- successfully_parsed_pages=278
- parsed_events=1277
- manual_review_events=12
- output=data/processed/events.csv

## 2026-05-26T13:45:57Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:45:57Z - Full event parse
- candidate_pages=278
- selected_pages=278
- detail_cache_hits=278
- detail_downloaded=0
- successfully_parsed_pages=278
- parsed_events=1277
- manual_review_events=12
- output=data/processed/events.csv

## 2026-05-26T13:46:42Z - Reused cached announcement index
- cached_candidates=278
- source=data/raw/binance_announcements/index_hits.json

## 2026-05-26T13:46:42Z - Full event parse
- candidate_pages=278
- selected_pages=278
- detail_cache_hits=278
- detail_downloaded=0
- successfully_parsed_pages=278
- parsed_events=1277
- manual_review_events=12
- output=data/processed/events.csv

## 2026-05-26T13:58:13Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:04:07Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:04:07Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:05:18Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:16:39Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:22:03Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:23:45Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:25:10Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv

## 2026-05-26T14:27:26Z - Price collection sample
- token_entity_id_sample=11
- events_covered=20
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/recovery_analysis_sample.csv,data/processed/pump_analysis_sample.csv,data/processed/fallback_data_quality_sample.csv

## 2026-05-26T14:30:34Z - Price collection sample
- token_entity_id=11
- events_covered=20
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/price_windows_sample.parquet,data/processed/recovery_analysis_sample.csv,data/processed/pump_analysis_sample.csv,data/processed/fallback_data_quality_sample.csv

## 2026-05-26T14:31:10Z - Price collection sample
- token_entity_id=11
- events_covered=20
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_sample_resolution.csv,data/processed/price_windows_sample.csv,data/processed/price_windows_sample.parquet,data/processed/recovery_analysis_sample.csv,data/processed/pump_analysis_sample.csv,data/processed/fallback_data_quality_sample.csv

## 2026-05-26T15:09:12Z - Price collection full
- token_entity_id=25
- events_covered=54
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/price_resolution.csv,data/processed/price_windows.csv,data/processed/price_windows.parquet,data/processed/recovery_analysis.csv,data/processed/pump_analysis.csv,data/processed/fallback_data_quality.csv

## 2026-05-26T15:20:07Z - Price collection full
- token_entity_id=5
- events_covered=8
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_000_005/price_resolution.csv,data/processed/batches/batch_000_005/price_windows.csv,data/processed/batches/batch_000_005/price_windows.parquet,data/processed/batches/batch_000_005/recovery_analysis.csv,data/processed/batches/batch_000_005/pump_analysis.csv,data/processed/batches/batch_000_005/fallback_data_quality.csv

## 2026-05-26T15:21:11Z - Price collection full
- token_entity_id=5
- events_covered=8
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_000_005/price_resolution.csv,data/processed/batches/batch_000_005/price_windows.csv,data/processed/batches/batch_000_005/price_windows.parquet,data/processed/batches/batch_000_005/recovery_analysis.csv,data/processed/batches/batch_000_005/pump_analysis.csv,data/processed/batches/batch_000_005/fallback_data_quality.csv

## 2026-05-26T15:24:44Z - Price collection full
- token_entity_id=25
- events_covered=54
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_000_025/price_resolution.csv,data/processed/batches/batch_000_025/price_windows.csv,data/processed/batches/batch_000_025/price_windows.parquet,data/processed/batches/batch_000_025/recovery_analysis.csv,data/processed/batches/batch_000_025/pump_analysis.csv,data/processed/batches/batch_000_025/fallback_data_quality.csv

## 2026-05-26T15:45:34Z - Price collection full
- token_entity_id=25
- events_covered=58
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_025_050/price_resolution.csv,data/processed/batches/batch_025_050/price_windows.csv,data/processed/batches/batch_025_050/price_windows.parquet,data/processed/batches/batch_025_050/recovery_analysis.csv,data/processed/batches/batch_025_050/pump_analysis.csv,data/processed/batches/batch_025_050/fallback_data_quality.csv

## 2026-05-26T16:19:48Z - Price collection full
- token_entity_id=25
- events_covered=56
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_050_075/price_resolution.csv,data/processed/batches/batch_050_075/price_windows.csv,data/processed/batches/batch_050_075/price_windows.parquet,data/processed/batches/batch_050_075/recovery_analysis.csv,data/processed/batches/batch_050_075/pump_analysis.csv,data/processed/batches/batch_050_075/fallback_data_quality.csv

## 2026-05-26T17:03:48Z - Price collection full
- token_entity_id=25
- events_covered=61
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_075_100/price_resolution.csv,data/processed/batches/batch_075_100/price_windows.csv,data/processed/batches/batch_075_100/price_windows.parquet,data/processed/batches/batch_075_100/recovery_analysis.csv,data/processed/batches/batch_075_100/pump_analysis.csv,data/processed/batches/batch_075_100/fallback_data_quality.csv

## 2026-05-26T17:43:29Z - Price collection full
- token_entity_id=25
- events_covered=59
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_100_125/price_resolution.csv,data/processed/batches/batch_100_125/price_windows.csv,data/processed/batches/batch_100_125/price_windows.parquet,data/processed/batches/batch_100_125/recovery_analysis.csv,data/processed/batches/batch_100_125/pump_analysis.csv,data/processed/batches/batch_100_125/fallback_data_quality.csv

## 2026-05-26T18:10:50Z - Price collection full
- token_entity_id=25
- events_covered=55
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_125_150/price_resolution.csv,data/processed/batches/batch_125_150/price_windows.csv,data/processed/batches/batch_125_150/price_windows.parquet,data/processed/batches/batch_125_150/recovery_analysis.csv,data/processed/batches/batch_125_150/pump_analysis.csv,data/processed/batches/batch_125_150/fallback_data_quality.csv

## 2026-05-26T18:34:27Z - Price collection full
- token_entity_id=25
- events_covered=59
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_150_175/price_resolution.csv,data/processed/batches/batch_150_175/price_windows.csv,data/processed/batches/batch_150_175/price_windows.parquet,data/processed/batches/batch_150_175/recovery_analysis.csv,data/processed/batches/batch_150_175/pump_analysis.csv,data/processed/batches/batch_150_175/fallback_data_quality.csv

## 2026-05-26T19:04:02Z - Price collection full
- token_entity_id=25
- events_covered=62
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_175_200/price_resolution.csv,data/processed/batches/batch_175_200/price_windows.csv,data/processed/batches/batch_175_200/price_windows.parquet,data/processed/batches/batch_175_200/recovery_analysis.csv,data/processed/batches/batch_175_200/pump_analysis.csv,data/processed/batches/batch_175_200/fallback_data_quality.csv

## 2026-05-26T19:42:55Z - Price collection full
- token_entity_id=25
- events_covered=67
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_200_225/price_resolution.csv,data/processed/batches/batch_200_225/price_windows.csv,data/processed/batches/batch_200_225/price_windows.parquet,data/processed/batches/batch_200_225/recovery_analysis.csv,data/processed/batches/batch_200_225/pump_analysis.csv,data/processed/batches/batch_200_225/fallback_data_quality.csv

## 2026-05-26T20:09:43Z - Price collection full
- token_entity_id=25
- events_covered=64
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_225_250/price_resolution.csv,data/processed/batches/batch_225_250/price_windows.csv,data/processed/batches/batch_225_250/price_windows.parquet,data/processed/batches/batch_225_250/recovery_analysis.csv,data/processed/batches/batch_225_250/pump_analysis.csv,data/processed/batches/batch_225_250/fallback_data_quality.csv

## 2026-05-26T20:32:28Z - Price collection full
- token_entity_id=25
- events_covered=56
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_250_275/price_resolution.csv,data/processed/batches/batch_250_275/price_windows.csv,data/processed/batches/batch_250_275/price_windows.parquet,data/processed/batches/batch_250_275/recovery_analysis.csv,data/processed/batches/batch_250_275/pump_analysis.csv,data/processed/batches/batch_250_275/fallback_data_quality.csv

## 2026-05-26T20:58:09Z - Price collection full
- token_entity_id=25
- events_covered=59
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_275_300/price_resolution.csv,data/processed/batches/batch_275_300/price_windows.csv,data/processed/batches/batch_275_300/price_windows.parquet,data/processed/batches/batch_275_300/recovery_analysis.csv,data/processed/batches/batch_275_300/pump_analysis.csv,data/processed/batches/batch_275_300/fallback_data_quality.csv

## 2026-05-26T22:09:06Z - Price collection full
- token_entity_id=25
- events_covered=55
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_300_325/price_resolution.csv,data/processed/batches/batch_300_325/price_windows.csv,data/processed/batches/batch_300_325/price_windows.parquet,data/processed/batches/batch_300_325/recovery_analysis.csv,data/processed/batches/batch_300_325/pump_analysis.csv,data/processed/batches/batch_300_325/fallback_data_quality.csv

## 2026-05-26T22:39:30Z - Price collection full
- token_entity_id=25
- events_covered=62
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_325_350/price_resolution.csv,data/processed/batches/batch_325_350/price_windows.csv,data/processed/batches/batch_325_350/price_windows.parquet,data/processed/batches/batch_325_350/recovery_analysis.csv,data/processed/batches/batch_325_350/pump_analysis.csv,data/processed/batches/batch_325_350/fallback_data_quality.csv

## 2026-05-26T23:01:19Z - Price collection full
- token_entity_id=25
- events_covered=54
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_350_375/price_resolution.csv,data/processed/batches/batch_350_375/price_windows.csv,data/processed/batches/batch_350_375/price_windows.parquet,data/processed/batches/batch_350_375/recovery_analysis.csv,data/processed/batches/batch_350_375/pump_analysis.csv,data/processed/batches/batch_350_375/fallback_data_quality.csv

## 2026-05-26T23:18:46Z - Price collection full
- token_entity_id=25
- events_covered=56
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_375_400/price_resolution.csv,data/processed/batches/batch_375_400/price_windows.csv,data/processed/batches/batch_375_400/price_windows.parquet,data/processed/batches/batch_375_400/recovery_analysis.csv,data/processed/batches/batch_375_400/pump_analysis.csv,data/processed/batches/batch_375_400/fallback_data_quality.csv

## 2026-05-26T23:33:39Z - Price collection full
- token_entity_id=25
- events_covered=47
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_400_425/price_resolution.csv,data/processed/batches/batch_400_425/price_windows.csv,data/processed/batches/batch_400_425/price_windows.parquet,data/processed/batches/batch_400_425/recovery_analysis.csv,data/processed/batches/batch_400_425/pump_analysis.csv,data/processed/batches/batch_400_425/fallback_data_quality.csv

## 2026-05-26T23:57:54Z - Price collection full
- token_entity_id=25
- events_covered=63
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_425_450/price_resolution.csv,data/processed/batches/batch_425_450/price_windows.csv,data/processed/batches/batch_425_450/price_windows.parquet,data/processed/batches/batch_425_450/recovery_analysis.csv,data/processed/batches/batch_425_450/pump_analysis.csv,data/processed/batches/batch_425_450/fallback_data_quality.csv

## 2026-05-27T00:15:58Z - Price collection full
- token_entity_id=25
- events_covered=55
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_450_475/price_resolution.csv,data/processed/batches/batch_450_475/price_windows.csv,data/processed/batches/batch_450_475/price_windows.parquet,data/processed/batches/batch_450_475/recovery_analysis.csv,data/processed/batches/batch_450_475/pump_analysis.csv,data/processed/batches/batch_450_475/fallback_data_quality.csv

## 2026-05-27T00:40:46Z - Price collection full
- token_entity_id=25
- events_covered=63
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_475_500/price_resolution.csv,data/processed/batches/batch_475_500/price_windows.csv,data/processed/batches/batch_475_500/price_windows.parquet,data/processed/batches/batch_475_500/recovery_analysis.csv,data/processed/batches/batch_475_500/pump_analysis.csv,data/processed/batches/batch_475_500/fallback_data_quality.csv

## 2026-05-27T01:02:58Z - Price collection full
- token_entity_id=25
- events_covered=54
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_500_525/price_resolution.csv,data/processed/batches/batch_500_525/price_windows.csv,data/processed/batches/batch_500_525/price_windows.parquet,data/processed/batches/batch_500_525/recovery_analysis.csv,data/processed/batches/batch_500_525/pump_analysis.csv,data/processed/batches/batch_500_525/fallback_data_quality.csv

## 2026-05-27T01:04:51Z - Price collection full
- token_entity_id=4
- events_covered=6
- tokens_filter=
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/batches/batch_525_544/price_resolution.csv,data/processed/batches/batch_525_544/price_windows.csv,data/processed/batches/batch_525_544/price_windows.parquet,data/processed/batches/batch_525_544/recovery_analysis.csv,data/processed/batches/batch_525_544/pump_analysis.csv,data/processed/batches/batch_525_544/fallback_data_quality.csv

## 2026-05-27T01:09:10Z - Full price batch merge and scenario reports
- production_batches=22
- excluded_test_batches=data/processed/batches/batch_000_005
- price_resolution_rows=529
- price_window_rows=22050
- recovery_rows=270
- pump_rows=110
- fallback_quality_rows=529
- scenario_rows=544
- scenario_summary_rows=13
- duplicate_checks=passed
- pair_removal_control_check=passed
- outputs=data/processed/price_resolution.csv,data/processed/price_windows.csv,data/processed/price_windows.parquet,data/processed/recovery_analysis.csv,data/processed/pump_analysis.csv,data/processed/fallback_data_quality.csv,data/processed/scenario_classification.csv,data/processed/scenario_classification.parquet,data/processed/scenario_summary.csv,data/processed/scenario_summary.parquet,docs/data_quality_report.md,docs/retrospective_report.md

## 2026-05-27T07:01:50Z - Execution research layer
- inputs=data/processed/scenario_classification.csv,data/processed/price_windows.csv,data/processed/recovery_analysis.csv,data/processed/pump_analysis.csv,data/processed/fallback_data_quality.csv,data/processed/events.csv,data/processed/token_lifecycle.csv
- raw_path_source=data/raw/klines local Binance cache
- clean_research_universe_rows=544
- research_eligible_rows=115
- execution_features_rows=269
- pump_fade_features_rows=110
- monitoring_tag_path_features_rows=124
- duplicate_checks=passed
- pair_removal_eligible_check=0
- note=Path features use cached Binance klines only; fallback-only path reconstruction is not attempted in v1.
- outputs=data/processed/clean_research_universe.csv,data/processed/clean_research_universe.parquet,data/processed/execution_features.csv,data/processed/execution_features.parquet,data/processed/pump_fade_features.csv,data/processed/pump_fade_features.parquet,data/processed/monitoring_tag_path_features.csv,data/processed/monitoring_tag_path_features.parquet,docs/execution_feature_quality_report.md,docs/trading_hypothesis_summary.md

## 2026-05-27T08:27:23Z - Event-driven backtest layer v1
- hypotheses=spot_delisting_announcement_shock,delisting_pump_fade_after_failed_breakout,monitoring_tag_failed_recovery_delayed_collapse
- inputs=data/processed/clean_research_universe.csv,data/processed/execution_features.csv,data/processed/pump_fade_features.csv,data/processed/monitoring_tag_path_features.csv,data/processed/price_windows.csv,data/processed/scenario_classification.csv,data/processed/events.csv
- raw_path_source=data/raw/klines local Binance cache
- roundtrip_cost_bps=0,20
- trade_rows=1010
- ok_trade_rows=1010
- summary_rows=48
- duplicate_checks=passed
- entry_before_event_check=0
- note=Pump-fade entry requires pump20 confirmation plus subsequent failed-breakout close; Monitoring failed-recovery trigger uses only +7d return known at trigger time.
- outputs=data/processed/backtest_trades.csv,data/processed/backtest_trades.parquet,data/processed/backtest_summary.csv,data/processed/backtest_summary.parquet,docs/hypothesis_backtest_report.md

## 2026-05-27T08:37:42Z - Backtest robustness validation v1
- inputs=data/processed/backtest_trades.csv,data/processed/backtest_summary.csv,data/processed/clean_research_universe.csv,data/processed/execution_features.csv,data/processed/scenario_classification.csv,data/processed/events.csv
- cost_views_bps=0,20,50,100
- time_splits=2023H2,2024H1,2024H2,2025H1,2025H2,2026YTD
- expanded_rows=2020
- robustness_summary_rows=952
- verdicts=monitoring_tag/tag_immediate_1h robust_candidate; monitoring_tag/tag_24h_delay robust_candidate; pump_fade tail_dependent; spot_delisting_immediate tail_dependent; delayed_7d_monitoring variants tail_dependent; rebound_failure spot-delisting small_sample
- outputs=data/processed/backtest_robustness_summary.csv,data/processed/backtest_robustness_summary.parquet,data/processed/backtest_robustness_trades_expanded.csv,docs/backtest_robustness_report.md

## 2026-05-27T09:56:04Z - Monitoring strategy refinement v1
- scope=Monitoring Tag immediate/24h only; spot delisting and pump-fade not modified
- inputs=data/processed/backtest_trades.csv,data/processed/backtest_robustness_summary.csv,data/processed/execution_features.csv,data/processed/monitoring_tag_path_features.csv,data/processed/clean_research_universe.csv,data/processed/scenario_classification.csv,data/processed/price_windows.csv
- cost_views_bps=0,20,50,100
- refinement_rows=525
- execution_variants=immediate_1h_confirmation,24h_delay,24h_failed_recovery_trigger,7d_delay_diagnostic,7d_failed_recovery_diagnostic
- recommendation=immediate_1h_confirmation + negative_1h_confirmation
- recommendation_20bps=n=89,median_return=0.071171,average_return=0.088677,profit_factor=2.199790,average_return_ex_top5=0.055304
- note=Scenario and post-path filters are reported as diagnostics but excluded from recommended entry-feasible candidate selection when they require future information.
- outputs=data/processed/monitoring_strategy_refinement.csv,data/processed/monitoring_strategy_refinement.parquet,docs/monitoring_strategy_refinement_report.md

## 2026-05-27T10:41:41Z - Monitoring live feasibility v1
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation only
- inputs=data/processed/monitoring_strategy_refinement.csv,data/processed/backtest_trades.csv,data/processed/execution_features.csv,data/processed/price_windows.csv,data/processed/clean_research_universe.csv,data/processed/events.csv,data/processed/scenario_classification.csv
- local_path_source=data/raw/klines spot/futures 1h cache
- candidate_trades=89
- feasibility_tiers=high:0,medium:55,low:34
- liquidity_flags=low_liquidity:22,extreme_wick_gap:5,abnormal_candle_gap:8,missing_1h_path:0,fallback_only_path:0
- shortability_proxy=futures_available_around_event:0,borrow_availability_unknown:89
- cost_views_bps=20,50,100,200,500
- note=Futures cache did not prove derivative availability around candidate event times; borrow/shortability is the primary blocker before live tradability claims.
- outputs=data/processed/monitoring_live_feasibility.csv,data/processed/monitoring_live_feasibility.parquet,data/processed/monitoring_live_feasibility_summary.csv,docs/monitoring_live_feasibility_report.md

## 2026-05-27T11:04:53Z - Monitoring shortability layer v1
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation only
- inputs=data/processed/monitoring_live_feasibility.csv,data/processed/events.csv,data/processed/token_lifecycle.csv,data/processed/price_windows.csv,data/raw/klines/futures_exchange_info.json,data/raw/klines/futures local cache
- candidate_trades=89
- confirmed_binance_perp_from_local_futures_ohlcv=0
- inferred_perp_from_active_futures_delisting_announcement=0
- unknown_shortability=84
- low_or_blocked_shortability=5
- funding_cache_available=0
- open_interest_cache_available=0
- current_futures_exchangeinfo_snapshot_utc=2026-05-26T13:54:55Z
- current_futures_exchangeinfo_candidate_matches=52
- note=Current exchangeInfo is recorded for lookup context only and is not used as historical proof at 2023-2026 entry timestamps.
- outputs=data/processed/monitoring_shortability.csv,data/processed/monitoring_shortability.parquet,data/processed/monitoring_strategy_tradeable_subset_summary.csv,docs/shortability_data_gaps_report.md

## 2026-05-27T12:03:08Z - Monitoring perp subset diagnostics
- scope=diagnose Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation shortability subsets; no strategy optimization
- inputs=data/processed/derivatives_availability.csv,data/processed/monitoring_live_feasibility.csv,data/processed/monitoring_strategy_refinement.csv,data/processed/backtest_trades.csv,data/processed/execution_features.csv,data/processed/price_windows.csv,data/processed/events.csv,data/processed/scenario_classification.csv
- diagnostic_rows=89
- comparison_groups=A_full_confirmed_or_inferred_binance_perp:52,B_medium_feasibility_confirmed_shortable:30,C_no_binance_perp_evidence:37
- key_result_100bps=A_full_confirmed_median=-0.176667,A_full_confirmed_avg=0.051852;B_medium_confirmed_median=0.109853,B_medium_confirmed_avg=0.097506;C_no_perp_evidence_median=0.104563,C_no_perp_evidence_avg=0.121186
- diagnosis=full confirmed subset is dragged down by 22 low-feasibility confirmed rows with low liquidity/gap/wick profile; medium-feasibility confirmed core remains positive
- outputs=data/processed/monitoring_perp_subset_diagnostics.csv,data/processed/monitoring_perp_subset_diagnostics.parquet,data/processed/monitoring_perp_subset_diagnostics_summary.csv,docs/monitoring_perp_subset_diagnostics_report.md

## 2026-05-27T12:08:27Z - Monitoring conservative strategy backtest
- scope=one conservative candidate only; no optimization
- rule=Monitoring Tag + immediate_1h_confirmation + negative_1h_confirmation + confirmed/inferred Binance perp + medium/high feasibility + no low liquidity + no abnormal candle gap + no extreme first-hour wick/gap
- inputs=data/processed/monitoring_perp_subset_diagnostics.csv,data/processed/monitoring_live_feasibility.csv,data/processed/derivatives_availability.csv,data/processed/backtest_trades.csv,data/processed/execution_features.csv,data/processed/price_windows.csv,data/processed/events.csv
- trades=30
- validation=duplicates:0,entry_after_event_violations:0,pair_removal_only:0,manual_review:0,shortability_violations:0
- result_100bps=win_rate:0.566667,median_return:0.109853,average_return:0.097506,profit_factor:2.273662,avg_ex_top5:0.061832,avg_ex_bottom5:0.127970
- risk=largest_mae:2.028,mae_gt_20pct:14,mae_gt_30pct:11,mae_gt_50pct:5
- note=confidence limited by n=30; suitable for paper/forward testing research only, not production/live advice
- outputs=data/processed/monitoring_conservative_strategy_trades.csv,data/processed/monitoring_conservative_strategy_trades.parquet,data/processed/monitoring_conservative_strategy_summary.csv,data/processed/monitoring_conservative_strategy_summary.parquet,docs/monitoring_conservative_strategy_report.md

## 2026-05-27T12:14:52Z - Monitoring risk-control simulation
- scope=post-entry risk controls for conservative Monitoring Tag candidate; no strategy optimization
- inputs=data/processed/monitoring_conservative_strategy_trades.csv,data/processed/monitoring_conservative_strategy_summary.csv,data/processed/price_windows.csv,data/processed/execution_features.csv,data/raw/klines spot 1h cache
- stop_losses=15pct,20pct,30pct,40pct,50pct
- take_profits=10pct,20pct,30pct,50pct
- holding_windows=24h,7d,30d
- trailing_variants=none,breakeven_after_10,trail15_after_20,trail20_after_30
- simulation_rows=7200
- summary_rows=240
- valid_path_rows=all
- recommended_profile_1=SL15pct_TP30pct_hold30d_no_trailing
- recommended_profile_2_diagnostic=SL50pct_TP50pct_hold30d_trail20_after_30
- note=1h OHLCV path simulation with conservative same-candle stop-before-TP handling; trailing profiles require caution because intrabar ordering is unresolved
- outputs=data/processed/monitoring_risk_control_simulation.csv,data/processed/monitoring_risk_control_simulation.parquet,data/processed/monitoring_risk_control_summary.csv,docs/monitoring_risk_control_report.md

## 2026-05-27T12:18:44Z - Monitoring paper trading spec and alerting design
- scope=paper/forward-test protocol only; no live trading and no new strategy variants
- strategy=Monitoring Tag + immediate_1h_confirmation + negative_1h_confirmation + confirmed/inferred Binance perp + medium/high feasibility + no low liquidity/gap/wick + SL15pct + TP30pct + max_hold30d
- artifacts=docs/monitoring_paper_trading_spec.md,docs/monitoring_alert_schema.json,data/processed/monitoring_paper_trade_log_template.csv,docs/monitoring_forward_test_checklist.md
- qa=json_schema_valid:true,trade_log_columns:38
- note=Spec separates signal quality from execution quality and requires tracking no-short-available, funding, slippage, missed fills, and manual review cases.

## 2026-05-27T11:17:52Z - Derivatives availability collector
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation candidate symbols
- output_rows=6
- new_api_request_attempts=18
- skipped_existing_rows=0
- confirmed_symbol_rows=0
- api_unavailable_rows=6
- outputs=data/processed/derivatives_availability.csv,data/processed/derivatives_availability.parquet,docs/derivatives_availability_quality_report.md,data/processed/monitoring_strategy_tradeable_subset_summary.csv

## 2026-05-27T11:40:12Z - Derivatives availability collector
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation candidate symbols
- output_rows=178
- new_api_request_attempts=516
- skipped_existing_rows=6
- confirmed_symbol_rows=52
- api_unavailable_rows=123
- outputs=data/processed/derivatives_availability.csv,data/processed/derivatives_availability.parquet,docs/derivatives_availability_quality_report.md,data/processed/monitoring_strategy_tradeable_subset_summary.csv

## 2026-05-27T11:41:11Z - Derivatives availability collector
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation candidate symbols
- output_rows=178
- new_api_request_attempts=18
- skipped_existing_rows=0
- confirmed_symbol_rows=52
- api_unavailable_rows=123
- outputs=data/processed/derivatives_availability.csv,data/processed/derivatives_availability.parquet,docs/derivatives_availability_quality_report.md,data/processed/monitoring_strategy_tradeable_subset_summary.csv

## 2026-05-27T11:42:10Z - Derivatives availability collector
- scope=Monitoring Tag immediate_1h_confirmation + negative_1h_confirmation candidate symbols
- output_rows=178
- new_api_request_attempts=534
- skipped_existing_rows=0
- confirmed_symbol_rows=52
- api_unavailable_rows=0
- outputs=data/processed/derivatives_availability.csv,data/processed/derivatives_availability.parquet,docs/derivatives_availability_quality_report.md,data/processed/monitoring_strategy_tradeable_subset_summary.csv

## 2026-06-08T10:00:11Z - Incremental announcement update
- scope=2026-05-27T00:00:00Z to 2026-06-08T23:59:59Z
- command=python3 scripts/collect_announcements.py --start 2026-05-27T00:00:00Z --end 2026-06-08T23:59:59Z --max-pages 20
- candidate_pages=2
- selected_pages=2
- detail_cache_hits=0
- detail_downloaded=2
- successfully_parsed_pages=2
- parsed_events=10
- manual_review_events=0
- new_event_types=SPOT_PAIR_REMOVED:7,SPOT_TOKEN_DELISTING_ANNOUNCED:3
- note=collector wrote delta to events.csv; delta preserved as data/processed/events_increment_2026-05-27_2026-06-08.csv, baseline restored from archive and merged.

## 2026-06-08T10:05:00Z - Manual event correction
- scope=Binance Will Delist COS, D, HIGH, MBOX on 2026-06-19
- correction=added missing single-letter token D as SPOT_TOKEN_DELISTING_ANNOUNCED
- reason=parser missed one-letter symbol D despite explicit official text "Dar Open Network (D)"
- final_events_rows=1288
- lifecycle_rows=548
- lifecycle_outcomes=delisted_after_tag:88,delisted_without_known_tag:26,still_tagged:24,spot_pair_removed_only:262

## 2026-06-08T10:15:00Z - Incremental price run
- scope=COS,D,HIGH,MBOX
- command=python3 scripts/price_pipeline.py --mode full --tokens COS,D,HIGH,MBOX --resume --rate-limit 0.15 --output-dir data/processed/increment_2026_06_08
- token_entity_id=4
- events_covered=15
- spot_pairs_resolved=4
- spot_pairs_missing=0
- futures_pairs_resolved=4
- price_window_rows=270
- missing_price_rows=76
- benchmark_gap_rows=76
- pump_rows=4
- fallback_quality_rows=4
- api_requests_spot=268
- api_429_count=0
- kline_cache_hits=18
- kline_downloads=6
- outputs=data/processed/increment_2026_06_08/price_resolution.csv,data/processed/increment_2026_06_08/price_windows.csv,data/processed/increment_2026_06_08/recovery_analysis.csv,data/processed/increment_2026_06_08/pump_analysis.csv,data/processed/increment_2026_06_08/fallback_data_quality.csv

## 2026-06-08T10:25:00Z - Direct fresh delisting reaction
- scope=COS,D,HIGH,MBOX spot delisting announcement 2026-06-05T07:00:07Z
- source=Binance Spot API /api/v3/klines interval=1h
- output=data/processed/increment_2026_06_08/new_delisting_reaction_direct_binance.csv
- note=direct reaction supplement used because fresh event windows in full price pipeline were missing; effective delisting is future dated at 2026-06-19T03:00:00Z.

## 2026-06-08T10:35:00Z - Bottom/rebound sample layer
- methodology=docs/bottom_rebound_methodology.md
- thresholds=config/research_thresholds.yaml bottom_rebound
- scripts=scripts/bottom_rebound_analysis.py,scripts/merge_bottom_rebound_batches.py
- sample_tokens=EPIC,HEI,ALCX,COOKIE,TLM,AERGO,BADGER,COS,HIGH,MBOX,CVX,ZEC,AKRO,0G
- outputs=data/processed/bottom_analysis_sample.csv,data/processed/rebound_analysis_sample.csv,data/processed/tradable_bottom_signals_sample.csv,data/processed/bottom_rebound_scenarios_sample.csv,data/processed/epic_like_cases_sample.csv,docs/bottom_rebound_sample_report.md
- first_sample=processed:14,tradable_signals:2,manual_review:9
- note=EPIC not confirmed in first sample due short local path.

## 2026-06-08T10:50:00Z - Fresh 2026 kline cache update and bottom/rebound sample rerun
- scope=EPIC,HEI,ALCX,COOKIE,TLM
- script=scripts/update_fresh_2026_klines.py
- source=Binance Spot API /api/v3/klines
- intervals=1h,15m,1d
- end=2026-06-08T23:59:59Z
- rows_per_token=1h:419,1d:18,15m:1771
- rerun_sample=processed:14,tradable_signals:4,manual_review:9
- epic_delta=max_rebound_after_bottom:2.36pct->331.41pct,tradable_signal:no->yes,epic_similarity_score:0.75,manual_review:yes
- note=Full bottom/rebound run not started.

## 2026-06-08T11:10:00Z - Bottom/rebound signal quality sample v2
- scope=same 14-token sample
- updated_script=scripts/bottom_rebound_analysis.py
- new_outputs=data/processed/signal_quality_sample.csv,data/processed/bottom_rebound_case_comparison_sample.csv,docs/bottom_rebound_signal_quality_sample_report.md
- tradable_signals=4
- signal_quality_rows=4
- tradeability_tiers=Manual Review:3,B:1,A:0,C:0
- epic_signal=HIGHER_LOW_BREAKOUT,signal_time:2026-06-01T05:00:00Z,quote_volume_at_signal:284460.51,volume_zscore_at_signal:4.13,stop_distance:18.98pct,mae_before_mfe:-5.78pct,time_to_20_target:6h,time_to_50_target:28h,time_to_100_target:53h,tradeability_tier:Manual Review
- note=EPIC has low liquidity at bottom but materially improved signal liquidity; full run still not started.

## 2026-06-08T11:25:00Z - Bottom/rebound signal quality sample v3
- scope=same 14-token sample
- change=separated bottom_liquidity_threshold,signal_liquidity_threshold,rebound_liquidity_threshold
- thresholds=bottom:25000,signal:100000,rebound:100000
- updated_script=scripts/bottom_rebound_analysis.py
- outputs=data/processed/signal_quality_sample.csv,data/processed/bottom_rebound_case_comparison_sample.csv,docs/bottom_rebound_signal_quality_sample_v3_report.md
- tradeability_tiers=B:2,C:1,Manual Review:1,A:0
- epic_signal_tier=B
- epic_final_tradeability_score=0.872
- epic_signal_manual_review=no
- note=EPIC scenario-level manual review remains due low-liquidity bottom; signal-level tradeability improves because signal quote volume is 284k USDT and confirmation is strong. Full run not started.

## 2026-06-08T11:45:00Z - Bottom/rebound 15m refinement sample v4
- scope=EPIC,HEI,COOKIE from the 14-token sample
- updated_script=scripts/refine_bottom_rebound_15m_sample.py
- outputs=data/processed/signal_15m_refinement_sample.csv,docs/bottom_rebound_signal_quality_sample_v4_report.md
- rows=3
- epic_15m_entry=2026-06-01T05:00:00Z,entry_price=0.2620,stop=0.18816,stop_distance=-28.18pct
- epic_15m_mfe_24h=46.18pct,epic_15m_mfe_3d=124.43pct,epic_15m_mfe_7d=214.50pct,epic_rr_7d=7.61
- epic_flags=wick_risk:no,single_candle_artifact:no,stop_failed:no,low_15m_entry_liquidity:yes
- hei_15m_signal_found=no
- cookie_stop_failed=yes,cookie_false_breakout_warning=yes,cookie_low_15m_entry_liquidity=yes
- note=Full bottom/rebound run was not started.

## 2026-06-08T13:55:00Z - Bottom/rebound batch 000_025
- methodology_update=docs/bottom_rebound_methodology.md updated with v4 liquidity separation and optional 15m QA layer
- thresholds_update=config/research_thresholds.yaml bottom_rebound methodology_version=v4
- added_script=scripts/refine_bottom_rebound_15m.py
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --start-index 0 --end-index 25 --batch-id 000_025
- first_attempt_error=empty daily path raised KeyError(timestamp) in sustained_daily; fixed missing-path handling
- processed=20
- requested=25
- anchor_events=SPOT_PAIR_REMOVED:17,MONITORING_TAG_ADDED:3
- absolute_bottoms=19
- tradable_signals=17
- signal_quality_rows=17
- tradeability_tiers=C:9,Manual Review:7,B:1,A:0
- epic_like_raw=2
- epic_like_token_risk=0
- manual_review_scenarios=7
- missing_1h_path=AI
- token_risk_15m_candidates=A2Z,ACA,AERGO
- outputs=data/processed/bottom_analysis_000_025.csv,data/processed/rebound_analysis_000_025.csv,data/processed/tradable_bottom_signals_000_025.csv,data/processed/signal_quality_000_025.csv,data/processed/bottom_rebound_scenarios_000_025.csv,data/processed/epic_like_cases_000_025.csv,data/processed/bottom_rebound_case_comparison_000_025.csv,docs/bottom_rebound_000_025_report.md,docs/bottom_rebound_000_025_qa.md
- note=Full monolithic bottom/rebound run was not started; batch is dominated by spot-pair-removal controls and is pipeline QA, not representative analytics.

## 2026-06-08T14:01:00Z - Bottom/rebound risk-focused batch risk_000_025
- script_update=scripts/bottom_rebound_analysis.py added --risk-only,--control-only,--event-types and token-risk QA report sections
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 0 --end-index 25 --batch-id risk_000_025
- risk_universe_size=149
- processed=25
- anchor_events=MONITORING_TAG_ADDED:21,SPOT_TOKEN_DELISTING_ANNOUNCED:3,VOTE_TO_DELIST_STARTED:1
- absolute_bottoms=24
- tradable_signals=17
- tradeability_tiers=Manual Review:8,B:5,C:2,A:2
- epic_like_candidates=3
- continued_bleed_or_death_spiral=2
- weak_rebound_90d_lt20=8
- strong_rebound_without_causal_signal_90d=4
- failed_signals=5
- manual_review_scenarios=16
- missing_1h_path=CML
- top_15m_refinement_candidates_include=A2Z,ACA,AERGO,ALPACA,ARDR,AST,ATA,BAKE,BIFI,BSW,CLV
- outputs=data/processed/bottom_analysis_risk_000_025.csv,data/processed/rebound_analysis_risk_000_025.csv,data/processed/tradable_bottom_signals_risk_000_025.csv,data/processed/signal_quality_risk_000_025.csv,data/processed/bottom_rebound_scenarios_risk_000_025.csv,data/processed/epic_like_cases_risk_000_025.csv,data/processed/bottom_rebound_case_comparison_risk_000_025.csv,docs/bottom_rebound_risk_000_025_report.md,docs/bottom_rebound_risk_000_025_qa.md
- note=Full monolithic bottom/rebound run was not started; control-only run remains separate.

## 2026-06-08T14:08:00Z - 15m refinement risk_000_025 selected candidates
- command=python3 scripts/refine_bottom_rebound_15m.py --input-signals data/processed/tradable_bottom_signals_risk_000_025.csv --tokens A2Z,ACA,AERGO,ALPACA,ARDR,AST,ATA,BAKE,BIFI,BSW,CLV --output data/processed/signal_15m_refinement_risk_000_025.csv
- rows=15
- clean_15m_confirmations=4
- rows_needing_review=11
- stop_failed_rows=5
- wick_or_range_risk_rows=6
- single_candle_artifact_rows=2
- hard_low_15m_liquidity_rows_lt25k=7
- epic_like_after_15m=BAKE confirmed strongest; ALPACA mixed; AST weakened/not clean
- AERGO=no_existing_1h_signal_for_selected_token
- CML_status=no local CMLUSDT path; source rows look like parser artifact from Collateral Margin Level text; keep manual_review/missing path, do not block batches
- outputs=data/processed/signal_15m_refinement_risk_000_025.csv,docs/bottom_rebound_15m_refinement_risk_000_025_report.md

## 2026-06-08T14:12:00Z - Bottom/rebound risk-focused batch risk_025_050
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 25 --end-index 50 --batch-id risk_025_050
- processed=25
- anchor_events=MONITORING_TAG_ADDED:21,SPOT_TOKEN_DELISTING_ANNOUNCED:4
- absolute_bottoms=24
- tradable_signals=16
- tradeability_tiers=C:7,Manual Review:5,B:3,A:1
- epic_like_candidates=3; CTXC,EPIC,FLOW
- continued_bleed_or_death_spiral=3
- weak_rebound_90d_lt20=9
- strong_rebound_without_causal_signal_90d=2
- failed_signals=8
- manual_review_scenarios=16
- missing_path=D:missing_1h_path_or_no_post_event_data
- outputs=data/processed/bottom_analysis_risk_025_050.csv,data/processed/rebound_analysis_risk_025_050.csv,data/processed/tradable_bottom_signals_risk_025_050.csv,data/processed/signal_quality_risk_025_050.csv,data/processed/bottom_rebound_scenarios_risk_025_050.csv,data/processed/epic_like_cases_risk_025_050.csv,data/processed/bottom_rebound_case_comparison_risk_025_050.csv,docs/bottom_rebound_risk_025_050_report.md,docs/bottom_rebound_risk_025_050_qa.md
- note=Full monolithic bottom/rebound run was not started.

## 2026-06-08T14:25:00Z - CML parser artifact exclusion and risk batch risk_050_075
- added_config=config/manual_token_exclusions.yaml with CML parser_artifact_collateral_margin_level
- script_update=scripts/bottom_rebound_analysis.py loads manual token exclusions for risk/control universe selection
- risk_universe_after_exclusion=148
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 50 --end-index 75 --batch-id risk_050_075
- processed=25
- anchor_events=MONITORING_TAG_ADDED:20,SPOT_TOKEN_DELISTING_ANNOUNCED:5
- absolute_bottoms=24
- tradable_signals=17
- tradeability_tiers=Manual Review:9,B:4,C:4,A:0
- epic_like_candidates=2; GHST,KEY
- continued_bleed_or_death_spiral=1
- weak_rebound_90d_lt20=7
- strong_rebound_without_causal_signal_90d=5
- failed_signals=10
- manual_review_scenarios=13
- missing_path=IDRT:missing_1h_path
- outputs=data/processed/bottom_analysis_risk_050_075.csv,data/processed/rebound_analysis_risk_050_075.csv,data/processed/tradable_bottom_signals_risk_050_075.csv,data/processed/signal_quality_risk_050_075.csv,data/processed/bottom_rebound_scenarios_risk_050_075.csv,data/processed/epic_like_cases_risk_050_075.csv,data/processed/bottom_rebound_case_comparison_risk_050_075.csv,docs/bottom_rebound_risk_050_075_report.md,docs/bottom_rebound_risk_050_075_qa.md
- gap_backfill=FORTH processed separately because CML exclusion shifted index boundary after prior risk_025_050 batch
- gap_command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --tokens FORTH --batch-id risk_gap_FORTH
- gap_result=FORTH processed:1,signals:0,manual_review:0
- note=Full monolithic bottom/rebound run was not started.

## 2026-06-08T14:35:00Z - Bottom/rebound risk-focused batch risk_075_100
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 75 --end-index 100 --batch-id risk_075_100
- processed=25
- anchor_events=MONITORING_TAG_ADDED:18,SPOT_TOKEN_DELISTING_ANNOUNCED:7
- absolute_bottoms=24
- tradable_signals=12
- tradeability_tiers=Manual Review:5,C:4,A:2,B:1
- epic_like_candidates=3; MOB,PDA,PORTAL
- continued_bleed_or_death_spiral=4
- weak_rebound_90d_lt20=11
- strong_rebound_without_causal_signal_90d=4
- failed_signals=6
- manual_review_scenarios=13
- missing_path=NON:missing_1h_path
- top_15m_refinement_candidates_include=MDT,MDX,MOB,MOVE,NKN,PDA,PERP,POLS,POND,PORTAL,PROS
- outputs=data/processed/bottom_analysis_risk_075_100.csv,data/processed/rebound_analysis_risk_075_100.csv,data/processed/tradable_bottom_signals_risk_075_100.csv,data/processed/signal_quality_risk_075_100.csv,data/processed/bottom_rebound_scenarios_risk_075_100.csv,data/processed/epic_like_cases_risk_075_100.csv,data/processed/bottom_rebound_case_comparison_risk_075_100.csv,docs/bottom_rebound_risk_075_100_report.md,docs/bottom_rebound_risk_075_100_qa.md
- note=Full monolithic bottom/rebound run was not started; no control-only run; no 15m refinement run.

## 2026-06-08T14:45:00Z - Bottom/rebound risk-focused batch risk_100_125
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 100 --end-index 125 --batch-id risk_100_125
- processed=25
- anchor_events=MONITORING_TAG_ADDED:18,SPOT_TOKEN_DELISTING_ANNOUNCED:4,MONITORING_TAG_REMOVED:3
- absolute_bottoms=21
- tradable_signals=12
- tradeability_tiers=C:5,Manual Review:5,B:1,A:1
- epic_like_candidates=1; STPT
- continued_bleed_or_death_spiral=2
- weak_rebound_90d_lt20=12
- strong_rebound_without_causal_signal_90d=2
- failed_signals=4
- manual_review_scenarios=15
- missing_path=REMOVE:missing_1h_path,SNM:missing_1h_path,SRM:missing_1h_path,TORN:missing_1h_path
- parser_artifact_watchlist=REMOVE
- top_15m_refinement_candidates_include=PYTH,QI,REEF,REI,REN,STPT,SUN,SXP,SYS,THE,TROY
- outputs=data/processed/bottom_analysis_risk_100_125.csv,data/processed/rebound_analysis_risk_100_125.csv,data/processed/tradable_bottom_signals_risk_100_125.csv,data/processed/signal_quality_risk_100_125.csv,data/processed/bottom_rebound_scenarios_risk_100_125.csv,data/processed/epic_like_cases_risk_100_125.csv,data/processed/bottom_rebound_case_comparison_risk_100_125.csv,docs/bottom_rebound_risk_100_125_report.md,docs/bottom_rebound_risk_100_125_qa.md
- note=Full monolithic bottom/rebound run was not started; no control-only run; no 15m refinement run. REMOVE was not excluded automatically.

## 2026-06-08T14:55:00Z - REMOVE parser artifact exclusion and final risk batch risk_125_148
- added_config_update=config/manual_token_exclusions.yaml with REMOVE parser_artifact_verb_remove
- risk_universe_after_exclusion=147
- command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --start-index 125 --end-index 148 --batch-id risk_125_148
- processed=22
- anchor_events=MONITORING_TAG_ADDED:19,SPOT_TOKEN_DELISTING_ANNOUNCED:3
- absolute_bottoms=21
- tradable_signals=10
- tradeability_tiers=C:5,Manual Review:3,B:2,A:0
- epic_like_candidates=1; UNFI
- continued_bleed_or_death_spiral=5
- weak_rebound_90d_lt20=8
- strong_rebound_without_causal_signal_90d=5
- failed_signals=7
- manual_review_scenarios=10
- missing_path=VAI:missing_1h_path
- top_15m_refinement_candidates_include=UNFI,VITE,VOXEL,WAVES,WIF,XEM,ZEC,ZEN
- outputs=data/processed/bottom_analysis_risk_125_148.csv,data/processed/rebound_analysis_risk_125_148.csv,data/processed/tradable_bottom_signals_risk_125_148.csv,data/processed/signal_quality_risk_125_148.csv,data/processed/bottom_rebound_scenarios_risk_125_148.csv,data/processed/epic_like_cases_risk_125_148.csv,data/processed/bottom_rebound_case_comparison_risk_125_148.csv,docs/bottom_rebound_risk_125_148_report.md,docs/bottom_rebound_risk_125_148_qa.md
- gap_backfill=TRU processed separately because REMOVE exclusion shifted index boundary after prior risk_100_125 batch
- gap_command=python3 scripts/bottom_rebound_analysis.py --mode full --resume --risk-only --tokens TRU --batch-id risk_gap_TRU
- gap_result=TRU processed:1,signals:0,manual_review:1
- note=Full monolithic bottom/rebound run was not started; no control-only run; no 15m refinement run.

## 2026-06-08T15:05:00Z - Bottom/rebound risk batch merge
- command=python3 scripts/merge_bottom_rebound_batches.py --scope risk
- script_update=scripts/merge_bottom_rebound_batches.py added --scope risk, signal_quality and case_comparison merge, manual token exclusions
- input_batches=risk_000_025,risk_025_050,risk_050_075,risk_075_100,risk_100_125,risk_125_148,risk_gap_FORTH,risk_gap_TRU
- output_rows=bottom_analysis:147,rebound_analysis:147,tradable_bottom_signals:84,signal_quality:84,bottom_rebound_scenarios:147,epic_like_cases:13,bottom_rebound_case_comparison:147
- schema_ok=all_tables_true
- duplicates_removed=0_all_tables
- exclusions_removed=CML_and_REMOVE_from entity-level tables
- coverage=147_of_147
- gap_backfills_included=FORTH:true,TRU:true
- excluded_artifacts=CML:true,REMOVE:true
- anchor_distribution=MONITORING_TAG_ADDED:118,SPOT_TOKEN_DELISTING_ANNOUNCED:26,MONITORING_TAG_REMOVED:3
- absolute_bottoms=140
- tradable_signals=84
- tradeability_tiers=Manual Review:35,C:27,B:16,A:6
- epic_like_candidates=13
- continued_bleed_or_death_spiral=18
- weak_rebound_90d_lt20=55
- strong_rebound_without_causal_signal_90d=22
- failed_signals=40
- manual_review_scenarios=82
- missing_path_symbols=D,IDRT,NON,SNM,SRM,TORN,VAI
- outputs=data/processed/bottom_analysis_risk.csv,data/processed/rebound_analysis_risk.csv,data/processed/tradable_bottom_signals_risk.csv,data/processed/signal_quality_risk.csv,data/processed/bottom_rebound_scenarios_risk.csv,data/processed/epic_like_cases_risk.csv,data/processed/bottom_rebound_case_comparison_risk.csv,data/processed/bottom_rebound_risk_merged_qa.md,docs/bottom_rebound_risk_merged_qa.md,docs/bottom_rebound_risk_summary_report.md
- note=Full monolithic bottom/rebound run was not started; no control-only run; no 15m refinement run.

## 2026-06-08T15:20:00Z - 15m refinement for merged risk top candidates
- command=python3 scripts/refine_bottom_rebound_15m.py --input-signals data/processed/tradable_bottom_signals_risk.csv --tokens MOB,THE,CTXC,BAKE,BSW,UNFI,EPIC,PORTAL,HARD,GPS,CREAM,ARDR,SUN,CLV,GHST,STPT,ALPACA,AST,FLOW,KEY,PDA --output data/processed/signal_15m_refinement_risk_top.csv
- scope=top A/B/high-rebound candidates plus all EPIC-like candidates with signal coverage
- rows=37
- clean_15m_confirmations=10
- stop_failed_rows=8
- wick_or_range_risk_rows=8
- single_candle_artifact_rows=2
- low_15m_entry_liquidity_rows_lt25k=11
- below_signal_liquidity_threshold_lt100k=reported_in_doc
- best_tradable_after_15m=BAKE,ARDR,THE,HARD,PORTAL
- epic_like_confirmed_after_15m=BAKE,PORTAL
- epic_like_downgraded_or_review=UNFI,ALPACA,EPIC,CTXC,PDA,GHST,AST,KEY,FLOW,MOB,STPT
- note=Full monolithic bottom/rebound run was not started; control-only was not run.
- outputs=data/processed/signal_15m_refinement_risk_top.csv,docs/bottom_rebound_15m_refinement_risk_top_report.md

## 2026-06-08T15:35:00Z - Historical bottom/rebound base-rate report
- scope=147 token-risk entities after excluding CML and REMOVE parser artifacts
- output=docs/bottom_rebound_historical_base_rate_report.md
- summary_csv=data/processed/bottom_rebound_historical_base_rate_summary.csv
- feature_csv=data/processed/bottom_rebound_historical_feature_summary.csv
- raw_epic_like=13/147=8.84pct
- clean_epic_like_after_15m=2/147=1.36pct; BAKE,PORTAL
- caveat_epic_like_after_15m=5/147=3.40pct; ALPACA,CTXC,EPIC,KEY,UNFI
- epic_like_failed_trap_or_no_signal_after_15m=6/147=4.08pct; AST,FLOW,GHST,MOB,PDA,STPT
- strong_rebound_without_causal_signal=22/147=14.97pct
- failed_trap_signal_cases_unique_tokens=39/147=26.53pct
- continued_bleed_or_death_spiral=18/147=12.24pct
- weak_rebound_90d_lt20=55/147=37.41pct
- note=Report is historical frequency/pattern research, not trading recommendation.

## 2026-06-08T10:00:11Z - Announcement index collection
- catalogId=48 (New Cryptocurrency Listing); pages_scanned=1; keyword_hits=0; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=49 (Latest Binance News); pages_scanned=1; keyword_hits=0; endpoint=/bapi/composite/v1/public/cms/article/list/query
- catalogId=161 (Delisting); pages_scanned=1; keyword_hits=2; endpoint=/bapi/composite/v1/public/cms/article/list/query

## 2026-06-08T10:00:11Z - Full event parse
- candidate_pages=2
- selected_pages=2
- detail_cache_hits=0
- detail_downloaded=2
- successfully_parsed_pages=2
- parsed_events=10
- manual_review_events=0
- output=data/processed/events.csv

## 2026-06-08T10:12:21Z - Price collection full
- token_entity_id=4
- events_covered=15
- tokens_filter=COS,D,HIGH,MBOX
- skip_fallback=False
- sources=Binance Spot API, Binance USD-M Futures API
- outputs=data/processed/increment_2026_06_08/price_resolution.csv,data/processed/increment_2026_06_08/price_windows.csv,data/processed/increment_2026_06_08/price_windows.parquet,data/processed/increment_2026_06_08/recovery_analysis.csv,data/processed/increment_2026_06_08/pump_analysis.csv,data/processed/increment_2026_06_08/fallback_data_quality.csv
