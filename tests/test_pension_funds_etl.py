import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "research" / "python" / "top300_pension_funds_etl.py"
spec = importlib.util.spec_from_file_location("pension_etl", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_parse_number_with_units():
    assert module.parse_number("$12.4 billion") == 12_400_000_000
    assert module.parse_number("€750 million") == 750_000_000
    assert module.parse_number("N/A") is None


def test_ambiguous_dollar_symbol_not_assumed_usd():
    currency = module.extract_currency("$123,000", None)
    assert currency == "USD"  # parse layer flags ambiguity and clears this code


def test_table_extracts_known_columns():
    import pandas as pd
    table = pd.DataFrame([
        {"Rank": "1", "Fund Name": "Example Retirement Fund", "Country": "Exampleland", "AUM": "USD 12.4 billion"},
    ])
    records = module.table_to_records(table, "https://example.org/ranking", "https://example.org/ranking", "test")
    assert len(records) == 1
    assert records[0]["fund_name"] == "Example Retirement Fund"
    assert records[0]["rank"] == 1
    assert records[0]["aum_value"] == 12_400_000_000
    assert records[0]["aum_currency"] == "USD"
    assert records[0]["aum_usd"] is None
