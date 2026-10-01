"""Global economy and 12-domain financial-intelligence feature layer."""
from datetime import date
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import yfinance as yf

FINANCIAL_DOMAINS = [
    {"name":"Economic Cycle","focus":"Business-cycle phase, output, inflation, employment and growth","metrics":["GDP Growth","Output Gap","Inflation","Unemployment","Real GDP"]},
    {"name":"Corporate Financial Health","focus":"Corporate profitability, leverage, liquidity and cash generation","metrics":["ROA","ROE","ROIC","Operating Margin","FCF Margin","Debt-to-GDP proxy"]},
    {"name":"Banking System","focus":"Bank credit, deposits, liquidity and financial-system conditions","metrics":["Bank Credit","Credit Growth","Financial Inclusion","Yield Curve","Financial Conditions"]},
    {"name":"Institutional Investors","focus":"Asset allocation, flows, exposures and portfolio risk","metrics":["Return","Volatility","Beta","Sharpe","Country Weight","Sector Weight"]},
    {"name":"Credit Markets","focus":"Credit conditions, spreads, default and loss measures","metrics":["Credit Spread","Default Spread","Expected Loss","Probability of Default","Credit Risk"]},
    {"name":"Derivatives Markets","focus":"Options, volatility, hedging and market-implied risk","metrics":["Implied Volatility","Delta","Gamma","Vega","Volatility Surface"]},
    {"name":"Structured Finance","focus":"Securitized assets, cash-flow structures and credit performance","metrics":["Credit Enhancement","Default Rate","Loss Severity","Prepayment","Tranche Risk"]},
    {"name":"Consumer Economy","focus":"Household demand, income, employment and consumption","metrics":["Consumption","Unemployment","Income","Inflation","Retail Demand"]},
    {"name":"Market Sentiment","focus":"Market expectations, momentum, positioning and risk appetite","metrics":["Return","Volume","Volatility","Drawdown","Correlation"]},
    {"name":"International Finance","focus":"Trade, capital flows, exchange rates and external balances","metrics":["Trade Openness","Current Account","FX Rate","FDI","Net Exports"]},
    {"name":"Monetary Policy","focus":"Interest rates, liquidity, money and central-bank conditions","metrics":["Policy Rate","Real Rate","Yield Curve","Money Supply","Financial Conditions"]},
    {"name":"Risk & Compliance","focus":"Market, sovereign, systemic, regulatory and data-quality risk","metrics":["VaR","CVaR","Drawdown","Sovereign Risk","Systemic Risk","Data Quality"]},
]

ECONOMIC_BLOCS = {
    "Global":["USA","CHN","DEU","JPN","IND","GBR","CAN","BRA","AUS","KOR","ZAF","MEX"],
    "G7":["USA","CAN","GBR","FRA","DEU","ITA","JPN"],
    "BRICS+":["BRA","RUS","IND","CHN","ZAF","EGY","ETH","IRN","ARE","SAU"],
    "European Union":["AUT","BEL","BGR","HRV","CYP","CZE","DNK","EST","FIN","FRA","DEU","GRC","HUN","IRL","ITA","LVA","LTU","LUX","MLT","NLD","POL","PRT","ROU","SVK","SVN","ESP","SWE"],
    "ASEAN":["BRN","KHM","IDN","LAO","MYS","MMR","PHL","SGP","THA","VNM"],
    "USMCA":["USA","CAN","MEX"],
    "MERCOSUR":["ARG","BRA","PRY","URY","BOL"],
    "GCC":["BHR","KWT","OMN","QAT","SAU","ARE"],
    "African Union":["DZA","EGY","ETH","GHA","KEN","MAR","NGA","RWA","SEN","TZA","ZAF"],
    "RCEP":["AUS","BRN","CHN","IDN","JPN","KHM","KOR","LAO","MYS","MMR","NZL","PHL","SGP","THA","VNM"],
    "CPTPP":["AUS","BRN","CAN","CHL","JPN","MYS","MEX","NZL","PER","SGP","VNM"],
}

REGIONS = {
    "Global":None,
    "North America":["USA","CAN","MEX"],
    "Latin America":["ARG","BRA","CHL","COL","MEX","PER","URY"],
    "Europe":["GBR","FRA","DEU","ITA","ESP","NLD","CHE","SWE","NOR","POL"],
    "Asia-Pacific":["CHN","JPN","KOR","IND","AUS","NZL","SGP","IDN","MYS","THA","VNM"],
    "Middle East":["SAU","ARE","QAT","KWT","ISR","TUR","IRN","EGY"],
    "Africa":["ZAF","NGA","EGY","KEN","GHA","MAR","ETH","TZA"],
}

MAP_INDICATORS = {
    "GDP Growth":"NY.GDP.MKTP.KD.ZG",
    "GDP Per Capita":"NY.GDP.PCAP.CD",
    "Inflation":"FP.CPI.TOTL.ZG",
    "Unemployment":"SL.UEM.TOTL.ZS",
    "Trade Openness":"NE.TRD.GNFS.ZS",
    "Exports (% GDP)":"NE.EXP.GNFS.ZS",
    "Imports (% GDP)":"NE.IMP.GNFS.ZS",
    "Current Account (% GDP)":"BN.CAB.XOKA.GD.ZS",
    "FDI Inflows (current US$)":"BX.KLT.DINV.CD.WD",
    "Bank Credit to Private Sector (% GDP)":"FS.AST.PRVT.GD.ZS",
    "R&D (% GDP)":"GB.XPD.RSDV.GD.ZS",
    "Debt (% GDP)":"GC.DOD.TOTL.GD.ZS",
    "Official Exchange Rate":"PA.NUS.FCRF",
}

@staticmethod
def _unused():
    return None

def worldbank_all(indicator, year):
    url=f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
    r=requests.get(url,params={"format":"json","per_page":400,"date":f"{year}:{year}"},timeout=30)
    r.raise_for_status()
    rows=[]
    for x in (r.json()[1] or []):
        if x.get("value") is not None and x.get("countryiso3code"):
            rows.append({"iso3":x["countryiso3code"],"country":x["country"]["value"],"value":x["value"],"year":int(x["date"])})
    return pd.DataFrame(rows)

def worldbank_country(indicator, iso3, start=2000, end=None):
    end=end or date.today().year
    url=f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}"
    r=requests.get(url,params={"format":"json","per_page":1000,"date":f"{start}:{end}"},timeout=30)
    r.raise_for_status()
    rows=[{"year":int(x["date"]),"value":x["value"]} for x in (r.json()[1] or []) if x.get("value") is not None]
    return pd.DataFrame(rows).sort_values("year") if rows else pd.DataFrame(columns=["year","value"])

def bloc_members(bloc, region):
    if bloc != "None":
        return ECONOMIC_BLOCS.get(bloc)
    return REGIONS.get(region)

def map_figure(df, title):
    if df.empty:
        return None
    return px.choropleth(df, locations="iso3", color="value", hover_name="country",
                         hover_data={"year":True,"value":":.3f","iso3":False},
                         color_continuous_scale="Viridis", projection="natural earth",
                         title=title)

def market_snapshot(tickers):
    rows=[]
    for ticker in [x.strip().upper() for x in tickers.split(",") if x.strip()]:
        try:
            d=yf.download(ticker,period="2y",interval="1d",auto_adjust=True,progress=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            if d.empty: continue
            c=d["Close"].dropna(); r=c.pct_change().dropna()
            dd=(c/c.cummax()-1)
            rows.append({"Ticker":ticker,"Last":float(c.iloc[-1]),"1Y Return":float(c.iloc[-252]/c.iloc[-1]*0+((c.iloc[-1]/c.iloc[-252])-1) if len(c)>252 else (c.iloc[-1]/c.iloc[0]-1)),
                         "Annual Volatility":float(r.std()*np.sqrt(252)),"Sharpe":float(r.mean()/r.std()*np.sqrt(252)) if r.std() else np.nan,
                         "Max Drawdown":float(dd.min()),"Observations":len(c)})
        except Exception:
            continue
    return pd.DataFrame(rows)

def domain_market_metrics(domain, market_df):
    if market_df.empty: return market_df
    d=market_df.copy()
    if domain in {"Economic Cycle","Consumer Economy"}:
        return d[["Ticker","1Y Return","Annual Volatility","Max Drawdown"]]
    if domain in {"Credit Markets","Risk & Compliance","Derivatives Markets"}:
        return d[["Ticker","Annual Volatility","Max Drawdown","Sharpe"]]
    if domain in {"Institutional Investors","Market Sentiment"}:
        return d[["Ticker","1Y Return","Sharpe","Annual Volatility"]]
    if domain in {"International Finance","Monetary Policy","Banking System"}:
        return d[["Ticker","1Y Return","Annual Volatility","Max Drawdown"]]
    return d

def bloc_market_summary(tickers, domain):
    d=market_snapshot(tickers)
    return domain_market_metrics(domain,d)
