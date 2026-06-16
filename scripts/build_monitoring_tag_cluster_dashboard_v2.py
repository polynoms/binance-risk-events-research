#!/usr/bin/env python3
"""Build a clearer Russian dashboard for Monitoring Tag cluster what-if results."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/processed/monitoring_tag_cluster_summary_whatif.csv"
TOKEN_PATH = ROOT / "data/processed/monitoring_tag_cluster_token_whatif.csv"
OUT_PATH = ROOT / "docs/monitoring_tag_cluster_dashboard_v2.html"

HOLD_ORDER = ["1d", "3d", "7d", "14d", "30d"]


def safe_float(value):
    if pd.isna(value):
        return None
    return float(value)


def safe_int(value):
    if pd.isna(value):
        return None
    return int(value)


def records(df: pd.DataFrame) -> list[dict]:
    out = []
    for row in df.to_dict(orient="records"):
        clean = {}
        for key, value in row.items():
            if pd.isna(value):
                clean[key] = None
            else:
                clean[key] = value
        out.append(clean)
    return out


def build_payload(summary: pd.DataFrame, tokens: pd.DataFrame) -> dict:
    token_lists = (
        tokens.groupby("cluster_date_utc")["token_symbol"]
        .apply(lambda x: ",".join(sorted({str(v) for v in x.dropna()})))
        .to_dict()
    )
    token_counts = (
        tokens.groupby("cluster_date_utc")["token_symbol"]
        .nunique()
        .to_dict()
    )

    clusters = []
    for date, grp in summary.groupby("cluster_date_utc", sort=True):
        first = grp.iloc[0]
        cluster_tokens = token_lists.get(date) or first["tokens"] or ""
        cluster_token_count = int(token_counts.get(date) or first["tokens_in_cluster"] or 0)
        by_hold = {}
        for _, row in grp.iterrows():
            hold = row["hold_window"]
            by_hold[hold] = {
                "valid": safe_int(row["valid_token_results"]),
                "missing": safe_int(row["missing_token_results"]),
                "liq": safe_int(row["liquidation_count_approx"]),
                "pnl": safe_float(row["total_pnl_usdt_liq_cap"]),
                "pnl_no_liq": safe_float(row["total_pnl_usdt_no_liq"]),
                "margin": safe_float(row["total_margin_usdt"]),
                "roi": safe_float(row["roi_on_margin_liq_cap"]),
                "roi_no_liq": safe_float(row["roi_on_margin_no_liq"]),
                "best": safe_float(row["best_token_pnl_liq_cap"]),
                "worst": safe_float(row["worst_token_pnl_liq_cap"]),
            }
        roi_1d = by_hold.get("1d", {}).get("roi")
        roi_7d = by_hold.get("7d", {}).get("roi")
        roi_30d = by_hold.get("30d", {}).get("roi")
        liq_30d = by_hold.get("30d", {}).get("liq")
        clusters.append(
            {
                "date": date,
                "tokens": cluster_tokens,
                "token_count": cluster_token_count,
                "by_hold": by_hold,
                "roi_1d": roi_1d,
                "roi_7d": roi_7d,
                "roi_30d": roi_30d,
                "liq_30d": liq_30d,
            }
        )

    token_rows = records(tokens)
    by_hold_totals = (
        summary.groupby("hold_window")
        .agg(
            valid=("valid_token_results", "sum"),
            liq=("liquidation_count_approx", "sum"),
            pnl=("total_pnl_usdt_liq_cap", "sum"),
            margin=("total_margin_usdt", "sum"),
            wins=("roi_on_margin_liq_cap", lambda x: int((x > 0).sum())),
            losses=("roi_on_margin_liq_cap", lambda x: int((x < 0).sum())),
        )
        .reset_index()
    )
    by_hold_totals["roi"] = by_hold_totals["pnl"] / by_hold_totals["margin"]
    by_hold_totals["rank"] = by_hold_totals["hold_window"].map({h: i for i, h in enumerate(HOLD_ORDER)})
    by_hold_totals = by_hold_totals.sort_values("rank")

    return {
        "clusters": clusters,
        "tokenRows": token_rows,
        "holdOrder": HOLD_ORDER,
        "totals": records(by_hold_totals),
    }


def build_dashboard() -> None:
    summary = pd.read_csv(SUMMARY_PATH)
    tokens = pd.read_csv(TOKEN_PATH)
    payload = build_payload(summary, tokens)

    html = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Monitoring Tag: карта кластеров</title>
  <style>
    :root {
      --bg: #f5f6f8;
      --panel: #fff;
      --ink: #17202a;
      --muted: #667085;
      --line: #d8dde6;
      --good: #087f5b;
      --bad: #c92a2a;
      --warn: #b7791f;
      --accent: #1d4ed8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 18px 24px 12px;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    h1 { margin: 0 0 6px; font-size: 23px; }
    h2 { margin: 0 0 10px; font-size: 17px; }
    p { margin: 0; color: var(--muted); line-height: 1.45; }
    main { padding: 18px 24px 32px; }
    .topgrid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 16px; }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }
    .label { font-size: 12px; color: var(--muted); }
    .value { font-size: 21px; font-weight: 750; margin-top: 3px; font-variant-numeric: tabular-nums; }
    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      margin: 10px 0 12px;
    }
    input, select, button {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 7px;
      padding: 8px 10px;
      font-size: 14px;
    }
    button { cursor: pointer; }
    button.active { border-color: var(--accent); color: var(--accent); font-weight: 700; }
    .layout { display: grid; grid-template-columns: minmax(620px, 1.45fr) minmax(420px, 1fr); gap: 14px; align-items: start; }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      overflow: hidden;
    }
    .scroll { overflow: auto; max-height: 72vh; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid var(--line); padding: 8px 9px; text-align: left; font-size: 13px; vertical-align: middle; }
    th { background: #f0f2f5; color: var(--muted); font-weight: 650; position: sticky; top: 0; z-index: 2; }
    tr.selected td { outline: 2px solid rgba(29,78,216,.18); background: #f8fbff; }
    .num { text-align: right; font-variant-numeric: tabular-nums; }
    .tokenlist { max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--muted); }
    .pill {
      display: inline-block;
      padding: 2px 7px;
      margin: 1px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fafbfc;
      color: var(--muted);
      font-size: 12px;
    }
    .heat {
      color: #111827;
      border-radius: 6px;
      padding: 6px 7px;
      min-width: 76px;
      display: inline-block;
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-weight: 700;
    }
    .sub { display: block; font-size: 11px; color: rgba(17,24,39,.62); font-weight: 600; margin-top: 2px; }
    .good { color: var(--good); }
    .bad { color: var(--bad); }
    .warn { color: var(--warn); }
    .hint { color: var(--muted); font-size: 12px; margin-top: 8px; }
    .mini { font-size: 12px; color: var(--muted); }
    .token-title { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
    .token-title strong { font-size: 16px; }
    .nowrap { white-space: nowrap; }
    .cluster-profit-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(92px, 1fr));
      gap: 7px;
      margin: 8px 0 10px;
    }
    .profit-box {
      border: 1px solid var(--line);
      background: #fafbfc;
      border-radius: 7px;
      padding: 7px;
    }
    .profit-box .hold { font-size: 12px; color: var(--muted); }
    .profit-box .profit { font-size: 15px; font-weight: 750; margin-top: 2px; font-variant-numeric: tabular-nums; }
    .profit-box .meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
    @media (max-width: 1180px) {
      .layout { grid-template-columns: 1fr; }
      .topgrid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 700px) {
      main, header { padding-left: 12px; padding-right: 12px; }
      .topgrid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Monitoring Tag: карта кластеров</h1>
    <p>Кластер = все токены из одного Binance announcement в один UTC-день. Модель: short по 100 USDT маржи на токен, 10x, фиксированное окно удержания, условная ликвидация при +10% adverse move.</p>
  </header>
  <main>
    <div id="totals" class="topgrid"></div>

    <div class="toolbar">
      <input id="search" placeholder="поиск токена или даты">
      <select id="clusterSize">
        <option value="0">любой размер кластера</option>
        <option value="3">минимум 3 токена</option>
        <option value="5">минимум 5 токенов</option>
        <option value="8">минимум 8 токенов</option>
      </select>
      <select id="quickView">
        <option value="all">все кластеры</option>
        <option value="bad_1d">убыточные 1d</option>
        <option value="bad_7d">убыточные 7d</option>
        <option value="bad_30d">убыточные 30d</option>
        <option value="many_liq">много ликвидаций 30d</option>
      </select>
      <button id="sortDate" class="active">сортировать по дате</button>
      <button id="sort30d">по ROI 30d</button>
      <button id="sortLiq">по ликвидациям</button>
    </div>

    <div class="layout">
      <section class="panel">
        <h2>1. Heatmap кластеров <span id="coverageCounter" class="mini"></span></h2>
        <div class="hint">Кликни по строке кластера, чтобы увидеть токены справа. Цвет ячейки = ROI кластера с liquidation cap; подпись снизу = долларовый PnL и число условных ликвидаций. Всего в датасете: <strong id="totalClustersText"></strong>.</div>
        <div class="scroll">
          <table id="clusterTable">
            <thead>
              <tr>
                <th>Дата</th>
                <th class="num">Токенов</th>
                <th>Состав</th>
                <th class="num">1d</th>
                <th class="num">3d</th>
                <th class="num">7d</th>
                <th class="num">14d</th>
                <th class="num">30d</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>

      <section class="panel">
        <div class="token-title">
          <strong id="selectedTitle">Токены кластера</strong>
          <span id="selectedMeta" class="mini"></span>
        </div>
        <div id="selectedProfitGrid" class="cluster-profit-grid"></div>
        <div class="toolbar">
          <select id="tokenHold">
            <option value="all">все окна</option>
            <option value="1d">1d</option>
            <option value="3d">3d</option>
            <option value="7d">7d</option>
            <option value="14d">14d</option>
            <option value="30d">30d</option>
          </select>
          <select id="tokenSort">
            <option value="token">по токену</option>
            <option value="pnlAsc">хуже сверху</option>
            <option value="pnlDesc">лучше сверху</option>
            <option value="liq">сначала ликвидации</option>
          </select>
        </div>
        <div class="scroll">
          <table id="tokenTable">
            <thead>
              <tr>
                <th>Токен</th>
                <th>Окно</th>
                <th>Исход</th>
                <th class="num">PnL USDT</th>
                <th class="num">ROI</th>
                <th class="num">Против</th>
                <th class="num">В пользу</th>
                <th>Флаг</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>
    </div>
  </main>

  <script>
    const DATA = __PAYLOAD__;
    const holdOrder = DATA.holdOrder;
    let selectedDate = DATA.clusters[0]?.date || '';
    let sortMode = 'date';

    const fmtNum = v => v === null || Number.isNaN(Number(v)) ? '' : Number(v).toLocaleString(undefined, {maximumFractionDigits: 2});
    const fmtPct = v => v === null || Number.isNaN(Number(v)) ? '' : (Number(v) * 100).toFixed(1) + '%';
    const cssSign = v => v === null || Number.isNaN(Number(v)) ? '' : (Number(v) >= 0 ? 'good' : 'bad');

    function heatStyle(roi) {
      if (roi === null || Number.isNaN(Number(roi))) return 'background:#eef1f5;color:#667085;';
      const r = Math.max(-1, Math.min(2, Number(roi)));
      if (r >= 0) {
        const a = 0.14 + Math.min(0.72, r / 2 * 0.72);
        return `background:rgba(8,127,91,${a});`;
      }
      const a = 0.14 + Math.min(0.72, Math.abs(r) * 0.72);
      return `background:rgba(201,42,42,${a});`;
    }

    function renderTotals() {
      const cards = DATA.totals.map(r => `
        <div class="card">
          <div class="label">${r.hold_window}: PnL / ROI / ликв.</div>
          <div class="value ${cssSign(r.pnl)}">${fmtNum(r.pnl)} USDT</div>
          <div class="mini">${fmtPct(r.roi)} ROI, ликвидаций: ${r.liq}, W/L: ${r.wins}/${r.losses}</div>
        </div>
      `).join('');
      document.getElementById('totals').innerHTML = cards;
    }

    function filteredClusters() {
      const q = document.getElementById('search').value.trim().toUpperCase();
      const minSize = Number(document.getElementById('clusterSize').value);
      const quick = document.getElementById('quickView').value;
      let rows = DATA.clusters.filter(c => c.token_count >= minSize);
      if (q) rows = rows.filter(c => c.date.includes(q) || String(c.tokens).toUpperCase().includes(q));
      if (quick === 'bad_1d') rows = rows.filter(c => (c.by_hold['1d']?.roi ?? 0) < 0);
      if (quick === 'bad_7d') rows = rows.filter(c => (c.by_hold['7d']?.roi ?? 0) < 0);
      if (quick === 'bad_30d') rows = rows.filter(c => (c.by_hold['30d']?.roi ?? 0) < 0);
      if (quick === 'many_liq') rows = rows.filter(c => (c.by_hold['30d']?.liq ?? 0) >= Math.max(2, Math.ceil(c.token_count / 2)));
      if (sortMode === 'date') rows.sort((a,b) => a.date.localeCompare(b.date));
      if (sortMode === 'roi30') rows.sort((a,b) => ((b.by_hold['30d']?.roi ?? -999) - (a.by_hold['30d']?.roi ?? -999)));
      if (sortMode === 'liq') rows.sort((a,b) => ((b.by_hold['30d']?.liq ?? -1) - (a.by_hold['30d']?.liq ?? -1)));
      return rows;
    }

    function holdCell(c, hold) {
      const h = c.by_hold[hold];
      if (!h || h.roi === null) return '<td class="num"><span class="heat" style="background:#eef1f5;color:#667085;">нет<span class="sub">цены</span></span></td>';
      return `<td class="num"><span class="heat" style="${heatStyle(h.roi)}">${fmtPct(h.roi)}<span class="sub">PnL $ ${fmtNum(h.pnl)}</span><span class="sub">liq ${h.liq}</span></span></td>`;
    }

    function renderClusters() {
      const rows = filteredClusters();
      if (!rows.some(c => c.date === selectedDate) && rows[0]) selectedDate = rows[0].date;
      const body = rows.map(c => `
        <tr data-date="${c.date}" class="${c.date === selectedDate ? 'selected' : ''}">
          <td class="nowrap"><strong>${c.date}</strong></td>
          <td class="num">${c.token_count}</td>
          <td><div class="tokenlist" title="${c.tokens || ''}">${c.tokens || ''}</div></td>
          ${holdOrder.map(h => holdCell(c, h)).join('')}
        </tr>
      `).join('');
      document.querySelector('#clusterTable tbody').innerHTML = body;
      document.getElementById('coverageCounter').textContent = `показано ${rows.length} из ${DATA.clusters.length}`;
      document.getElementById('totalClustersText').textContent = `${DATA.clusters.length} кластеров / ${DATA.tokenRows.filter(r => r.hold_window === '1d').length} Monitoring Tag events`;
      document.querySelectorAll('#clusterTable tbody tr').forEach(tr => {
        tr.addEventListener('click', () => {
          selectedDate = tr.dataset.date;
          renderClusters();
          renderTokens();
        });
      });
    }

    function renderTokens() {
      const hold = document.getElementById('tokenHold').value;
      const sort = document.getElementById('tokenSort').value;
      let rows = DATA.tokenRows.filter(r => r.cluster_date_utc === selectedDate);
      if (hold !== 'all') rows = rows.filter(r => r.hold_window === hold);
      if (sort === 'token') rows.sort((a,b) => String(a.token_symbol).localeCompare(String(b.token_symbol)) || holdOrder.indexOf(a.hold_window) - holdOrder.indexOf(b.hold_window));
      if (sort === 'pnlAsc') rows.sort((a,b) => (Number(a.pnl_usdt_liq_cap ?? 999999) - Number(b.pnl_usdt_liq_cap ?? 999999)));
      if (sort === 'pnlDesc') rows.sort((a,b) => (Number(b.pnl_usdt_liq_cap ?? -999999) - Number(a.pnl_usdt_liq_cap ?? -999999)));
      if (sort === 'liq') rows.sort((a,b) => String(b.liquidation_touched_approx).localeCompare(String(a.liquidation_touched_approx)));
      const cluster = DATA.clusters.find(c => c.date === selectedDate);
      document.getElementById('selectedTitle').textContent = `Кластер ${selectedDate}`;
      document.getElementById('selectedMeta').textContent = cluster ? `${cluster.token_count} токенов` : '';
      document.getElementById('selectedProfitGrid').innerHTML = cluster
        ? holdOrder.map(h => {
            const x = cluster.by_hold[h];
            if (!x || x.pnl === null) {
              return `<div class="profit-box"><div class="hold">${h}</div><div class="profit">нет цены</div><div class="meta">нет результата</div></div>`;
            }
            return `<div class="profit-box">
              <div class="hold">${h}</div>
              <div class="profit ${cssSign(x.pnl)}">${fmtNum(x.pnl)} USDT</div>
              <div class="meta">ROI ${fmtPct(x.roi)}, liq ${x.liq}</div>
              <div class="meta">без liq-cap: ${fmtNum(x.pnl_no_liq)} USDT</div>
            </div>`;
          }).join('')
        : '';
      document.querySelector('#tokenTable tbody').innerHTML = rows.map(r => {
        const flag = r.missing_price_flag === 'yes'
          ? `нет цены: ${r.missing_price_reason || ''}`
          : (r.liquidation_touched_approx === 'yes' ? 'условная ликвидация' : '');
        return `<tr>
          <td><strong>${r.token_symbol || ''}</strong></td>
          <td><span class="pill">${r.hold_window || ''}</span></td>
          <td>${r.final_outcome || ''}</td>
          <td class="num ${cssSign(r.pnl_usdt_liq_cap)}">${fmtNum(r.pnl_usdt_liq_cap)}</td>
          <td class="num ${cssSign(r.roi_on_margin_liq_cap)}">${fmtPct(r.roi_on_margin_liq_cap)}</td>
          <td class="num warn">${fmtPct(r.max_adverse_return_path)}</td>
          <td class="num good">${fmtPct(r.max_favorable_return_path)}</td>
          <td>${flag}</td>
        </tr>`;
      }).join('');
    }

    function setSort(mode) {
      sortMode = mode;
      document.querySelectorAll('button[id^="sort"]').forEach(b => b.classList.remove('active'));
      if (mode === 'date') document.getElementById('sortDate').classList.add('active');
      if (mode === 'roi30') document.getElementById('sort30d').classList.add('active');
      if (mode === 'liq') document.getElementById('sortLiq').classList.add('active');
      renderClusters();
    }

    document.getElementById('search').addEventListener('input', () => { renderClusters(); renderTokens(); });
    document.getElementById('clusterSize').addEventListener('change', () => { renderClusters(); renderTokens(); });
    document.getElementById('quickView').addEventListener('change', () => { renderClusters(); renderTokens(); });
    document.getElementById('tokenHold').addEventListener('change', renderTokens);
    document.getElementById('tokenSort').addEventListener('change', renderTokens);
    document.getElementById('sortDate').addEventListener('click', () => setSort('date'));
    document.getElementById('sort30d').addEventListener('click', () => setSort('roi30'));
    document.getElementById('sortLiq').addEventListener('click', () => setSort('liq'));

    renderTotals();
    renderClusters();
    renderTokens();
  </script>
</body>
</html>
"""
    html = html.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    build_dashboard()
