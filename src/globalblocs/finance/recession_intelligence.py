"""Country and economic-BLOC recession assessment engine.

This module combines macroeconomic and country-level micro/structural indicators.
It deliberately separates an analytical recession signal from an official recession
dating decision, because definitions and source coverage differ by country.
"""
from datetime import date
import numpy as np
import pandas as pd
import requests

INDICATORS = {
    "real_gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "gdp_per_capita_growth": "NY.GDP.PCAP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "household_consumption": "NE.CON.PRVT.KD.ZG",
    "investment_growth": "NE.GDI.FTOT.KD.ZG",
    "trade_growth": "NE.TRD.GNFS.KD.ZG",
    "exports_gdp": "NE.EXP.GNFS.ZS",
    "imports_gdp": "NE.IMP.GNFS.ZS",
    "bank_credit_gdp": "FS.AST.PRVT.GD.ZS",
    "current_account_gdp": "BN.CAB.XOKA.GD.ZS",
    "government_debt_gdp": "GC.DOD.TOTL.GD.ZS",
    "manufacturing_value_added_growth": "NV.IND.MANF.KD.ZG",
    "industry_value_added_growth": "NV.IND.TOTL.KD.ZG",
    "services_value_added_growth": "NV.SRV.TOTL.KD.ZG",
    "agriculture_value_added_growth": "NV.AGR.TOTL.KD.ZG",
}

def _get(indicator, iso3, start=1990, end=None):
    end = end or date.today().year
    r = requests.get(
        f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}",
        params={"format": "json", "per_page": 1000, "date": f"{start}:{end}"},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    rows = [
        {"year": int(x["date"]), "value": float(x["value"])}
        for x in (payload[1] if len(payload) > 1 and payload[1] else [])
        if x.get("value") is not None
    ]
    return pd.DataFrame(rows).sort_values("year") if rows else pd.DataFrame(columns=["year", "value"])

def country_economic_panel(iso3, start=1990, end=None):
    frames = []
    for name, code in INDICATORS.items():
        d = _get(code, iso3, start, end).rename(columns={"value": name}).set_index("year")
        if not d.empty:
            frames.append(d)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).sort_index()

def _slope(series, window=3):
    s = pd.Series(series).dropna().tail(window)
    return float(np.polyfit(np.arange(len(s)), s.to_numpy(), 1)[0]) if len(s) >= 2 else np.nan

def _recent_change(series):
    s = pd.Series(series).dropna()
    return float(s.iloc[-1] - s.iloc[-2]) if len(s) >= 2 else np.nan

def assess_country(iso3, name=None, start=1990, end=None):
    d = country_economic_panel(iso3, start, end)
    if d.empty or "real_gdp_growth" not in d or len(d.dropna(subset=["real_gdp_growth"])) < 3:
        return {"iso3": iso3, "country": name or iso3, "status": "Insufficient data", "confidence": 0.0, "panel": d}

    latest = d.iloc[-1]
    g = d["real_gdp_growth"].dropna()
    gchg = _recent_change(g)
    g3 = _slope(g)
    pc = d["gdp_per_capita_growth"].dropna()
    cchg = _recent_change(d["household_consumption"])
    ichg = _recent_change(d["investment_growth"])
    unemp_slope = _slope(d["unemployment"])
    trade_chg = _recent_change(d["trade_growth"])
    sector_cols = [x for x in ["manufacturing_value_added_growth","industry_value_added_growth","services_value_added_growth","agriculture_value_added_growth"] if x in d]
    sector_latest = d[sector_cols].iloc[-1].dropna() if sector_cols else pd.Series(dtype=float)

    macro_negative = int(g.iloc[-1] < 0)
    macro_accelerating_down = int(g3 < 0 and gchg < 0)
    broad_activity = int(sum([
        pd.notna(latest.get("household_consumption", np.nan)) and latest["household_consumption"] < 0,
        pd.notna(latest.get("investment_growth", np.nan)) and latest["investment_growth"] < 0,
        pd.notna(latest.get("trade_growth", np.nan)) and latest["trade_growth"] < 0,
        pd.notna(latest.get("gdp_per_capita_growth", np.nan)) and latest["gdp_per_capita_growth"] < 0,
        pd.notna(unemp_slope) and unemp_slope > 0,
        (sector_latest < 0).sum() >= max(1, int(np.ceil(len(sector_latest) / 2))) if len(sector_latest) else False,
    ]))

    # Annual-data recession screen: contraction in output plus broad weakening.
    if macro_negative and broad_activity >= 3:
        status = "Recession signal"
    elif macro_negative or broad_activity >= 3 or macro_accelerating_down:
        status = "Contraction / recession risk"
    else:
        status = "No recession signal"

    evidence = [
        g.iloc[-1] < 0,
        pd.notna(gchg) and gchg < 0,
        pd.notna(pc.iloc[-1]) and pc.iloc[-1] < 0 if len(pc) else False,
        cchg < 0 if pd.notna(cchg) else False,
        ichg < 0 if pd.notna(ichg) else False,
        unemp_slope > 0 if pd.notna(unemp_slope) else False,
    ]
    confidence = float(np.mean(evidence))
    if status == "No recession signal":
        confidence = 1 - confidence
    return {
        "iso3": iso3,
        "country": name or iso3,
        "status": status,
        "confidence": round(max(0, min(1, confidence)), 2),
        "latest_year": int(g.index[-1]),
        "real_gdp_growth": float(g.iloc[-1]),
        "gdp_growth_change": gchg,
        "gdp_growth_slope": g3,
        "gdp_per_capita_growth": float(pc.iloc[-1]) if len(pc) else np.nan,
        "unemployment_slope": unemp_slope,
        "household_consumption_growth": float(latest.get("household_consumption", np.nan)),
        "investment_growth": float(latest.get("investment_growth", np.nan)),
        "trade_growth": float(latest.get("trade_growth", np.nan)),
        "inflation": float(latest.get("inflation", np.nan)),
        "broad_weakening_signals": broad_activity,
        "panel": d,
    }

def assess_bloc(members, names=None, start=1990, end=None):
    rows = []
    names = names or {}
    for iso3 in members:
        try:
            a = assess_country(iso3, names.get(iso3, iso3), start, end)
            if a.get("status") != "Insufficient data":
                rows.append({k:v for k,v in a.items() if k != "panel"})
        except Exception:
            continue
    table = pd.DataFrame(rows)
    if table.empty:
        return {"status": "Insufficient data", "confidence": 0.0, "table": table}

    # The BLOC screen is breadth-based rather than a simple average of countries.
    recession_share = (table["status"] == "Recession signal").mean()
    contraction_share = table["status"].isin(["Recession signal","Contraction / recession risk"]).mean()
    weighted_growth = float(table["real_gdp_growth"].mean())
    if recession_share >= 0.50 and weighted_growth < 0:
        status = "BLOC-wide recession signal"
    elif contraction_share >= 0.50 or weighted_growth < 0:
        status = "BLOC contraction / elevated recession risk"
    else:
        status = "No BLOC-wide recession signal"
    return {
        "status": status,
        "confidence": round(float(max(recession_share, 1-recession_share if "No" in status else contraction_share)), 2),
        "recession_share": float(recession_share),
        "contraction_share": float(contraction_share),
        "mean_real_gdp_growth": weighted_growth,
        "table": table,
    }

def micro_macro_summary(assessment):
    return {
        "Macro": {
            "Real GDP growth": assessment.get("real_gdp_growth"),
            "GDP per-capita growth": assessment.get("gdp_per_capita_growth"),
            "Inflation": assessment.get("inflation"),
            "Unemployment trend": assessment.get("unemployment_slope"),
        },
        "Micro / activity": {
            "Household consumption growth": assessment.get("household_consumption_growth"),
            "Investment growth": assessment.get("investment_growth"),
            "Trade growth": assessment.get("trade_growth"),
            "Broad weakening signals": assessment.get("broad_weakening_signals"),
        },
    }
