#!/usr/bin/env python3
"""Build a static Russian dashboard for Monitoring Tag cluster what-if results."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/processed/monitoring_tag_cluster_summary_whatif.csv"
TOKEN_PATH = ROOT / "data/processed/monitoring_tag_cluster_token_whatif.csv"
OUT_PATH = ROOT / "docs/monitoring_tag_cluster_dashboard.html"

HOLD_ORDER = ["1d", "3d", "7d", "14d", "30d"]


def fmt_pct(x: float | int | None) -> str:
    if pd.isna(x):
        return ""
    return f"{float(x) * 100:.1f}%"


def fmt_num(x: float | int | None) -> str:
    if pd.isna(x):
        return ""
    return f"{float(x):,.2f}"


def clean_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for row in df.to_dict(orient="records"):
        cleaned = {}
        for key, value in row.items():
            if pd.isna(value):
                cleaned[key] = None
            elif isinstance(value, (pd.Timestamp,)):
                cleaned[key] = value.isoformat()
            else:
                cleaned[key] = value
        records.append(cleaned)
    return records


def build_dashboard() -> None:
    summary = pd.read_csv(SUMMARY_PATH)
    tokens = pd.read_csv(TOKEN_PATH)

    summary["hold_rank"] = summary["hold_window"].map({h: i for i, h in enumerate(HOLD_ORDER)})
    summary = summary.sort_values(["cluster_date_utc", "hold_rank"])
    tokens["hold_rank"] = tokens["hold_window"].map({h: i for i, h in enumerate(HOLD_ORDER)})
    tokens = tokens.sort_values(["cluster_date_utc", "token_symbol", "hold_rank"])

    total_clusters = summary["cluster_id"].nunique()
    unique_tokens = tokens["token_symbol"].nunique()
    cluster_dates = sorted(summary["cluster_date_utc"].dropna().unique().tolist())

    by_hold = (
        summary.groupby("hold_window")
        .agg(
            clusters=("cluster_id", "nunique"),
            valid_tokens=("valid_token_results", "sum"),
            missing_tokens=("missing_token_results", "sum"),
            liquidations=("liquidation_count_approx", "sum"),
            margin_usdt=("total_margin_usdt", "sum"),
            pnl_liq=("total_pnl_usdt_liq_cap", "sum"),
            pnl_no_liq=("total_pnl_usdt_no_liq", "sum"),
            median_cluster_roi=("roi_on_margin_liq_cap", "median"),
            winning_clusters=("roi_on_margin_liq_cap", lambda x: int((x > 0).sum())),
            losing_clusters=("roi_on_margin_liq_cap", lambda x: int((x < 0).sum())),
        )
        .reset_index()
    )
    by_hold["hold_rank"] = by_hold["hold_window"].map({h: i for i, h in enumerate(HOLD_ORDER)})
    by_hold["roi_liq"] = by_hold["pnl_liq"] / by_hold["margin_usdt"]
    by_hold["roi_no_liq"] = by_hold["pnl_no_liq"] / by_hold["margin_usdt"]
    by_hold = by_hold.sort_values("hold_rank")

    worst_30d = (
        summary[summary["hold_window"] == "30d"]
        .dropna(subset=["roi_on_margin_liq_cap"])
        .sort_values("roi_on_margin_liq_cap")
        .head(5)
    )
    best_30d = (
        summary[summary["hold_window"] == "30d"]
        .dropna(subset=["roi_on_margin_liq_cap"])
        .sort_values("roi_on_margin_liq_cap", ascending=False)
        .head(5)
    )

    payload = {
        "summary": clean_records(summary),
        "tokens": clean_records(tokens),
        "holdOrder": HOLD_ORDER,
        "clusterDates": cluster_dates,
    }

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Дашборд кластеров Monitoring Tag</title>
  <style>
    :root {{
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #1b1f24;
      --muted: #65707d;
      --line: #d9dee6;
      --good: #087f5b;
      --bad: #c92a2a;
      --warn: #b7791f;
      --accent: #2457c5;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      padding: 22px 28px 14px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      position: sticky;
      top: 0;
      z-index: 5;
    }}
    h1 {{ margin: 0 0 8px; font-size: 24px; letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); line-height: 1.45; }}
    main {{ padding: 22px 28px 36px; }}
    .grid {{ display: grid; gap: 14px; }}
    .cards {{ grid-template-columns: repeat(4, minmax(150px, 1fr)); margin-bottom: 18px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .label {{ color: var(--muted); font-size: 12px; }}
    .value {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
    section {{ margin-top: 18px; }}
    h2 {{ font-size: 18px; margin: 0 0 10px; }}
    .toolbar {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }}
    select, input {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 14px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      font-size: 13px;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; background: #f0f2f5; position: sticky; top: 93px; z-index: 2; }}
    tr:last-child td {{ border-bottom: none; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .good {{ color: var(--good); font-weight: 650; }}
    .bad {{ color: var(--bad); font-weight: 650; }}
    .warn {{ color: var(--warn); font-weight: 650; }}
    .pill {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 7px;
      color: var(--muted);
      background: #fafbfc;
      font-size: 12px;
      margin: 1px 2px 1px 0;
    }}
    .barwrap {{ width: 160px; height: 9px; background: #edf0f4; border-radius: 999px; overflow: hidden; display: inline-block; }}
    .bar {{ height: 100%; background: var(--accent); }}
    .two {{ grid-template-columns: 1fr 1fr; }}
    .note {{ margin: 10px 0; color: var(--muted); font-size: 13px; }}
    .scroll {{ overflow: auto; max-height: 620px; border-radius: 8px; }}
    a {{ color: var(--accent); }}
    @media (max-width: 960px) {{
      .cards, .two {{ grid-template-columns: 1fr; }}
      th {{ position: static; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Дашборд кластеров Monitoring Tag</h1>
    <p>Кластеры сгруппированы по UTC-дате Binance announcement. Модель: short на каждый токен, 100 USDT маржи, 10x, фиксированные окна удержания, liquidation cap при +10% adverse move.</p>
  </header>
  <main>
    <div class="grid cards">
      <div class="card"><div class="label">Кластеры</div><div class="value">{total_clusters}</div></div>
      <div class="card"><div class="label">Уникальные токены</div><div class="value">{unique_tokens}</div></div>
      <div class="card"><div class="label">Строки токен-окно</div><div class="value">{len(tokens):,}</div></div>
      <div class="card"><div class="label">Строки кластер-окно</div><div class="value">{len(summary):,}</div></div>
    </div>

    <section>
      <h2>Сводка по окнам удержания</h2>
      <table>
        <thead><tr>
          <th>Окно</th><th class="num">Токены с ценами</th><th class="num">Усл. ликвидации</th><th class="num">PnL с liq-cap</th><th class="num">ROI с liq-cap</th><th class="num">PnL без liq-cap</th><th class="num">ROI без liq-cap</th><th class="num">Медианный ROI кластера</th><th class="num">W/L кластеры</th>
        </tr></thead>
        <tbody>
          {''.join(f'<tr><td>{r.hold_window}</td><td class="num">{int(r.valid_tokens)}</td><td class="num">{int(r.liquidations)}</td><td class="num {("good" if r.pnl_liq >= 0 else "bad")}">{fmt_num(r.pnl_liq)}</td><td class="num {("good" if r.roi_liq >= 0 else "bad")}">{fmt_pct(r.roi_liq)}</td><td class="num {("good" if r.pnl_no_liq >= 0 else "bad")}">{fmt_num(r.pnl_no_liq)}</td><td class="num {("good" if r.roi_no_liq >= 0 else "bad")}">{fmt_pct(r.roi_no_liq)}</td><td class="num">{fmt_pct(r.median_cluster_roi)}</td><td class="num">{int(r.winning_clusters)} / {int(r.losing_clusters)}</td></tr>' for r in by_hold.itertuples())}
        </tbody>
      </table>
    </section>

    <section class="grid two">
      <div>
        <h2>Худшие 30d кластеры</h2>
        <table>
          <thead><tr><th>Дата</th><th>Токены</th><th class="num">Ликв.</th><th class="num">PnL</th><th class="num">ROI</th></tr></thead>
          <tbody>
            {''.join(f'<tr><td>{r.cluster_date_utc}</td><td>{r.tokens}</td><td class="num">{int(r.liquidation_count_approx)}</td><td class="num bad">{fmt_num(r.total_pnl_usdt_liq_cap)}</td><td class="num bad">{fmt_pct(r.roi_on_margin_liq_cap)}</td></tr>' for r in worst_30d.itertuples())}
          </tbody>
        </table>
      </div>
      <div>
        <h2>Лучшие 30d кластеры</h2>
        <table>
          <thead><tr><th>Дата</th><th>Токены</th><th class="num">Ликв.</th><th class="num">PnL</th><th class="num">ROI</th></tr></thead>
          <tbody>
            {''.join(f'<tr><td>{r.cluster_date_utc}</td><td>{r.tokens}</td><td class="num">{int(r.liquidation_count_approx)}</td><td class="num good">{fmt_num(r.total_pnl_usdt_liq_cap)}</td><td class="num good">{fmt_pct(r.roi_on_margin_liq_cap)}</td></tr>' for r in best_30d.itertuples())}
          </tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Просмотр кластеров</h2>
      <div class="toolbar">
        <label>Дата announcement <select id="clusterSelect"></select></label>
        <label>Окно удержания <select id="holdSelect"><option value="all">все</option>{''.join(f'<option value="{h}">{h}</option>' for h in HOLD_ORDER)}</select></label>
        <label>Фильтр по токену <input id="tokenFilter" placeholder="например CVX"></label>
      </div>
      <div id="clusterMeta" class="note"></div>
      <div class="scroll">
        <table id="clusterTable">
          <thead><tr>
            <th>Дата</th><th>Окно</th><th>Токены</th><th class="num">С ценами</th><th class="num">Нет цены</th><th class="num">Усл. ликв.</th><th class="num">PnL с liq-cap</th><th class="num">ROI</th><th class="num">Лучший токен</th><th class="num">Худший токен</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Результаты токенов внутри выбранного кластера</h2>
      <div class="scroll">
        <table id="tokenTable">
          <thead><tr>
            <th>Токен</th><th>Исход</th><th>Окно</th><th>Пара</th><th class="num">Вход</th><th class="num">Выход</th><th class="num">Spot return</th><th class="num">PnL с liq-cap</th><th class="num">ROI</th><th class="num">Макс. против</th><th class="num">Макс. в пользу</th><th>Ликв. задета</th><th>Нет цены</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const DATA = {json.dumps(payload, ensure_ascii=False)};
    const holdOrder = DATA.holdOrder;
    const fmtNum = v => v === null || Number.isNaN(v) ? '' : Number(v).toLocaleString(undefined, {{maximumFractionDigits: 2}});
    const fmtPct = v => v === null || Number.isNaN(v) ? '' : (Number(v) * 100).toFixed(1) + '%';
    const cls = v => v === null || Number.isNaN(v) ? '' : (Number(v) >= 0 ? 'good' : 'bad');
    const clusterSelect = document.getElementById('clusterSelect');
    const holdSelect = document.getElementById('holdSelect');
    const tokenFilter = document.getElementById('tokenFilter');
    for (const d of DATA.clusterDates) {{
      const opt = document.createElement('option');
      opt.value = d;
      opt.textContent = d;
      clusterSelect.appendChild(opt);
    }}
    function render() {{
      const date = clusterSelect.value || DATA.clusterDates[0];
      const hold = holdSelect.value;
      const tokenNeedle = tokenFilter.value.trim().toUpperCase();
      let clusterRows = DATA.summary.filter(r => r.cluster_date_utc === date);
      if (hold !== 'all') clusterRows = clusterRows.filter(r => r.hold_window === hold);
      if (tokenNeedle) clusterRows = clusterRows.filter(r => String(r.tokens || '').toUpperCase().includes(tokenNeedle));
      clusterRows.sort((a,b) => holdOrder.indexOf(a.hold_window) - holdOrder.indexOf(b.hold_window));
      document.querySelector('#clusterTable tbody').innerHTML = clusterRows.map(r => `
        <tr>
          <td>${{r.cluster_date_utc}}</td>
          <td><span class="pill">${{r.hold_window}}</span></td>
          <td>${{String(r.tokens || '').split(',').map(t => `<span class="pill">${{t}}</span>`).join('')}}</td>
          <td class="num">${{r.valid_token_results}}</td>
          <td class="num">${{r.missing_token_results}}</td>
          <td class="num">${{r.liquidation_count_approx}}</td>
          <td class="num ${{cls(r.total_pnl_usdt_liq_cap)}}">${{fmtNum(r.total_pnl_usdt_liq_cap)}}</td>
          <td class="num ${{cls(r.roi_on_margin_liq_cap)}}">${{fmtPct(r.roi_on_margin_liq_cap)}}</td>
          <td class="num">${{fmtNum(r.best_token_pnl_liq_cap)}}</td>
          <td class="num">${{fmtNum(r.worst_token_pnl_liq_cap)}}</td>
        </tr>`).join('');

      let tokenRows = DATA.tokens.filter(r => r.cluster_date_utc === date);
      if (hold !== 'all') tokenRows = tokenRows.filter(r => r.hold_window === hold);
      if (tokenNeedle) tokenRows = tokenRows.filter(r => String(r.token_symbol || '').toUpperCase().includes(tokenNeedle));
      tokenRows.sort((a,b) => String(a.token_symbol).localeCompare(String(b.token_symbol)) || holdOrder.indexOf(a.hold_window) - holdOrder.indexOf(b.hold_window));
      const tokens = [...new Set(tokenRows.map(r => r.token_symbol))].filter(Boolean);
      document.getElementById('clusterMeta').textContent = `${{date}}: показано токенов: ${{tokens.length}}; строк токен-окно: ${{tokenRows.length}}.`;
      document.querySelector('#tokenTable tbody').innerHTML = tokenRows.map(r => `
        <tr>
          <td><strong>${{r.token_symbol || ''}}</strong></td>
          <td>${{r.final_outcome || ''}}</td>
          <td><span class="pill">${{r.hold_window}}</span></td>
          <td>${{r.symbol_pair || ''}}</td>
          <td class="num">${{fmtNum(r.entry_price)}}</td>
          <td class="num">${{fmtNum(r.exit_price)}}</td>
          <td class="num ${{cls(-Number(r.spot_raw_return || 0))}}">${{fmtPct(r.spot_raw_return)}}</td>
          <td class="num ${{cls(r.pnl_usdt_liq_cap)}}">${{fmtNum(r.pnl_usdt_liq_cap)}}</td>
          <td class="num ${{cls(r.roi_on_margin_liq_cap)}}">${{fmtPct(r.roi_on_margin_liq_cap)}}</td>
          <td class="num warn">${{fmtPct(r.max_adverse_return_path)}}</td>
          <td class="num good">${{fmtPct(r.max_favorable_return_path)}}</td>
          <td>${{r.liquidation_touched_approx || ''}}</td>
          <td>${{r.missing_price_flag === 'yes' ? (r.missing_price_reason || 'missing') : ''}}</td>
        </tr>`).join('');
    }}
    clusterSelect.addEventListener('change', render);
    holdSelect.addEventListener('change', render);
    tokenFilter.addEventListener('input', render);
    clusterSelect.value = DATA.clusterDates[0];
    render();
  </script>
</body>
</html>
"""

    OUT_PATH.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_dashboard()
    print(f"wrote {OUT_PATH}")
