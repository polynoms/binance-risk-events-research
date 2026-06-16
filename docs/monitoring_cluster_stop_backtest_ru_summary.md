# Monitoring Tag cluster short backtest: краткое резюме

Это ретроспективный расчет, не торговая рекомендация.

## Модель

- Событие: `MONITORING_TAG_ADDED`.
- Кластер: все токены из Monitoring Tag announcement в один UTC-день.
- Entry: open первой доступной 1h свечи после публикации announcement.
- Номинал: 100 USDT маржи на токен, 10x, то есть 1000 USDT notional.
- Цена: Binance spot 1h OHLCV как proxy для path.
- Горизонты: 1h, 4h, 12h, 1d, 3d, 7d, 14d, 30d, 60d, 90d.
- Stop models: no_stop, fixed stop 10/15/20/30/50%.
- BE models: no_be, move-to-BE after +5/+10/+15/+20% favorable move.
- Conservative same-candle rule: fixed stop проверяется до BE activation.

## Universe

### All Monitoring Tag tokens

- Unique tokens: 119.
- Valid tokens with 1h path: 117.
- Clusters: 20.
- Missing path artifacts/issues: `VAI`, `REMOVE`.

### Shortable-only proxy

- Unique tokens: 52.
- Clusters: 17.
- Missing path: 0.
- Shortability proxy основан на `derivatives_availability.csv`; это не полноценное доказательство borrow/perp availability в live-режиме.

## Главный вывод по удержанию

Если смотреть только исторический price path, чем дольше удержание, тем выше ретроспективный PnL. Но это сильно конфликтует с реальной 10x механикой: длинные удержания резко повышают вероятность adverse squeeze / stop-out.

Для 10x самый реалистичный stop из этой сетки: `stop_10`. Stop 15/20% при 10x уже требует иной маржинальной логики или более низкого плеча.

## Practical variants: all tokens

ROI ниже указан как прибыль / начальная маржа.

| Hold | stop_10 no BE | stop_10 BE after 10% | stop_10 BE after 20% |
|---|---:|---:|---:|
| 1d | 57.6% | 45.2% | 54.8% |
| 3d | 70.3% | 51.9% | 64.1% |
| 7d | 121.9% | 78.4% | 90.0% |
| 14d | 131.5% | 81.0% | 109.4% |
| 30d | 271.2% | 196.8% | 229.3% |
| 60d | 437.9% | 313.8% | 369.2% |
| 90d | 587.9% | 413.8% | 477.7% |

Stop-out rate для `stop_10 no BE` растет от 13.4% на 1d до 75.6% на 90d.

## Practical variants: shortable-only proxy

| Hold | stop_10 no BE | stop_10 BE after 10% | stop_10 BE after 20% |
|---|---:|---:|---:|
| 1d | 59.3% | 49.7% | 59.1% |
| 3d | 57.9% | 52.0% | 54.5% |
| 7d | 103.6% | 89.1% | 80.6% |
| 14d | 135.6% | 118.2% | 123.8% |
| 30d | 241.2% | 247.5% | 251.8% |
| 60d | 472.5% | 484.0% | 487.3% |
| 90d | 563.5% | 560.4% | 582.6% |

Stop-out rate для `stop_10 no BE` растет от 15.1% на 1d до 75.5% на 90d.

## 15m strict recalculation

После пересчета на 15m свечах shortable-only картина стала более реалистичной. Длинное удержание все еще исторически прибыльное, но эффект стал заметно ниже, а риск squeeze/stop лучше виден.

| Hold | stop_10 no BE | stop_10 BE after 10% | stop_10 BE after 20% |
|---|---:|---:|---:|
| 1d | 88.5% | 73.3% | 84.2% |
| 3d | 92.9% | 86.6% | 86.3% |
| 7d | 172.1% | 140.6% | 137.5% |
| 14d | 193.2% | 159.8% | 164.6% |
| 30d | 163.8% | 173.5% | 178.4% |
| 60d | 195.9% | 198.4% | 202.9% |
| 90d | 271.7% | 267.0% | 286.4% |

Сравнение с 1h proxy показывает, что старый dashboard завышал долгий хвост:

- `no_stop 90d`: 1569.4% на 1h proxy против 732.0% на 15m strict.
- `stop_10 + BE20 90d`: 582.6% на 1h proxy против 286.4% на 15m strict.
- `stop_10 no BE 30d`: 241.2% на 1h proxy против 163.8% на 15m strict.

То есть вывод “держи вечно и будешь богатым” ослабевает. На 15m самый интересный практический диапазон выглядит ближе к `7d-14d` как базовый hold, а `30d+` нужно тестировать только через частичную фиксацию и basket-level equity path.

## Практический смысл

1. На истории Monitoring Tag basket-short действительно имел сильный downside drift.
2. 1d-3d дают более быстрый и менее “ночной” риск, но пропускают большую часть долгого падения.
3. 7d-14d выглядят как первый разумный компромисс: уже ловят drift, но stop-out rate еще не такой экстремальный, как 30d+.
4. 30d-90d дают максимальный исторический PnL, но требуют переживать большое количество squeeze/stop events. Для live это уже скорее позиционная корзина с жестким риск-бюджетом, а не простой “зашел и забыл”.
5. BE after 10% заметно снижает tail-risk, но часто забирает позицию слишком рано. BE after 20% исторически лучше сохраняет upside drift, но дает больше stop-outs до активации BE.

## Осторожная рабочая гипотеза для будущего анализа

- Базовый candidate для дальнейшей проверки: `stop_10 + BE after 20%`, hold 7d/14d/30d.
- Более защитный candidate: `stop_10 + BE after 10%`, hold 7d/14d.
- Агрессивный analytical upper-bound: `stop_10 no BE`, hold 14d/30d, но live-риск squeeze выше.

Нужный следующий слой: считать не только fixed holding, а “cluster equity path” с поэтапной фиксацией: часть прибыли на 1d/3d/7d, остаток держать до 14d/30d с BE.
