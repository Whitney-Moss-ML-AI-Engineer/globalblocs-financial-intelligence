"""Energy Intelligence API: company coverage, yfinance history, and EIA access."""
from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Any
import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/energy", tags=["energy-intelligence"])

COMPANIES = [
("Exxon Mobil","XOM","integrated","Integrated oil & gas","Upstream, refining, chemicals and low-carbon solutions"),
("Chevron","CVX","integrated","Integrated oil & gas","Upstream, refining and chemicals"),
("ConocoPhillips","COP","upstream","Exploration & production","Oil and natural gas exploration and production"),
("Occidental Petroleum","OXY","upstream","Exploration & production","Oil and gas production, chemicals and carbon management"),
("Devon Energy","DVN","upstream","Exploration & production","U.S. oil and gas production"),
("EOG Resources","EOG","upstream","Exploration & production","Oil and natural gas exploration and production"),
("Diamondback Energy","FANG","upstream","Exploration & production","Permian Basin oil and gas production"),
("Halliburton","HAL","services","Oilfield services","Drilling, completion and production services"),
("SLB","SLB","services","Oilfield services","Energy technology and oilfield services"),
("Baker Hughes","BKR","services","Oilfield services","Oilfield technology and industrial energy equipment"),
("Weatherford","WFRD","services","Oilfield services","Oilfield equipment and services"),
("Nabors Industries","NBR","services","Drilling","Land drilling rigs and services"),
("Helmerich & Payne","HP","services","Drilling","Contract drilling services"),
("Patterson-UTI Energy","PTEN","services","Drilling","Drilling and completion services"),
("Valaris","VAL","services","Offshore drilling","Offshore contract drilling"),
("Transocean","RIG","services","Offshore drilling","Offshore drilling services"),
("Liberty Energy","LBRT","services","Completion services","Hydraulic fracturing and completion services"),
("Kinder Morgan","KMI","midstream","Pipelines & storage","Natural gas, refined products and CO2 infrastructure"),
("Enterprise Products Partners","EPD","midstream","Pipelines & storage","NGL, crude oil, natural gas and storage"),
("Energy Transfer","ET","midstream","Pipelines & storage","Natural gas, NGL, crude oil and terminals"),
("ONEOK","OKE","midstream","Pipelines & processing","Natural gas liquids and natural gas infrastructure"),
("Enbridge","ENB","midstream","Pipelines & utilities","Liquids pipelines, gas transmission and utilities"),
("Williams Companies","WMB","midstream","Natural gas infrastructure","Natural gas gathering, processing and transmission"),
("Targa Resources","TRGP","midstream","Pipelines & processing","NGL gathering, processing, fractionation and export"),
("Plains All American Pipeline","PAA","midstream","Crude pipelines","Crude oil gathering, transportation and storage"),
("TC Energy","TRP","midstream","Pipelines & storage","Natural gas and liquids infrastructure"),
("DT Midstream","DTM","midstream","Natural gas infrastructure","Interstate pipelines, gathering and storage"),
("Phillips 66","PSX","refining","Refining & downstream","Refining, midstream, chemicals and marketing"),
("Marathon Petroleum","MPC","refining","Refining & downstream","Refining, marketing and midstream"),
("Valero Energy","VLO","refining","Refining & downstream","Petroleum refining and renewable diesel"),
("HF Sinclair","DINO","refining","Refining & downstream","Refining, marketing and lubricants"),
("PBF Energy","PBF","refining","Refining & downstream","Petroleum refining and logistics"),
("CVR Energy","CVI","refining","Refining & downstream","Petroleum refining and nitrogen fertilizers"),
("Delek US Holdings","DK","refining","Refining & downstream","Refining, logistics and convenience retail"),
("Par Pacific","PARR","refining","Refining & downstream","Refining, logistics and retail"),
("Spire","SR","gas_utility","Natural gas utility","Regulated natural gas distribution; St. Louis-area utility"),
("Atmos Energy","ATO","gas_utility","Natural gas utility","Regulated natural gas distribution and transmission"),
("ONE Gas","OGS","gas_utility","Natural gas utility","Regulated natural gas distribution"),
("NiSource","NI","gas_utility","Gas & electric utility","Regulated natural gas and electric utility operations"),
("Southwest Gas Holdings","SWX","gas_utility","Natural gas utility","Natural gas distribution and infrastructure services"),
("UGI Corporation","UGI","gas_utility","Gas utility & distribution","Natural gas utility and propane distribution"),
("Chesapeake Utilities","CPK","gas_utility","Gas utility & distribution","Regulated energy delivery and propane distribution"),
("National Fuel Gas","NFG","gas_utility","Integrated gas utility","Gas utility, gathering, pipeline and exploration"),
("Ameren","AEE","electric_utility","Electric & gas utility","Regulated electric and natural gas utility; Missouri/Illinois"),
("Southern Company","SO","electric_utility","Electric utility","Regulated electric and gas utilities"),
("Dominion Energy","D","electric_utility","Electric utility","Regulated electric utility and energy infrastructure"),
("Entergy","ETR","electric_utility","Electric utility","Regulated electric utility and power generation"),
]
SEGMENTS = [{"id":k,"name":v} for k,v in [
("integrated","Integrated oil & gas"),("upstream","Exploration & production"),
("services","Oilfield services & drilling"),("midstream","Pipelines & midstream"),
("refining","Refining & downstream"),("gas_utility","Natural gas utilities"),
("electric_utility","Electric utilities")] ]
COMPANY_ROWS = [dict(name=n,ticker=t,segment=s,subsector=sub,business_model=b) for n,t,s,sub,b in COMPANIES]
EIA_DATASETS = [
{"id":"petroleum_spot_prices","name":"Petroleum spot prices","path":"/v2/petroleum/pri/spt/data/","frequency":"daily","description":"Crude and petroleum product spot prices; select valid product, process and area facets."},
{"id":"petroleum_stocks","name":"Petroleum stocks and inventories","path":"/v2/petroleum/stoc/wstk/data/","frequency":"weekly","description":"Weekly petroleum stocks; select valid product and area facets."},
{"id":"petroleum_production","name":"Petroleum production","path":"/v2/petroleum/crd/crpdn/data/","frequency":"monthly","description":"Crude oil production; verify available dimensions in EIA metadata."},
{"id":"natural_gas_prices","name":"Natural gas futures prices","path":"/v2/natural-gas/pri/fut/data/","frequency":"daily","description":"Natural gas futures price observations; select valid series facets."},
{"id":"natural_gas_storage","name":"Natural gas storage","path":"/v2/natural-gas/stor/wkly/data/","frequency":"weekly","description":"Weekly natural gas storage; select valid series facets."},
{"id":"lng_exports","name":"LNG exports","path":"/v2/natural-gas/move/expcap/data/","frequency":"monthly","description":"LNG export-related observations; confirm dataset dimensions in EIA metadata."},
]

@router.get("/universe")
def company_universe(segment: str | None = Query(default=None)):
    rows=COMPANY_ROWS if not segment or segment=="all" else [x for x in COMPANY_ROWS if x["segment"]==segment]
    return {"count":len(rows),"total_coverage":len(COMPANY_ROWS),"segments":SEGMENTS,"companies":rows,"data_mode":"curated_company_universe","as_of":datetime.now(timezone.utc).isoformat()}

@router.get("/catalog")
def energy_catalog():
    return {"commodities":[
        {"id":"wti","name":"WTI crude oil","unit":"USD/barrel","market_symbol":"CL=F","source":"EIA / yfinance"},
        {"id":"brent","name":"Brent crude oil","unit":"USD/barrel","market_symbol":"BZ=F","source":"EIA / yfinance"},
        {"id":"henry_hub","name":"Henry Hub natural gas","unit":"USD/MMBtu","market_symbol":"NG=F","source":"EIA / yfinance"},
        {"id":"rbob","name":"RBOB gasoline","unit":"USD/gallon","market_symbol":"RB=F","source":"EIA / yfinance"},
        {"id":"heating_oil","name":"Heating oil / ULSD proxy","unit":"USD/gallon","market_symbol":"HO=F","source":"EIA / yfinance"}],
        "eia_datasets":EIA_DATASETS,
        "market_data_note":"yfinance is a research convenience adapter, not an exchange-licensed real-time feed. Review provider terms before commercial use."}

@router.get("/market-data")
def market_data(symbols: str=Query(default="CL=F,BZ=F,NG=F,SR,AEE,XOM,CVX,KMI,EPD,MPC,VLO"),period: str=Query(default="1y",pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$")):
    tickers=list(dict.fromkeys(x.strip().upper() for x in symbols.split(",") if x.strip()))
    if not tickers or len(tickers)>30: raise HTTPException(400,"Provide between 1 and 30 comma-separated ticker symbols.")
    try:
        import yfinance as yf
        frame=yf.download(tickers=tickers,period=period,interval="1d",auto_adjust=True,progress=False,threads=False)
        if frame.empty: raise ValueError("Provider returned no observations.")
        output=[]
        for ticker in tickers:
            try:
                series=frame["Close"][ticker].dropna() if getattr(frame.columns,"nlevels",1)>1 else frame["Close"].dropna()
                if series.empty: continue
                returns=series.pct_change().dropna()
                latest=float(series.iloc[-1]); prior=float(series.iloc[-22]) if len(series)>=22 else float(series.iloc[0]); start=float(series.iloc[0])
                output.append({"symbol":ticker,"latest_close":latest,"return_1m":latest/prior-1 if prior else None,"return_period":latest/start-1 if start else None,"volatility_30d_annualized":float(returns.tail(30).std()*252**0.5) if len(returns)>=2 else None,"observations":int(len(series)),"data_as_of":str(series.index[-1].date())})
            except (KeyError,TypeError,ValueError): continue
        return {"provider":"Yahoo Finance via yfinance","data_mode":"historical_market_data","period":period,"retrieved_at":datetime.now(timezone.utc).isoformat(),"symbols_requested":tickers,"observations":output,"disclaimer":"Historical observations may be delayed, adjusted or incomplete. Not an executable quote or investment recommendation."}
    except Exception as exc: raise HTTPException(502,f"Market-data retrieval failed: {exc}") from exc

class EIAQueryRequest(BaseModel):
    dataset_id: str
    params: dict[str,str]=Field(default_factory=dict)
    length: int=Field(default=100,ge=1,le=5000)

@router.post("/eia/query")
def query_eia(request: EIAQueryRequest):
    dataset=next((x for x in EIA_DATASETS if x["id"]==request.dataset_id),None)
    if dataset is None: raise HTTPException(400,"Unknown EIA dataset. Retrieve /api/v1/energy/catalog for supported datasets.")
    api_key=os.getenv("EIA_API_KEY")
    if not api_key: raise HTTPException(503,"EIA_API_KEY is not configured server-side. Add it to the server environment; never place it in browser code.")
    reserved={"api_key","frequency","data[0]","sort[0][column]","sort[0][direction]","offset","length"}
    if reserved.intersection(request.params):
        raise HTTPException(400,"Do not override reserved EIA request parameters; supply only dataset facet/filter parameters.")
    params={"api_key":api_key,"frequency":dataset["frequency"],"data[0]":"value","sort[0][column]":"period","sort[0][direction]":"desc","offset":"0","length":str(request.length)}
    params.update(request.params)
    try:
        response=requests.get("https://api.eia.gov"+dataset["path"],params=params,timeout=30)
        response.raise_for_status(); payload=response.json()
        return {"provider":"U.S. Energy Information Administration","dataset":dataset,"retrieved_at":datetime.now(timezone.utc).isoformat(),"request_parameters":{k:v for k,v in params.items() if k!="api_key"},"response":payload.get("response",{}),"api_warnings":payload.get("warnings",[]),"source_url":"https://www.eia.gov/opendata/"}
    except requests.RequestException as exc: raise HTTPException(502,f"EIA request failed: {exc}") from exc
    except ValueError as exc: raise HTTPException(502,"EIA returned a non-JSON response.") from exc
