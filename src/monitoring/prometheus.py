from prometheus_client import Counter, Histogram, Gauge
REQUESTS=Counter('platform_http_requests_total','HTTP requests',['method','path','status'])
LATENCY=Histogram('platform_http_request_seconds','HTTP request latency',['method','path'])
PREDICTIONS=Counter('platform_predictions_total','Predictions served')
DRIFT_PSI=Gauge('platform_feature_drift_psi','Latest feature PSI',['feature'])
