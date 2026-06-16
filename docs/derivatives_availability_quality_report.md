# Derivatives Availability Quality Report

Generated at UTC: 2026-05-27T11:42:10Z

Scope: Binance USD-M derivatives availability for Monitoring Tag candidate trades.

Current exchangeInfo is not used as historical proof. Evidence comes from historical futures klines, funding, and open-interest API responses around `entry_time`.

## Coverage

- candidate_trades_with_any_result: 89
- confirmed_binance_perp: 52
- inferred_from_futures_klines: 50
- funding_available: 51
- oi_available: 7
- no_binance_perp_evidence: 37
- api_unavailable: 0
- manual_review_needed: 2

## Raw Symbol-Level Status Counts

| availability_status                                                                |   count |
|:-----------------------------------------------------------------------------------|--------:|
| no_binance_perp_evidence                                                           |     126 |
| confirmed_binance_perp;inferred_from_futures_klines;funding_available              |      42 |
| confirmed_binance_perp;inferred_from_futures_klines;funding_available;oi_available |       7 |
| confirmed_binance_perp;funding_available;manual_review_needed                      |       2 |
| confirmed_binance_perp;inferred_from_futures_klines                                |       1 |

## Tradeable Subset Metrics at 100 bps

| view                                                    |   cost_bps |   n_trades | win_rate   | median_return   | average_return   | p25_return   | p75_return   | worst_trade   | best_trade   | median_mae   | median_mfe   |   profit_factor |
|:--------------------------------------------------------|-----------:|-----------:|:-----------|:----------------|:-----------------|:-------------|:-------------|:--------------|:-------------|:-------------|:-------------|----------------:|
| confirmed_or_inferred_shortable                         |        100 |         52 | 48.1%      | -17.7%          | 5.2%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 26.9%        | 38.8%        |         1.56527 |
| inferred_from_futures_klines                            |        100 |         50 | 46.0%      | -17.7%          | 3.7%             | -17.7%       | 30.3%        | -17.7%        | 41.9%        | 26.9%        | 38.0%        |         1.38976 |
| funding_available                                       |        100 |         51 | 49.0%      | -17.7%          | 5.6%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 24.5%        | 39.3%        |         1.62547 |
| oi_available                                            |        100 |          7 | 85.7%      | 21.2%           | 15.5%            | 13.4%        | 22.8%        | -17.7%        | 32.7%        | 1.5%         | 22.2%        |         7.15111 |
| no_binance_perp_evidence                                |        100 |         37 | 67.6%      | 10.5%           | 12.1%            | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 18.1%        | 38.2%        |         3.11505 |
| api_unavailable                                         |        100 |          0 | NA         | NA              | NA               | NA           | NA           | NA            | NA           | NA           | NA           |       nan       |
| manual_review_needed                                    |        100 |          2 | 100.0%     | 41.9%           | 41.9%            | 41.9%        | 41.9%        | 41.9%         | 41.9%        | 24.0%        | 56.7%        |       nan       |
| medium_feasibility_plus_confirmed_or_inferred_shortable |        100 |         30 | 56.7%      | 11.0%           | 9.8%             | -17.7%       | 41.9%        | -17.7%        | 41.9%        | 12.8%        | 37.0%        |         2.27366 |

## Unresolved / Manual Review Queue

| token_symbol   | entry_time           | futures_symbol   | availability_status      | api_errors                     |
|:---------------|:---------------------|:-----------------|:-------------------------|:-------------------------------|
| MOB            | 2024-01-04T09:59:59Z | MOBUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| BETA           | 2023-10-04T08:59:59Z | BETAUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| PROS           | 2024-10-03T09:59:59Z | PROSUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| POLS           | 2024-07-01T09:59:59Z | POLSUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| FARM           | 2026-04-14T04:59:59Z | FARMUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| BURGER         | 2025-03-04T10:59:59Z | BURGERUSDT       | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| KMD            | 2025-06-05T07:59:59Z | KMDUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| QI             | 2026-03-13T11:59:59Z | QIUSDT           | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| POND           | 2026-04-30T09:59:59Z | PONDUSDT         | no_binance_perp_evidence | http_400:Bad Request           |
| WTC            | 2023-10-04T08:59:59Z | WTCUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| DATA           | 2026-01-02T12:59:59Z | DATAUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| ALCX           | 2026-05-22T10:59:59Z | ALCXUSDT         | no_binance_perp_evidence | http_400:Bad Request           |
| FIRO           | 2024-01-04T09:59:59Z | FIROUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| KP3R           | 2024-01-04T09:59:59Z | KP3RUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| BOND           | 2023-10-04T08:59:59Z | BONDUSDT         | no_binance_perp_evidence | http_400:                      |
| CTXC           | 2024-07-01T09:59:59Z | CTXCUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| SLF            | 2025-07-07T05:59:59Z | SLFUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| WING           | 2025-04-03T09:59:59Z | WINGUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| WNXM           | 2024-04-03T08:59:59Z | WNXMUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| MDX            | 2024-01-04T09:59:59Z | MDXUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| IRIS           | 2024-07-01T09:59:59Z | IRISUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| UFT            | 2025-03-04T10:59:59Z | UFTUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| BIFI           | 2025-06-05T07:59:59Z | BIFIUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| ARDR           | 2025-04-03T09:59:59Z | ARDRUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| VITE           | 2024-10-03T09:59:59Z | VITEUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| CLV            | 2024-10-03T09:59:59Z | CLVUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| DOCK           | 2024-07-01T09:59:59Z | DOCKUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| HARD           | 2024-07-01T09:59:59Z | HARDUSDT         | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| AST            | 2025-03-04T10:59:59Z | ASTUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| SUN            | 2024-07-01T09:59:59Z | SUNUSDT          | no_binance_perp_evidence | http_400:                      |
| VIB            | 2025-04-03T09:59:59Z | VIBUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| EPX            | 2024-04-03T08:59:59Z | EPXUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| ACA            | 2026-01-02T12:59:59Z | ACAUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| LTO            | 2025-04-03T09:59:59Z | LTOUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| CVP            | 2024-07-01T09:59:59Z | CVPUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |
| DODO           | 2026-05-22T10:59:59Z | DODOUSDT         | no_binance_perp_evidence | nan                            |
| WAN            | 2025-10-09T04:59:59Z | WANUSDT          | no_binance_perp_evidence | http_400:Bad Request;http_400: |

## Notes

- `confirmed_binance_perp=yes` means at least one of futures klines, funding, or open-interest rows was found around entry.
- `inferred_from_futures_klines=yes` is the strongest free public evidence in this collector.
- `api_unavailable=yes` means API errors or limitations prevented a clean conclusion.
- Empty responses without API errors are kept as `no_binance_perp_evidence`, not proof that no contract existed.