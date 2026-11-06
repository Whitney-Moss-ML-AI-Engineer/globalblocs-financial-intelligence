"""SEC EDGAR company-facts adapter for energy issuer financial research.

Uses public SEC JSON endpoints. Configure SEC_USER_AGENT with an identifying
application name and contact email per SEC fair-access guidance.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Any
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/energy/sec", tags=["energy-sec-financials"])
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
TIMEOUT = 25
CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "assets": ["Assets"],
    "cash_from_operations": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "equity": ["StockholdersEquity"],
}
HEADERS = {"User-Agent": os.getenv("SEC_USER_AGENT", "GlobalBLOCS Financial Intelligence contact: configure-SEC_USER_AGENT"), "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}

def _get_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    payload=response.json()
    if not isinstance(payload,dict):
        raise ValueError("SEC returned an unexpected JSON structure.")
    return payload

def _resolve_cik(ticker: str) -> tuple[str,str]:
    payload=_get_json(SEC_TICKERS_URL, HEADERS)
    wanted=ticker.strip().upper()
    for item in payload.values():
        if str(item.get("ticker","")).upper()==wanted:
            return str(item["cik_str"]).zfill(10), str(item.get("title",wanted))
    raise HTTPException(status_code=404, detail=f"Ticker {wanted} was not found in the SEC company ticker directory.")

def _annual_values(facts: dict[str,Any], candidates: list[str], unit_preference: str="USD") -> list[dict[str,Any]]:
    gaap=facts.get("facts",{}).get("us-gaap",{})
    for tag in candidates:
        concept=gaap.get(tag)
        if not concept:
            continue
        units=concept.get("units",{})
        unit=unit_preference if unit_preference in units else next(iter(units),None)
        if not unit:
            continue
        records=[]
        for row in units.get(unit,[]):
            if row.get("form") not in ("10-K","20-F","40-F") or not row.get("fy") or not row.get("end"):
                continue
            start=row.get("start")
            if start and (datetime.fromisoformat(row["end"])-datetime.fromisoformat(start)).days not in range(300, 430):
                continue
            records.append({
                "fiscal_year":row.get("fy"),"period_end":row.get("end"),"period_start":start,
                "value":row.get("val"),"unit":unit,"form":row.get("form"),
                "filed":row.get("filed"),"accession_number":row.get("accn"),
                "frame":row.get("frame"),"concept":tag,
            })
        # Keep the most recently filed observation for each fiscal year/period end.
        latest={}
        for row in sorted(records,key=lambda x:(x["filed"] or "",x["accession_number"] or "")):
            latest[(row["fiscal_year"],row["period_end"])]=row
        if latest:
            return sorted(latest.values(),key=lambda x:x["period_end"],reverse=True)[:5]
    return []

@router.get("/company/{ticker}/facts")
def company_facts(ticker: str):
    ticker=ticker.strip().upper()
    if not ticker or len(ticker)>12 or not ticker.replace(".","").replace("-","").isalnum():
        raise HTTPException(status_code=400,detail="Provide a valid listed-company ticker.")
    if not os.getenv("SEC_USER_AGENT"):
        raise HTTPException(status_code=503,detail="Configure SEC_USER_AGENT with your application name and contact email before requesting SEC data.")
    try:
        cik,company_name=_resolve_cik(ticker)
        headers={**HEADERS,"Host":"data.sec.gov"}
        payload=_get_json(SEC_FACTS_URL.format(cik=cik),headers)
        facts={}
        for metric,candidates in CONCEPTS.items():
            facts[metric]=_annual_values(payload,candidates)
        return {
            "provider":"SEC EDGAR Company Facts","ticker":ticker,"company_name":company_name,
            "cik":cik,"retrieved_at":datetime.now(timezone.utc).isoformat(),
            "financials":facts,
            "source_url":f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            "filing_source_url":f"https://www.sec.gov/edgar/browse/?CIK={cik}",
            "limitations":[
                "Values are issuer-reported XBRL facts; taxonomy extensions and company-specific tags may not be captured by this starter mapping.",
                "Annual observations are selected from 10-K, 20-F or 40-F filings; fiscal years may differ across issuers.",
                "Cash-flow capital expenditures are reported as cash outflows and are not converted into positive investment amounts.",
                "This endpoint does not calculate valuation multiples or investment recommendations."
            ]
        }
    except HTTPException:
        raise
    except requests.HTTPError as exc:
        status=exc.response.status_code if exc.response is not None else 502
        raise HTTPException(status_code=502,detail=f"SEC request failed (upstream status {status}). Check SEC availability and request headers.") from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502,detail="Could not reach SEC EDGAR. Retry later.") from exc
    except (ValueError,KeyError,TypeError) as exc:
        raise HTTPException(status_code=502,detail=f"Could not parse SEC company facts: {exc}") from exc
