from fastapi.testclient import TestClient

from globalblocs.api.main import app

client = TestClient(app)


def test_api_health_and_metric_catalog():
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    catalog = client.get("/api/v1/production/metrics/knowledge-base")
    assert catalog.status_code == 200
    body = catalog.json()
    assert body["catalog_validation"]["valid"] is True
    assert body["count"] == 350


def test_api_metric_execution_and_validation():
    executed = client.post(
        "/api/v1/production/metrics/execute/1",
        json={"records": [{"values": [100.0, 110.0]}]},
    )
    assert executed.status_code == 200
    assert executed.json()["status"] == "executed"
    assert abs(executed.json()["value"] - 0.10) < 1e-12

    validation = client.get("/api/v1/production/metrics/validate")
    assert validation.status_code == 200
    assert validation.json()["all_contracts_valid"] is True


def test_api_visualization_and_evaluation_integration():
    viz = client.get("/api/v1/production/metrics/knowledge-base/1/visualization")
    assert viz.status_code == 200
    assert "line" in viz.json()["available"]

    evaluation = client.get("/api/v1/production/evaluations/actual_predicted")
    assert evaluation.status_code == 200
    assert "MAE" in evaluation.json()["evaluation_metrics"]


def test_api_data_quality_risk_and_cycle_workspaces():
    quality = client.post(
        "/api/v1/production/intelligence/data-quality",
        json={"records": [{"value": 100}, {"value": 101}]},
    )
    assert quality.status_code == 200
    assert quality.json()["profile"]["rows"] == 2

    risk = client.post(
        "/api/v1/production/intelligence/risk",
        json={"prices": [100, 101, 99, 103, 102]},
    )
    assert risk.status_code == 200
    assert "maximum_drawdown" in risk.json()["risk_summary"]

    cycle = client.post(
        "/api/v1/production/intelligence/business-cycle",
        json={"records": [
            {"gdp_growth": 1.0, "unemployment": 5.0, "industrial_production": 100, "yield_curve_spread": 0.2},
            {"gdp_growth": 1.5, "unemployment": 4.8, "industrial_production": 101, "yield_curve_spread": 0.3},
            {"gdp_growth": 2.0, "unemployment": 4.5, "industrial_production": 103, "yield_curve_spread": 0.4},
        ]},
    )
    assert cycle.status_code == 200
    assert cycle.json()["phase"] in {"Expansion", "Transition", "Late Cycle / Transition"}
