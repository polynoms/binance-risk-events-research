#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW_KLINES = ROOT / "data" / "raw" / "klines"
DOCS = ROOT / "docs"

STOP_LOSSES = [0.15, 0.20, 0.30, 0.40, 0.50]
TAKE_PROFITS = [0.10, 0.20, 0.30, 0.50]
HOLDING_WINDOWS = [1, 7, 30]
ROUNDTRIP_COST_BPS = 100

TRAILING_VARIANTS = {
    "none": None,
    "breakeven_after_10": {"activation": 0.10, "mode": "breakeven", "trail": 0.0},
    "trail15_after_20": {"activation": 0.20, "mode": "trail", "trail": 0.15},
    "trail20_after_30": {"activation": 0.30, "mode": "trail", "trail": 0.20},
}


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100 * float(value):.1f}%"


def iso(ts: pd.Timestamp | None) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


class KlineStore:
    def __init__(self) -> None:
        self.cache: dict[tuple[str, str], pd.DataFrame] = {}

    def load(self, pair: str, market_type: str = "spot") -> pd.DataFrame:
        if not pair or str(pair) == "nan":
            return pd.DataFrame()
        key = (market_type, str(pair))
        if key in self.cache:
            return self.cache[key]
        folder = RAW_KLINES / market_type / str(pair)
        frames = []
        for path in sorted(folder.glob("1h_*_paged.json")):
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
                    }
                )
            if rows:
                frames.append(pd.DataFrame(rows))
        if frames:
            df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
        else:
            df = pd.DataFrame()
        self.cache[key] = df
        return df


def profit_factor(ret: pd.Series) -> float:
    wins = ret[ret > 0].sum()
    losses = -ret[ret < 0].sum()
    if losses == 0:
        return np.nan
    return float(wins / losses)


def simulate_short_path(
    path: pd.DataFrame,
    entry_time: pd.Timestamp,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    holding_days: int,
    trailing_name: str,
) -> dict[str, Any]:
    end_time = entry_time + pd.Timedelta(days=holding_days)
    sub = path[(path["open_time"] > entry_time) & (path["open_time"] <= end_time)].copy()
    if sub.empty or entry_price <= 0:
        return {"status": "missing_path"}

    fixed_stop_price = entry_price * (1 + stop_loss)
    tp_price = entry_price * (1 - take_profit)
    trail_cfg = TRAILING_VARIANTS[trailing_name]
    trail_active = False
    trail_stop_price = np.nan
    low_watermark = entry_price

    exit_reason = "timeout"
    exit_time = pd.Timestamp(sub.iloc[-1]["close_time"])
    exit_price = float(sub.iloc[-1]["close"])
    time_to_stop = np.nan
    time_to_tp = np.nan
    time_to_trailing = np.nan

    max_high = float(sub["high"].max())
    min_low = float(sub["low"].min())
    mae = max_high / entry_price - 1
    mfe = entry_price / min_low - 1 if min_low > 0 else np.nan

    for _, row in sub.iterrows():
        high = float(row["high"])
        low = float(row["low"])
        close_time = pd.Timestamp(row["close_time"])

        # Conservative same-candle assumption: existing stops are checked before TP.
        if high >= fixed_stop_price:
            exit_reason = "stop_loss"
            exit_time = close_time
            exit_price = fixed_stop_price
            time_to_stop = (exit_time - entry_time).total_seconds() / 3600
            break

        if trail_active and high >= trail_stop_price:
            exit_reason = "trailing_stop"
            exit_time = close_time
            exit_price = trail_stop_price
            time_to_trailing = (exit_time - entry_time).total_seconds() / 3600
            break

        if trail_cfg is not None:
            favorable = entry_price / low - 1 if low > 0 else 0
            if favorable >= trail_cfg["activation"]:
                trail_active = True
                low_watermark = min(low_watermark, low)
                if trail_cfg["mode"] == "breakeven":
                    trail_stop_price = min(entry_price, fixed_stop_price)
                else:
                    trail_stop_price = min(trail_stop_price, low_watermark * (1 + trail_cfg["trail"])) if pd.notna(trail_stop_price) else low_watermark * (1 + trail_cfg["trail"])
            elif trail_active and low < low_watermark:
                low_watermark = low
                if trail_cfg["mode"] == "trail":
                    trail_stop_price = min(trail_stop_price, low_watermark * (1 + trail_cfg["trail"]))

        if low <= tp_price:
            exit_reason = "take_profit"
            exit_time = close_time
            exit_price = tp_price
            time_to_tp = (exit_time - entry_time).total_seconds() / 3600
            break

    gross_return = entry_price / exit_price - 1
    net_return = gross_return - ROUNDTRIP_COST_BPS / 10000
    return {
        "status": "ok",
        "exit_time": iso(exit_time),
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "gross_return": gross_return,
        "net_return": net_return,
        "win": "yes" if net_return > 0 else "no",
        "mae": mae,
        "mfe": mfe,
        "time_to_stop_hours": time_to_stop,
        "time_to_tp_hours": time_to_tp,
        "time_to_trailing_hours": time_to_trailing,
        "holding_time_hours": (exit_time - entry_time).total_seconds() / 3600,
        "stop_hit": "yes" if exit_reason == "stop_loss" else "no",
        "tp_hit": "yes" if exit_reason == "take_profit" else "no",
        "trailing_hit": "yes" if exit_reason == "trailing_stop" else "no",
        "timeout_exit": "yes" if exit_reason == "timeout" else "no",
    }


def build_simulation() -> pd.DataFrame:
    trades = read_csv("monitoring_conservative_strategy_trades.csv")
    store = KlineStore()
    rows = []
    for _, trade in trades.iterrows():
        entry_time = pd.to_datetime(trade["entry_time"], utc=True, errors="coerce")
        entry_price = float(trade["entry_price"])
        pair = str(trade["symbol_pair"])
        path = store.load(pair, "spot")
        for stop_loss in STOP_LOSSES:
            for take_profit in TAKE_PROFITS:
                for holding_days in HOLDING_WINDOWS:
                    for trailing_name in TRAILING_VARIANTS:
                        sim = simulate_short_path(path, entry_time, entry_price, stop_loss, take_profit, holding_days, trailing_name)
                        rows.append(
                            {
                                "event_id": trade["event_id"],
                                "token_symbol": trade["token_symbol"],
                                "symbol_pair": pair,
                                "futures_symbol": trade["futures_symbol"],
                                "event_time": trade["event_time"],
                                "entry_time": trade["entry_time"],
                                "entry_price": entry_price,
                                "primary_scenario": trade["primary_scenario"],
                                "event_half": trade["event_half"],
                                "stop_loss": stop_loss,
                                "take_profit": take_profit,
                                "holding_days": holding_days,
                                "trailing_variant": trailing_name,
                                "roundtrip_cost_bps": ROUNDTRIP_COST_BPS,
                                **sim,
                            }
                        )
    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "monitoring_risk_control_simulation.csv", index=False)
    out.to_parquet(PROCESSED / "monitoring_risk_control_simulation.parquet", index=False)
    return out


def summarize(sim: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ok = sim[sim["status"].eq("ok")].copy()
    keys = ["stop_loss", "take_profit", "holding_days", "trailing_variant"]
    for vals, grp in ok.groupby(keys, dropna=False):
        if not isinstance(vals, tuple):
            vals = (vals,)
        ret = pd.to_numeric(grp["net_return"], errors="coerce").dropna()
        if ret.empty:
            continue
        rows.append(
            {
                **{k: v for k, v in zip(keys, vals)},
                "n_trades": int(len(ret)),
                "valid_path_rate": float(len(ret) / 30),
                "win_rate": float((ret > 0).mean()),
                "median_return": float(ret.median()),
                "average_return": float(ret.mean()),
                "p25_return": float(ret.quantile(0.25)),
                "p75_return": float(ret.quantile(0.75)),
                "worst_trade": float(ret.min()),
                "best_trade": float(ret.max()),
                "profit_factor": profit_factor(ret),
                "expectancy": float(ret.mean()),
                "stop_hit_rate": float(grp["stop_hit"].eq("yes").mean()),
                "tp_hit_rate": float(grp["tp_hit"].eq("yes").mean()),
                "trailing_hit_rate": float(grp["trailing_hit"].eq("yes").mean()),
                "timeout_exit_rate": float(grp["timeout_exit"].eq("yes").mean()),
                "median_holding_time_hours": float(pd.to_numeric(grp["holding_time_hours"], errors="coerce").median()),
                "max_loss_after_stop_simulation": float(ret.min()),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["holding_days", "trailing_variant", "stop_loss", "take_profit"])
    summary.to_csv(PROCESSED / "monitoring_risk_control_summary.csv", index=False)
    return summary


def fmt_table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
    if df.empty:
        return "No rows."
    view = df[cols].head(n).copy()
    for c in view.columns:
        if any(x in c for x in ["rate", "return", "trade", "loss"]):
            if c != "n_trades":
                view[c] = view[c].map(pct)
    return view.to_markdown(index=False)


def write_report(summary: pd.DataFrame, sim: pd.DataFrame) -> None:
    valid_counts = sim.groupby(["stop_loss", "take_profit", "holding_days", "trailing_variant"])["status"].apply(lambda s: s.eq("ok").sum())
    low_valid = int((valid_counts < 20).sum())
    base = summary[summary["trailing_variant"].eq("none")].copy()
    best_practical = base[
        (base["n_trades"] >= 20)
        & (base["average_return"] > 0)
        & (base["median_return"] > 0)
        & (base["stop_hit_rate"] <= 0.50)
    ].sort_values(["holding_days", "profit_factor", "median_return"], ascending=[True, False, False])
    balanced_fixed = base[
        (base["n_trades"] >= 20)
        & (base["holding_days"] == 30)
        & (base["stop_loss"] <= 0.20)
        & (base["take_profit"].isin([0.20, 0.30]))
        & (base["average_return"] > 0)
        & (base["median_return"] > 0)
    ].sort_values(["average_return", "profit_factor"], ascending=False)
    trailing = summary[summary["trailing_variant"].ne("none")].copy()
    trailing_best = trailing[
        (trailing["n_trades"] >= 20)
        & (trailing["average_return"] > 0)
        & (trailing["median_return"] > 0)
    ].sort_values(["profit_factor", "median_return"], ascending=False)

    tight = summary[(summary["stop_loss"].eq(0.15)) & (summary["trailing_variant"].eq("none"))].sort_values(["holding_days", "take_profit"])
    wide = summary[(summary["stop_loss"].eq(0.30)) & (summary["trailing_variant"].eq("none"))].sort_values(["holding_days", "take_profit"])

    if not balanced_fixed.empty:
        r = balanced_fixed.iloc[0]
        rec1 = f"`SL {int(r.stop_loss*100)}% / TP {int(r.take_profit*100)}% / hold {int(r.holding_days)}d / no trailing`"
    elif not best_practical.empty:
        r = best_practical.iloc[0]
        rec1 = f"`SL {int(r.stop_loss*100)}% / TP {int(r.take_profit*100)}% / hold {int(r.holding_days)}d / no trailing`"
    else:
        rec1 = "No fixed SL/TP profile clears the basic positive median/average screen."
    if not trailing_best.empty:
        r = trailing_best.iloc[0]
        rec2 = f"`SL {int(r.stop_loss*100)}% / TP {int(r.take_profit*100)}% / hold {int(r.holding_days)}d / {r.trailing_variant}`"
    else:
        rec2 = "No trailing profile improves enough to recommend for paper testing."

    report = [
        "# Monitoring Risk-Control Simulation",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Scope: conservative Monitoring Tag candidate only. This is research, not trading advice.",
        "",
        "Simulation uses post-entry 1h OHLCV path. Same-candle handling is conservative for shorts: stop is assumed before TP when both are touched.",
        "",
        f"- Simulation rows: {len(sim)}",
        f"- Parameter combinations with fewer than 20 valid path rows: {low_valid}",
        f"- Round-trip cost assumption: {ROUNDTRIP_COST_BPS} bps",
        "",
        "## Recommended Paper-Test Profiles",
        "",
        f"1. {rec1}",
        f"2. {rec2} (diagnostic/riskier; trailing behavior uses 1h candles and intrabar ordering is uncertain)",
        "",
        "## Best Fixed SL/TP Profiles",
        "",
        fmt_table(
            best_practical,
            ["stop_loss", "take_profit", "holding_days", "trailing_variant", "n_trades", "win_rate", "median_return", "average_return", "p25_return", "p75_return", "profit_factor", "stop_hit_rate", "tp_hit_rate", "timeout_exit_rate", "median_holding_time_hours", "max_loss_after_stop_simulation"],
            12,
        ),
        "",
        "## Best Trailing Profiles",
        "",
        fmt_table(
            trailing_best,
            ["stop_loss", "take_profit", "holding_days", "trailing_variant", "n_trades", "win_rate", "median_return", "average_return", "profit_factor", "stop_hit_rate", "tp_hit_rate", "trailing_hit_rate", "timeout_exit_rate", "median_holding_time_hours", "max_loss_after_stop_simulation"],
            12,
        ),
        "",
        "## Tight Stop Diagnostic: 15%",
        "",
        fmt_table(
            tight,
            ["stop_loss", "take_profit", "holding_days", "n_trades", "win_rate", "median_return", "average_return", "profit_factor", "stop_hit_rate", "tp_hit_rate", "timeout_exit_rate"],
            20,
        ),
        "",
        "## Wider Stop Diagnostic: 30%",
        "",
        fmt_table(
            wide,
            ["stop_loss", "take_profit", "holding_days", "n_trades", "win_rate", "median_return", "average_return", "profit_factor", "stop_hit_rate", "tp_hit_rate", "timeout_exit_rate"],
            20,
        ),
        "",
        "## Interpretation",
        "",
        "- Tight stops do not automatically destroy expectancy in this proxy, but stop hit rates are material and same-candle ordering is conservative.",
        "- Very large historical MAE in the underlying candidate set means real liquidation/margin rules matter more than the simple OHLCV proxy.",
        "- TP rules around 20-30% often preserve the core edge better than waiting for extreme 50% targets.",
        "- Trailing rules should be treated cautiously because 1h candles cannot resolve intrabar ordering.",
        "- This layer supports paper/forward testing, not production deployment.",
        "",
    ]
    (DOCS / "monitoring_risk_control_report.md").write_text("\n".join(report))


def main() -> None:
    sim = build_simulation()
    summary = summarize(sim)
    write_report(summary, sim)
    print(
        {
            "simulation_rows": int(len(sim)),
            "summary_rows": int(len(summary)),
            "output": str(PROCESSED / "monitoring_risk_control_simulation.csv"),
            "report": str(DOCS / "monitoring_risk_control_report.md"),
        }
    )


if __name__ == "__main__":
    main()
