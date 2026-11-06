import json
from pathlib import Path
import pytest
from scripts.energy.import_phmsa_incidents import import_file, load_mapping, normalize_row

def test_normalize_phmsa_row_uses_explicit_mapping_and_preserves_raw_fields():
    row={"INC_NO":"12345","EVENT_DATE":"2024-01-05","STATE":"MO","FATAL":"1","PROP_DMG":"12500"}
    mapping={"source_record_id":"INC_NO","incident_date":"EVENT_DATE","state_code":"STATE","fatalities":"FATAL","estimated_property_damage_usd":"PROP_DMG"}
    out=normalize_row(row,mapping,"gas_transmission_incidents","source.tsv","2024-09","https://example.gov/source")
    assert out["source_record_id"]=="12345"
    assert out["incident_date"]=="2024-01-05"
    assert out["fatalities"]==1
    assert out["estimated_property_damage_usd"]==12500.0
    assert out["raw_record"]==row

def test_import_phmsa_tsv_writes_normalized_jsonl(tmp_path):
    source=tmp_path/"incidents.tsv"
    source.write_text("INC_NO\tEVENT_DATE\tSTATE\n123\t01/05/2024\tMO\n",encoding="utf-8")
    mapping=tmp_path/"mapping.json"
    mapping.write_text(json.dumps({"source_record_id":"INC_NO","incident_date":"EVENT_DATE","state_code":"STATE"}),encoding="utf-8")
    output=tmp_path/"normalized.jsonl"
    count=import_file(source,mapping,output,"liquid_incidents","auto","release-2024",None)
    records=[json.loads(x) for x in output.read_text().splitlines()]
    assert count==1
    assert records[0]["incident_date"]=="2024-01-05"
    assert records[0]["source_dataset"]=="liquid_incidents"

def test_import_rejects_unmapped_source_headers(tmp_path):
    source=tmp_path/"source.csv";source.write_text("ID,WHEN\n1,2024-01-01\n")
    mapping=tmp_path/"mapping.json";mapping.write_text(json.dumps({"source_record_id":"NOT_A_COLUMN"}))
    with pytest.raises(ValueError,match="Mapped source columns not found"):
        import_file(source,mapping,tmp_path/"out.jsonl","dataset","auto",None,None)

def test_import_rejects_missing_source_record_identifier(tmp_path):
    bad=tmp_path/"bad.json"
    bad.write_text("{}")
    with pytest.raises(ValueError,match="Mapping must contain at least one"):
        load_mapping(bad)
