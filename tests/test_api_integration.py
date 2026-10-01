from globalblocs.api.main import app
from globalblocs.api.production_routes import (
    business_cycle,
    data_quality,
    risk,
    CycleRequest,
    RecordsRequest,
    RiskRequest,
)
from globalblocs.finance.metric_execution import execute_metric, validate_all_metrics


def test_api_route_contract_and_health():
    routes = {route.path for route in app.routes}
    assert "/api/v1/health" in routes
    assert "/api/v1/production/metrics/knowledge-base" in routes
    assert "/api/v1/production/metrics/execute/{metric_id}" in routes
    assert "/api/v1/production/metrics/validate" in routes
    assert app.openapi()["info"]["title"] == "GlobalBLOCS Financial Intelligence API"


def test_api_metric_execution_and_validation():
    executed = execute_metric(1, {"values": [100.0, 110.0]})
    assert executed["status"] == "executed"
    assert abs(executed["value"] - 0.10) < 1e-12

    validation = validate_all_metrics({"values": [100.0, 101.0, 103.0]})
    assert validation["all_contracts_valid"] is True
    assert validation["validation_pass_rate"] == 1.0


def test_api_data_quality_risk_and_cycle_workspaces():
    quality = data_quality(RecordsRequest(records=[{"value": 100}, {"value": 101}]))
    assert quality["profile"]["rows"] == 2

    risk_result = risk(RiskRequest(prices=[100, 101, 99, 103, 102]))
    assert "maximum_drawdown" in risk_result["risk_summary"]

    cycle = business_cycle(CycleRequest(records=[
        {"gdp_growth": 1.0, "unemployment": 5.0, "industrial_production": 100, "yield_curve_spread": 0.2},
        {"gdp_growth": 1.5, "unemployment": 4.8, "industrial_production": 101, "yield_curve_spread": 0.3},
        {"gdp_growth": 2.0, "unemployment": 4.5, "industrial_production": 103, "yield_curve_spread": 0.4},
    ]))
    assert cycle["phase"] in {"Expansion", "Transition", "Late Cycle / Transition"}


def test_api_visualization_and_evaluation_route_contracts():
    paths = {route.path for route in app.routes}
    assert "/api/v1/production/metrics/knowledge-base/{metric_id}/visualization" in paths
    assert "/api/v1/production/evaluations/{chart_type}" in paths
