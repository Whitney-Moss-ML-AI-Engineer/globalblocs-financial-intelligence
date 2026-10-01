import pandas as pd
from globalblocs.analytics.economic_cycle import business_cycle_screen
from globalblocs.analytics.risk import maximum_drawdown, sharpe_ratio
from globalblocs.features.financial_features import build_features
from globalblocs.ingestion.source_connectors import get_source, list_sources
from globalblocs.models.model_registry import list_models

def test_source_registry():
    assert get_source("fred").provider == "Federal Reserve FRED"
    assert len(list_sources()) >= 8

def test_features_and_cycle():
    frame = pd.DataFrame({
        "gdp_growth": [1.0, 1.5, 2.0],
        "unemployment": [5.0, 4.8, 4.5],
        "industrial_production": [100, 101, 103],
        "yield_curve_spread": [0.1, 0.2, 0.3],
        "price": [100, 102, 101],
    })
    features = build_features(frame, ["price"])
    assert "price_pct_change" in features.columns
    assert business_cycle_screen(frame)["phase"] in {"Expansion", "Transition", "Late Cycle / Transition"}

def test_risk_and_models():
    prices = pd.Series([100, 110, 105, 115])
    assert maximum_drawdown(prices) < 0
    assert pd.notna(sharpe_ratio(prices))
    assert "deep_learning" in list_models()

from globalblocs.api.production_routes import data_quality, risk, business_cycle, RiskRequest, CycleRequest, RecordsRequest

def test_intelligence_workspace_endpoints():
    quality = data_quality(RecordsRequest(records=[{"date":"2026-01-01","value":100},{"date":"2026-01-02","value":101}]))
    assert quality["profile"]["rows"] == 2
    assert quality["quality_score"] > 0

    risk_result = risk(RiskRequest(prices=[100, 101, 99, 103, 102]))
    assert "maximum_drawdown" in risk_result["risk_summary"]

    cycle = business_cycle(CycleRequest(records=[
        {"gdp_growth":1.0,"unemployment":5.0,"industrial_production":100,"yield_curve_spread":0.2},
        {"gdp_growth":1.5,"unemployment":4.8,"industrial_production":101,"yield_curve_spread":0.3},
        {"gdp_growth":2.0,"unemployment":4.5,"industrial_production":103,"yield_curve_spread":0.4},
    ]))
    assert cycle["phase"] in {"Expansion","Transition","Late Cycle / Transition"}

from globalblocs.finance.metric_knowledge_base import validate_catalog, metric_catalog
from globalblocs.finance.visualization_registry import visualization_profile, compatible_visualizations
from globalblocs.models.evaluation_registry import evaluations_for_visualization

def test_350_metric_knowledge_base():
    result = validate_catalog()
    assert result["valid"] is True
    assert result["count"] == 350
    assert result["unique"] == 350
    assert result["categories"] == {"return_performance": 100, "portfolio_risk": 100, "risk_adjusted": 50, "quantitative_finance": 100}

def test_metric_visualization_profile_is_unrestricted_by_recommendation():
    metric = metric_catalog()[0]
    profile = visualization_profile(metric)
    assert profile["default"]
    assert profile["recommended"]
    assert len(profile["available"]) >= len(profile["recommended"])
    assert "line" in profile["available"]

def test_visualization_compatibility_and_evaluation():
    compatible = compatible_visualizations(["date", "value"], ["value"])
    assert "line" in compatible
    assert "histogram" in compatible
    assert "scatter" not in compatible
    assert "MAE" in evaluations_for_visualization("actual_predicted")
