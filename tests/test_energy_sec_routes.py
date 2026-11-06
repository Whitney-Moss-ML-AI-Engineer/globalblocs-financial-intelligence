from fastapi.testclient import TestClient
from globalblocs.api.main import app
from globalblocs.api import energy_sec_routes

client=TestClient(app)

def test_sec_company_facts_requires_contact_user_agent(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT",raising=False)
    response=client.get("/api/v1/energy/sec/company/XOM/facts")
    assert response.status_code==503
    assert "SEC_USER_AGENT" in response.json()["detail"]

def test_sec_company_facts_returns_annual_filing_observations(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT","GlobalBLOCS test contact:test@example.com")
    def fake_get_json(url,headers):
        if "company_tickers.json" in url:
            return {"0":{"cik_str":34088,"ticker":"XOM","title":"EXXON MOBIL CORP"}}
        return {"facts":{"us-gaap":{
            "Revenues":{"units":{"USD":[
                {"fy":2024,"fp":"FY","form":"10-K","filed":"2025-02-20","end":"2024-12-31","start":"2024-01-01","val":339000000000,"accn":"0000034088-25-000001"}
            ]}},
            "NetIncomeLoss":{"units":{"USD":[
                {"fy":2024,"fp":"FY","form":"10-K","filed":"2025-02-20","end":"2024-12-31","start":"2024-01-01","val":33000000000,"accn":"0000034088-25-000001"}
            ]}}
        }}}
    monkeypatch.setattr(energy_sec_routes,"_get_json",fake_get_json)
    response=client.get("/api/v1/energy/sec/company/XOM/facts")
    assert response.status_code==200
    payload=response.json()
    assert payload["cik"]=="0000034088"
    assert payload["financials"]["revenue"][0]["value"]==339000000000
    assert payload["financials"]["revenue"][0]["form"]=="10-K"
    assert payload["financials"]["net_income"][0]["period_end"]=="2024-12-31"

def test_sec_company_facts_rejects_invalid_ticker():
    response=client.get("/api/v1/energy/sec/company/!!!/facts")
    assert response.status_code==400
