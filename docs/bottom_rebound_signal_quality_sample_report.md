# Bottom/Rebound Signal Quality Sample v2

Sample tokens:

`EPIC, HEI, ALCX, COOKIE, TLM, AERGO, BADGER, COS, HIGH, MBOX, CVX, ZEC, AKRO, 0G`

Full run was not started.

## QA

- Tokens processed: 14
- Tradable signals before fresh-cache update: 2
- Tradable signals after fresh-cache update / sample v2: 4
- `signal_quality_sample.csv` rows: 4
- `bottom_rebound_case_comparison_sample.csv` rows: 14

Tradeability tier distribution:

- `Manual Review`: 3
- `B`: 1
- `A`: 0
- `C`: 0

## EPIC

EPIC signal:

- Signal type: `HIGHER_LOW_BREAKOUT`
- Signal timestamp: `2026-06-01T05:00:00Z`
- Signal price: `0.277`
- Recent low: `0.229`
- Stop price: `0.22442`
- Stop distance: `-18.98%`
- Quote volume at bottom: `15,480 USDT`
- Quote volume at signal: `284,461 USDT`
- Volume z-score at signal: `4.13`
- Next 3 candles confirmation: `yes`
- MAE after signal: `-5.78%`
- MAE before MFE: `-5.78%`
- 7d MFE: `+197.47%`
- 7d R/R: `10.40`
- Time to 20% target: `6h`
- Time to 50% target: `28h`
- Time to 100% target: `53h`
- Stop failed: `no`
- Signal quality score: `0.452`
- Tradeability tier: `Manual Review`

Interpretation:

EPIC is no longer just hindsight rebound. It has a causal breakout-style signal after the low, with strong signal volume and excellent post-signal MFE/Risk.

Manual review remains because the detected bottom itself had low quote volume. This distinction matters: bottom liquidity was weak, but signal liquidity improved.

## HEI

HEI:

- Max rebound after bottom: `+262.89%`
- Tradable signal found: `no`
- Main no-signal reason:
  `bottom_manual_review;low_liquidity_at_bottom;strong_rebound_without_causal_confirmation;no_capitulation_reclaim`

Interpretation:

HEI had a strong rebound, but v1 rules did not find a causal entry. This is the class: rebound exists, but not tradable under current confirmation rules.

## COOKIE

COOKIE:

- Signal type: `SLOW_BLEED_SQUEEZE_BREAKOUT`
- Signal timestamp: `2026-05-29T11:00:00Z`
- Quote volume at signal: `22,177 USDT`
- Volume z-score: `1.56`
- Stop distance: `-5.32%`
- 7d MFE: `+16.95%`
- 7d R/R: `3.18`
- Stop failed: `yes`
- Signal failure reason:
  `false_breakout;low_liquidity_at_signal`
- Signal quality score: `0.121`
- Tradeability tier: `Manual Review`

Interpretation:

COOKIE is a failed signal example: the proxy signal appeared, but liquidity was poor and the stop was hit.

## Continued Bleed / Weak Rebound

ALCX:

- Drawdown to bottom: `-35.18%`
- Max rebound: `+7.62%`
- No tradable signal.
- Main reason:
  `bottom_manual_review;low_liquidity_at_bottom;weak_rebound_below_20pct;no_capitulation_reclaim`

TLM:

- Drawdown to bottom: `-44.79%`
- Max rebound: `+8.10%`
- No tradable signal.
- Main reason:
  `bottom_manual_review;low_liquidity_at_bottom;weak_rebound_below_20pct;no_capitulation_reclaim`

These remain closer to continued bleed / weak rebound.

## Other Cases

AERGO:

- Max rebound: `+66.49%`
- No causal signal.
- Manual review remains due low quote volume / suspicious historical pump context.

COS:

- Signal type: `HIGHER_LOW_BREAKOUT`
- 7d MFE: `+63.70%`
- 7d R/R: `1.47`
- Signal quote volume: `2.69M USDT`
- Manual review remains because the bottom was low-liquidity/wick-like.

HIGH:

- Max rebound: `+450.47%`
- Manual review: no
- No signal under v1 rules.
- Not EPIC-like because drawdown before rebound was only `-16.08%`.

0G:

- Signal tier: `B`
- But `0G` is `spot_pair_removed_only`.
- It remains control-only and is excluded from token-risk conclusions.

## Research Answer

The sample now separates the three requested classes:

1. Continued bleed / weak rebound:
   - ALCX
   - TLM

2. Rebound exists but not tradable under current rules:
   - HEI
   - AERGO
   - HIGH

3. Rebound with causal signal, but execution/data caveats:
   - EPIC
   - COS
   - COOKIE failed signal

No sample case currently reaches clean tier `A`.

## Threshold Notes Before Full Run

Do not weaken manual review yet.

The key threshold to revisit before full run is:

- `bottom_rebound.low_liquidity_quote_volume_min = 100000`

For small Binance risk-event names this threshold may be too strict at the exact bottom, but it is useful as a safety guard. A better v2 rule may separate:

- bottom liquidity threshold;
- signal liquidity threshold;
- execution liquidity threshold.

EPIC is the example: low bottom liquidity, but materially improved signal liquidity.

## Full Run Readiness

Full run is not ready yet.

Recommended next step:

- add separate bottom-liquidity vs signal-liquidity thresholds;
- preserve EPIC/COS as manual-review unless signal liquidity and confirmation are strong enough;
- then rerun sample once more before full batch processing.

Look-ahead protection remains intact:

- signals are after anchor event;
- entry is after confirmation candle;
- stop is known at signal time;
- future low/max rebound are used only for outcome evaluation.
