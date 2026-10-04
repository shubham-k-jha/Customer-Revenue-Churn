from __future__ import annotations
from pathlib import Path
import json, pandas as pd

def export_powerbi_package(df:pd.DataFrame, output_dir, date_col=None, entity_cols=None, measures=None):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); entity_cols=entity_cols or []
    fact=df.copy(); dims={}
    for c in entity_cols:
        if c in fact: dims[f'dim_{c}']=fact[[c]].drop_duplicates().reset_index(drop=True)
    if date_col and date_col in fact:
        d=pd.to_datetime(fact[date_col],errors='coerce',format='mixed').dropna();
        if not d.empty:
            dims['dim_date']=pd.DataFrame({'date':d.dt.normalize().drop_duplicates().sort_values()})
    fact.to_csv(out/'fact_table.csv',index=False)
    for name,table in dims.items(): table.to_csv(out/f'{name}.csv',index=False)
    rel=[{'from':'fact_table','column':c,'to':f'dim_{c}','to_column':c} for c in entity_cols if c in fact and f'dim_{c}' in dims]
    (out/'relationships.json').write_text(json.dumps(rel,indent=2))
    dax=measures or {'Total Rows':'COUNTROWS(fact_table)'}
    (out/'measures.dax').write_text('\n'.join(f'{k} = {v}' for k,v in dax.items())+'\n')
    (out/'README.md').write_text('# Power BI Package\nImport fact_table and dimension CSVs, then create relationships from relationships.json. Measures are in measures.dax.\n')
    return out
