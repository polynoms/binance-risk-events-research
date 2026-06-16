# Monitoring Tag Cluster What-If

Assumption: short every token in each same-day Monitoring Tag cluster immediately at announcement/event price.

- Margin per token: `100 USDT`.
- Leverage: `10x`.
- Notional per token: `1000 USDT`.
- Liquidation approximation: if post-entry 1h path trades `+10%` against the short, PnL is capped at `-100 USDT`.
- Fees, funding, borrow, slippage, and real liquidation maintenance margin are not included.

## Overall By Hold Window

| hold_window   |   clusters |   valid_token_results |   liquidations |   total_pnl_liq_cap |   total_margin |   median_cluster_roi |   overall_roi_on_margin_liq_cap |
|:--------------|-----------:|----------------------:|---------------:|--------------------:|---------------:|---------------------:|--------------------------------:|
| 14d           |         20 |                   111 |             60 |            14811.6  |          11100 |             0.54779  |                        1.33437  |
| 1d            |         20 |                   120 |             12 |             7551.36 |          12000 |             0.535844 |                        0.62928  |
| 30d           |         20 |                   101 |             65 |            17898.7  |          10100 |             0.752317 |                        1.77214  |
| 3d            |         20 |                   120 |             29 |            10168.6  |          12000 |             0.501132 |                        0.847383 |
| 7d            |         20 |                   111 |             48 |            13327.4  |          11100 |             0.824814 |                        1.20067  |

## Outputs

- `data/processed/monitoring_tag_cluster_token_whatif.csv`
- `data/processed/monitoring_tag_cluster_summary_whatif.csv`