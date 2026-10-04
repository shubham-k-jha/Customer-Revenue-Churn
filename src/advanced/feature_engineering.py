from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer


def numeric_transform_candidates(df):
    rows=[]
    for c in df.select_dtypes(include=[np.number]).columns:
        s=pd.to_numeric(df[c],errors="coerce").dropna()
        if len(s)<3: continue
        skew=float(s.skew())
        rows.append({"column":c,"skewness":skew,"suggest_log1p":bool((s>=0).all() and abs(skew)>1),"suggest_yeojohnson":bool(abs(skew)>1)})
    return pd.DataFrame(rows)


def safe_ratios(df, numerator, denominator, name=None, eps=1e-12):
    if numerator not in df or denominator not in df: raise KeyError("ratio columns not found")
    n=pd.to_numeric(df[numerator],errors="coerce"); d=pd.to_numeric(df[denominator],errors="coerce")
    out=n/d.where(d.abs()>eps,np.nan)
    return out.rename(name or f"{numerator}_per_{denominator}")


def winsorize(series, lower=.01, upper=.99):
    if not 0<=lower<upper<=1: raise ValueError("invalid winsorization quantiles")
    s=pd.Series(series,dtype=float); lo,hi=s.quantile([lower,upper]); return s.clip(lo,hi)
