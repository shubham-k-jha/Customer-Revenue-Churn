from __future__ import annotations
import numpy as np, pandas as pd

def add_safe_date_features(df,date_columns=None):
    out=df.copy()
    for c in date_columns or []:
        if c not in out: continue
        d=pd.to_datetime(out[c],errors='coerce',format='mixed')
        out[f'{c}__year']=d.dt.year; out[f'{c}__month']=d.dt.month; out[f'{c}__quarter']=d.dt.quarter; out[f'{c}__weekday']=d.dt.weekday; out[f'{c}__dayofmonth']=d.dt.day
    return out

def add_ratio_features(df,numerators_denominators=None):
    out=df.copy()
    for name,num,den in numerators_denominators or []:
        if num in out and den in out: out[name]=pd.to_numeric(out[num],errors='coerce')/pd.to_numeric(out[den],errors='coerce').replace(0,np.nan)
    return out
