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
