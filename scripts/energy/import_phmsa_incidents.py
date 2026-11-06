"""Normalize PHMSA incident files using a user-reviewed source column map.

No source column names are assumed. Create the JSON mapping from the data
dictionary accompanying the exact PHMSA release being imported.
"""
from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ALLOWED_FIELDS={
 "source_record_id","report_type","incident_date","report_date","operator_name","operator_id",
 "asset_type","state_code","county_name","city_name","commodity","cause_category",
 "fatalities","injuries","evacuation_count","estimated_property_damage_usd",
 "released_quantity","released_quantity_unit"
}
DATE_FIELDS={"incident_date","report_date"}
INTEGER_FIELDS={"fatalities","injuries","evacuation_count"}
NUMBER_FIELDS={"estimated_property_damage_usd","released_quantity"}

def parse_date(value:str)->str|None:
 value=(value or "").strip()
 if not value:return None
 for fmt in ("%Y-%m-%d","%m/%d/%Y","%m/%d/%y","%Y%m%d"):
  try:return datetime.strptime(value,fmt).date().isoformat()
  except ValueError:pass
 raise ValueError(f"Unsupported date value {value!r}; extend the reviewed parser for this source release.")

def normalize_row(row:dict[str,str],mapping:dict[str,str],dataset:str,source_file:str,source_version:str|None,source_url:str|None)->dict[str,Any]:
 out={}
 for target,column in mapping.items():
  value=(row.get(column) or "").strip()
  if target in DATE_FIELDS:out[target]=parse_date(value)
  elif target in INTEGER_FIELDS:out[target]=int(value) if value else None
  elif target in NUMBER_FIELDS:out[target]=float(value.replace(",","")) if value else None
  else:out[target]=value or None
 record_id=out.get("source_record_id")
 if not record_id:raise ValueError("Mapped source_record_id is missing; configure a unique source ID column.")
 out.update({
  "source_code":"PHMSA","source_dataset":dataset,"source_file_name":source_file,
  "source_file_version":source_version,"source_url":source_url,"raw_record":row
 })
 return out

def load_mapping(path:Path)->dict[str,str]:
 mapping=json.loads(path.read_text(encoding="utf-8"))
 if not isinstance(mapping,dict) or not mapping:raise ValueError("Mapping must contain at least one source-field mapping; provide a non-empty JSON object.")
 mapping.pop("_comment",None)
 if not mapping:raise ValueError("Mapping must contain at least one source-field mapping.")
 unknown=set(mapping)-ALLOWED_FIELDS
 if unknown:raise ValueError("Unsupported normalized fields: "+", ".join(sorted(unknown)))
 if "source_record_id" not in mapping:raise ValueError("Mapping must include source_record_id.")
 if not all(isinstance(k,str) and isinstance(v,str) and v for k,v in mapping.items()):
  raise ValueError("Mapping values must be non-empty source column names.")
 return mapping

def import_file(input_path:Path,mapping_path:Path,output_path:Path,dataset:str,delimiter:str,source_version:str|None,source_url:str|None)->int:
 mapping=load_mapping(mapping_path)
 actual_delimiter="\t" if delimiter=="tab" else "," if delimiter=="comma" else None
 count=0
 with input_path.open("r",encoding="utf-8-sig",newline="") as src, output_path.open("w",encoding="utf-8") as dst:
  sample=src.read(8192);src.seek(0)
  if actual_delimiter is None:
   try:actual_delimiter=csv.Sniffer().sniff(sample,delimiters=",\t").delimiter
   except csv.Error as exc:raise ValueError("Could not detect CSV/TSV delimiter; specify --delimiter.") from exc
  reader=csv.DictReader(src,delimiter=actual_delimiter)
  missing=set(mapping.values())-set(reader.fieldnames or [])
  if missing:raise ValueError("Mapped source columns not found in file: "+", ".join(sorted(missing)))
  for line_number,row in enumerate(reader,start=2):
   try:record=normalize_row(row,mapping,dataset,input_path.name,source_version,source_url)
   except (ValueError,TypeError) as exc:raise ValueError(f"Invalid row at line {line_number}: {exc}") from exc
   dst.write(json.dumps(record,ensure_ascii=False,default=str)+"\n");count+=1
 return count

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--input",required=True,type=Path)
 parser.add_argument("--mapping",required=True,type=Path,help="JSON map from normalized field names to exact source column headers")
 parser.add_argument("--output",required=True,type=Path,help="Output normalized JSONL path")
 parser.add_argument("--dataset",required=True,help="PHMSA source dataset/release identifier")
 parser.add_argument("--delimiter",choices=["auto","tab","comma"],default="auto")
 parser.add_argument("--source-version")
 parser.add_argument("--source-url")
 args=parser.parse_args()
 count=import_file(args.input,args.mapping,args.output,args.dataset,args.delimiter,args.source_version,args.source_url)
 print(json.dumps({"records_written":count,"output":str(args.output),"dataset":args.dataset}))
if __name__=="__main__":main()
