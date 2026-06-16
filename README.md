# Binance Risk Events Research Dataset Package

Дата сборки архива: 2026-06-16.

## Что это

Архив с результатами исследования Binance Monitoring Tag / Seed Tag / delisting-risk events.

Пакет предназначен для загрузки в GitHub как воспроизводимый research artifact: код, документация, processed datasets, дашборды и компактные raw-source слои.

## Включено

- `data/processed/` — основные итоговые таблицы исследования:
  - `events.csv`
  - `token_lifecycle.csv`
  - `price_windows.csv/.parquet`
  - `recovery_analysis.csv`
  - `pump_analysis.csv`
  - `scenario_classification.csv`
  - `bottom/rebound` outputs
  - `monitoring cluster` backtests
  - `ladder/partial TP` outputs
- `data/raw/binance_announcements/` — raw Binance announcement corpus.
- `data/raw/derivatives_availability/` — компактные raw-запросы по futures availability/funding/OI, где были собраны.
- `docs/` — methodology, QA reports, dashboards, research reports.
- `scripts/` — сбор данных, price pipeline, backtests, dashboards.
- `src/` — вспомогательный source code.
- `config/` — thresholds, manual mappings, manual exclusions.
- `GITHUB_DATA_PACKAGE_README_2026-06-16.md` — этот файл.

## Не включено

Из GitHub-пакета исключены тяжёлые raw price caches:

- `data/raw/klines/` — около 3.5 GB.
- `data/raw/fallback_prices/` — около 4.4 GB.

Причина: обычный GitHub плохо подходит для таких объёмов. Для этих данных лучше использовать:

- Git LFS;
- GitHub Releases;
- S3/R2/Backblaze;
- DVC;
- отдельный локальный архив.

## Важные ограничения

- Это исследовательский датасет, не торговая рекомендация.
- События собраны best-effort из official Binance announcements и API/cache.
- Некоторые rows имеют `manual_review_required`.
- Futures/shortability availability местами является proxy/inferred, а не live-proof.
- Raw spot/futures OHLCV caches исключены из GitHub-пакета, поэтому полное пересчитывание price paths потребует отдельного raw archive.

## Рекомендуемая структура репозитория

```text
config/
data/
  processed/
  raw/
    binance_announcements/
    derivatives_availability/
docs/
scripts/
src/
GITHUB_DATA_PACKAGE_README_2026-06-16.md
```

## Как открыть дашборды

HTML-файлы лежат в `docs/`.

Основные:

- `docs/monitoring_cluster_stop_dashboard.html`
- `docs/monitoring_ladder_dashboard.html`
- `docs/monitoring_tag_cluster_dashboard_v2.html`

Их можно открыть двойным кликом в браузере.

