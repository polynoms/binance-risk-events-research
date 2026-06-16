#!/usr/bin/env python3
"""Build partial take-profit basket dashboard for Monitoring Tag short clusters."""

from __future__ import annotations

import json
import math
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed"
RAW_KLINES = ROOT / "data/raw/klines/spot"
DOCS = ROOT / "docs"
PACKAGE_DIR = ROOT / "dashboard_package" / "monitoring_ladder_dashboard"
ZIP_PATH = ROOT / "monitoring_ladder_dashboard_package.zip"

MARGIN_USDT = 100.0
LEVERAGE = 10.0
NOTIONAL_USDT = MARGIN_USDT * LEVERAGE
INTERVAL = "15m"
HOLD_WINDOWS = {
    "1d": pd.Timedelta(days=1),
    "3d": pd.Timedelta(days=3),
    "7d": pd.Timedelta(days=7),
    "14d": pd.Timedelta(days=14),
    "30d": pd.Timedelta(days=30),
    "60d": pd.Timedelta(days=60),
    "90d": pd.Timedelta(days=90),
}


@dataclass(frozen=True)
class LadderStrategy:
    strategy_id: str
    name: str
    stop_pct: float
    be_trigger_pct: float | None
    tp1_pct: float | None
    tp1_weight: float
    tp2_pct: float | None
    tp2_weight: float
    runner_weight: float
    notes: str


STRATEGIES = [
    LadderStrategy(
        "defensive_7p5_be10_tp10_20",
        "Defensive: stop 7.5%, BE +10%, TP +10/+20",
        0.075,
        0.10,
        0.10,
        0.40,
        0.20,
        0.30,
        0.30,
        "Быстро снижает риск, но часто рано выходит в BE.",
    ),
    LadderStrategy(
        "base_10_be20_tp15_30",
        "Base: stop 10%, BE +20%, TP +15/+30",
        0.10,
        0.20,
        0.15,
        0.33,
        0.30,
        0.33,
        0.34,
        "Базовая схема из обсуждения: часть фиксируется, остаток держится как runner.",
    ),
    LadderStrategy(
        "balanced_10_be15_tp10_30",
        "Balanced: stop 10%, BE +15%, TP +10/+30",
        0.10,
        0.15,
        0.10,
        0.30,
        0.30,
        0.40,
        0.30,
        "Компромисс между быстрым risk-off и сохранением runner.",
    ),
    LadderStrategy(
        "aggressive_10_be20_tp20_50",
        "Aggressive: stop 10%, BE +20%, TP +20/+50",
        0.10,
        0.20,
        0.20,
        0.30,
        0.50,
        0.40,
        0.30,
        "Дольше ждет сильное падение, чаще не успевает снизить риск.",
    ),
    LadderStrategy(
        "runner_only_10_no_be",
        "Runner only: stop 10%, no BE, no partial TP",
        0.10,
        None,
        None,
        0.0,
        None,
        0.0,
        1.0,
        "Контрольная схема: один runner до горизонта или stop.",
    ),
]


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[str, pd.DataFrame] = {}

    def load(self, pair: str) -> pd.DataFrame:
        if pair in self.cache:
            return self.cache[pair]
        folder = RAW_KLINES / pair
        frames = []
        for path in sorted(folder.glob(f"{INTERVAL}_*_paged.json")):
            try:
                data = json.loads(path.read_text())
            except Exception:
                continue
            rows = []
            for item in data or []:
                if len(item) < 7:
                    continue
                rows.append(
                    {
                        "open_time": pd.to_datetime(int(item[0]), unit="ms", utc=True),
                        "open": float(item[1]),
                        "high": float(item[2]),
                        "low": float(item[3]),
                        "close": float(item[4]),
                        "volume": float(item[5]),
                        "close_time": pd.to_datetime(int(item[6]), unit="ms", utc=True),
                        "quote_volume": float(item[7]) if len(item) > 7 else np.nan,
                    }
                )
            if rows:
                frames.append(pd.DataFrame(rows))
        if frames:
            df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        else:
            df = pd.DataFrame()
        self.cache[pair] = df
        return df


def short_return(entry: float, exit_price: float) -> float:
    if entry <= 0 or exit_price <= 0:
        return np.nan
    return entry / exit_price - 1


def shortable_monitoring_events() -> pd.DataFrame:
    token = pd.read_csv(PROCESSED / "monitoring_cluster_stop_token_shortable_only_15m.csv", low_memory=False)
    cols = ["cluster_id", "cluster_date_utc", "event_id", "token_symbol", "symbol_pair", "publication_datetime_utc", "shortability_status"]
    events = token[cols].drop_duplicates().copy()
    events["event_dt"] = pd.to_datetime(events["publication_datetime_utc"], utc=True, errors="coerce")
    return events.sort_values(["event_dt", "token_symbol"]).reset_index(drop=True)


def entry_path(store: KlineStore, pair: str, event_time: pd.Timestamp, horizon: pd.Timedelta) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = store.load(pair)
    if df.empty:
        return pd.DataFrame(), {"path_issue": "missing_15m_path"}
    entries = df[df["open_time"] >= event_time]
    if entries.empty:
        return pd.DataFrame(), {"path_issue": "missing_entry_after_event"}
    entry = entries.iloc[0]
    end = entry["open_time"] + horizon
    path = df[(df["open_time"] >= entry["open_time"]) & (df["open_time"] <= end)].copy()
    if path.empty:
        return pd.DataFrame(), {"path_issue": "missing_horizon_path"}
    return path, {
        "path_issue": "",
        "entry_time": entry["open_time"],
        "entry_price": float(entry["open"]),
        "entry_quote_volume": float(entry.get("quote_volume", np.nan)),
    }


def leg_pnl(entry_price: float, exit_price: float, weight: float) -> float:
    return NOTIONAL_USDT * weight * short_return(entry_price, exit_price)


def simulate_ladder(path: pd.DataFrame, entry_time: pd.Timestamp, entry_price: float, strategy: LadderStrategy) -> dict[str, Any]:
    stop_price_initial = entry_price * (1 + strategy.stop_pct)
    be_active = False
    be_time = ""
    current_stop = stop_price_initial
    open_weight = 1.0
    realized_pnl = 0.0
    tp1_hit = "no"
    tp2_hit = "no"
    stop_triggered = "no"
    stop_time = ""
    tp1_time = ""
    tp2_time = ""
    max_adv = 0.0
    max_fav = 0.0
    mfe_time = pd.NaT
    mae_time = pd.NaT
    exit_time = pd.Timestamp(path.iloc[-1]["close_time"])
    final_exit_reason = "time_exit"

    for _, candle in path.iterrows():
        high = float(candle["high"])
        low = float(candle["low"])
        close_time = pd.Timestamp(candle["close_time"])
        adv = high / entry_price - 1
        fav = entry_price / low - 1 if low > 0 else np.nan
        if pd.notna(adv) and adv > max_adv:
            max_adv = adv
            mae_time = close_time
        if pd.notna(fav) and fav > max_fav:
            max_fav = fav
            mfe_time = close_time

        # Conservative ambiguity rule: if adverse stop and favorable target happen in same 15m candle, stop wins.
        if open_weight > 0 and high >= current_stop:
            realized_pnl += leg_pnl(entry_price, current_stop, open_weight)
            stop_triggered = "yes"
            stop_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            exit_time = close_time
            final_exit_reason = "breakeven_stop" if be_active and math.isclose(current_stop, entry_price) else "fixed_stop"
            open_weight = 0.0
            break

        if strategy.tp1_pct is not None and tp1_hit == "no" and open_weight > 0:
            target = entry_price * (1 - strategy.tp1_pct)
            if low <= target:
                weight = min(strategy.tp1_weight, open_weight)
                realized_pnl += leg_pnl(entry_price, target, weight)
                open_weight -= weight
                tp1_hit = "yes"
                tp1_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if strategy.tp2_pct is not None and tp2_hit == "no" and open_weight > 0:
            target = entry_price * (1 - strategy.tp2_pct)
            if low <= target:
                weight = min(strategy.tp2_weight, open_weight)
                realized_pnl += leg_pnl(entry_price, target, weight)
                open_weight -= weight
                tp2_hit = "yes"
                tp2_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if strategy.be_trigger_pct is not None and not be_active and low <= entry_price * (1 - strategy.be_trigger_pct):
            be_active = True
            be_time = close_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            current_stop = entry_price

    if open_weight > 0:
        final_price = float(path.iloc[-1]["close"])
        realized_pnl += leg_pnl(entry_price, final_price, open_weight)
        exit_time = pd.Timestamp(path.iloc[-1]["close_time"])
        final_exit_reason = "time_exit_partial" if (tp1_hit == "yes" or tp2_hit == "yes") else "time_exit"

    return {
        "exit_timestamp_utc": exit_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "exit_reason": final_exit_reason,
        "pnl_usdt": realized_pnl,
        "roi_on_margin": realized_pnl / MARGIN_USDT,
        "open_weight_at_time_exit": open_weight,
        "tp1_hit": tp1_hit,
        "tp1_time_utc": tp1_time,
        "tp2_hit": tp2_hit,
        "tp2_time_utc": tp2_time,
        "be_active": "yes" if be_active else "no",
        "be_time_utc": be_time,
        "stop_triggered": stop_triggered,
        "stop_time_utc": stop_time,
        "max_favorable_excursion": max_fav,
        "max_adverse_excursion": max_adv,
        "time_to_mfe_hours": (mfe_time - entry_time).total_seconds() / 3600 if pd.notna(mfe_time) else np.nan,
        "time_to_mae_hours": (mae_time - entry_time).total_seconds() / 3600 if pd.notna(mae_time) else np.nan,
    }


def profit_factor(values: pd.Series) -> float:
    gains = values[values > 0].sum()
    losses = -values[values < 0].sum()
    if losses == 0:
        return np.inf if gains > 0 else np.nan
    return gains / losses


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    events = shortable_monitoring_events()
    store = KlineStore()
    rows = []
    for _, event in events.iterrows():
        event_time = pd.Timestamp(event["event_dt"])
        for hold, horizon in HOLD_WINDOWS.items():
            path, meta = entry_path(store, str(event["symbol_pair"]), event_time, horizon)
            for strategy in STRATEGIES:
                base = {
                    "cluster_id": event["cluster_id"],
                    "cluster_date_utc": event["cluster_date_utc"],
                    "event_id": event["event_id"],
                    "token_symbol": event["token_symbol"],
                    "symbol_pair": event["symbol_pair"],
                    "shortability_status": event["shortability_status"],
                    "publication_datetime_utc": event["publication_datetime_utc"],
                    "hold_window": hold,
                    "strategy_id": strategy.strategy_id,
                    "strategy_name": strategy.name,
                    "stop_pct": strategy.stop_pct,
                    "be_trigger_pct": strategy.be_trigger_pct,
                    "tp1_pct": strategy.tp1_pct,
                    "tp1_weight": strategy.tp1_weight,
                    "tp2_pct": strategy.tp2_pct,
                    "tp2_weight": strategy.tp2_weight,
                    "runner_weight": strategy.runner_weight,
                    "price_interval": INTERVAL,
                }
                if path.empty:
                    rows.append(
                        {
                            **base,
                            "entry_timestamp_utc": "",
                            "entry_price": np.nan,
                            "entry_quote_volume": np.nan,
                            "exit_timestamp_utc": "",
                            "exit_reason": "missing_path",
                            "pnl_usdt": np.nan,
                            "roi_on_margin": np.nan,
                            "missing_path_flag": "yes",
                            "path_issue": meta["path_issue"],
                            "manual_review_required": "yes",
                        }
                    )
                    continue
                entry_time = pd.Timestamp(meta["entry_time"])
                result = simulate_ladder(path, entry_time, float(meta["entry_price"]), strategy)
                rows.append(
                    {
                        **base,
                        "entry_timestamp_utc": entry_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "entry_price": float(meta["entry_price"]),
                        "entry_quote_volume": meta["entry_quote_volume"],
                        "missing_path_flag": "no",
                        "path_issue": "",
                        "manual_review_required": "no",
                        **result,
                    }
                )

    token = pd.DataFrame(rows)
    valid = token[token["missing_path_flag"].eq("no") & token["pnl_usdt"].notna()].copy()
    cluster_rows = []
    for keys, grp in valid.groupby(["cluster_id", "cluster_date_utc", "hold_window", "strategy_id"], dropna=False):
        cluster_id, date, hold, strategy_id = keys
        pnl = pd.to_numeric(grp["pnl_usdt"], errors="coerce")
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_date_utc": date,
                "hold_window": hold,
                "strategy_id": strategy_id,
                "tokens_count": int(grp["token_symbol"].nunique()),
                "total_margin_usdt": float(len(grp) * MARGIN_USDT),
                "total_notional_usdt": float(len(grp) * NOTIONAL_USDT),
                "total_pnl_usdt": float(pnl.sum()),
                "roi_on_margin": float(pnl.sum() / (len(grp) * MARGIN_USDT)),
                "winning_tokens": int((pnl > 0).sum()),
                "losing_tokens": int((pnl < 0).sum()),
                "tp1_tokens": int(grp["tp1_hit"].eq("yes").sum()),
                "tp2_tokens": int(grp["tp2_hit"].eq("yes").sum()),
                "be_tokens": int(grp["be_active"].eq("yes").sum()),
                "stopped_tokens": int(grp["stop_triggered"].eq("yes").sum()),
                "median_token_pnl": float(pnl.median()),
                "worst_token_pnl": float(pnl.min()),
                "best_token_pnl": float(pnl.max()),
                "tokens": ",".join(sorted(grp["token_symbol"].astype(str).unique())),
            }
        )
    cluster = pd.DataFrame(cluster_rows)
    summary_rows = []
    for keys, grp in valid.groupby(["hold_window", "strategy_id"], dropna=False):
        hold, strategy_id = keys
        pnl = pd.to_numeric(grp["pnl_usdt"], errors="coerce")
        cl = cluster[(cluster["hold_window"].eq(hold)) & (cluster["strategy_id"].eq(strategy_id))]
        summary_rows.append(
            {
                "hold_window": hold,
                "strategy_id": strategy_id,
                "token_trades": int(len(grp)),
                "clusters": int(grp["cluster_id"].nunique()),
                "total_margin_usdt": float(len(grp) * MARGIN_USDT),
                "total_pnl_usdt": float(pnl.sum()),
                "roi_on_margin": float(pnl.sum() / (len(grp) * MARGIN_USDT)),
                "token_win_rate": float((pnl > 0).mean()),
                "cluster_win_rate": float((cl["total_pnl_usdt"] > 0).mean()),
                "median_token_pnl": float(pnl.median()),
                "median_cluster_roi": float(cl["roi_on_margin"].median()),
                "p25_token_pnl": float(pnl.quantile(0.25)),
                "p75_token_pnl": float(pnl.quantile(0.75)),
                "best_token_pnl": float(pnl.max()),
                "worst_token_pnl": float(pnl.min()),
                "profit_factor": float(profit_factor(pnl)),
                "tp1_rate": float(grp["tp1_hit"].eq("yes").mean()),
                "tp2_rate": float(grp["tp2_hit"].eq("yes").mean()),
                "be_active_rate": float(grp["be_active"].eq("yes").mean()),
                "stopped_out_rate": float(grp["stop_triggered"].eq("yes").mean()),
                "median_mfe": float(pd.to_numeric(grp["max_favorable_excursion"], errors="coerce").median()),
                "median_mae": float(pd.to_numeric(grp["max_adverse_excursion"], errors="coerce").median()),
                "max_mae": float(pd.to_numeric(grp["max_adverse_excursion"], errors="coerce").max()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    equity_rows = []
    for keys, grp in cluster.groupby(["hold_window", "strategy_id"], dropna=False):
        hold, strategy_id = keys
        grp = grp.sort_values("cluster_date_utc").copy()
        cumulative_pnl = 0.0
        peak = 0.0
        for _, row in grp.iterrows():
            cumulative_pnl += float(row["total_pnl_usdt"])
            peak = max(peak, cumulative_pnl)
            equity_rows.append(
                {
                    "hold_window": hold,
                    "strategy_id": strategy_id,
                    "cluster_date_utc": row["cluster_date_utc"],
                    "cluster_pnl_usdt": row["total_pnl_usdt"],
                    "cluster_roi_on_margin": row["roi_on_margin"],
                    "cumulative_pnl_usdt": cumulative_pnl,
                    "drawdown_from_peak_usdt": cumulative_pnl - peak,
                    "tokens_count": row["tokens_count"],
                }
            )
    equity = pd.DataFrame(equity_rows)
    return token, cluster, summary, equity


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, float):
        if math.isinf(value):
            return None
        return round(value, 10)
    return value


def records(df: pd.DataFrame) -> list[dict]:
    return [{k: clean_value(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def write_dashboard(token: pd.DataFrame, cluster: pd.DataFrame, summary: pd.DataFrame, equity: pd.DataFrame) -> Path:
    payload = {
        "strategies": [s.__dict__ for s in STRATEGIES],
        "holdOrder": list(HOLD_WINDOWS.keys()),
        "summary": records(summary),
        "cluster": records(cluster),
        "token": records(token),
        "equity": records(equity),
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Monitoring Tag ladder dashboard</title>
  <style>
    :root{{--bg:#f5f6f8;--panel:#fff;--ink:#171923;--muted:#667085;--line:#d8dde6;--good:#087f5b;--bad:#c92a2a;--accent:#1d4ed8;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    header{{position:sticky;top:0;z-index:10;background:var(--panel);border-bottom:1px solid var(--line);padding:14px 18px 10px}}
    h1{{margin:0 0 4px;font-size:22px}} h2{{margin:0 0 10px;font-size:17px}} p{{margin:0;color:var(--muted);line-height:1.4}}
    main{{padding:14px 18px 28px}} .toolbar{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:10px}}
    label{{font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:3px}} select,input,button{{border:1px solid var(--line);border-radius:7px;background:#fff;color:var(--ink);padding:7px 9px;font-size:13px;min-height:34px}}
    .grid{{display:grid;grid-template-columns:repeat(6,minmax(130px,1fr));gap:9px;margin:12px 0}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px}}
    .label{{color:var(--muted);font-size:12px}} .value{{font-size:20px;font-weight:760;margin-top:3px;font-variant-numeric:tabular-nums}}
    .layout{{display:grid;grid-template-columns:minmax(640px,1.2fr) minmax(520px,1fr);gap:12px;align-items:start}} .panel{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:11px;overflow:hidden}}
    .scroll{{max-height:62vh;overflow:auto}} table{{width:100%;border-collapse:collapse}} th,td{{border-bottom:1px solid var(--line);padding:7px 8px;font-size:12.5px;text-align:left;vertical-align:middle}}
    th{{background:#f0f2f5;color:var(--muted);position:sticky;top:0;z-index:2}} tr.selected td{{background:#f7fbff;outline:1px solid rgba(29,78,216,.18)}}
    .num{{text-align:right;font-variant-numeric:tabular-nums}} .good{{color:var(--good);font-weight:700}} .bad{{color:var(--bad);font-weight:700}} .muted{{color:var(--muted)}}
    .tokens{{max-width:360px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--muted)}} .pill{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 7px;background:#fafbfc;color:var(--muted);font-size:12px;margin:1px}}
    .mini{{font-size:12px;color:var(--muted);margin-top:6px}} .heat{{border-radius:6px;padding:5px 7px;display:inline-block;min-width:72px;text-align:right;font-weight:750}}
    .chart{{height:220px;width:100%;border:1px solid var(--line);border-radius:8px;background:#fbfcfe}}
    @media(max-width:1100px){{.grid{{grid-template-columns:repeat(2,minmax(130px,1fr))}}.layout{{grid-template-columns:1fr}}header{{position:static}}}}
  </style>
</head>
<body>
<header>
  <h1>Monitoring Tag: partial TP / BE basket dashboard</h1>
  <p>15m strict / shortable-only proxy. 100 USDT margin на токен, 10x notional. Entry: первая 15m свеча после Monitoring Tag announcement. Это исследовательская симуляция, не live-рекомендация.</p>
  <div class="toolbar">
    <label>Strategy<select id="strategy"></select></label>
    <label>Hold<select id="hold"></select></label>
    <label>Поиск токена/даты<input id="search" placeholder="EPIC или 2026-05-22"></label>
  </div>
</header>
<main>
  <div class="grid" id="kpis"></div>
  <section class="panel" style="margin-bottom:12px;">
    <h2>Cumulative cluster PnL</h2>
    <canvas id="equityChart" class="chart" width="1200" height="220"></canvas>
    <div class="mini">Линия показывает накопленный PnL, если проходить исторические кластеры последовательно выбранной схемой.</div>
  </section>
  <div class="layout">
    <section class="panel">
      <h2>Кластеры</h2>
      <div class="scroll"><table id="clusterTable"></table></div>
    </section>
    <section class="panel">
      <h2 id="detailTitle">Токены кластера</h2>
      <div class="scroll"><table id="tokenTable"></table></div>
    </section>
  </div>
  <section class="panel" style="margin-top:12px;">
    <h2>Сводка схем</h2>
    <div class="scroll" style="max-height:46vh;"><table id="summaryTable"></table></div>
  </section>
</main>
<script>
const DATA={data};
const state={{strategy:"base_10_be20_tp15_30",hold:"14d",selectedCluster:null,search:""}};
const fmtPct=x=>x==null||Number.isNaN(Number(x))?"—":(Number(x)*100).toFixed(1)+"%";
const fmtUsd=x=>x==null||Number.isNaN(Number(x))?"—":Number(x).toLocaleString("en-US",{{maximumFractionDigits:0}})+" $";
const cls=x=>Number(x)>=0?"good":"bad";
const heat=x=>{{if(x==null||Number.isNaN(Number(x)))return'<span class="heat">—</span>';const v=Number(x),a=Math.min(Math.abs(v),3)/3,c=v>=0?`rgba(8,127,91,${{.12+a*.42}})`:`rgba(201,42,42,${{.12+a*.42}})`;return`<span class="heat ${{cls(v)}}" style="background:${{c}}">${{fmtPct(v)}}</span>`;}};
function init(){{fill("strategy",DATA.strategies.map(s=>[s.strategy_id,s.name]),state.strategy);fill("hold",DATA.holdOrder.map(h=>[h,h]),state.hold);document.getElementById("search").oninput=e=>{{state.search=e.target.value.trim().toLowerCase();render();}};render();}}
function fill(id,items,val){{const el=document.getElementById(id);el.innerHTML=items.map(([v,t])=>`<option value="${{v}}">${{t}}</option>`).join("");el.value=val;el.onchange=()=>{{state[id]=el.value;state.selectedCluster=null;render();}};}}
function summary(){{return DATA.summary.find(r=>r.strategy_id===state.strategy&&r.hold_window===state.hold)||{{}};}}
function clusters(){{const q=state.search;return DATA.cluster.filter(r=>r.strategy_id===state.strategy&&r.hold_window===state.hold).filter(r=>!q||String(r.cluster_date_utc).toLowerCase().includes(q)||String(r.tokens).toLowerCase().includes(q)).sort((a,b)=>String(a.cluster_date_utc).localeCompare(String(b.cluster_date_utc)));}}
function renderKpis(){{const s=summary();const strat=DATA.strategies.find(x=>x.strategy_id===state.strategy)||{{}};const cards=[["Strategy",strat.strategy_id||state.strategy],["Hold",state.hold],["Token trades",s.token_trades??"—"],["Clusters",s.clusters??"—"],["Total PnL",fmtUsd(s.total_pnl_usdt)],["ROI",fmtPct(s.roi_on_margin)],["Cluster win",fmtPct(s.cluster_win_rate)],["Token win",fmtPct(s.token_win_rate)],["TP1 rate",fmtPct(s.tp1_rate)],["TP2 rate",fmtPct(s.tp2_rate)],["BE active",fmtPct(s.be_active_rate)],["Stopped",fmtPct(s.stopped_out_rate)]];document.getElementById("kpis").innerHTML=cards.map(([l,v])=>`<div class="card"><div class="label">${{l}}</div><div class="value">${{v}}</div></div>`).join("");}}
function renderClusters(){{const rows=clusters();if(!state.selectedCluster&&rows.length)state.selectedCluster=rows[0].cluster_id;let html='<thead><tr><th>Date</th><th class="num">N</th><th class="num">PnL</th><th class="num">ROI</th><th class="num">Win</th><th class="num">TP1</th><th class="num">TP2</th><th class="num">BE</th><th class="num">Stop</th><th>Tokens</th></tr></thead><tbody>';html+=rows.map(r=>`<tr data-cluster="${{r.cluster_id}}" class="${{r.cluster_id===state.selectedCluster?'selected':''}}"><td>${{r.cluster_date_utc}}</td><td class="num">${{r.tokens_count}}</td><td class="num ${{cls(r.total_pnl_usdt)}}">${{fmtUsd(r.total_pnl_usdt)}}</td><td class="num">${{heat(r.roi_on_margin)}}</td><td class="num">${{r.winning_tokens}}/${{r.tokens_count}}</td><td class="num">${{r.tp1_tokens}}</td><td class="num">${{r.tp2_tokens}}</td><td class="num">${{r.be_tokens}}</td><td class="num">${{r.stopped_tokens}}</td><td><div class="tokens" title="${{r.tokens||''}}">${{r.tokens||''}}</div></td></tr>`).join("");const table=document.getElementById("clusterTable");table.innerHTML=html+"</tbody>";table.querySelectorAll("tbody tr").forEach(tr=>tr.onclick=()=>{{state.selectedCluster=tr.dataset.cluster;render();}});}}
function renderTokens(){{const rows=DATA.token.filter(r=>r.cluster_id===state.selectedCluster&&r.strategy_id===state.strategy&&r.hold_window===state.hold).sort((a,b)=>Number(b.pnl_usdt||-1e9)-Number(a.pnl_usdt||-1e9));document.getElementById("detailTitle").textContent=`Токены кластера ${{state.selectedCluster||""}}`;let html='<thead><tr><th>Token</th><th>Exit</th><th class="num">PnL</th><th class="num">ROI</th><th class="num">MFE</th><th class="num">MAE</th><th>Flags</th></tr></thead><tbody>';html+=rows.map(r=>`<tr><td><b>${{r.token_symbol}}</b></td><td>${{r.exit_reason}}</td><td class="num ${{cls(r.pnl_usdt)}}">${{fmtUsd(r.pnl_usdt)}}</td><td class="num ${{cls(r.roi_on_margin)}}">${{fmtPct(r.roi_on_margin)}}</td><td class="num">${{fmtPct(r.max_favorable_excursion)}}</td><td class="num">${{fmtPct(r.max_adverse_excursion)}}</td><td>${{r.tp1_hit==='yes'?'<span class="pill">TP1</span>':''}}${{r.tp2_hit==='yes'?'<span class="pill">TP2</span>':''}}${{r.be_active==='yes'?'<span class="pill">BE</span>':''}}${{r.stop_triggered==='yes'?'<span class="pill">stop</span>':''}}</td></tr>`).join("");document.getElementById("tokenTable").innerHTML=html+"</tbody>";}}
function renderSummary(){{const rows=[...DATA.summary].sort((a,b)=>Number(b.roi_on_margin||0)-Number(a.roi_on_margin||0));let html='<thead><tr><th>Hold</th><th>Strategy</th><th class="num">PnL</th><th class="num">ROI</th><th class="num">Cluster win</th><th class="num">TP1</th><th class="num">TP2</th><th class="num">BE</th><th class="num">Stop</th><th class="num">Med MFE</th><th class="num">Med MAE</th></tr></thead><tbody>';html+=rows.map(r=>`<tr><td>${{r.hold_window}}</td><td>${{r.strategy_id}}</td><td class="num ${{cls(r.total_pnl_usdt)}}">${{fmtUsd(r.total_pnl_usdt)}}</td><td class="num">${{heat(r.roi_on_margin)}}</td><td class="num">${{fmtPct(r.cluster_win_rate)}}</td><td class="num">${{fmtPct(r.tp1_rate)}}</td><td class="num">${{fmtPct(r.tp2_rate)}}</td><td class="num">${{fmtPct(r.be_active_rate)}}</td><td class="num">${{fmtPct(r.stopped_out_rate)}}</td><td class="num">${{fmtPct(r.median_mfe)}}</td><td class="num">${{fmtPct(r.median_mae)}}</td></tr>`).join("");document.getElementById("summaryTable").innerHTML=html+"</tbody>";}}
function drawEquity(){{const c=document.getElementById("equityChart"),ctx=c.getContext("2d");ctx.clearRect(0,0,c.width,c.height);const rows=DATA.equity.filter(r=>r.strategy_id===state.strategy&&r.hold_window===state.hold);if(!rows.length)return;const vals=rows.map(r=>Number(r.cumulative_pnl_usdt));const min=Math.min(0,...vals),max=Math.max(0,...vals);const pad=24,w=c.width-pad*2,h=c.height-pad*2;ctx.strokeStyle='#d8dde6';ctx.beginPath();ctx.moveTo(pad,pad+h*(1-(0-min)/(max-min||1)));ctx.lineTo(pad+w,pad+h*(1-(0-min)/(max-min||1)));ctx.stroke();ctx.strokeStyle='#1d4ed8';ctx.lineWidth=2;ctx.beginPath();rows.forEach((r,i)=>{{const x=pad+(i/(Math.max(rows.length-1,1)))*w;const y=pad+h*(1-(Number(r.cumulative_pnl_usdt)-min)/(max-min||1));if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}});ctx.stroke();ctx.fillStyle='#667085';ctx.font='12px system-ui';ctx.fillText(`Final: ${{fmtUsd(vals[vals.length-1])}}`,pad,16);ctx.fillText(rows[0].cluster_date_utc,pad,c.height-6);ctx.fillText(rows[rows.length-1].cluster_date_utc,c.width-100,c.height-6);}}
function render(){{renderKpis();renderClusters();renderTokens();renderSummary();drawEquity();}}
init();
</script>
</body>
</html>
"""
    out = DOCS / "monitoring_ladder_dashboard.html"
    out.write_text(html, encoding="utf-8")
    return out


def write_readme(dashboard_path: Path) -> Path:
    readme = ROOT / "README_monitoring_ladder_dashboard.md"
    readme.write_text(
        f"""# Monitoring Tag Ladder Dashboard

Это автономный пакет для просмотра ретроспективной симуляции short basket после Binance Monitoring Tag announcements.

## Как открыть

Откройте файл:

`monitoring_ladder_dashboard.html`

в Chrome/Safari/Edge двойным кликом. Интернет не нужен: данные встроены в HTML.

## Что внутри

- Universe: `15m strict / shortable-only proxy`.
- Entry: первая 15m свеча после Monitoring Tag announcement.
- Размер: 100 USDT margin на токен, 10x notional.
- Кластер: все shortable Monitoring Tag токены из одного announcement date.
- Симуляция: частичная фиксация прибыли, BE, stop, runner до выбранного горизонта.

## Стратегии

- `defensive_7p5_be10_tp10_20`: stop 7.5%, BE после +10%, TP +10/+20.
- `base_10_be20_tp15_30`: stop 10%, BE после +20%, TP +15/+30.
- `balanced_10_be15_tp10_30`: stop 10%, BE после +15%, TP +10/+30.
- `aggressive_10_be20_tp20_50`: stop 10%, BE после +20%, TP +20/+50.
- `runner_only_10_no_be`: контрольная схема без частичной фиксации.

## Ограничения

- Это ретроспективное исследование, не торговая рекомендация.
- Используется spot OHLCV как price path proxy.
- Фьючерсная доступность является historical proxy, а не live proof.
- Не учтены funding, комиссии, real liquidation engine, spread, slippage и latency.
- Внутри одной 15m свечи используется консервативное правило: adverse stop проверяется раньше favorable TP/BE.

## Файлы

- `monitoring_ladder_dashboard.html` — сам дашборд.
- `monitoring_ladder_token_trades.csv` — token-level результаты.
- `monitoring_ladder_cluster_results.csv` — cluster-level результаты.
- `monitoring_ladder_summary.csv` — сводка по стратегиям и hold windows.
- `monitoring_ladder_equity_curve.csv` — cumulative cluster PnL.
- `README_monitoring_ladder_dashboard.md` — этот файл.

Исходный HTML создан из:

`{dashboard_path.relative_to(ROOT)}`
""",
        encoding="utf-8",
    )
    return readme


def write_outputs_and_package(token: pd.DataFrame, cluster: pd.DataFrame, summary: pd.DataFrame, equity: pd.DataFrame, dashboard_path: Path) -> None:
    token_path = PROCESSED / "monitoring_ladder_token_trades.csv"
    cluster_path = PROCESSED / "monitoring_ladder_cluster_results.csv"
    summary_path = PROCESSED / "monitoring_ladder_summary.csv"
    equity_path = PROCESSED / "monitoring_ladder_equity_curve.csv"
    token.to_csv(token_path, index=False)
    cluster.to_csv(cluster_path, index=False)
    summary.to_csv(summary_path, index=False)
    equity.to_csv(equity_path, index=False)
    readme_path = write_readme(dashboard_path)

    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True)
    package_files = [
        (dashboard_path, "monitoring_ladder_dashboard.html"),
        (token_path, "data/monitoring_ladder_token_trades.csv"),
        (cluster_path, "data/monitoring_ladder_cluster_results.csv"),
        (summary_path, "data/monitoring_ladder_summary.csv"),
        (equity_path, "data/monitoring_ladder_equity_curve.csv"),
        (readme_path, "README_monitoring_ladder_dashboard.md"),
    ]
    for src, rel in package_files:
        dst = PACKAGE_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in PACKAGE_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(PACKAGE_DIR.parent))


def main() -> None:
    token, cluster, summary, equity = build_tables()
    dashboard_path = write_dashboard(token, cluster, summary, equity)
    write_outputs_and_package(token, cluster, summary, equity, dashboard_path)
    print(
        {
            "dashboard": str(dashboard_path),
            "package": str(ZIP_PATH),
            "token_rows": len(token),
            "cluster_rows": len(cluster),
            "summary_rows": len(summary),
            "equity_rows": len(equity),
            "package_size_mb": round(ZIP_PATH.stat().st_size / 1024 / 1024, 2),
        }
    )


if __name__ == "__main__":
    main()

