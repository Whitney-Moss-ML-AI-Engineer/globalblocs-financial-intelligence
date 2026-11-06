"""Derived energy issuer operating and financial analytics from SEC facts.

Only comparable reported annual XBRL facts are used. Ratios are not forecasts
or valuation multiples; missing concepts remain null rather than imputed.
"""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from globalblocs.api.energy_sec_routes import company_facts

router=APIRouter(prefix="/api/v1/energy/analytics",tags=["energy-analytics"])

def _index(financials:dict,metric:str)->dict[str,dict]:
    return {str(row.get("period_end")):row for row in financials.get(metric,[]) if row.get("period_end") and isinstance(row.get("value"),(int,float))}

def _value(index:dict[str,dict],period:str):
    row=index.get(period)
    return float(row["value"]) if row and row.get("value") is not None else None

def _ratio(numerator,denominator):
    if numerator is None or denominator in (None,0):return None
    return numerator/denominator

@router.get("/company/{ticker}")
def company_analytics(ticker:str):
    facts=company_facts(ticker)
    financials=facts.get("financials",{})
    metrics={key:_index(financials,key) for key in (
        "revenue","operating_income","net_income","assets","cash_from_operations",
        "capital_expenditures","long_term_debt","equity","cash_and_equivalents"
    )}
    periods=sorted(set().union(*(set(x.keys()) for x in metrics.values())),reverse=True)
    output=[]
    for period in periods[:5]:
        revenue=_value(metrics["revenue"],period)
        operating_income=_value(metrics["operating_income"],period)
        net_income=_value(metrics["net_income"],period)
        assets=_value(metrics["assets"],period)
        cash_ops=_value(metrics["cash_from_operations"],period)
        capex=_value(metrics["capital_expenditures"],period)
        debt=_value(metrics["long_term_debt"],period)
        equity=_value(metrics["equity"],period)
        cash=_value(metrics["cash_and_equivalents"],period)
        prior_periods=[p for p in periods if p<period and _value(metrics["revenue"],p) is not None]
        prior_revenue=_value(metrics["revenue"],prior_periods[0]) if prior_periods else None
        fcf=(cash_ops-abs(capex)) if cash_ops is not None and capex is not None else None
        output.append({
            "period_end":period,
            "fiscal_year":(metrics["revenue"].get(period) or metrics["net_income"].get(period) or {}).get("fiscal_year"),
            "revenue_growth":_ratio(revenue-prior_revenue,prior_revenue) if revenue is not None and prior_revenue not in (None,0) else None,
            "operating_margin":_ratio(operating_income,revenue),
            "net_margin":_ratio(net_income,revenue),
            "free_cash_flow":fcf,
            "free_cash_flow_margin":_ratio(fcf,revenue),
            "cash_conversion":_ratio(cash_ops,net_income),
            "return_on_assets":_ratio(net_income,assets),
            "return_on_equity":_ratio(net_income,equity),
            "long_term_debt_to_assets":_ratio(debt,assets),
            "long_term_debt_to_equity":_ratio(debt,equity),
            "net_debt":(debt-cash) if debt is not None and cash is not None else None,
            "capital_expenditure_intensity":_ratio(abs(capex),revenue),
            "source_filing":(metrics["revenue"].get(period) or metrics["net_income"].get(period) or {}).get("accession_number")
        })
    return {
        "provider":"SEC EDGAR Company Facts; GlobalBLOCS derived calculations",
        "ticker":facts.get("ticker"),"company_name":facts.get("company_name"),
        "retrieved_at":datetime.now(timezone.utc).isoformat(),"periods":output,
        "methodology":{
            "free_cash_flow":"Cash from operations minus absolute reported PP&E acquisition cash outflow; null if either input is missing.",
            "return_on_assets":"Net income divided by reported period-end total assets (not average assets).",
            "return_on_equity":"Net income divided by reported period-end stockholders' equity (not average equity).",
            "cash_conversion":"Cash from operations divided by net income; null when net income is zero or missing.",
            "leverage":"Long-term debt divided by period-end assets or equity. Current debt is not included unless the reported concept includes it.",
            "limitations":"Annual SEC facts only; standard-tag mapping may omit issuer-specific extensions. Fiscal year ends differ. Ratios are not investment recommendations. EV/EBITDA, ROIC and reserve/production metrics are not calculated in this phase."
        }
    }
