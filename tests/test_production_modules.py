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
