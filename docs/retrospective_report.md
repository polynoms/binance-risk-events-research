# Retrospective Report v1

## Executive Summary

V1 собрал официальный корпус Binance risk-events, lifecycle layer и price layer с батчевой загрузкой OHLCV/fallback. Это не инвестиционная рекомендация и не прогноз делистинга; результат предназначен для ретроспективной карты сценариев.

- Всего событий: 1277.
- Lifecycle entities: 544.
- Price-layer entities: 529; 15 lifecycle rows с `unknown` outcome не вошли в price universe.
- Pump20 cases после delisting-announcement: 24.
- Pump-and-dump cases: 23.
- Manual-review scenario rows: 21.

## Data Coverage

- `SPOT_PAIR_REMOVED`: 824
- `MONITORING_TAG_ADDED`: 124
- `SPOT_TOKEN_DELISTING_ANNOUNCED`: 110
- `FUTURES_CONTRACT_DELISTING_ANNOUNCED`: 93
- `SEED_TAG_ADDED`: 69
- `SEED_TAG_REMOVED`: 23
- `VOTE_TO_DELIST_RESULT`: 15
- `MONITORING_TAG_REMOVED`: 11
- `VOTE_TO_DELIST_STARTED`: 8

## Lifecycle Outcomes

- `spot_pair_removed_only`: 259
- `delisted_after_tag`: 85
- `futures_only_delisting`: 62
- `seed_tag_only`: 61
- `still_tagged`: 27
- `delisted_without_known_tag`: 25
- `unknown`: 15
- `tag_removed`: 10

## Scenario Map

| primary_scenario                     |   number_of_tokens |   share_of_sample |   median_return_1h |   median_return_24h |   median_return_7d |   median_return_30d |   median_return_90d |   recovery_90_sustained_rate |   recovery_100_sustained_rate |   pump20_rate |   pump_and_dump_rate |   manual_review_count | example_tokens                                                     |
|:-------------------------------------|-------------------:|------------------:|-------------------:|--------------------:|-------------------:|--------------------:|--------------------:|-----------------------------:|------------------------------:|--------------:|---------------------:|----------------------:|:-------------------------------------------------------------------|
| PAIR_REMOVAL_ONLY                    |                259 |        0.476103   |         0          |          0.00314795 |        -0.00337268 |           0.0450854 |          0.00483418 |                     0        |                      0        |     0         |                 0    |                     0 | 0G, 1000CAT, 1INCH, 2Z, AAVE, ACE, ACH, ACM                        |
| TAG_TO_DELISTING_TO_COLLAPSE         |                 66 |        0.121324   |        -0.0207807  |         -0.0616265  |        -0.133084   |          -0.217777  |         -0.140666   |                     0.757576 |                      0.5      |     0.0151515 |                 0    |                     0 | A2Z, ACA, AERGO, ALPHA, ANT, AST, ATA, BADGER                      |
| FUTURES_ONLY_DELISTING               |                 62 |        0.113971   |        -0.014982   |         -0.0514139  |        -0.0557128  |          -0.0572022 |         -0.0628903  |                     0.564516 |                      0.290323 |     0         |                 0    |                     0 | 1000WHY, 1000X, 42, ADA, AI, AIA, APT, AUDIO                       |
| SEED_TAG_ONLY                        |                 61 |        0.112132   |        -0.0252294  |         -0.0252294  |        -0.24075    |          -0.460673  |         -0.547865   |                     0.639344 |                      0.540984 |     0         |                 0    |                     0 | 1000CHEEMS, 1000SATS, 1MBABYDOGE, ACT, ACX, AIGENSYN, AIXBT, ASTER |
| DELISTED_WITHOUT_KNOWN_PRIOR_TAG     |                 25 |        0.0459559  |        -0.0318907  |         -0.123487   |        -0.381904   |          -0.322034  |         -0.527301   |                     0.24     |                      0.2      |     0.16      |                 0.16 |                     2 | AKRO, AMB, BTS, CREAM, DREP, ELF, GFT, IDRT                        |
| DELISTING_ANNOUNCEMENT_PUMP_AND_DUMP |                 19 |        0.0349265  |        -0.02067    |         -0.0841709  |        -0.187397   |          -0.20657   |         -0.0750784  |                     0.684211 |                      0.421053 |     1         |                 1    |                     4 | ALPACA, BAKE, BAL, BOND, BSW, DOCK, EPX, FUN                       |
| UNKNOWN_MANUAL_REVIEW                |                 15 |        0.0275735  |       nan          |        nan          |       nan          |         nan         |        nan          |                     0        |                      0        |     0         |                 0    |                    15 | ARKM, BERA, BIO, CML, ETHFI, GMX, ONDO, PENDLE                     |
| NO_CLEAR_REACTION                    |                 14 |        0.0257353  |        -0.00714286 |         -0.0162602  |         0.0482539  |           0.371245  |        nan          |                     0.642857 |                      0.357143 |     0         |                 0    |                     0 | COOKIE, COS, HEI, HFT, HIGH, NFP, NOM, POND                        |
| TAG_REMOVED_AND_RECOVERED            |                  7 |        0.0128676  |        -0.0113636  |         -0.0467172  |        -0.0749782  |          -0.0827114 |          0.118466   |                     1        |                      0.857143 |     0         |                 0    |                     0 | CVX, MBL, PYTH, SUN, THE, ZEC, ZEN                                 |
| SLOW_BLEED_AFTER_TAG                 |                  5 |        0.00919118 |        -0.00568182 |          0.00568182 |        -0.134021   |          -0.164773  |         -0.2005     |                     0.8      |                      0.8      |     0         |                 0    |                     0 | GTC, MOVE, QI, STPT, WIF                                           |
| IMMEDIATE_DUMP_AFTER_TAG             |                  4 |        0.00735294 |        -0.00904552 |         -0.108892   |        -0.150649   |          -0.0727273 |        nan          |                     0        |                      0        |     0         |                 0    |                     0 | DODO, EPIC, RESOLV, TLM                                            |
| TEMPORARY_PANIC_THEN_RECOVERY        |                  4 |        0.00735294 |        -0.0458713  |         -0.12928    |        -0.11731    |          -0.306452  |          0.16602    |                     1        |                      0.5      |     0         |                 0    |                     0 | ALCX, ARDR, MBOX, PORTAL                                           |
| TAG_REMOVED_BUT_NOT_RECOVERED        |                  3 |        0.00551471 |        -0.0331674  |         -0.0448139  |        -0.11117    |          -0.512802  |         -0.638899   |                     0        |                      0        |     0         |                 0    |                     0 | FLOW, GPS, TAO                                                     |

## Monitoring Tag Analysis

Monitoring Tag не трактуется как гарантированный делистинг. Для tagged lifecycle сценарии разделены на immediate dump, slow bleed, temporary recovery, tag removal и tag-to-delisting. Recovery считается отдельно как sustained close logic, поэтому одиночные wicks не засчитываются как настоящее восстановление.

## Tag Removal Analysis

Tag removal cases классифицируются отдельно: `TAG_REMOVED_AND_RECOVERED` требует sustained recovery к pre-tag baseline, а `TAG_REMOVED_BUT_NOT_RECOVERED` сохраняет случаи, где bounce не стал устойчивым восстановлением.

## Delisting Announcement Analysis

Delisting announcement rows анализируются через `pump_analysis.csv`. Pump-and-dump требует pump20 flag, сильный subsequent drawdown и отсутствие sustained recovery. Fallback prices явно отделены от Binance через `price_source`/exchange.

## Futures Delisting Analysis

Futures-only rows сохранены отдельно как `FUTURES_ONLY_DELISTING`; normal BUSD sunset/migration cases не смешиваются со spot token delisting.

## Pair Removal Control Group

`SPOT_PAIR_REMOVED` остаётся control class. Эти события классифицируются как `PAIR_REMOVAL_ONLY` и не становятся token delisting outcome.

## Pre-Announcement Behavior

Pre-announcement weakness/dump сохраняется как secondary flag, если движение до official publication проходит locked thresholds. Это не доказывает leak или причинность.

## Caveats And Limitations

- Public fallback providers неполны; CoinGecko public API был ненадёжен в текущем окружении, поэтому v1 использует CCXT/CEX fallback.
- Низкая ликвидность и suspicious fallback spikes требуют manual review.
- Ticker reuse, rebrand, redenomination и non-standard symbols остаются источником residual risk.
- Market-adjusted returns зависят от v1 equal-weight Binance USDT alt benchmark, без historical universe snapshots.
- Нельзя смешивать spot delisting, futures delisting и pair removal.

## Implications For Future Monitoring

Для будущего мониторинга стоит отслеживать tag status, transition to Vote-to-Delist, volume collapse, market-adjusted underperformance, distance from pre-tag baseline, recovery failure, abnormal delisting-announcement volume, fallback-source anomalies и time since tag. Это диагностические признаки, не торговые рекомендации.
