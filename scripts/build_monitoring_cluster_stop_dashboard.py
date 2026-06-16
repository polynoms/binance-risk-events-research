#!/usr/bin/env python3
"""Build a standalone dashboard for Monitoring Tag cluster stop/BE backtests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"
DOCS = ROOT / "docs"
OUT = DOCS / "monitoring_cluster_stop_dashboard.html"

HOLD_ORDER = ["1h", "4h", "12h", "1d", "3d", "7d", "14d", "30d", "60d", "90d"]


def clean_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, float):
        if value == float("inf"):
            return None
        return round(value, 10)
    return value


def records(df: pd.DataFrame, columns: list[str] | None = None) -> list[dict]:
    if columns is not None:
        df = df[[c for c in columns if c in df.columns]].copy()
    out = []
    for row in df.to_dict(orient="records"):
        out.append({k: clean_value(v) for k, v in row.items()})
    return out


def load_universe(suffix: str) -> dict:
    summary_path = PROCESSED / f"monitoring_cluster_stop_summary_{suffix}.csv"
    cluster_path = PROCESSED / f"monitoring_cluster_stop_cluster_{suffix}.csv"
    token_path = PROCESSED / f"monitoring_cluster_stop_token_{suffix}.csv"
    if not summary_path.exists() or not cluster_path.exists() or not token_path.exists():
        return {"summary": [], "cluster": [], "token": []}
    summary = pd.read_csv(summary_path)
    cluster = pd.read_csv(cluster_path)
    token = pd.read_csv(token_path, low_memory=False)

    token_cols = [
        "cluster_id",
        "cluster_date_utc",
        "token_symbol",
        "hold_window",
        "stop_model",
        "be_model",
        "shortability_status",
        "entry_timestamp_utc",
        "entry_price",
        "exit_timestamp_utc",
        "exit_price",
        "exit_reason",
        "pnl_usdt",
        "roi_on_margin",
        "max_favorable_excursion",
        "max_adverse_excursion",
        "stop_loss_triggered",
        "breakeven_triggered",
        "missing_path_flag",
        "path_issue",
    ]
    return {
        "summary": records(summary),
        "cluster": records(cluster),
        "token": records(token, token_cols),
    }


def build_payload() -> dict:
    return {
        "holdOrder": HOLD_ORDER,
        "datasets": {
            "1h_all": load_universe("all"),
            "1h_shortable_only": load_universe("shortable_only"),
            "15m_shortable_only": load_universe("shortable_only_15m"),
        },
    }


def build_html(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Monitoring Tag cluster stop dashboard</title>
  <style>
    :root {{
      --bg:#f5f6f8; --panel:#fff; --ink:#151922; --muted:#667085; --line:#d9dee7;
      --good:#087f5b; --bad:#c92a2a; --warn:#9a6700; --accent:#1d4ed8;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0; background:var(--bg); color:var(--ink);
      font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      position:sticky; top:0; z-index:20; background:var(--panel); border-bottom:1px solid var(--line);
      padding:14px 18px 10px;
    }}
    h1 {{ margin:0 0 4px; font-size:22px; }}
    h2 {{ margin:0 0 10px; font-size:17px; }}
    p {{ margin:0; color:var(--muted); line-height:1.4; }}
    main {{ padding:14px 18px 28px; }}
    .toolbar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:10px; }}
    label {{ font-size:12px; color:var(--muted); display:flex; flex-direction:column; gap:3px; }}
    select, input, button {{
      border:1px solid var(--line); border-radius:7px; background:#fff; color:var(--ink);
      padding:7px 9px; font-size:13px; min-height:34px;
    }}
    button {{ cursor:pointer; }}
    button.active {{ border-color:var(--accent); color:var(--accent); font-weight:700; }}
    .grid {{ display:grid; grid-template-columns:repeat(6, minmax(130px,1fr)); gap:9px; margin:12px 0; }}
    .card {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:10px; }}
    .label {{ color:var(--muted); font-size:12px; }}
    .value {{ font-size:20px; font-weight:760; margin-top:3px; font-variant-numeric:tabular-nums; }}
    .layout {{ display:grid; grid-template-columns:minmax(620px,1.2fr) minmax(520px,1fr); gap:12px; align-items:start; }}
    .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:11px; overflow:hidden; }}
    .scroll {{ max-height:66vh; overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; }}
    th, td {{ border-bottom:1px solid var(--line); padding:7px 8px; font-size:12.5px; text-align:left; vertical-align:middle; }}
    th {{ background:#f0f2f5; color:var(--muted); position:sticky; top:0; z-index:3; }}
    tr.selected td {{ background:#f7fbff; outline:1px solid rgba(29,78,216,.18); }}
    .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
    .good {{ color:var(--good); font-weight:700; }}
    .bad {{ color:var(--bad); font-weight:700; }}
    .muted {{ color:var(--muted); }}
    .pill {{
      display:inline-block; border:1px solid var(--line); border-radius:999px; padding:2px 7px;
      background:#fafbfc; color:var(--muted); font-size:12px; margin:1px;
    }}
    .tokens {{ max-width:360px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:var(--muted); }}
    .mini {{ font-size:12px; color:var(--muted); margin-top:6px; }}
    .heat {{ border-radius:6px; padding:5px 7px; display:inline-block; min-width:72px; text-align:right; font-weight:750; }}
    .tabs {{ display:flex; gap:6px; flex-wrap:wrap; margin:8px 0 0; }}
    @media (max-width:1100px) {{
      .grid {{ grid-template-columns:repeat(2, minmax(130px,1fr)); }}
      .layout {{ grid-template-columns:1fr; }}
      header {{ position:static; }}
    }}
  </style>
</head>
<body>
<header>
  <h1>Monitoring Tag: кластерный short backtest со стопами и BE</h1>
  <p>Ретроспективный расчёт: 100 USDT margin на токен, 10x, entry на первой 1h свече после Binance Monitoring Tag announcement. Это исследовательский dashboard, не торговая рекомендация.</p>
  <div class="toolbar">
    <label>Dataset
      <select id="universe">
        <option value="15m_shortable_only">15m strict / shortable_only</option>
        <option value="1h_shortable_only">1h proxy / shortable_only</option>
        <option value="1h_all">1h proxy / all</option>
      </select>
    </label>
    <label>Hold
      <select id="hold"></select>
    </label>
    <label>Stop
      <select id="stop"></select>
    </label>
    <label>BE
      <select id="be"></select>
    </label>
    <label>Поиск токена/даты
      <input id="search" placeholder="EPIC или 2026-05-22">
    </label>
    <button id="reset">Сброс</button>
  </div>
  <div class="tabs" id="quickTabs"></div>
</header>
<main>
  <div class="grid" id="kpis"></div>
  <div class="layout">
    <section class="panel">
      <h2>Кластеры по announcement date</h2>
      <div class="mini">Клик по строке показывает токены кластера для выбранных Hold / Stop / BE.</div>
      <div class="scroll"><table id="clusterTable"></table></div>
    </section>
    <section class="panel">
      <h2 id="detailTitle">Токены выбранного кластера</h2>
      <div class="scroll"><table id="tokenTable"></table></div>
    </section>
  </div>
  <section class="panel" style="margin-top:12px;">
    <h2>Сводка вариантов</h2>
    <div class="mini">Сортировка по ROI. Используй для сравнения горизонтов и риск-моделей.</div>
    <div class="scroll" style="max-height:52vh;"><table id="summaryTable"></table></div>
  </section>
</main>
<script>
const DATA = {data};
const fmtPct = x => x == null || Number.isNaN(Number(x)) ? "—" : (Number(x)*100).toFixed(1) + "%";
const fmtUsd = x => x == null || Number.isNaN(Number(x)) ? "—" : (Number(x)).toLocaleString("en-US", {{maximumFractionDigits:0}}) + " $";
const fmtNum = (x,d=2) => x == null || Number.isNaN(Number(x)) ? "—" : Number(x).toFixed(d);
const cls = x => Number(x) >= 0 ? "good" : "bad";
const heat = x => {{
  if (x == null || Number.isNaN(Number(x))) return '<span class="heat">—</span>';
  const v = Number(x);
  const a = Math.min(Math.abs(v), 3) / 3;
  const color = v >= 0 ? `rgba(8,127,91,${{0.12 + a*0.42}})` : `rgba(201,42,42,${{0.12 + a*0.42}})`;
  return `<span class="heat ${{cls(v)}}" style="background:${{color}}">${{fmtPct(v)}}</span>`;
}};

const state = {{ universe:"15m_shortable_only", hold:"7d", stop:"stop_10", be:"be_after_20", selectedCluster:null, search:"" }};

function uniq(arr) {{ return [...new Set(arr.filter(Boolean))]; }}
function current() {{ return DATA.datasets[state.universe]; }}

function initControls() {{
  const uni = document.getElementById("universe");
  uni.value = state.universe;
  uni.onchange = () => {{ state.universe = uni.value; state.selectedCluster = null; fillOptionControls(); render(); }};
  document.getElementById("search").oninput = e => {{ state.search = e.target.value.trim().toLowerCase(); render(); }};
  document.getElementById("reset").onclick = () => {{
    state.universe = "15m_shortable_only"; state.hold = "7d"; state.stop = "stop_10"; state.be = "be_after_20"; state.selectedCluster = null; state.search = "";
    document.getElementById("universe").value = state.universe;
    document.getElementById("search").value = "";
    fillOptionControls(); render();
  }};
  fillOptionControls();
  const tabs = [
    ["1d / stop10 / BE20","1d","stop_10","be_after_20"],
    ["7d / stop10 / BE20","7d","stop_10","be_after_20"],
    ["14d / stop10 / BE20","14d","stop_10","be_after_20"],
    ["30d / stop10 / BE20","30d","stop_10","be_after_20"],
    ["7d / stop10 / no BE","7d","stop_10","no_be"],
    ["30d / stop10 / no BE","30d","stop_10","no_be"],
  ];
  const holder = document.getElementById("quickTabs");
  holder.innerHTML = tabs.map((t,i)=>`<button data-i="${{i}}">${{t[0]}}</button>`).join("");
  holder.querySelectorAll("button").forEach(btn => btn.onclick = () => {{
    const t = tabs[Number(btn.dataset.i)];
    state.hold=t[1]; state.stop=t[2]; state.be=t[3];
    fillOptionControls(); render();
  }});
}}

function fillOptionControls() {{
  const s = current().summary;
  const holds = DATA.holdOrder.filter(h => s.some(r => r.hold_window === h));
  const stops = uniq(s.map(r => r.stop_model)).sort((a,b)=>a.localeCompare(b));
  const bes = uniq(s.map(r => r.be_model)).sort((a,b)=>a.localeCompare(b));
  fillSelect("hold", holds, state.hold);
  fillSelect("stop", stops, state.stop);
  fillSelect("be", bes, state.be);
}}

function fillSelect(id, values, selected) {{
  const el = document.getElementById(id);
  if (!values.includes(selected)) selected = values[0];
  state[id] = selected;
  el.innerHTML = values.map(v=>`<option value="${{v}}">${{v}}</option>`).join("");
  el.value = selected;
  el.onchange = () => {{ state[id] = el.value; render(); }};
}}

function selectedSummary() {{
  return current().summary.find(r => r.hold_window===state.hold && r.stop_model===state.stop && r.be_model===state.be);
}}

function filteredClusters() {{
  const q = state.search;
  return current().cluster.filter(r => r.hold_window===state.hold && r.stop_model===state.stop && r.be_model===state.be)
    .filter(r => !q || String(r.cluster_date_utc).toLowerCase().includes(q) || String(r.tokens).toLowerCase().includes(q))
    .sort((a,b)=>String(a.cluster_date_utc).localeCompare(String(b.cluster_date_utc)));
}}

function renderKpis() {{
  const s = selectedSummary() || {{}};
  const cards = [
    ["Universe", state.universe],
    ["Variant", `${{state.hold}} / ${{state.stop}} / ${{state.be}}`],
    ["Token trades", s.token_trades ?? "—"],
    ["Clusters", s.clusters ?? "—"],
    ["Total PnL", fmtUsd(s.total_pnl_usdt)],
    ["ROI on margin", fmtPct(s.roi_on_margin)],
    ["Token win rate", fmtPct(s.token_win_rate)],
    ["Cluster win rate", fmtPct(s.cluster_win_rate)],
    ["Stop rate", fmtPct(s.stopped_out_rate)],
    ["BE exit rate", fmtPct(s.breakeven_exit_rate)],
    ["Median MFE", fmtPct(s.median_mfe)],
    ["Median MAE", fmtPct(s.median_mae)],
  ];
  document.getElementById("kpis").innerHTML = cards.map(([l,v])=>`<div class="card"><div class="label">${{l}}</div><div class="value">${{v}}</div></div>`).join("");
}}

function renderClusterTable() {{
  const rows = filteredClusters();
  if (!state.selectedCluster && rows.length) state.selectedCluster = rows[0].cluster_id;
  let html = `<thead><tr>
    <th>Date</th><th class="num">N</th><th class="num">PnL</th><th class="num">ROI</th>
    <th class="num">Win</th><th class="num">Stop</th><th class="num">BE</th><th>Tokens</th>
  </tr></thead><tbody>`;
  html += rows.map(r => `<tr data-cluster="${{r.cluster_id}}" class="${{r.cluster_id===state.selectedCluster?'selected':''}}">
    <td>${{r.cluster_date_utc}}</td>
    <td class="num">${{r.tokens_count}}</td>
    <td class="num ${{cls(r.total_pnl_usdt)}}">${{fmtUsd(r.total_pnl_usdt)}}</td>
    <td class="num">${{heat(r.roi_on_margin)}}</td>
    <td class="num">${{r.winning_tokens}}/${{r.tokens_count}}</td>
    <td class="num">${{r.stopped_tokens}}</td>
    <td class="num">${{r.breakeven_tokens}}</td>
    <td><div class="tokens" title="${{r.tokens || ''}}">${{r.tokens || ''}}</div></td>
  </tr>`).join("");
  html += "</tbody>";
  const table = document.getElementById("clusterTable");
  table.innerHTML = html;
  table.querySelectorAll("tbody tr").forEach(tr => tr.onclick = () => {{ state.selectedCluster = tr.dataset.cluster; render(); }});
}}

function renderTokenTable() {{
  const rows = current().token.filter(r => r.cluster_id===state.selectedCluster && r.hold_window===state.hold && r.stop_model===state.stop && r.be_model===state.be)
    .sort((a,b)=>Number(b.pnl_usdt||-1e9)-Number(a.pnl_usdt||-1e9));
  const title = document.getElementById("detailTitle");
  title.textContent = `Токены кластера ${{state.selectedCluster || ""}}`;
  let html = `<thead><tr>
    <th>Token</th><th>Status</th><th>Exit</th><th class="num">PnL</th><th class="num">ROI</th>
    <th class="num">MFE</th><th class="num">MAE</th><th>Flags</th>
  </tr></thead><tbody>`;
  html += rows.map(r => `<tr>
    <td><b>${{r.token_symbol}}</b></td>
    <td>${{r.shortability_status || ""}}</td>
    <td>${{r.exit_reason || r.path_issue || ""}}</td>
    <td class="num ${{cls(r.pnl_usdt)}}">${{fmtUsd(r.pnl_usdt)}}</td>
    <td class="num ${{cls(r.roi_on_margin)}}">${{fmtPct(r.roi_on_margin)}}</td>
    <td class="num">${{fmtPct(r.max_favorable_excursion)}}</td>
    <td class="num">${{fmtPct(r.max_adverse_excursion)}}</td>
    <td>${{r.stop_loss_triggered==='yes'?'<span class="pill">stop</span>':''}}${{r.breakeven_triggered==='yes'?'<span class="pill">BE</span>':''}}${{r.missing_path_flag==='yes'?'<span class="pill">missing</span>':''}}</td>
  </tr>`).join("");
  html += rows.length ? "</tbody>" : `<tbody><tr><td colspan="8" class="muted">Нет строк для выбранного фильтра.</td></tr></tbody>`;
  document.getElementById("tokenTable").innerHTML = html;
}}

function renderSummaryTable() {{
  const rows = [...current().summary].sort((a,b)=>Number(b.roi_on_margin||0)-Number(a.roi_on_margin||0));
  let html = `<thead><tr>
    <th>Hold</th><th>Stop</th><th>BE</th><th class="num">Trades</th><th class="num">Clusters</th>
    <th class="num">PnL</th><th class="num">ROI</th><th class="num">Token win</th><th class="num">Cluster win</th>
    <th class="num">Stop</th><th class="num">BE</th><th class="num">Med MFE</th><th class="num">Med MAE</th>
  </tr></thead><tbody>`;
  html += rows.map(r => `<tr>
    <td>${{r.hold_window}}</td><td>${{r.stop_model}}</td><td>${{r.be_model}}</td>
    <td class="num">${{r.token_trades}}</td><td class="num">${{r.clusters}}</td>
    <td class="num ${{cls(r.total_pnl_usdt)}}">${{fmtUsd(r.total_pnl_usdt)}}</td>
    <td class="num">${{heat(r.roi_on_margin)}}</td>
    <td class="num">${{fmtPct(r.token_win_rate)}}</td><td class="num">${{fmtPct(r.cluster_win_rate)}}</td>
    <td class="num">${{fmtPct(r.stopped_out_rate)}}</td><td class="num">${{fmtPct(r.breakeven_exit_rate)}}</td>
    <td class="num">${{fmtPct(r.median_mfe)}}</td><td class="num">${{fmtPct(r.median_mae)}}</td>
  </tr>`).join("");
  document.getElementById("summaryTable").innerHTML = html + "</tbody>";
}}

function renderTabs() {{
  document.querySelectorAll("#quickTabs button").forEach(btn => {{
    btn.classList.toggle("active", btn.textContent.includes(state.hold) && btn.textContent.includes(state.stop.replace("_","")) === false);
  }});
}}

function render() {{
  renderKpis();
  renderClusterTable();
  renderTokenTable();
  renderSummaryTable();
}}

initControls();
render();
</script>
</body>
</html>
"""


def main() -> None:
    OUT.write_text(build_html(build_payload()), encoding="utf-8")
    print({"output": str(OUT), "size_mb": round(OUT.stat().st_size / 1024 / 1024, 2)})


if __name__ == "__main__":
    main()
