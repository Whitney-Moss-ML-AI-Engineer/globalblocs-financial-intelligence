from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_energy_dashboard_workspace_is_integrated():
    html=(ROOT/"dashboard"/"index.html").read_text(encoding="utf-8")
    js=(ROOT/"dashboard"/"energy.js").read_text(encoding="utf-8")
    css=(ROOT/"dashboard"/"energy.css").read_text(encoding="utf-8")
    assert 'data-page="energy"' in html
    assert 'id="energy"' in html
    assert 'src="energy.js"' in html
    assert "/api/v1/energy/universe" in js
    assert "/api/v1/energy/market-data" in js
    assert "/api/v1/energy/eia/query" in js
    assert "EIA_API_KEY" in html or "server" in html.lower()
    assert "energy-metrics" in css
