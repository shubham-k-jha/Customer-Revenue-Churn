from __future__ import annotations
import numpy as np
import pandas as pd

def _events(values):
    raw=pd.Series(values)
    if pd.api.types.is_bool_dtype(raw): return raw.astype(bool)
    numeric=pd.to_numeric(raw,errors='coerce')
    if numeric.isna().any() or not numeric.isin([0,1]).all():
        raise ValueError('events must contain only 0/1 or boolean values')
    return numeric.astype(bool)

def kaplan_meier(durations, events):
    t=pd.to_numeric(pd.Series(durations),errors='coerce')
    e=_events(events)
    if len(t)!=len(e): raise ValueError('durations and events must have equal length')
    m=t.notna() & np.isfinite(t.to_numpy())
    t=t[m].to_numpy(float); e=e[m].to_numpy(bool)
    if len(t)==0: raise ValueError('No valid survival observations')
    if (t<0).any(): raise ValueError('durations cannot be negative')
    order=np.argsort(t,kind='mergesort'); t=t[order]; e=e[order]
    unique=np.unique(t); at_risk=[]; events_count=[]; survival=[]; s=1.0
    for ti in unique:
        risk=int((t>=ti).sum()); ev=int(e[t==ti].sum())
        at_risk.append(risk); events_count.append(ev)
        if risk: s*=max(0.0,1.0-ev/risk)
        survival.append(s)
    return pd.DataFrame({'time':unique,'at_risk':at_risk,'events':events_count,'survival_probability':survival})

def retention_curve(durations, events, horizons=None):
    km=kaplan_meier(durations,events)
    if horizons is None: h=np.sort(km['time'].unique())
    else:
        h=np.asarray(horizons,float).reshape(-1)
        if h.size and (not np.all(np.isfinite(h)) or (h<0).any()): raise ValueError('horizons must be finite and non-negative')
        h=np.sort(h)
    vals=[]
    for x in h:
        prior=km[km.time<=x]
        vals.append(float(prior.survival_probability.iloc[-1]) if not prior.empty else 1.0)
    return pd.DataFrame({'time':h,'retention_probability':vals})
