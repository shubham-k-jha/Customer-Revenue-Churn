from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
class ExperimentTracker:
    def __init__(self,path='reports/experiments.jsonl'): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def log(self,experiment,params,metrics,artifacts=None):
        record={'run_id':hashlib.sha256(f"{experiment}|{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],'timestamp':datetime.now(timezone.utc).isoformat(),'experiment':experiment,'params':params,'metrics':metrics,'artifacts':artifacts or {}}
        with self.path.open('a',encoding='utf-8') as f: f.write(json.dumps(record,default=str)+'\n')
        return record

def try_mlflow_log(experiment,params,metrics,artifacts=None):
    try:
        import mlflow
        mlflow.set_experiment(experiment)
        with mlflow.start_run():
            mlflow.log_params(params); mlflow.log_metrics({k:float(v) for k,v in metrics.items() if isinstance(v,(int,float))})
            for p in artifacts or []: mlflow.log_artifact(str(p))
        return True
    except Exception:
        return False
