from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_metric_execution_integration_contract():
    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
    assert "metricExecutionValidation" in html
    assert "/api/v1/production/metrics/validate" in js
    assert "/api/v1/production/metrics/knowledge-base/" in js
    assert "GlobalBLOCSViz.render" in js or "GlobalBLOCS" in js
    assert "\\n" not in js


def test_dashboard_core_assets_exist():
    for path in [
        ROOT / "dashboard" / "index.html",
        ROOT / "dashboard" / "styles.css",
        ROOT / "dashboard" / "app.js",
        ROOT / "dashboard" / "visualization.js",
    ]:
        assert path.exists()
        assert path.stat().st_size > 0
