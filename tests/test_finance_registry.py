from globalblocs.finance.api_contracts import list_contracts, get_contract
from globalblocs.finance.investment_metrics import METRICS

def test_api_contract_registry_and_metrics():
    contracts=list_contracts()
    assert len(contracts)>=7
    assert get_contract("custom-credentialed")["auth"]
    assert len(METRICS)==50
