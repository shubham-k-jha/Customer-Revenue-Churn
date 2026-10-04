from __future__ import annotations
import numpy as np, pandas as pd
from scipy.stats import ks_2samp

def psi(expected,actual,bins=10):
    e=np.asarray(pd.Series(expected).dropna(),float); a=np.asarray(pd.Series(actual).dropna(),float)
    if len(e)<10 or len(a)<10:return 0.0
    quantiles=np.unique(np.quantile(e,np.linspace(0,1,bins+1)))
    if len(quantiles)<3:return 0.0
    cuts=np.r_[-np.inf,quantiles[1:-1],np.inf]
    ep=np.histogram(e,cuts)[0]/len(e); ap=np.histogram(a,cuts)[0]/len(a); ep=np.clip(ep,1e-6,None); ap=np.clip(ap,1e-6,None)
    return float(np.sum((ap-ep)*np.log(ap/ep)))

def ks_drift(expected,actual):
    e=pd.Series(expected).dropna(); a=pd.Series(actual).dropna()
    if len(e)<10 or len(a)<10:return {'statistic':0.0,'p_value':1.0}
    r=ks_2samp(e,a); return {'statistic':float(r.statistic),'p_value':float(r.pvalue)}

def dataframe_drift(reference,current,numeric_columns):
    return {c:{'psi':psi(reference[c],current[c]),'ks':ks_drift(reference[c],current[c])} for c in numeric_columns if c in reference and c in current}
