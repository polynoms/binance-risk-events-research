# Shortability Data Gaps Report

Generated at UTC: 2026-05-27T11:04:38.354961+00:00

Scope: Monitoring Tag candidate `immediate_1h_confirmation + negative_1h_confirmation` only.

Current Binance futures `exchangeInfo` is not used as historical proof. It is insufficient for determining whether a contract existed at a 2023-2026 entry timestamp.

## Coverage

- Candidate trades: 89
- Confirmed Binance perp availability from local futures OHLCV around entry: 0
- Inferred availability from futures delisting announcement active window: 0
- Unknown shortability: 84
- Low/blocked shortability: 5
- Futures OHLCV around entry available: 0
- Funding cache around entry available: 0
- Open interest cache around entry available: 0
- Current futures exchangeInfo snapshot UTC: 2026-05-26T13:54:55Z
- Candidate symbols present in current futures exchangeInfo: 52 (not used as historical proof)

## Tradeable Subset Metrics at 100 bps

| view                                                    |   cost_bps |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | worst_trade   | best_trade   | median_mae   | median_mfe   |   profit_factor |
|:--------------------------------------------------------|-----------:|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:--------------|:-------------|:-------------|:-------------|----------------:|
| confirmed_or_inferred_shortable                         |        100 |          0 | NA         | NA              | NA               | NA           | NA           | NA            | NA           | NA           | NA           |       nan       |
| unknown_shortability                                    |        100 |         84 | 54.8%      | 7.2%            | 7.7%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 21.6%        | 38.8%        |         1.96416 |
| low_or_blocked_shortability                             |        100 |          5 | 80.0%      | 4.0%            | 14.1%            | 0.7%         | 41.9%        | -17.7%        | 41.9%        | 13.2%        | 37.7%        |         5.00463 |
| medium_feasibility_plus_confirmed_or_inferred_shortable |        100 |          0 | NA         | NA              | NA               | NA           | NA           | NA            | NA           | NA           | NA           |       nan       |

## Main Gap

For most candidates, the historical market signal can be measured from spot OHLCV, but short execution cannot be proven because we lack historical borrow availability and/or historical perp listing metadata at entry time.

## Manual Exchange Lookup Queue

| token_symbol   | entry_time           | shortability_blocker                                         | futures_symbol_candidate   | futures_cache_symbol_dirs_present   |
|:---------------|:---------------------|:-------------------------------------------------------------|:---------------------------|:------------------------------------|
| BETA           | 2023-10-04T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | BETAUSDT,BETABUSD          |                                     |
| BOND           | 2023-10-04T08:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | BONDUSDT,BONDBUSD          |                                     |
| WTC            | 2023-10-04T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | WTCUSDT,WTCBUSD            |                                     |
| ANT            | 2024-01-04T09:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | ANTUSDT,ANTBUSD            |                                     |
| FIRO           | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | FIROUSDT,FIROBUSD          |                                     |
| KP3R           | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | KP3RUSDT,KP3RBUSD          |                                     |
| MDX            | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | MDXUSDT,MDXBUSD            |                                     |
| MOB            | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | MOBUSDT,MOBBUSD            |                                     |
| ZEC            | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | ZECUSDT,ZECBUSD            |                                     |
| ZEN            | 2024-01-04T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | ZENUSDT,ZENBUSD            |                                     |
| EPX            | 2024-04-03T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | EPXUSDT,EPXBUSD            |                                     |
| UNFI           | 2024-04-03T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | UNFIUSDT,UNFIBUSD          |                                     |
| WAVES          | 2024-04-03T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | WAVESUSDT,WAVESBUSD        |                                     |
| WNXM           | 2024-04-03T08:59:59Z | missing_historical_perp_listing_or_borrow_data               | WNXMUSDT,WNXMBUSD          |                                     |
| CTXC           | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | CTXCUSDT,CTXCBUSD          |                                     |
| CVP            | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | CVPUSDT,CVPBUSD            |                                     |
| CVX            | 2024-07-01T09:59:59Z | perp_delisted_before_entry                                   | CVXUSDT,CVXBUSD            |                                     |
| DOCK           | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | DOCKUSDT,DOCKBUSD          |                                     |
| HARD           | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | HARDUSDT,HARDBUSD          |                                     |
| IRIS           | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | IRISUSDT,IRISBUSD          |                                     |
| MBL            | 2024-07-01T09:59:59Z | perp_delisted_before_entry                                   | MBLUSDT,MBLBUSD            |                                     |
| POLS           | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | POLSUSDT,POLSBUSD          |                                     |
| SNT            | 2024-07-01T09:59:59Z | perp_delisted_before_entry                                   | SNTUSDT,SNTBUSD            |                                     |
| SUN            | 2024-07-01T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | SUNUSDT,SUNBUSD            |                                     |
| BLZ            | 2024-10-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | BLZUSDT,BLZBUSD            |                                     |
| CLV            | 2024-10-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | CLVUSDT,CLVBUSD            |                                     |
| KEY            | 2024-10-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | KEYUSDT,KEYBUSD            |                                     |
| PROS           | 2024-10-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | PROSUSDT,PROSBUSD          |                                     |
| VITE           | 2024-10-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | VITEUSDT,VITEBUSD          |                                     |
| STMX           | 2025-01-02T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | STMXUSDT,STMXBUSD          |                                     |
| TROY           | 2025-01-02T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | TROYUSDT,TROYBUSD          |                                     |
| ALPACA         | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | ALPACAUSDT,ALPACABUSD      |                                     |
| AST            | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | ASTUSDT,ASTBUSD            |                                     |
| BURGER         | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | BURGERUSDT,BURGERBUSD      |                                     |
| NULS           | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | NULSUSDT,NULSBUSD          |                                     |
| UFT            | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | UFTUSDT,UFTBUSD            |                                     |
| VIDT           | 2025-03-04T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | VIDTUSDT,VIDTBUSD          |                                     |
| ARDR           | 2025-04-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | ARDRUSDT,ARDRBUSD          |                                     |
| BSW            | 2025-04-03T09:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | BSWUSDT,BSWBUSD            |                                     |
| FLM            | 2025-04-03T09:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | FLMUSDT,FLMBUSD            |                                     |
| LTO            | 2025-04-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | LTOUSDT,LTOBUSD            |                                     |
| NKN            | 2025-04-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | NKNUSDT,NKNBUSD            |                                     |
| PERP           | 2025-04-03T09:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | PERPUSDT,PERPBUSD          |                                     |
| VIB            | 2025-04-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | VIBUSDT,VIBBUSD            |                                     |
| VOXEL          | 2025-04-03T09:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | VOXELUSDT,VOXELBUSD        |                                     |
| WING           | 2025-04-03T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | WINGUSDT,WINGBUSD          |                                     |
| ALPHA          | 2025-05-07T10:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | ALPHAUSDT,ALPHABUSD        |                                     |
| HIFI           | 2025-05-07T10:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | HIFIUSDT,HIFIBUSD          |                                     |
| LEVER          | 2025-05-07T10:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | LEVERUSDT,LEVERBUSD        |                                     |
| MOVE           | 2025-05-07T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | MOVEUSDT,MOVEBUSD          |                                     |
| PORTAL         | 2025-05-07T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | PORTALUSDT,PORTALBUSD      |                                     |
| REI            | 2025-05-07T10:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | REIUSDT,REIBUSD            |                                     |
| BIFI           | 2025-06-05T07:59:59Z | missing_historical_perp_listing_or_borrow_data               | BIFIUSDT,BIFIBUSD          |                                     |
| FIS            | 2025-06-05T07:59:59Z | only_later_futures_delisting_announcement_not_proof_at_entry | FISUSDT,FISBUSD            |                                     |
| KMD            | 2025-06-05T07:59:59Z | missing_historical_perp_listing_or_borrow_data               | KMDUSDT,KMDBUSD            |                                     |
| SLF            | 2025-07-07T05:59:59Z | missing_historical_perp_listing_or_borrow_data               | SLFUSDT,SLFBUSD            |                                     |
| WAN            | 2025-10-09T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | WANUSDT,WANBUSD            |                                     |
| GHST           | 2025-12-01T06:59:59Z | missing_historical_perp_listing_or_borrow_data               | GHSTUSDT,GHSTBUSD          |                                     |
| ACA            | 2026-01-02T12:59:59Z | missing_historical_perp_listing_or_borrow_data               | ACAUSDT,ACABUSD            |                                     |
| DATA           | 2026-01-02T12:59:59Z | missing_historical_perp_listing_or_borrow_data               | DATAUSDT,DATABUSD          |                                     |
| FLOW           | 2026-01-02T12:59:59Z | missing_historical_perp_listing_or_borrow_data               | FLOWUSDT,FLOWBUSD          |                                     |
| COS            | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | COSUSDT,COSBUSD            |                                     |
| DEGO           | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | DEGOUSDT,DEGOBUSD          |                                     |
| FORTH          | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | FORTHUSDT,FORTHBUSD        |                                     |
| HOOK           | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | HOOKUSDT,HOOKBUSD          |                                     |
| LRC            | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | LRCUSDT,LRCBUSD            |                                     |
| MBOX           | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | MBOXUSDT,MBOXBUSD          |                                     |
| OXT            | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | OXTUSDT,OXTBUSD            |                                     |
| WIF            | 2026-03-06T10:59:59Z | missing_historical_perp_listing_or_borrow_data               | WIFUSDT,WIFBUSD            |                                     |
| A2Z            | 2026-03-13T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | A2ZUSDT,A2ZBUSD            |                                     |
| FIO            | 2026-03-13T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | FIOUSDT,FIOBUSD            |                                     |
| NTRN           | 2026-03-13T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | NTRNUSDT,NTRNBUSD          |                                     |
| QI             | 2026-03-13T11:59:59Z | missing_historical_perp_listing_or_borrow_data               | QIUSDT,QIBUSD              |                                     |
| FARM           | 2026-04-14T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | FARMUSDT,FARMBUSD          |                                     |
| HIGH           | 2026-04-14T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | HIGHUSDT,HIGHBUSD          |                                     |
| MLN            | 2026-04-14T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | MLNUSDT,MLNBUSD            |                                     |
| RESOLV         | 2026-04-14T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | RESOLVUSDT,RESOLVBUSD      |                                     |
| SYS            | 2026-04-14T04:59:59Z | missing_historical_perp_listing_or_borrow_data               | SYSUSDT,SYSBUSD            |                                     |
| NFP            | 2026-04-30T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | NFPUSDT,NFPBUSD            |                                     |
| NOM            | 2026-04-30T09:59:59Z | missing_historical_perp_listing_or_borrow_data               | NOMUSDT,NOMBUSD            |                                     |

## Required Next Data

- Historical Binance USD-M futures exchangeInfo snapshots or symbol listing/delisting history.
- Funding rate history and open interest history around each entry.
- Spot margin borrow availability and borrow fee history by asset.
- Historical bid/ask spread or order book snapshots to convert volume proxy into executable size assumptions.
