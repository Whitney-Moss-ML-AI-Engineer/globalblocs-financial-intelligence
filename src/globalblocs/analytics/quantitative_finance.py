"""Core quantitative-finance calculations used by the GlobalBLOCS metric layer."""
from __future__ import annotations
import numpy as np
import pandas as pd

def simple_return(beginning, ending): return ending / beginning - 1
def cagr(beginning, ending, years): return (ending / beginning) ** (1 / years) - 1
def pe_ratio(price, eps): return price / eps if eps not in (0, None) else np.nan
def price_to_book(price, book_value_per_share): return price / book_value_per_share if book_value_per_share not in (0, None) else np.nan
def price_to_sales(market_cap, revenue): return market_cap / revenue if revenue not in (0, None) else np.nan
def ev_ebitda(enterprise_value, ebitda): return enterprise_value / ebitda if ebitda not in (0, None) else np.nan
def free_cash_flow(operating_cash_flow, capex): return operating_cash_flow - capex
def fcf_yield(fcf, market_cap): return fcf / market_cap if market_cap not in (0, None) else np.nan
def current_ratio(current_assets, current_liabilities): return current_assets / current_liabilities if current_liabilities not in (0, None) else np.nan
def debt_to_equity(debt, equity): return debt / equity if equity not in (0, None) else np.nan
def roe(net_income, average_equity): return net_income / average_equity if average_equity not in (0, None) else np.nan
def roa(net_income, average_assets): return net_income / average_assets if average_assets not in (0, None) else np.nan
def roic(nopat, invested_capital): return nopat / invested_capital if invested_capital not in (0, None) else np.nan
def cash_conversion_cycle(dso, dio, dpo): return dso + dio - dpo
def rsi(returns, periods=14):
    r=pd.Series(returns,dtype="float64")
    gain=r.clip(lower=0).rolling(periods).mean()
    loss=(-r.clip(upper=0)).rolling(periods).mean()
    rs=gain/loss.replace(0,np.nan)
    return 100-(100/(1+rs))
