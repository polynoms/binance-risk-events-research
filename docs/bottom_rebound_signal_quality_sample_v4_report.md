# Bottom/Rebound 15m Refinement Sample v4

Full run was not started.

## EPIC

- Refined 15m entry: `2026-06-01T05:00:00+00:00`
- Refined entry price: `0.262`
- Refined stop price: `0.18816`
- Stop distance: `-28.18%`
- MAE before MFE: `-1.91%`
- MFE 24h: `46.18%`
- MFE 3d: `124.43%`
- MFE 7d: `214.50%`
- RR 7d: `7.61`
- Time to +20% target: `5.5h`
- Time to +50% target: `24.75h`
- Time to +100% target: `53.25h`
- Wick risk: `no`
- Single candle artifact: `no`
- 15m entry quote volume: `23332.81`
- 15m entry volume z-score: `1.22`

Interpretation: EPIC remains a B-quality tradable candidate, not A. The 15m path does not mark it as a single-candle artifact and wick risk is not flagged, but the first 15m entry slice has low quote volume versus the 1h signal candle and the refined stop is wide.

## HEI

- Missed 15m signal flag: `no`
- Notes: `strong_rebound_exists_but_15m_structure_did_not_form_clean_higher_low_breakout`

Interpretation: HEI still belongs to strong rebound without clean causal confirmation under the current v1/v3 signal rules.

## COOKIE

- Refined 15m entry: `2026-05-29T11:00:00+00:00`
- Stop failed: `yes`
- False breakout warning: `yes`
- 15m entry liquidity: `7929.9909`
- Notes: `low_15m_entry_liquidity`

Interpretation: COOKIE remains a failed/low-quality signal. Low entry liquidity and stop failure were visible risks.

## Rule Implications

- Do not promote EPIC to tier A yet.
- Keep HEI as rebound-without-signal.
- Keep COOKIE as false-breakout / low-liquidity negative case.
- Before full run, higher-low breakout rules do not need to be loosened; the next improvement should be adding 15m refinement as an optional QA layer for top candidates.
