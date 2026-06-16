# Bottom/Rebound 15m Refinement: risk_000_025

Scope: selected candidates from `risk_000_025` only. Full bottom/rebound run was not started.

Candidates requested: `A2Z`, `ACA`, `AERGO`, `ALPACA`, `ARDR`, `AST`, `ATA`, `BAKE`, `BIFI`, `BSW`, `CLV`.

## Summary

- rows produced: 15
- candidates with existing 1h signal rows: 10
- candidates without existing 1h signal: 1 (`AERGO`)
- clean 15m confirmations: 4
- rows needing manual/review caution: 11
- stop failed on 15m path: 5
- wick/range risk rows: 6
- single-candle artifact rows: 2
- hard low 15m liquidity rows, quote volume < 25k: 7
- below v4 signal-liquidity threshold, quote volume < 100k: 11

## Confirmed / Cleaner 15m Set

| token_symbol   | signal_type                 | refined_15m_entry_time    |   liquidity_at_15m_entry |   refined_rr_7d |   refined_mfe_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   |
|:---------------|:----------------------------|:--------------------------|-------------------------:|----------------:|-----------------:|:--------------|:-----------------|:------------------------------|
| ALPACA         | SLOW_BLEED_SQUEEZE_BREAKOUT | 2025-03-11T14:00:00+00:00 |                 204413   |        0.698422 |         0.188092 | no            | no               | no                            |
| ARDR           | HIGHER_LOW_BREAKOUT         | 2025-04-15T09:00:00+00:00 |                 136989   |       10.1536   |         1.8865   | no            | no               | no                            |
| BAKE           | CAPITULATION_RECLAIM        | 2025-09-09T19:00:00+00:00 |                  62493.3 |       66.4493   |         5.22507  | no            | no               | no                            |
| BAKE           | SLOW_BLEED_SQUEEZE_BREAKOUT | 2025-07-16T16:00:00+00:00 |                  42330.8 |        2.69896  |         0.258564 | no            | no               | no                            |

## EPIC-Like Candidates After 15m

| token_symbol   | best_signal_type            | entry_time                |   liquidity_15m |       rr7 |      mfe7 | stop_failed   | wick   | artifact   | notes                             | verdict                                |
|:---------------|:----------------------------|:--------------------------|----------------:|----------:|----------:|:--------------|:-------|:-----------|:----------------------------------|:---------------------------------------|
| ALPACA         | CAPITULATION_RECLAIM        | 2025-04-17T06:00:00+00:00 |         10262.9 | 18.7754   | 1.83775   | no            | no     | no         | low_15m_entry_liquidity           | mixed_after_15m                        |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT | 2025-03-13T08:00:00+00:00 |         53936.8 |  0.705882 | 0.0812641 | yes           | yes    | no         | 15m_entry_has_wick_or_large_range | not_clean_after_15m                    |
| BAKE           | CAPITULATION_RECLAIM        | 2025-09-09T19:00:00+00:00 |         62493.3 | 66.4493   | 5.22507   | no            | no     | no         | nan                               | confirmed_epic_like_tradable_candidate |

Interpretation:

- `BAKE` is the strongest EPIC-like tradable candidate in this batch after 15m refinement: clean 15m path, no stop failure, no single-candle artifact, very large MFE/RR.
- `ALPACA` is mixed: one later capitulation-reclaim signal has strong RR but hard-low 15m liquidity; the earlier squeeze signal is clean/liquid but weak on 7d RR after the refined entry.
- `AST` weakens materially after 15m: one signal is a single-candle artifact with low liquidity, another has wick/range risk and failed stop.

## A/B-Tier 1h Signals After 15m For Selected Candidates

| token_symbol   | signal_type                 | tradeability_tier   |   final_tradeability_score |   liquidity_at_15m_entry |   refined_rr_7d | stop_failed   | wick_risk_flag   | single_candle_artifact_flag   | after_15m_status        |
|:---------------|:----------------------------|:--------------------|---------------------------:|-------------------------:|----------------:|:--------------|:-----------------|:------------------------------|:------------------------|
| ARDR           | HIGHER_LOW_BREAKOUT         | B                   |                      0.795 |                136989    |        10.1536  | no            | no               | no                            | valid_clean             |
| BAKE           | CAPITULATION_RECLAIM        | A                   |                      0.923 |                 62493.3  |        66.4493  | no            | no               | no                            | valid_clean             |
| BAKE           | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |                      0.913 |                 42330.8  |         2.69896 | no            | no               | no                            | valid_clean             |
| BSW            | HIGHER_LOW_BREAKOUT         | A                   |                      0.923 |                 60517    |         7.71693 | no            | yes              | no                            | needs_review_or_invalid |
| BSW            | SLOW_BLEED_SQUEEZE_BREAKOUT | B                   |                      0.761 |                 17382    |         2.83505 | yes           | yes              | no                            | needs_review_or_invalid |
| CLV            | HIGHER_LOW_BREAKOUT         | B                   |                      0.764 |                  6462.76 |        62.806   | no            | no               | no                            | needs_review_or_invalid |

## Failed Signals And Pre-Entry Warning Clues

| token_symbol   | signal_type                 |   liquidity_at_15m_entry | wick_risk_flag   | single_candle_artifact_flag   | false_breakout_warning_flag   | refinement_notes                                          |   refined_rr_7d |
|:---------------|:----------------------------|-------------------------:|:-----------------|:------------------------------|:------------------------------|:----------------------------------------------------------|----------------:|
| A2Z            | SLOW_BLEED_SQUEEZE_BREAKOUT |                 22734.8  | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity |       21.8226   |
| ACA            | SLOW_BLEED_SQUEEZE_BREAKOUT |                 15411.6  | no               | no                            | yes                           | low_15m_entry_liquidity                                   |        0.530786 |
| AST            | SLOW_BLEED_SQUEEZE_BREAKOUT |                 53936.8  | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range                         |        0.705882 |
| ATA            | SLOW_BLEED_SQUEEZE_BREAKOUT |                  3245.67 | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity |        0.324675 |
| BSW            | SLOW_BLEED_SQUEEZE_BREAKOUT |                 17382    | yes              | no                            | yes                           | 15m_entry_has_wick_or_large_range;low_15m_entry_liquidity |        2.83505  |

Main filterable warning clues:

- Low 15m entry liquidity was visible in `A2Z`, `ACA`, `ATA`, and one `BSW` signal.
- Wick/range risk was visible in `A2Z`, `AST`, `ATA`, `BSW`, and `BIFI`.
- Single-candle artifact was visible in `AST` capitulation reclaim and `BIFI` higher-low breakout.
- `AERGO` had no 1h causal signal in this batch; it remains strong rebound without causal entry under current rules.

## Files

- `data/processed/signal_15m_refinement_risk_000_025.csv`
