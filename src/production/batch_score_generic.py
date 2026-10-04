from __future__ import annotations
from pathlib import Path
import joblib, pandas as pd

def score(input_path, output_path, model_path):
    bundle=joblib.load(model_path); df=pd.read_csv(input_path)
    target=bundle.get('target'); drops=set(bundle.get('drop_columns',[]))|({target} if target else set())
    required=list(bundle.get('features', []))
    if not required:
        raise ValueError('Model bundle does not contain a non-empty feature schema')
    missing=[c for c in required if c not in df.columns and c not in drops]
    if missing:
        raise ValueError(f'Input is missing required model features: {missing}')
    X=df.drop(columns=list(drops),errors='ignore').reindex(columns=required)
    model=bundle['model']; task=bundle.get('task')
    out=df.copy()
    if task=='classification':
        if hasattr(model,'predict_proba'): out['prediction_probability']=model.predict_proba(X)[:,1] if len(model.classes_)==2 else model.predict_proba(X).max(axis=1)
        out['prediction']=model.predict(X)
    else: out['prediction']=model.predict(X)
    Path(output_path).parent.mkdir(parents=True,exist_ok=True); out.to_csv(output_path,index=False); return Path(output_path)
