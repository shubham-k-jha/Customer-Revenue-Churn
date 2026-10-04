from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from src.universal.io import read_table, list_excel_sheets
from src.universal.profile import profile_dataframe, rank_target_candidates
from src.universal.model import train_generic


def main():
    parser = argparse.ArgumentParser(description="Universal tabular data profiler and ML runner")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("profile"); p.add_argument("path"); p.add_argument("--sheet", default=0)
    t = sub.add_parser("train"); t.add_argument("path"); t.add_argument("--target", required=True); t.add_argument("--task", choices=["classification", "regression"]); t.add_argument("--drop", nargs="*", default=[]); t.add_argument("--artifact", default="artifacts/generic_model_bundle.joblib"); t.add_argument("--date-column"); t.add_argument("--sheet", default=0)
    args = parser.parse_args()
    if args.cmd == "profile":
        sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
        df = read_table(args.path, sheet)
        result = profile_dataframe(df); result["target_candidates"] = rank_target_candidates(df)
        result["excel_sheets"] = list_excel_sheets(args.path)
        print(json.dumps(result, indent=2, default=str))
    else:
        sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
        df = read_table(args.path, sheet)
        print(json.dumps(train_generic(df, args.target, args.task, args.drop, args.artifact, args.date_column), indent=2, default=str))

if __name__ == "__main__": main()
