from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def iqr_flags(series, multiplier=1.5):
    if not np.isfinite(multiplier) or multiplier < 0: raise ValueError('multiplier must be finite and non-negative')
    s=pd.Series(series,dtype=float); q1,q3=s.quantile([.25,.75]); iqr=q3-q1
    if not np.isfinite(iqr): raise ValueError("series has no finite spread")
    lo,hi=q1-multiplier*iqr,q3+multiplier*iqr
    return pd.DataFrame({"value":s,"lower":lo,"upper":hi,"is_anomaly":(s<lo)|(s>hi)},index=s.index)


def isolation_flags(df, contamination="auto", random_state=42):
    x=df.select_dtypes(include=[np.number]).copy()
    if x.shape[1]==0: raise ValueError("No numeric features available")
    x=x.replace([np.inf,-np.inf],np.nan).dropna()
    if len(x)<20: raise ValueError("At least 20 complete numeric rows required")
    model=IsolationForest(contamination=contamination,random_state=random_state,n_jobs=-1)
    pred=model.fit_predict(x); score=-model.score_samples(x)
    return {"rows_scored":int(len(x)),"anomaly_count":int((pred==-1).sum()),"anomaly_rate":float((pred==-1).mean()),"scores":pd.DataFrame({"anomaly_score":score,"is_anomaly":pred==-1},index=x.index)}
