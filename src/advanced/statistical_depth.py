from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests


def normality(values, method="auto"):
    x=np.asarray(values,float); x=x[np.isfinite(x)]
    if len(x)<3: raise ValueError("At least 3 finite observations required")
    if method=="auto": method="shapiro" if len(x)<=5000 else "normaltest"
    if method=="shapiro": stat,p=stats.shapiro(x)
    elif method=="normaltest": stat,p=stats.normaltest(x)
    else: raise ValueError("method must be auto, shapiro or normaltest")
    return {"method":method,"statistic":float(stat),"p_value":float(p),"normal_5pct":bool(p>=.05),"n":int(len(x))}


def correlation_matrix(df: pd.DataFrame, method="spearman"):
    if method not in {"pearson","spearman","kendall"}: raise ValueError("invalid correlation method")
    numeric=df.select_dtypes(include=[np.number])
    if numeric.shape[1]<2: raise ValueError("At least two numeric columns required")
    return numeric.corr(method=method)


def pairwise_correlations(df: pd.DataFrame, method="spearman"):
    x=df.select_dtypes(include=[np.number]); cols=list(x.columns); rows=[]
    for i,a in enumerate(cols):
        for b in cols[i+1:]:
            xa=x[a]; xb=x[b]; mask=xa.notna()&xb.notna()
            if mask.sum()<3: continue
            if method=="pearson": r,p=stats.pearsonr(xa[mask],xb[mask])
            elif method=="kendall": r,p=stats.kendalltau(xa[mask],xb[mask])
            else: r,p=stats.spearmanr(xa[mask],xb[mask])
            rows.append({"feature_a":a,"feature_b":b,"correlation":float(r),"p_value":float(p),"n":int(mask.sum())})
    out=pd.DataFrame(rows)
    if out.empty: return out
    out["q_value_bh"]=multipletests(out["p_value"],method="fdr_bh")[1]
    out["significant_fdr_5pct"]=out["q_value_bh"]<.05
    return out.sort_values("q_value_bh").reset_index(drop=True)


def bootstrap_ci(values, statistic="mean", n_boot=5000, seed=42, alpha=.05):
    x=np.asarray(values,float); x=x[np.isfinite(x)]
    if len(x)<2: raise ValueError("At least 2 observations required")
    if n_boot<100: raise ValueError("n_boot must be >=100")
    if statistic=="mean": fn=np.mean
    elif statistic=="median": fn=np.median
    elif statistic=="std": fn=lambda z: np.std(z,ddof=1)
    else: raise ValueError("statistic must be mean, median or std")
    rng=np.random.default_rng(seed); samples=rng.choice(x,(n_boot,len(x)),replace=True); vals=np.apply_along_axis(fn,1,samples); lo,hi=np.quantile(vals,[alpha/2,1-alpha/2])
    return {"estimate":float(fn(x)),"ci_low":float(lo),"ci_high":float(hi),"alpha":float(alpha),"n_boot":int(n_boot)}
