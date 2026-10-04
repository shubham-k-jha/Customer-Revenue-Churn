from __future__ import annotations
import argparse, json, pandas as pd
from src.governance.data_contracts import validate_contract
from src.bi.powerbi_export import export_powerbi_package

def main():
 p=argparse.ArgumentParser(description='V4 production utilities'); sub=p.add_subparsers(dest='cmd',required=True)
 c=sub.add_parser('contract'); c.add_argument('--input',required=True); c.add_argument('--contract',required=True)
 b=sub.add_parser('powerbi'); b.add_argument('--input',required=True); b.add_argument('--output',required=True); b.add_argument('--date'); b.add_argument('--entities',nargs='*')
 a=p.parse_args()
 if a.cmd=='contract':
  df=pd.read_csv(a.input); contract=json.load(open(a.contract)); print(json.dumps(validate_contract(df,contract),indent=2))
 else: export_powerbi_package(pd.read_csv(a.input),a.output,a.date,a.entities); print(a.output)
if __name__=='__main__': main()
