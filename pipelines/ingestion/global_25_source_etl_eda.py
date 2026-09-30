"""GlobalBLOCS 25-source ETL + EDA starter pipeline."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Callable
import pandas as pd
import requests
from globalblocs.analytics.six_questions import run_six_questions
from globalblocs.ingestion.http import add_lineage, fetch_csv, fetch_excel, fetch_json

RAW_DIR, SILVER_DIR, GOLD_DIR = Path("data/bronze"), Path("data/silver"), Path("data/gold")

def save_bronze(df, source_id):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{source_id}.parquet"
    df.to_parquet(path, index=False)
    return path

def standardize_common_columns(df):
    out = df.copy()
    for src, dst in {"country":"entity_name","country_name":"entity_name","Country":"entity_name",
                     "date":"period","Date":"period","year":"period","Year":"period",
                     "Value":"value"}.items():
        if src in out.columns and dst not in out.columns:
            out[dst] = out[src]
    if "period" in out.columns:
        out["period"] = out["period"].astype(str)
    return out

def transform_and_profile(df, source_id):
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    out = standardize_common_columns(df)
    out.to_parquet(SILVER_DIR / f"{source_id}.parquet", index=False)
    return out

def six_question_eda(df, source_id, value_col="value", group_col="entity_name",
                     time_col="period", target_col=None, predictors=None):
    if value_col not in df:
        raise ValueError(f"{source_id}: expected '{value_col}' or pass value_col explicitly.")
    report = run_six_questions(df, value_col, group_col, time_col, target_col, predictors)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    report.descriptive.to_csv(GOLD_DIR / f"{source_id}_descriptive.csv")
    report.exploratory.to_csv(GOLD_DIR / f"{source_id}_exploratory.csv")
    return report

# 1 World Bank WDI
def world_bank_wdi(indicator="NY.GDP.MKTP.CD", date_range="2000:2025"):
    url = "https://api.worldbank.org/v2/country/all/indicator/" + indicator
    payload = fetch_json(url, {"format":"json","per_page":100000,"date":date_range})
    return add_lineage(pd.DataFrame(payload[1]), "world_bank_wdi", indicator, url)

# 2 IMF WEO/DataMapper
def imf_weo(indicator="NGDP_R"):
    url = f"https://www.imf.org/external/datamapper/api/v2/{indicator}"
    payload = fetch_json(url)
    rows = [{"entity_name": c, "period": p, "value": v}
            for c, vals in payload.get("values", {}).get(indicator, {}).items()
            for p, v in vals.items()]
    return add_lineage(pd.DataFrame(rows), "imf_weo", indicator, url)

# 3 WTO Timeseries API
def wto_timeseries(url=None, params=None):
    if not url:
        raise ValueError("Supply the WTO Timeseries API URL/query from the WTO API portal.")
    payload = fetch_json(url, params, {"Ocp-Apim-Subscription-Key": os.getenv("WTO_API_KEY","")})
    rows = payload.get("Dataset", payload if isinstance(payload, list) else [])
    return add_lineage(pd.DataFrame(rows), "wto", "timeseries", url)

# 4 UN Comtrade
def un_comtrade(reporter_code=840, period="2025", cmd_code="TOTAL", flow_code="X"):
    url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
    params = {"reporterCode":reporter_code,"period":period,"cmdCode":cmd_code,
              "flowCode":flow_code,"partnerCode":0,"partner2Code":0,
              "customsCode":"C00","motCode":0,"maxRecords":500}
    payload = fetch_json(url, params)
    return add_lineage(pd.DataFrame(payload.get("data",[])), "un_comtrade", "HS", url)

# 5 OECD
def oecd_sdmx(url):
    return add_lineage(fetch_csv(url), "oecd", "sdmx_dataset", url)

# 6 BIS
def bis_statistics(url):
    return add_lineage(fetch_csv(url), "bis", "statistics", url)

# 7 FRED
def fred(series_id="GDP", api_key=None):
    api_key = api_key or os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY is required.")
    url = "https://api.stlouisfed.org/fred/series/observations"
    payload = fetch_json(url, {"series_id":series_id,"api_key":api_key,"file_type":"json"})
    return add_lineage(pd.DataFrame(payload["observations"]), "fred", series_id, url)

# 8 U.S. Treasury Fiscal Data
def treasury_fiscal_data(url, params=None):
    payload = fetch_json(url, params)
    return add_lineage(pd.DataFrame(payload["data"]), "us_treasury_fiscal", "fiscal_data", url)

# 9 New York Fed Markets Data / SOFR
def ny_fed_sofr(start_date="2025-01-01", end_date="2025-12-31"):
    url = "https://markets.newyorkfed.org/api/rates/secured/sofr/search.json"
    payload = fetch_json(url, {"startDate":start_date,"endDate":end_date,"type":"rate"})
    return add_lineage(pd.DataFrame(payload.get("refRates", payload.get("data",[]))),
                       "ny_fed", "sofr", url)

# 10 EIA
def eia_api(url, params=None):
    payload = fetch_json(url, params)
    rows = payload.get("response",{}).get("data",[])
    return add_lineage(pd.DataFrame(rows), "eia", "energy", url)

# 11 OPEC
def opec_download(url):
    return add_lineage(fetch_excel(url), "opec", "annual_statistical_bulletin", url)

# 12 IEA
def iea_download(url):
    return add_lineage(fetch_csv(url), "iea", "energy_dataset", url)

# 13 ECB
def ecb_data(flow="EXR/D.USD.EUR.SP00.A", start_period="2025-01-01"):
    url = f"https://data-api.ecb.europa.eu/service/data/{flow}"
    r = requests.get(url, params={"startPeriod":start_period,"format":"csvdata"}, timeout=120)
    r.raise_for_status()
    from io import StringIO
    return add_lineage(pd.read_csv(StringIO(r.text)), "ecb", flow, url)

# 14 Eurostat
def eurostat(dataset_code="nama_10_gdp", params=None):
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_code}"
    payload = fetch_json(url, params)
    values, dims, sizes = payload.get("value",{}), payload.get("id",[]), payload.get("size",[])
    if not dims:
        return add_lineage(pd.DataFrame(), "eurostat", dataset_code, url)
    categories = []
    for dim in dims:
        idx = payload["dimension"][dim]["category"]["index"]
        categories.append([k for k,_ in sorted(idx.items(), key=lambda kv:kv[1])])
    rows = []
    for flat_idx, value in values.items():
        n, coords = int(flat_idx), []
        for size, cats in reversed(list(zip(sizes,categories))):
            coords.append(cats[n % size]); n //= size
        row = dict(zip(reversed(dims), reversed(coords)))
        row["value"] = value
        rows.append(row)
    return add_lineage(pd.DataFrame(rows), "eurostat", dataset_code, url)

# 15 Bank of England
def bank_of_england(url):
    return add_lineage(fetch_csv(url), "bank_of_england", "iadb", url)

# 16 Bank of Japan
def bank_of_japan(url):
    return add_lineage(fetch_csv(url), "bank_of_japan", "time_series", url)

# 17 People's Bank of China
def peoples_bank_of_china(url):
    return add_lineage(fetch_excel(url), "pboc", "statistics", url)

# 18 Reserve Bank of India
def reserve_bank_of_india(url):
    return add_lineage(fetch_csv(url), "rbi", "dbie", url)

# 19 UNCTADstat
def unctadstat(url):
    return add_lineage(fetch_csv(url), "unctadstat", "statistics", url)

# 20 FAOSTAT
def faostat(url):
    return add_lineage(fetch_csv(url), "faostat", "statistics", url)

# 21 World Bank Worldwide Governance Indicators
def world_governance_indicators(indicator="CC.EST"):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
    payload = fetch_json(url, {"format":"json","per_page":100000})
    return add_lineage(pd.DataFrame(payload[1]), "world_bank_wgi", indicator, url)

# 22 V-Dem
def vdem(url):
    return add_lineage(fetch_csv(url), "vdem", "country_year", url)

# 23 Penn World Table
def penn_world_table(url):
    return add_lineage(fetch_excel(url), "penn_world_table", "pwt", url)

# 24 World Inequality Database
def world_inequality_database(url):
    return add_lineage(fetch_csv(url), "wid", "inequality", url)

# 25 SIPRI Military Expenditure
def sipri_milex(url):
    return add_lineage(fetch_excel(url), "sipri", "military_expenditure", url)

SOURCES: dict[str, Callable] = {
    "world_bank_wdi": world_bank_wdi, "imf_weo": imf_weo, "wto": wto_timeseries,
    "un_comtrade": un_comtrade, "oecd": oecd_sdmx, "bis": bis_statistics, "fred": fred,
    "us_treasury_fiscal": treasury_fiscal_data, "ny_fed_sofr": ny_fed_sofr, "eia": eia_api,
    "opec": opec_download, "iea": iea_download, "ecb": ecb_data, "eurostat": eurostat,
    "bank_of_england": bank_of_england, "bank_of_japan": bank_of_japan,
    "pboc": peoples_bank_of_china, "rbi": reserve_bank_of_india, "unctadstat": unctadstat,
    "faostat": faostat, "wgi": world_governance_indicators, "vdem": vdem,
    "pwt": penn_world_table, "wid": world_inequality_database, "sipri_milex": sipri_milex,
}

if __name__ == "__main__":
    df = fred("GDP")
    bronze = save_bronze(df, "fred_gdp")
    silver = transform_and_profile(df, "fred_gdp")
    report = six_question_eda(silver, "fred_gdp", value_col="value")
    print(report.descriptive.head())
    print(f"Saved bronze data to {bronze}")
