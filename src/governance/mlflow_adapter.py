from __future__ import annotations

def log_run(experiment, params, metrics, artifacts=None, tracking_uri=None):
    import mlflow
    if tracking_uri: mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)
    with mlflow.start_run() as run:
        if params: mlflow.log_params({str(k):str(v) for k,v in params.items()})
        if metrics: mlflow.log_metrics({str(k):float(v) for k,v in metrics.items() if isinstance(v,(int,float))})
        for path in artifacts or []: mlflow.log_artifact(str(path))
        return run.info.run_id
