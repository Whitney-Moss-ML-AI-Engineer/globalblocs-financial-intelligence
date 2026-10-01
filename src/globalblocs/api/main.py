from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from globalblocs.api.finance_routes import router as finance_router

app = FastAPI(
    title="GlobalBLOCS Financial Intelligence API",
    version="0.2.0",
    description="Evidence-first API layer for the GlobalBLOCS dashboard.",
)

app.include_router(finance_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to the deployed dashboard origin in production.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DOMAINS = [
    {"id": "economic-cycle", "name": "Economic Cycle", "status": "ready"},
    {"id": "corporate-health", "name": "Corporate Financial Health", "status": "planned"},
    {"id": "banking", "name": "Banking System", "status": "planned"},
    {"id": "institutional-investors", "name": "Institutional Investment", "status": "planned"},
    {"id": "credit", "name": "Credit Markets", "status": "planned"},
    {"id": "derivatives", "name": "Derivatives Markets", "status": "planned"},
    {"id": "structured-finance", "name": "Structured Finance", "status": "planned"},
    {"id": "consumer", "name": "Consumer Economy", "status": "planned"},
    {"id": "sentiment", "name": "Market Sentiment", "status": "planned"},
    {"id": "international", "name": "International Finance", "status": "planned"},
    {"id": "monetary-policy", "name": "Monetary Policy", "status": "ready"},
    {"id": "risk-compliance", "name": "Risk & Compliance", "status": "planned"},
]


class DashboardObservation(BaseModel):
    country: str
    bloc: str
    variable: str
    period: str
    value: float
    unit: str


DEMO_OBSERVATIONS = [
    DashboardObservation(country="United States", bloc="North America", variable="Real GDP Growth", period="2025", value=2.8, unit="%"),
    DashboardObservation(country="United States", bloc="North America", variable="Inflation Rate", period="2025", value=3.1, unit="%"),
    DashboardObservation(country="Germany", bloc="European Union", variable="Real GDP Growth", period="2025", value=1.1, unit="%"),
    DashboardObservation(country="Japan", bloc="Asia-Pacific", variable="Real GDP Growth", period="2025", value=1.0, unit="%"),
    DashboardObservation(country="Brazil", bloc="Emerging Markets", variable="Inflation Rate", period="2025", value=4.8, unit="%"),
    DashboardObservation(country="India", bloc="Emerging Markets", variable="Real GDP Growth", period="2025", value=6.4, unit="%"),
]


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "globalblocs-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_mode": "demo",
    }


@app.get("/api/v1/domains")
def domains() -> dict[str, Any]:
    return {"domains": DOMAINS}


@app.get("/api/v1/overview")
def overview() -> dict[str, Any]:
    return {
        "data_mode": "demo",
        "lineage_required": True,
        "source_of_truth": "validated Gold-layer datasets",
        "kpis": {
            "real_gdp_growth": {"value": 2.8, "unit": "%"},
            "inflation": {"value": 3.1, "unit": "%"},
            "unemployment": {"value": 4.2, "unit": "%"},
            "policy_rate": {"value": 4.25, "unit": "%"},
            "trade_balance": {"value": -215, "unit": "USD billions"},
        },
    }


@app.get("/api/v1/observations", response_model=list[DashboardObservation])
def observations(
    country: str | None = Query(default=None),
    bloc: str | None = Query(default=None),
    variable: str | None = Query(default=None),
    period: str | None = Query(default=None),
) -> list[DashboardObservation]:
    result = DEMO_OBSERVATIONS
    if country and country != "All":
        result = [x for x in result if x.country == country]
    if bloc and bloc != "All":
        result = [x for x in result if x.bloc == bloc]
    if variable:
        result = [x for x in result if x.variable == variable]
    if period:
        result = [x for x in result if x.period == period]
    return result
