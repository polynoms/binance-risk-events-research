# Binance Risk Events Research

Исследование ценовых реакций на события Binance Monitoring Tag, Seed Tag и делистинги. Quantitative event-study на реальных данных с полным backtesting-пайплайном.

Дата сборки пакета: 2026-06-16.

## Что внутри

**500+ token-level событий** из официальных анонсов Binance за 2022-2026, обработанных в воспроизводимый research artifact.

В GitHub-пакет включены код, документация, processed datasets, dashboards и компактные raw-source слои. Тяжёлые raw OHLCV caches вынесены в отдельный полный архив.

## Ключевые результаты

- Медианное движение токена в первые 24ч после Monitoring Tag: **-6.2%**.
- Monitoring Tag sample: **120 rows / 118 unique tokens** с доступными +24h price windows.
- Практический горизонт basket-short: **7-14d для основной позиции**, 30-90d только как runner.
- Base ladder strategy (`stop_10`, `BE20`, `TP15/30`) дала:
  - **+82.4% ROI on margin** на 1d
  - **+118.5%** на 7d
  - **+128.2%** на 14d
  - **+132.9%** на 30d
  - **+139.9%** на 60d
  - **+168.3%** на 90d
- Сравнение **5 конфигураций TP/SL ladder**: defensive, balanced, base, aggressive, runner-only.

## Дашборды

HTML dashboards можно открыть прямо в браузере:

- [Cluster Stop Dashboard](docs/monitoring_cluster_stop_dashboard.html)
- [Ladder Dashboard](docs/monitoring_ladder_dashboard.html)
- [Cluster Dashboard v2](docs/monitoring_tag_cluster_dashboard_v2.html)

## Структура

- `data/processed/` — готовые CSV/Parquet datasets и результаты backtest.
- `data/raw/binance_announcements/` — raw Binance announcement corpus.
- `data/raw/derivatives_availability/` — компактные raw-запросы по futures availability/funding/OI.
- `docs/` — methodology, QA reports, research reports и HTML dashboards.
- `scripts/` — сбор данных, price pipeline, backtests, dashboards.
- `src/binance_retro/` — вспомогательные модули парсинга и Binance API.
- `config/` — manual mappings, exclusions, thresholds.

## Что не включено в GitHub-пакет

Из GitHub-пакета исключены тяжёлые raw price caches:

- `data/raw/klines/` — около 3.5 GB.
- `data/raw/fallback_prices/` — около 4.4 GB.

Полный локальный архив с raw data лежит отдельно:

```text
/Users/rus_dor_/Downloads/binance_risk_events_full_archive_2026-06-16.tar.gz
```

## Стек

Python · pandas · numpy · Plotly · Jupyter

## Ограничения

Это research artifact, не финансовая рекомендация. События собраны best-effort из official Binance announcements и API/cache. Некоторые rows требуют manual review, а futures/shortability availability местами является proxy/inferred, а не live-proof.
