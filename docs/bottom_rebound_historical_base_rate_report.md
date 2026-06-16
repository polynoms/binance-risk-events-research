# Bottom/Rebound Historical Base-Rate Report

Scope: Binance risk-event token universe after parser exclusions. This is historical pattern research, not a live trading recommendation.

## Universe

- token-risk entities: 147
- exclusions: `CML`, `REMOVE` parser artifacts
- anchors: Monitoring Tag, Monitoring Tag Removed, Spot Token Delisting
- full monolithic run: not used
- control-only pair-removal group: not included in this report

## Base Rates

| class                                               |   count | share_of_147   | definition                                                                                          |
|:----------------------------------------------------|--------:|:---------------|:----------------------------------------------------------------------------------------------------|
| Raw EPIC-like candidates                            |      13 | 8.84%          | Retrospective label before 15m QA.                                                                  |
| Clean EPIC-like after 15m QA                        |       2 | 1.36%          | EPIC-like with clean 15m entry, no stop fail, no wick/artifact, entry quote volume >=25k, RR7d >=3. |
| EPIC-like with caveats after 15m QA                 |       5 | 3.4%           | EPIC-like but low-liquidity, weak RR after refined entry, wick/artifact, or downgraded/unclear.     |
| EPIC-like failed/trap/no causal signal after 15m QA |       6 | 4.08%          | EPIC-like raw label but 15m QA found failed trap or no causal 1h/15m signal.                        |
| Strong rebound without causal signal                |      22 | 14.97%         | >=50% max 90d rebound but no causal tradable signal under current rules.                            |
| Failed/trap signal cases                            |      39 | 26.53%         | At least one causal signal row failed stop.                                                         |
| Continued bleed / death spiral                      |      18 | 12.24%         | Scenario class NO_BOTTOM_CONTINUED_BLEED or DELISTING_DEATH_SPIRAL.                                 |
| Weak rebound <20% max 90d                           |      55 | 37.41%         | Max rebound after bottom <20% within 90d or missing/zero path.                                      |

Important: these classes are diagnostic flags, not a mutually exclusive strategy taxonomy. For example, a token can have a failed signal and also a large rebound.

## EPIC-Like Frequency

- Raw EPIC-like candidates: 13/147 = 8.8%
- Clean EPIC-like after 15m QA: 2/147 = 1.4%
- EPIC-like with caveats after 15m QA: 5/147 = 3.4%
- Raw EPIC-like that failed/no-signal after 15m QA: 6/147 = 4.1%

### Raw EPIC-Like Candidates

ALPACA, AST, BAKE, CTXC, EPIC, FLOW, GHST, KEY, MOB, PDA, PORTAL, STPT, UNFI

### Clean EPIC-Like After 15m QA

BAKE, PORTAL

### EPIC-Like With Caveats

ALPACA, CTXC, EPIC, KEY, UNFI

### Raw EPIC-Like Rejected / Trap / No Signal After 15m QA

AST, FLOW, GHST, MOB, PDA, STPT

## Class Feature Summary

| class                        |   n |   median_drawdown_to_bottom |   median_days_to_bottom |   median_quote_volume_at_bottom |   median_quote_volume_at_signal_1h |   median_quote_volume_at_signal_15m |   median_rebound_90d | signal_types                                                           | 15m_statuses                                                                                                    | tokens                                                                                                                                                                                                                                                                                                                      |
|:-----------------------------|----:|----------------------------:|------------------------:|--------------------------------:|-----------------------------------:|------------------------------------:|---------------------:|:-----------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| clean_epic_like              |   2 |                   -0.662812 |                 55.4061 |                        344024   |                        1.29746e+06 |                             73224.8 |            3.89862   | SLOW_BLEED_SQUEEZE_BREAKOUT, CAPITULATION_RECLAIM, HIGHER_LOW_BREAKOUT | clean_confirmed                                                                                                 | BAKE, PORTAL                                                                                                                                                                                                                                                                                                                |
| caveat_epic_like             |   5 |                   -0.663267 |                 10.5831 |                        446282   |                   482645           |                             85674.2 |            1.34966   | SLOW_BLEED_SQUEEZE_BREAKOUT, CAPITULATION_RECLAIM, HIGHER_LOW_BREAKOUT | downgraded_unclear, low_liquidity_caveat, wick_or_artifact                                                      | ALPACA, CTXC, EPIC, KEY, UNFI                                                                                                                                                                                                                                                                                               |
| failed_trap_epic_like        |   6 |                   -0.799634 |                 50.5515 |                        210390   |                   164028           |                             20347.7 |            3.23342   | SLOW_BLEED_SQUEEZE_BREAKOUT, CAPITULATION_RECLAIM, HIGHER_LOW_BREAKOUT | failed_or_trap, no_15m_or_no_1h_signal                                                                          | AST, FLOW, GHST, MOB, PDA, STPT                                                                                                                                                                                                                                                                                             |
| strong_rebound_no_signal     |  22 |                   -0.341608 |                  6.2495 |                        127269   |                      nan           |                               nan   |            1.20289   | none                                                                   | none                                                                                                            | AERGO, BETA, BOND, BTS, CVX, FIRO, GTC, HEI, HIGH, IDEX, KP3R, MDX, PERP, POND, PROS, QI, REEF, VIC, WAN, WIF, WNXM, ZEC                                                                                                                                                                                                    |
| failed_trap_all              |  39 |                   -0.735079 |                 35.3118 |                         86133.6 |                   164028           |                             57226.9 |            1.13163   | SLOW_BLEED_SQUEEZE_BREAKOUT, HIGHER_LOW_BREAKOUT, CAPITULATION_RECLAIM | failed_or_trap, wick_or_artifact, clean_confirmed, clean_but_weaker, downgraded_unclear, no_15m_or_no_1h_signal | A2Z, ACA, AST, ATA, BSW, COOKIE, DEGO, DENT, EPX, FIS, FLM, FLOW, FOR, GHST, GPS, HIFI, HOOK, IRIS, KDA, KEY, KMD, LTO, MDT, MOB, MOVE, NKN, PDA, PORTAL, STMX, STPT, SYS, TROY, UFT, UNFI, VGX, VITE, VOXEL, WAVES, ZEN                                                                                                    |
| continued_bleed_death_spiral |  18 |                   -0.883801 |                 28.7913 |                        262841   |                        2.00626e+06 |                               nan   |            0.167125  | SLOW_BLEED_SQUEEZE_BREAKOUT                                            | none                                                                                                            | ALPHA, BURGER, CVP, DOCK, DREP, FORTH, LEVER, MULTI, OOKI, PERL, PNT, SLF, TROY, VIB, VIDT, WAVES, WING, WTC                                                                                                                                                                                                                |
| weak_rebound                 |  55 |                   -0.773173 |                 24.7391 |                        143253   |                   940548           |                               nan   |            0.0762195 | SLOW_BLEED_SQUEEZE_BREAKOUT                                            | none                                                                                                            | AKRO, ALCX, ALPHA, AMB, BADGER, BURGER, CHESS, COOKIE, CVP, D, DATA, DF, DOCK, DODO, DREP, FIO, FORTH, FUN, GFT, HFT, IDRT, LEVER, LOOM, LRC, MLN, MULTI, NFP, NON, NTRN, OAX, OOKI, OXT, PERL, PHB, PNT, QUICK, RDNT, RESOLV, SLF, SNM, SRM, STORJ, SYN, TLM, TORN, TROY, TRU, VAI, VIB, VIDT, WAVES, WING, WRX, WTC, YFII |

## Clean EPIC-Like Pattern

Observed clean cases: BAKE, PORTAL.

Common features in this small clean subset:

- Deep post-risk-event drawdown before rebound.
- Causal signal survives 15m QA: no stop failure, no wick/range artifact, no single-candle artifact.
- 15m entry quote volume is not necessarily huge, but is above hard low-liquidity threshold.
- Rebound after refined entry is large enough that R/R remains strong after moving from 1h to 15m path.
- Signal types in clean subset: SLOW_BLEED_SQUEEZE_BREAKOUT, CAPITULATION_RECLAIM, HIGHER_LOW_BREAKOUT.

## Caveat EPIC-Like Pattern

Caveat cases: ALPACA, CTXC, EPIC, KEY, UNFI.

Typical caveats:

- Low quote volume at the actual 15m entry, even when the 1h candle looked acceptable.
- Rebound exists, but refined 15m entry produces weak R/R.
- Wick/range or artifact warning on the confirmation candle.
- Manual review remains necessary when the rebound is real but execution quality is questionable.

## Failed / Trap Cases Versus Clean EPIC-Like

Failed/trap cases are not simply “no rebound” cases. Many had large historical MFE, but 15m QA showed the signal was poor.

Differences versus clean EPIC-like:

- Stop failure is common: 39/147 = 26.5% of the full universe had at least one failed signal.
- Failed/trap signals more often show low entry liquidity, wick/range risk, or false-breakout flags.
- Some traps still have high future rebound, which is exactly why 15m QA is needed: raw rebound alone overstates pattern quality.
- Clean EPIC-like retained high R/R after 15m refinement; failed/trap cases often lost quality when entry was moved from coarse 1h logic to 15m path.

## Continued Bleed / Weak Rebound

- Continued bleed / death spiral: 18/147 = 12.2%
- Weak rebound <20% max 90d: 55/147 = 37.4%

These are the historical counterweight to EPIC-like cases: many risk-event tokens either did not form a meaningful rebound or remained too data-poor / low-liquidity to classify confidently.

## Future Monitoring Implications

Signals that historically increased EPIC-like quality:

- Deep drawdown followed by a causal confirmation structure, not just a wick off the low.
- Improved liquidity at the signal versus the absolute bottom.
- Clean 15m confirmation: no single-candle artifact, no obvious wick/range risk, no immediate stop failure.
- Strong post-signal MFE that remains strong after 15m entry refinement.

Signals that historically looked more like trap / continued bleed:

- Low quote volume at the actual signal candle.
- Rebound measured mostly from one wick or one illiquid candle.
- Stop failure soon after the signal.
- Strong rebound without causal signal: historically present in 22/147 = 15.0%.
- Missing path / old delisted data, which should remain manual review instead of being forced into a clean class.

Manual review should remain mandatory for:

- low-liquidity bottoms or signal candles;
- suspicious fallback or single-exchange spikes;
- missing 1h path;
- raw EPIC-like labels without clean 15m confirmation;
- cases where rebound exists but causal signal was not observable under the rules.

## Output Tables

- `data/processed/bottom_rebound_historical_base_rate_summary.csv`
- `data/processed/bottom_rebound_historical_feature_summary.csv`
