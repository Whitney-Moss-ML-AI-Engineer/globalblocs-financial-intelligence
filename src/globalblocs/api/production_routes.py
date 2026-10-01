"""Production capability registry endpoints for the GlobalBLOCS dashboard."""
from fastapi import APIRouter, HTTPException
from globalblocs.finance.script_registry import list_scripts
from globalblocs.ingestion.source_connectors import list_sources
from globalblocs.models.model_registry import list_models, model_requirements

router = APIRouter(prefix="/api/v1/production", tags=["production"])

@router.get("/scripts")
def scripts():
    return {"scripts": list_scripts()}

@router.get("/sources")
def sources():
    return {"sources": list_sources()}

@router.get("/models")
def models():
    return {"models": list_models()}

@router.get("/models/{family}")
def model_family(family: str):
    requirements = model_requirements(family)
    if not requirements["models"]:
        raise HTTPException(status_code=404, detail=f"Unknown model family: {family}")
    return requirements


# Dedicated analytical workspaces. These endpoints accept user-supplied records so the
# API can be exercised without embedding market data or credentials in the repository.
from typing import Any
import pandas as pd
from pydantic import BaseModel, Field
from globalblocs.analytics.economic_cycle import business_cycle_screen
from globalblocs.analytics.risk import risk_summary
from globalblocs.finance.investment_metrics import metric_catalog
from globalblocs.finance.recession_intelligence import INDICATORS as RECESSION_INDICATORS
from globalblocs.finance.global_intelligence import FINANCIAL_DOMAINS, ECONOMIC_BLOCS, REGIONS
from globalblocs.finance.research_providers import RATING_RESEARCH_PROVIDERS
from globalblocs.validation.data_quality import profile, quality_score

class RecordsRequest(BaseModel):
    records: list[dict[str, Any]] = Field(default_factory=list)

class RiskRequest(BaseModel):
    prices: list[float] = Field(min_length=2)
    risk_free: float = 0.0

class CycleRequest(BaseModel):
    records: list[dict[str, Any]] = Field(default_factory=list)
    gdp_column: str = "gdp_growth"
    unemployment_column: str = "unemployment"
    industrial_column: str = "industrial_production"
    spread_column: str = "yield_curve_spread"

@router.get("/intelligence/domains")
def intelligence_domains():
    return {"domains": FINANCIAL_DOMAINS}

@router.get("/intelligence/blocs")
def economic_blocs():
    return {"blocs": ECONOMIC_BLOCS, "regions": REGIONS}

@router.get("/intelligence/recession-indicators")
def recession_indicators():
    return {"indicators": RECESSION_INDICATORS}

@router.get("/intelligence/metrics")
def investment_metric_catalog():
    return {"count": int(len(metric_catalog())), "metrics": metric_catalog().to_dict(orient="records")}

@router.get("/intelligence/research-providers")
def research_providers():
    return {"providers": RATING_RESEARCH_PROVIDERS}

@router.post("/intelligence/data-quality")
def data_quality(request: RecordsRequest):
    frame = pd.DataFrame(request.records)
    return {"profile": profile(frame), "quality_score": quality_score(frame)}

@router.post("/intelligence/risk")
def risk(request: RiskRequest):
    frame = pd.Series(request.prices, dtype="float64")
    return {"risk_summary": risk_summary(frame), "observations": int(len(frame))}

@router.post("/intelligence/business-cycle")
def business_cycle(request: CycleRequest):
    frame = pd.DataFrame(request.records)
    result = business_cycle_screen(
        frame,
        gdp_col=request.gdp_column,
        unemployment_col=request.unemployment_column,
        industrial_col=request.industrial_column,
        spread_col=request.spread_column,
    )
    result["quality_score"] = quality_score(frame)
    return result

from globalblocs.finance.metric_knowledge_base import metric_catalog as metric_knowledge_catalog, get_metric as get_metric_knowledge, search_metrics as search_metric_knowledge, validate_catalog as validate_metric_catalog
from globalblocs.finance.visualization_registry import build_metric_visualization_profile, compatible_visualizations, VISUALIZATIONS

@router.get("/metrics/knowledge-base")
def metric_knowledge_base(query: str = "", category: str = ""):
    metrics = search_metric_knowledge(query, category or None)
    return {"count": len(metrics), "catalog_validation": validate_metric_catalog(), "metrics": metrics}

@router.get("/metrics/knowledge-base/{metric_id}")
def metric_knowledge(metric_id: int):
    metric = get_metric_knowledge(metric_id)
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric

@router.get("/metrics/knowledge-base/{metric_id}/visualization")
def metric_visualization_profile(metric_id: int):
    metric = get_metric_knowledge(metric_id)
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return build_metric_visualization_profile(metric)

@router.get("/visualizations")
def visualization_library():
    return {"count": len(VISUALIZATIONS), "visualizations": VISUALIZATIONS}

class VisualizationCompatibilityRequest(BaseModel):
    columns: list[str] = Field(default_factory=list)
    numeric_columns: list[str] = Field(default_factory=list)

@router.post("/visualizations/compatible")
def visualization_compatibility(request: VisualizationCompatibilityRequest):
    return {"compatible": compatible_visualizations(request.columns, request.numeric_columns)}

from globalblocs.models.evaluation_registry import evaluations_for_visualization

@router.get("/evaluations/{chart_type}")
def visualization_evaluations(chart_type: str):
    return {"visualization": chart_type, "evaluation_metrics": evaluations_for_visualization(chart_type)}
