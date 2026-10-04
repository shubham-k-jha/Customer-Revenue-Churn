from __future__ import annotations
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass
class ContractIssue:
    severity:str; rule:str; column:str|None; message:str

def validate_contract(df:pd.DataFrame, contract:dict)->dict:
    issues=[]; required=contract.get('required_columns',[])
    for c in required:
        if c not in df: issues.append(ContractIssue('critical','required_column',c,'required column missing'))
    for c,spec in contract.get('columns',{}).items():
        if c not in df: continue
        if 'dtype' in spec:
            dtype=str(df[c].dtype)
            allowed=spec['dtype'] if isinstance(spec['dtype'],list) else [spec['dtype']]
            if not any(a in dtype for a in allowed): issues.append(ContractIssue('critical','dtype',c,f'{dtype} does not match {allowed}'))
        null_max=spec.get('max_null_rate')
        if null_max is not None and float(df[c].isna().mean())>float(null_max): issues.append(ContractIssue('critical','null_rate',c,'null rate exceeds contract'))
        if spec.get('unique') and not df[c].is_unique: issues.append(ContractIssue('critical','unique',c,'values must be unique'))
        if 'min' in spec:
            x=pd.to_numeric(df[c],errors='coerce');
            if (x.dropna()<spec['min']).any(): issues.append(ContractIssue('critical','min',c,'value below contract minimum'))
        if 'max' in spec:
            x=pd.to_numeric(df[c],errors='coerce');
            if (x.dropna()>spec['max']).any(): issues.append(ContractIssue('critical','max',c,'value above contract maximum'))
        allowed_values=spec.get('allowed_values')
        if allowed_values is not None:
            bad=~df[c].isin(allowed_values) & df[c].notna()
            if bad.any(): issues.append(ContractIssue('critical','allowed_values',c,'contains values outside contract'))
    return {'status':'fail' if any(i.severity=='critical' for i in issues) else 'pass','rows':len(df),'issues':[asdict(i) for i in issues]}
