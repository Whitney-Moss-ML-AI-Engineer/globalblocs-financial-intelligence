from fastapi.testclient import TestClient
from globalblocs.api.main import app

client = TestClient(app)

def test_energy_company_universe_and_segment_filter():
    response=client.get("/api/v1/energy/universe")
    assert response.status_code==200
    payload=response.json()
    assert payload["count"]>=40
    assert any(x["ticker"]=="SR" for x in payload["companies"])
    assert any(x["ticker"]=="AEE" for x in payload["companies"])
    midstream=client.get("/api/v1/energy/universe?segment=midstream").json()
    assert midstream["count"]>0
    assert all(x["segment"]=="midstream" for x in midstream["companies"])

def test_energy_catalog_contains_commodity_and_eia_sources():
    payload=client.get("/api/v1/energy/catalog").json()
    assert {x["id"] for x in payload["commodities"]}>={"wti","brent","henry_hub"}
    assert {x["id"] for x in payload["eia_datasets"]}>={"petroleum_spot_prices","natural_gas_storage"}

def test_eia_query_requires_server_side_key(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY",raising=False)
    response=client.post("/api/v1/energy/eia/query",json={"dataset_id":"petroleum_spot_prices"})
    assert response.status_code==503
    assert "EIA_API_KEY" in response.json()["detail"]

def test_eia_query_rejects_unknown_dataset():
    response=client.post("/api/v1/energy/eia/query",json={"dataset_id":"https://example.com"})
    assert response.status_code==400

def test_energy_market_data_rejects_more_than_30_symbols():
    response=client.get("/api/v1/energy/market-data?symbols="+",".join([f"S{i}" for i in range(31)]))
    assert response.status_code==400
