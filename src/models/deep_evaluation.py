from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score, balanced_accuracy_score, brier_score_loss,
    f1_score, precision_recall_curve, precision_score, recall_score,
    roc_auc_score,
)


def classification_report_deep(y_true, proba, threshold=.5, positive_label=1):
    y=np.asarray(y_true); p=np.asarray(proba,dtype=float)
    if len(np.unique(y)) != 2: raise ValueError('classification_report_deep requires a binary target')
    if p.ndim != 1 or len(y)!=len(p): raise ValueError("y_true and proba must be equal-length 1D arrays")
    if not np.all(np.isfinite(p)) or np.any((p<0)|(p>1)): raise ValueError("probabilities must be finite and in [0,1]")
    if not 0<threshold<1: raise ValueError("threshold must be between 0 and 1")
    pred=(p>=threshold).astype(int)
    result={"threshold":float(threshold),"precision":float(precision_score(y,pred,pos_label=positive_label,zero_division=0)),"recall":float(recall_score(y,pred,pos_label=positive_label,zero_division=0)),"f1":float(f1_score(y,pred,pos_label=positive_label,zero_division=0)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),"brier":float(brier_score_loss(y,p))}
    if len(np.unique(y))==2:
        result["roc_auc"]=float(roc_auc_score(y,p)); result["pr_auc"]=float(average_precision_score(y,p))
    return result


def optimize_threshold(y_true, proba, metric="f1", min_recall=None, min_precision=None, grid=None):
    grid=np.asarray(grid if grid is not None else np.linspace(.05,.95,181),dtype=float)
    rows=[]
    for t in grid:
        r=classification_report_deep(y_true,proba,float(t));
        if min_recall is not None and r["recall"]<min_recall: continue
        if min_precision is not None and r["precision"]<min_precision: continue
        rows.append(r)
    if not rows: raise ValueError("No threshold satisfies the requested constraints")
    if metric not in rows[0]: raise ValueError(f"Unknown threshold metric {metric!r}")
    return max(rows,key=lambda r:(r[metric],-abs(r["threshold"]-.5)))


def calibration_diagnostics(y_true, proba, bins=10):
    y=np.asarray(y_true); p=np.asarray(proba,dtype=float)
    if bins<2: raise ValueError("bins must be >=2")
    if len(np.unique(y))!=2: raise ValueError("Calibration requires binary targets")
    frac,mean=calibration_curve(y,p,n_bins=bins,strategy="quantile")
    return {"brier":float(brier_score_loss(y,p)),"mean_predicted":mean.tolist(),"observed_frequency":frac.tolist(),"bins_returned":int(len(frac))}


def decision_curve(y_true, proba, thresholds=None):
    y=np.asarray(y_true).astype(int); p=np.asarray(proba,float)
    if len(y)!=len(p): raise ValueError("length mismatch")
    thresholds=np.asarray(thresholds if thresholds is not None else np.arange(.05,.96,.05),float)
    n=len(y); prevalence=float(y.mean()); rows=[]
    for t in thresholds:
        if not 0<t<1: continue
        pred=p>=t; tp=np.sum(pred & (y==1)); fp=np.sum(pred & (y==0))
        nb=float(tp/n - fp/n*(t/(1-t)))
        treat_all=prevalence-(1-prevalence)*(t/(1-t))
        rows.append({"threshold":float(t),"net_benefit_model":nb,"net_benefit_treat_all":float(treat_all),"net_benefit_treat_none":0.0})
    return pd.DataFrame(rows)
