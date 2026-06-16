# Bottom / Rebound Methodology

This module studies post-risk-event bottoms and rebounds for Binance risk-event tokens.

It deliberately separates:

1. Retrospective labels.
2. Tradable candidate signals.
3. Scenario classification.

The purpose is research classification, not investment advice or live signal generation.

## Anchors

Primary anchor events:

- `MONITORING_TAG_ADDED`
- `SPOT_TOKEN_DELISTING_ANNOUNCED`
- `MONITORING_TAG_REMOVED`

Control anchor:

- `SPOT_PAIR_REMOVED`

`SPOT_PAIR_REMOVED` remains a control class and must not be treated as token-level delisting.

## Baseline

Baseline priority:

1. `baseline_vwap_7d`
2. `baseline_median_close_7d`
3. `baseline_close_1d`
4. event price, only if no pre-event baseline is available

All drawdowns are measured versus the selected baseline.

## Absolute Bottom Detection

Absolute bottom is a retrospective label only.

For each anchor event, the module scans post-event OHLCV paths over:

- 7 days
- 14 days
- 30 days
- 60 days
- 90 days

For each window it records:

- minimum low price
- timestamp of that low
- drawdown from baseline
- days from event to low
- volume and quote volume at low
- volume z-score at low
- wick ratio

Absolute bottom cannot be used as an entry signal because it is only known after the fact.

## Capitulation Bottom Detection

A capitulation bottom candidate requires:

- drawdown from baseline <= `deep_drawdown_min`
- volume z-score at or near low >= `capitulation_volume_zscore_min`
- meaningful lower wick or reclaim from intraperiod low
- no immediate lower low in the next confirmation candles
- price reclaim of at least `reclaim_pct_from_low`

If the low is a one-candle extreme with weak volume or very low quote volume, it receives:

- `low_liquidity_wick_flag = true`
- lower confidence
- possible manual review

## Liquidity-Death Bottom

Liquidity-death bottom means price is low but the market is not reliably tradable.

Flags:

- quote volume below `low_liquidity_quote_volume_min`
- many zero-volume candles
- sparse fallback data
- missing 1h path

This should not be treated as a valid rebound setup without manual review.

## Liquidity Thresholds V4

The v4 methodology separates liquidity at three different moments:

- `bottom_liquidity_threshold`: liquidity around the retrospective absolute bottom.
- `signal_liquidity_threshold`: liquidity at the causal entry signal.
- `rebound_liquidity_threshold`: liquidity around the measured rebound high.

Low liquidity at the absolute bottom is a caution flag, not an automatic rejection of a later signal. If the market is thin at the low but later produces a causal signal with stronger quote volume, volume expansion, clean confirmation candles, and manageable stop distance, the case can remain tradable but should carry a note such as:

- `bottom liquidity weak, signal liquidity improved`

Low liquidity at the signal candle is more serious. It directly reduces tradeability score and can trigger manual review because it affects whether the entry was realistically executable.

## Rebound Detection

After the retrospective bottom, the module measures max rebound from bottom over:

- 24h
- 3d
- 7d
- 14d
- 30d
- 60d
- 90d

Threshold flags:

- `rebound_20_flag`
- `rebound_50_flag`
- `rebound_100_flag`
- `rebound_200_flag`

Sustained rebound requires at least `sustained_rebound_min_closes` daily closes above the relevant rebound threshold.

Pump-and-dump after bottom:

- strong rebound
- followed by drawdown <= `pump_and_dump_drawdown_min`
- no sustained recovery

Dead cat bounce:

- rebound >= 20%
- not sustained
- price later revisits or breaks the bottom area

## Tradable Candidate Signals

Tradable signals are causal. They cannot use future absolute bottoms or future max rebound.

Rules:

- `signal_timestamp_utc` must be after the anchor event.
- entry occurs only after confirmation candle.
- stop is defined at signal time.
- recent low must already be observable before entry.
- MFE/MAE are measured only after entry.

Signal quality scoring weights the signal itself more heavily than the retrospective low:

- quote volume at signal
- volume z-score at signal
- confirmation candles after signal
- stop distance
- MAE before MFE
- risk/reward after signal
- source/data quality

Bottom liquidity is retained as a scenario caveat, but it should not by itself convert a clean later entry into a failed signal.

Signal types:

### CAPITULATION_RECLAIM

Requirements:

- deep drawdown from baseline
- capitulation candle or volume spike
- price reclaims `low * (1 + reclaim_pct_from_low)`
- next candle does not update the low
- stop below recent low

### HIGHER_LOW_BREAKOUT

Requirements:

- observable recent low
- first bounce
- pullback forms higher low above previous low by `higher_low_min_pct`
- entry after breakout above local bounce high
- stop below higher low

### SLOW_BLEED_SQUEEZE_BREAKOUT

Requirements:

- several days after risk event
- price far below baseline
- compressed volume/volatility
- breakout candle with volume z-score >= `breakout_volume_zscore_min`
- entry after close confirmation, not on a wick

### TAG_REMOVAL_RECLAIM

Requirements:

- token had Monitoring Tag
- tag later removed
- price reclaims an important level after removal
- volume confirmation

## EPIC-Like Classification

A case is EPIC-like if:

- deep drawdown after risk event
- local bottom forms
- rebound after bottom >= 50%, preferably >= 100%
- rebound has volume expansion
- not a low-liquidity wick
- at least one tradable signal exists
- post-rebound drawdown does not immediately erase the entire move

Manual review remains required if:

- rebound depends on one fallback exchange
- quote volume is low
- spike is one-candle only
- 1h path is missing
- suspicious wick dominates the measurement

EPIC itself is treated as a case-study candidate, not a pre-labeled correct pattern.

## 15m Refinement QA

The primary bottom/rebound module uses 1h candles for full-batch analysis. A separate optional 15m QA layer is used only for selected candidates:

- EPIC-like candidates
- high rebound cases
- A/B-tier tradable signals
- suspicious or manual-review cases

The 15m refinement checks:

- whether the 1h signal is a single-candle artifact
- realistic 15m entry time and entry price
- 15m stop distance
- MAE before MFE after entry
- 24h/3d/7d MFE and risk/reward
- wick/range risk at entry
- first-slice quote volume and volume z-score
- false-breakout warning

The 15m layer is a QA overlay, not a separate optimization pass. It should not loosen higher-low or breakout rules after seeing the outcome.

## Look-Ahead Bias Controls

Retrospective labels may use future information:

- absolute low
- max rebound
- scenario label

Tradable signals may not:

- use future low
- use future max rebound
- enter before confirmation
- use information unavailable at signal timestamp

All tradable signal outcomes are evaluated after signal time.

## Integration

Inputs:

- `events.csv`
- `token_lifecycle.csv`
- raw OHLCV under `data/raw/klines/`
- fallback data quality tables where available

Outputs:

- `bottom_analysis.csv`
- `rebound_analysis.csv`
- `tradable_bottom_signals.csv`
- `signal_quality.csv`
- `bottom_rebound_scenarios.csv`
- `epic_like_cases.csv`
- optional selected-candidate QA: `signal_15m_refinement.csv`

The module is batch-safe and does not overwrite existing price pipeline outputs.
