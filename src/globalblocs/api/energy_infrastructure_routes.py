"""Public energy infrastructure source catalog and FERC metadata adapter.

PHMSA NPMS detailed pipeline GIS is access-controlled. This module links only
public PHMSA incident/operator summary sources and does not expose restricted
pipeline geometry or operationally sensitive facility details.
"""
from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from typing import Any
import requests
from fastapi import APIRouter, HTTPException, Path

router=APIRouter(prefix="/api/v1/energy/infrastructure",tags=["energy-infrastructure"])
FERC_BASE="https://api.ferc.gov/v1"
TIMEOUT=30
PHMSA_SOURCES=[
 {"id":"pipeline_incidents","name":"Pipeline incident and accident reports","agency":"PHMSA","coverage":"Natural gas transmission, distribution and gathering; hazardous liquids; LNG; incident causes and consequences","format":"ZIP / tab-delimited data","access":"public_download","url":"https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data","limitations":"Download and inspect the source data dictionary before ingestion. Incident reporting thresholds and definitions have changed over time."},
 {"id":"pipeline_mileage","name":"Pipeline mileage and facilities summaries","agency":"PHMSA","coverage":"Public summary statistics for pipeline mileage and facilities","format":"Download / public summary","access":"public_summary","url":"https://www.phmsa.dot.gov/data-and-statistics/pipeline/data-and-statistics-overview","limitations":"Detailed NPMS pipeline GIS data is restricted; do not attempt to retrieve it from the public dashboard."},
 {"id":"operator_directory","name":"Pipeline operator directory","agency":"PHMSA / NPMS","coverage":"Public operator lookup and high-level pipeline information","format":"Public web directory","access":"public_web","url":"https://www.npms.phmsa.dot.gov/GeneralPublic","limitations":"Public map and operator summaries are not a substitute for restricted NPMS datasets."},
 {"id":"lng_facilities","name":"LNG plants and county summaries","agency":"PHMSA / NPMS","coverage":"Public LNG plant summary information","format":"Download / public summary","access":"public_summary","url":"https://www.npms.phmsa.dot.gov/GeneralPublic","limitations":"Use public summaries only; facility-specific detailed GIS may be restricted."},
 {"id":"flagged_incidents","name":"Pipeline incident flagged files and trends","agency":"PHMSA","coverage":"Serious/significant incidents and trend reporting","format":"ZIP download","access":"public_download","url":"https://www.phmsa.dot.gov/data-and-statistics/pipeline/data-and-statistics-overview","limitations":"Review flagged-file definitions and the data dictionary; do not combine with all-incident counts without reconciling scope."}
]
FERC_DATA_ASSETS_URL=FERC_BASE+"/data-assets/"
def _ferc_headers():
 key=os.getenv("FERC_API_KEY")
 if not key:
  raise HTTPException(503,"FERC_API_KEY is not configured. Register for a FERC Data API key and store it in the server environment.")
 return {"X-Api-Key":key,"Accept":"application/json","User-Agent":"GlobalBLOCS Financial Intelligence"}
def _ferc_get(path:str)->Any:
 try:
  response=requests.get(FERC_BASE+path,headers=_ferc_headers(),timeout=TIMEOUT)
  response.raise_for_status()
  return response.json()
 except HTTPException:
  raise
 except requests.HTTPError as exc:
  status=exc.response.status_code if exc.response is not None else 502
  raise HTTPException(502,f"FERC Data API request failed (upstream status {status}).") from exc
 except requests.RequestException as exc:
  raise HTTPException(502,"Could not reach the FERC Data API. Retry later.") from exc
 except ValueError as exc:
  raise HTTPException(502,"FERC returned a non-JSON response.") from exc

@router.get("/sources")
def infrastructure_sources():
 return {"retrieved_at":datetime.now(timezone.utc).isoformat(),"phmsa_sources":PHMSA_SOURCES,
  "ferc":{"name":"FERC Data API","catalog_url":"https://data.ferc.gov/datacatalog/","developer_docs":"https://data.ferc.gov/developer/gettingstarted/","access":"api_key_required","description":"Discover dataset IDs dynamically through the data-assets endpoint; IDs may change."},
  "security_notice":"Only public PHMSA summaries and reports are linked. Detailed NPMS pipeline GIS access is restricted to eligible government agencies and pipeline operators."}

@router.get("/ferc/assets")
def ferc_assets():
 payload=_ferc_get("/data-assets/")
 return {"provider":"Federal Energy Regulatory Commission","retrieved_at":datetime.now(timezone.utc).isoformat(),"catalog":payload,"source_url":"https://data.ferc.gov/datacatalog/","note":"Dataset identifiers are provider-managed and may change; use returned IDs and metadata rather than hard-coded IDs."}

@router.get("/ferc/datasets/{dataset_id}/details")
def ferc_dataset_details(dataset_id:str=Path(pattern="^[A-Za-z0-9_-]{1,80}$")):
 payload=_ferc_get(f"/dataset/{dataset_id}/details/")
 return {"provider":"Federal Energy Regulatory Commission","dataset_id":dataset_id,"retrieved_at":datetime.now(timezone.utc).isoformat(),"details":payload,"source_url":"https://data.ferc.gov/datacatalog/"}
