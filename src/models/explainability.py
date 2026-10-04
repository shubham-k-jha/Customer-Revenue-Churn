from __future__ import annotations
import numpy as np, pandas as pd

def permutation_importance_table(model,X,y,n_repeats=5,random_state=42):
    from sklearn.inspection import permutation_importance
    if len(X)==0: raise ValueError('X must not be empty')
    r=permutation_importance(model,X,y,n_repeats=n_repeats,random_state=random_state,n_jobs=-1)
    names=list(X.columns); return pd.DataFrame({'feature':names,'importance_mean':r.importances_mean,'importance_std':r.importances_std}).sort_values('importance_mean',ascending=False).reset_index(drop=True)

def prediction_explanation(model,row:pd.DataFrame):
    if len(row)!=1: raise ValueError('row must contain exactly one observation')
    if hasattr(model,'predict_proba'): return {'prediction':model.predict(row).tolist()[0],'probability':model.predict_proba(row).max(axis=1).tolist()[0]}
    return {'prediction':float(model.predict(row)[0])}
