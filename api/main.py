from datetime import datetime,timezone
import math
from pathlib import Path
import os,joblib,pandas as pd,hmac
from fastapi import FastAPI,HTTPException,UploadFile,File,Header,Request
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from src.production.settings import settings
from src.monitoring.metrics import PredictionMonitor
from src.monitoring.prometheus import REQUESTS,LATENCY,PREDICTIONS
from src.universal.service import profile_uploaded_file
from src.security.guards import validate_upload,validate_read_only_sql
from src.agent.provider import OpenAICompatibleProvider
from src.agent.orchestrator import AnalyticsAgent
from src.advanced.time_series_analysis import TimeSeriesConfig, analyze_time_series
import time
app=FastAPI(title='AI Data Intelligence Platform',version='4.2.0')

def _json_safe(value):
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value

_bundle=None;monitor=PredictionMonitor(settings.prediction_log_path);API_KEY=os.getenv('PLATFORM_API_KEY')
def auth(key):
    if API_KEY and (not key or not hmac.compare_digest(key,API_KEY)): raise HTTPException(401,'Invalid API key')
@app.middleware('http')
async def metrics_middleware(request:Request,call_next):
    start=time.perf_counter(); status=500
    try:
        response=await call_next(request);status=response.status_code;return response
    finally:
        path=request.url.path; REQUESTS.labels(request.method,path,str(status)).inc(); LATENCY.labels(request.method,path).observe(time.perf_counter()-start)
@app.get('/health')
def health():return {'status':'ok','timestamp':datetime.now(timezone.utc).isoformat()}
@app.get('/metrics')
def metrics():return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
@app.get('/model')
def model_info(x_api_key:str|None=Header(default=None)):
    auth(x_api_key);p=Path(settings.model_path)
    if not p.exists():return {'status':'no_model'}
    b=joblib.load(p);return {'status':'ready','task':b.get('task'),'target':b.get('target'),'version':b.get('version'),'features':len(b.get('features',[]))}
@app.get('/monitoring')
def monitoring(x_api_key:str|None=Header(default=None)):auth(x_api_key);return monitor.summary()
@app.post('/data/profile')
async def profile_data(request:Request,file:UploadFile=File(...),x_api_key:str|None=Header(default=None)):
    auth(x_api_key)
    filename=file.filename or 'upload.csv'
    max_bytes=100*1024*1024
    try:
        validate_upload(filename, 0)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    content_length=request.headers.get('content-length')
    if content_length:
        try:
            declared_length=int(content_length)
        except ValueError as exc:
            raise HTTPException(400, 'Invalid Content-Length header') from exc
        if declared_length > max_bytes + 1024*1024:
            raise HTTPException(413, 'Uploaded file exceeds 100 MB limit')
    chunks=[]; total=0
    while True:
        chunk=await file.read(1024*1024)
        if not chunk: break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(413, 'Uploaded file exceeds 100 MB limit')
        chunks.append(chunk)
    contents=b''.join(chunks)
    try:
        validate_upload(filename,len(contents))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    try:return profile_uploaded_file(contents,filename)
    except Exception as exc:raise HTTPException(422,f'Could not read tabular file: {exc}') from exc
class SQLRequest(BaseModel):sql:str
@app.post('/sql/validate')
def sql_validate(req:SQLRequest,x_api_key:str|None=Header(default=None)):
    auth(x_api_key)
    try:return {'valid':True,'sql':validate_read_only_sql(req.sql)}
    except ValueError as exc:raise HTTPException(400,str(exc))

class AgentRequest(BaseModel):
    question: str
    schema_payload: dict

@app.post('/agent/plan')
def agent_plan(req:AgentRequest,x_api_key:str|None=Header(default=None)):
    auth(x_api_key)
    try:
        plan=AnalyticsAgent(OpenAICompatibleProvider()).plan(req.question,req.schema_payload)
        return plan.__dict__
    except Exception as exc:
        raise HTTPException(422,f'Agent planning failed: {exc}') from exc


class TimeSeriesRequest(BaseModel):
    data: list[dict]
    date_col: str
    value_col: str
    seasonal_period: int | None = None
    max_lags: int = 24
    rolling_window: int = 7

@app.post('/analytics/time-series')
def time_series_analysis(req: TimeSeriesRequest, x_api_key: str|None=Header(default=None)):
    auth(x_api_key)
    try:
        result=analyze_time_series(pd.DataFrame(req.data), TimeSeriesConfig(req.date_col,req.value_col,req.seasonal_period,req.max_lags,req.rolling_window))
        # DataFrames are converted to JSON-safe records for the API boundary.
        if hasattr(result.get('rolling'), 'to_dict'):
            result['rolling']=result['rolling'].to_dict(orient='records')
        if hasattr(result.get('decomposition'), 'to_dict'):
            result['decomposition']=result['decomposition'].to_dict(orient='records')
        return _json_safe(result)
    except (KeyError,ValueError) as exc:
        raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422,f'Time-series analysis failed: {exc}') from exc

class DeepTimeSeriesRequest(BaseModel):
    data: list[dict]
    date_col: str
    value_col: str
    frequency: str | None = None
    seasonal_period: int | None = None
    rolling_window: int = 7
    max_lags: int = 24

@app.post('/analytics/time-series/deep')
def deep_time_series_analysis(req: DeepTimeSeriesRequest, x_api_key: str|None=Header(default=None)):
    auth(x_api_key)
    try:
        from src.advanced.deep_timeseries import clean_series, regularize, full_diagnostics
        s=clean_series(pd.DataFrame(req.data),req.date_col,req.value_col)
        if req.frequency:
            s=regularize(s,req.frequency)
        result=full_diagnostics(s,req.seasonal_period,req.rolling_window,req.max_lags)
        result['series']=[{'timestamp':idx.isoformat(),'value':float(v) if math.isfinite(float(v)) else None} for idx,v in s.tail(500).items()]
        return _json_safe(result)
    except (KeyError,ValueError) as exc:
        raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422,f'Deep time-series analysis failed: {exc}') from exc

class ForecastBacktestRequest(BaseModel):
    data: list[dict]
    date_col: str
    value_col: str
    horizon: int = 7
    initial_train: int = 56
    step: int = 7
    seasonal_period: int | None = 7

@app.post('/analytics/forecast/backtest')
def forecast_backtest(req: ForecastBacktestRequest, x_api_key: str|None=Header(default=None)):
    auth(x_api_key)
    try:
        from src.advanced.deep_timeseries import clean_series
        from src.advanced.forecasting_deep import expanding_backtest
        s=clean_series(pd.DataFrame(req.data),req.date_col,req.value_col)
        return expanding_backtest(s,req.horizon,req.initial_train,req.step,req.seasonal_period)
    except (KeyError,ValueError) as exc:
        raise HTTPException(400,str(exc)) from exc
    except Exception as exc:
        raise HTTPException(422,f'Forecast backtest failed: {exc}') from exc
