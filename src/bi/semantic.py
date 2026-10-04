from __future__ import annotations
import pandas as pd

def build_star_schema(df, date_col=None, entity_cols=None):
    entity_cols=entity_cols or []
    fact=df.copy(); dims={}
    for c in entity_cols:
        if c in fact:
            dims[f'dim_{c}']=fact[[c]].drop_duplicates().reset_index(drop=True)
    if date_col and date_col in fact:
        d=pd.to_datetime(fact[date_col],errors='coerce',format='mixed'); dims['dim_date']=pd.DataFrame({'date':d.dropna().drop_duplicates()})
    return {'fact_table':fact,'dimensions':dims}
