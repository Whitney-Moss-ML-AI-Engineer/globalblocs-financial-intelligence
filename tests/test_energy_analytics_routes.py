from fastapi.testclient import TestClient
from globalblocs.api.main import app
from globalblocs.api import energy_analytics_routes

client=TestClient(app)

def test_company_analytics_derives_fcf_margins_and_leverage(monkeypatch):
    def fake_company_facts(ticker):
        return {"ticker":ticker,"company_name":"Example Energy","financials":{
            "revenue":[
                {"period_end":"2024-12-31","fiscal_year":2024,"value":200,"accession_number":"acc-24"},
                {"period_end":"2023-12-31","fiscal_year":2023,"value":160,"accession_number":"acc-23"}],
            "operating_income":[{"period_end":"2024-12-31","value":30}],
            "net_income":[{"period_end":"2024-12-31","value":20}],
            "assets":[{"period_end":"2024-12-31","value":250}],
            "cash_from_operations":[{"period_end":"2024-12-31","value":40}],
            "capital_expenditures":[{"period_end":"2024-12-31","value":15}],
            "long_term_debt":[{"period_end":"2024-12-31","value":60}],
            "equity":[{"period_end":"2024-12-31","value":100}],
            "cash_and_equivalents":[{"period_end":"2024-12-31","value":10}]
        }}
    monkeypatch.setattr(energy_analytics_routes,"company_facts",fake_company_facts)
    response=client.get("/api/v1/energy/analytics/company/XOM")
    assert response.status_code==200
    period=response.json()["periods"][0]
    assert period["revenue_growth"]==0.25
    assert period["operating_margin"]==0.15
    assert period["free_cash_flow"]==25
    assert period["free_cash_flow_margin"]==0.125
    assert period["net_debt"]==50
    assert period["long_term_debt_to_assets"]==0.24

def test_company_analytics_keeps_missing_facts_null(monkeypatch):
    monkeypatch.setattr(energy_analytics_routes,"company_facts",lambda ticker:{"ticker":ticker,"financials":{"revenue":[{"period_end":"2024-12-31","value":100}]}})
    response=client.get("/api/v1/energy/analytics/company/ABC")
    assert response.status_code==200
    period=response.json()["periods"][0]
    assert period["operating_margin"] is None
    assert period["free_cash_flow"] is None
