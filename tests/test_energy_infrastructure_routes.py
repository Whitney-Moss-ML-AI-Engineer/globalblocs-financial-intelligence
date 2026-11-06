from fastapi.testclient import TestClient
from globalblocs.api.main import app
from globalblocs.api import energy_infrastructure_routes

client=TestClient(app)

def test_infrastructure_catalog_lists_public_phmsa_sources_and_access_limits():
    response=client.get("/api/v1/energy/infrastructure/sources")
    assert response.status_code==200
    payload=response.json()
    ids={x["id"] for x in payload["phmsa_sources"]}
    assert {"pipeline_incidents","pipeline_mileage","operator_directory","lng_facilities","flagged_incidents"} <= ids
    assert "restricted" in payload["security_notice"].lower()
    assert all(x["url"].startswith("https://") for x in payload["phmsa_sources"])

def test_ferc_assets_requires_server_side_key(monkeypatch):
    monkeypatch.delenv("FERC_API_KEY",raising=False)
    response=client.get("/api/v1/energy/infrastructure/ferc/assets")
    assert response.status_code==503
    assert "FERC_API_KEY" in response.json()["detail"]

def test_ferc_assets_uses_private_header_and_returns_provider_catalog(monkeypatch):
    monkeypatch.setenv("FERC_API_KEY","test-secret")
    def fake_get(path):
        assert path=="/data-assets/"
        assert energy_infrastructure_routes._ferc_headers()["X-Api-Key"]=="test-secret"
        return {"data":[{"id":"42","name":"Form 6"}]}
    monkeypatch.setattr(energy_infrastructure_routes,"_ferc_get",fake_get)
    response=client.get("/api/v1/energy/infrastructure/ferc/assets")
    assert response.status_code==200
    assert response.json()["catalog"]["data"][0]["id"]=="42"

def test_ferc_dataset_details_rejects_invalid_identifier():
    response=client.get("/api/v1/energy/infrastructure/ferc/datasets/../../etc/passwd/details")
    assert response.status_code in (404,422)
