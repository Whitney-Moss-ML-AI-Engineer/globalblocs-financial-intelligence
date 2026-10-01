"""Financial intelligence API routes: credentialed ingestion, API-specific ETL/EDA and features."""
from __future__ import annotations
from typing import Any
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from globalblocs.finance.api_contracts import list_contracts, get_contract
from globalblocs.finance.api_ingestion import APIConfig, request_api, normalize_ingested_data, analytical_summary, trend_summary
from globalblocs.finance.api_etl_eda import api_etl_eda_pipeline
from globalblocs.finance.investment_metrics import calculate_metrics, METRICS
from globalblocs.finance.economic_concepts import MACRO_CONCEPTS, MICRO_CONCEPTS
from globalblocs.finance.concept_securities import securities_for_concept, concept_security_categories
from globalblocs.finance.research_providers import provider_dataframe, product_dataframe, regulatory_dataframe

router = APIRouter(prefix="/api/v1/finance", tags=["financial-intelligence"])

class RuleRequest(BaseModel):
    column: str | None = None
    operation: str
    new_name: str | None = None
    feature_name: str | None = None
    source_column: str | None = None
    window: int = 20
    periods: int = 1

class DatasetRequest(BaseModel):
    provider: str = "User Dataset"
    endpoint: str = "inline"
    records: list[dict[str, Any]] = Field(default_factory=list)
    transform_rules: list[RuleRequest] = Field(default_factory=list)
    feature_rules: list[RuleRequest] = Field(default_factory=list)

class CredentialedIngestionRequest(BaseModel):
    provider: str
    endpoint: str
    method: str = "GET"
    auth_method: str = "Bearer token"
    credential_name: str = ""
    credential_value: str = ""
    api_key_header: str = "X-API-Key"
    api_key_param: str = "api_key"
    username: str = ""
    password: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    json_body: dict[str, Any] = Field(default_factory=dict)
    timeout: int = 30
    transform_rules: list[RuleRequest] = Field(default_factory=list)
    feature_rules: list[RuleRequest] = Field(default_factory=list)

def _rules(items: list[RuleRequest]) -> list[dict[str, Any]]:
    return [x.model_dump(exclude_none=True) for x in items]

def _records(frame: pd.DataFrame, limit: int = 200) -> list[dict[str, Any]]:
    return frame.head(limit).where(pd.notna(frame.head(limit)), None).to_dict("records")

def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return _records(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try: return value.item()
        except Exception: pass
    return value

def _analyze(frame: pd.DataFrame, provider: str, endpoint: str, tr, fr) -> dict[str, Any]:
    pipeline = api_etl_eda_pipeline(frame, provider, endpoint, _rules(tr), _rules(fr))
    result = {
        "provider": provider,
        "endpoint": endpoint,
        "row_count": len(frame),
        "column_count": len(frame.columns),
        "data_dictionary": pipeline["data_dictionary"],
        "eda": pipeline["eda_before"],
        "transformation_audit": pipeline["transformation_audit"],
        "feature_audit": pipeline["feature_audit"],
        "silver_preview": pipeline["silver"],
        "feature_table": pipeline["feature_table"],
        "feature_matrix": pipeline["feature_matrix"],
        "analytical_summary": analytical_summary(pipeline["silver"]),
        "trend_summary": trend_summary(pipeline["silver"]),
        "provenance": pipeline["provenance"],
    }
    if "Close" in pipeline["silver"].columns:
        try:
            metrics = calculate_metrics(pipeline["silver"], info={})
            result["investment_metrics"] = metrics
        except Exception:
            result["investment_metrics"] = pd.DataFrame()
    return _json_safe(result)

@router.get("/api-contracts")
def api_contracts() -> dict[str, Any]:
    return {"contracts": list_contracts()}

@router.get("/api-contracts/{contract_id}")
def api_contract(contract_id: str) -> dict[str, Any]:
    try:
        return get_contract(contract_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="API data contract not found")

@router.post("/analyze")
def analyze_dataset(request: DatasetRequest) -> dict[str, Any]:
    if not request.records:
        raise HTTPException(status_code=400, detail="records cannot be empty")
    frame = pd.json_normalize(request.records)
    return _analyze(frame, request.provider, request.endpoint, request.transform_rules, request.feature_rules)

@router.post("/ingest-and-analyze")
def ingest_and_analyze(request: CredentialedIngestionRequest) -> dict[str, Any]:
    config = APIConfig(
        provider=request.provider, endpoint=request.endpoint, method=request.method,
        auth_method=request.auth_method, credential_name=request.credential_name,
        credential_value=request.credential_value, api_key_header=request.api_key_header,
        api_key_param=request.api_key_param, username=request.username,
        password=request.password, params=request.params, json_body=request.json_body, timeout=request.timeout,
    )
    try:
        result = request_api(config)
        frame = normalize_ingested_data(result["frame"], request.provider, request.endpoint)
        analysis = _analyze(frame, request.provider, request.endpoint, request.transform_rules, request.feature_rules)
        return {
            "status_code": result["status_code"],
            "elapsed_seconds": result["elapsed_seconds"],
            "content_type": result["content_type"],
            "analysis": analysis,
            "security": {
                "credentials_persisted": False,
                "credentials_returned": False,
                "note": "Use a server-side secret manager for scheduled production ingestion."
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Credentialed API ingestion failed: {exc}")

@router.get("/metrics")
def metrics_registry() -> dict[str, Any]:
    return {"metrics":[{"id":i,"name":name,"category":category} for i,name,category in METRICS]}

@router.get("/economic-concepts")
def economic_concepts() -> dict[str, Any]:
    return {"macro": MACRO_CONCEPTS, "micro": MICRO_CONCEPTS}

@router.get("/concept-securities/{concept_name}")
def concept_securities(concept_name: str) -> dict[str, Any]:
    return {"concept":concept_name,"categories":concept_security_categories(concept_name),"securities":securities_for_concept(concept_name)}

@router.get("/research-providers")
def research_providers() -> dict[str, Any]:
    return {"providers":provider_dataframe(),"regulatory_reports":regulatory_dataframe(),"products":product_dataframe()}
