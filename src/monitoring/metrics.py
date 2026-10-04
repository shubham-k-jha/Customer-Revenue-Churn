import json
from pathlib import Path
import pandas as pd, numpy as np
class PredictionMonitor:
    def __init__(self,log_path='artifacts/prediction_log.parquet'):
        self.path=Path(log_path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def log(self,rows):
        new=pd.DataFrame(rows)
        if new.empty:return
        if self.path.exists():
            try: old=pd.read_parquet(self.path); new=pd.concat([old,new],ignore_index=True)
            except Exception: pass
        try:new.to_parquet(self.path,index=False)
        except Exception:new.to_csv(self.path.with_suffix('.csv'),index=False)
    def summary(self):
        if not self.path.exists(): return {'predictions':0}
        try: df=pd.read_parquet(self.path)
        except Exception:
            p=self.path.with_suffix('.csv'); df=pd.read_csv(p) if p.exists() else pd.DataFrame()
        if df.empty:return {'predictions':0}
        return {'predictions':int(len(df)),'mean_probability':float(df['probability'].mean()) if 'probability' in df else None,'high_risk_rate':float((df['risk_band']=='High').mean()) if 'risk_band' in df else None,'latest_timestamp':str(df['timestamp'].max()) if 'timestamp' in df else None}

def population_stability_index(expected,actual,bins=10):
    e=np.asarray(expected,dtype=float);a=np.asarray(actual,dtype=float)
    if len(e)<10 or len(a)<10:return 0.0
    cuts=np.unique(np.quantile(e,np.linspace(0,1,bins+1)))
    if len(cuts)<3:return 0.0
    ep=np.histogram(e,cuts)[0]/len(e);ap=np.histogram(a,cuts)[0]/len(a);ep=np.clip(ep,1e-6,None);ap=np.clip(ap,1e-6,None)
    return float(np.sum((ap-ep)*np.log(ap/ep)))
