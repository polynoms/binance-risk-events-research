# Bottom/Rebound Signal Quality Sample v3

Full run was not started.

## Methodology Change

Liquidity thresholds are now separated:

- `bottom_liquidity_threshold`: `25,000 USDT`
- `signal_liquidity_threshold`: `100,000 USDT`
- `rebound_liquidity_threshold`: `100,000 USDT`

Low liquidity at absolute bottom is now a caution flag, not an automatic signal rejection.

Low liquidity at signal remains a strong manual-review / quality penalty.

## Outputs

- `data/processed/tradable_bottom_signals_sample.csv`
- `data/processed/signal_quality_sample.csv`
- `data/processed/bottom_rebound_case_comparison_sample.csv`

## Tier Distribution

- `B`: 2
- `C`: 1
- `Manual Review`: 1
- `A`: 0

## EPIC

EPIC moved from signal-level `Manual Review` to `B`.

Metrics:

- Signal: `HIGHER_LOW_BREAKOUT`
- Signal timestamp: `2026-06-01T05:00:00Z`
- Quote volume at bottom: `15,480 USDT`
- Quote volume at signal: `284,461 USDT`
- Volume z-score at signal: `4.13`
- Stop distance: `18.98%`
- MAE before MFE: `-5.78%`
- Time to +20% target: `6h`
- Time to +50% target: `28h`
- Time to +100% target: `53h`
- 7d MFE: `+197.47%`
- 7d R/R: `10.40`
- Stop failed: `no`
- Bottom liquidity score: `0.155`
- Signal liquidity score: `0.948`
- Signal confirmation score: `1.000`
- Risk management score: `0.900`
- Execution quality score: `0.850`
- Final tradeability score: `0.872`
- Signal-level manual review: `no`
- Signal tradeability tier: `B`

Why not A:

- absolute bottom liquidity was weak;
- scenario-level manual review remains;
- sample size is too small for full confidence.

Interpretation:

EPIC is now best described as:

`low-liquidity bottom, but improved-liquidity causal breakout signal`.

This is materially different from a pure hindsight bottom.

## HEI

HEI still has no signal.

Reason:

`bottom_manual_review;low_liquidity_at_bottom;strong_rebound_without_causal_confirmation;no_capitulation_reclaim`

Interpretation:

HEI belongs to the class:

`rebound exists, but not tradable under v1 signal rules`.

## COOKIE

COOKIE remains a negative signal-quality case.

Metrics:

- Signal: `SLOW_BLEED_SQUEEZE_BREAKOUT`
- Signal quote volume: `22,177 USDT`
- Signal liquidity flag: low
- Stop failed: yes
- Failure reason: `false_breakout;low_liquidity_at_signal`
- Final tradeability score: `0.089`
- Tier: `Manual Review`

Interpretation:

The signal existed, but execution quality was poor.

## ALCX / TLM

ALCX:

- Max rebound: `+7.62%`
- No tradable signal.
- Status: weak rebound / continued bleed.

TLM:

- Max rebound: `+8.10%`
- No tradable signal.
- Status: weak rebound / continued bleed.

## AERGO / COS / HIGH

AERGO:

- Strong rebound exists.
- No causal signal under v1.
- Remains manual-review due low-liquidity / suspicious pump context.

COS:

- Signal: `HIGHER_LOW_BREAKOUT`
- Signal liquidity strong: `2.69M USDT`
- 7d R/R: `1.47`
- Final tradeability score: `0.703`
- Tier: `C`
- Reason: stop distance is very wide and R/R is weaker than EPIC.

HIGH:

- Strong rebound: `+450.47%`
- No v1 signal.
- Not EPIC-like because pre-rebound drawdown was only `-16.08%`.

## 0G Control

0G remains control-only:

- `spot_pair_removed_only`
- Tier `B` signal exists, but excluded from token-risk conclusions.

## Recommended Thresholds Before Full Run

Keep:

- `bottom_liquidity_threshold = 25,000`
- `signal_liquidity_threshold = 100,000`
- `rebound_liquidity_threshold = 100,000`

Do not loosen manual-review logic for:

- low liquidity at signal;
- fallback-only spikes;
- suspicious wick-only moves;
- failed stop / false breakout.

## Full Run Readiness

Bottom/rebound full run is closer, but I would still do one more small validation before full:

- add 15m refinement around EPIC signal and HEI rebound;
- verify whether HEI truly has no causal signal or whether v1 signal rules are too strict;
- confirm EPIC signal is not a single-candle artifact.

Current research classification:

1. Continued bleed / weak rebound:
   - ALCX
   - TLM

2. Rebound exists but not tradable under v1:
   - HEI
   - AERGO
   - HIGH

3. Rebound with causal tradable signal and caveats:
   - EPIC
   - COS

4. Failed signal:
   - COOKIE

5. Control-only:
   - 0G
