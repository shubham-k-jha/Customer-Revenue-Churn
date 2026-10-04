from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA


def _prepare(df, date_col, value_col):
    from src.advanced.deep_timeseries import clean_series
    return clean_series(df, date_col, value_col)


def _metrics(actual, pred):
    a=np.asarray(actual,float); p=np.asarray(pred,float)
    mae=mean_absolute_error(a,p); rmse=mean_squared_error(a,p)**.5
    denom=np.where(np.abs(a)<1e-12, np.nan, np.abs(a))
    mape=float(np.nanmean(np.abs((a-p)/denom))*100) if np.any(np.isfinite(denom)) else None
    smape=float(np.mean(2*np.abs(a-p)/(np.abs(a)+np.abs(p)+1e-12))*100)
    return {"mae":float(mae),"rmse":float(rmse),"mape_pct":mape,"smape_pct":smape}


def expanding_backtest(series: pd.Series, horizon: int, initial_train: int, step: int, seasonal_period: int | None = None, models: tuple[str,...] = ("naive","drift","seasonal_naive","ets","arima")) -> dict:
    s=pd.Series(series,dtype=float).dropna().reset_index(drop=True)
    if horizon<1 or step<1 or initial_train<10: raise ValueError("invalid horizon/initial_train/step")
    if initial_train+horizon>len(s): raise ValueError("initial_train + horizon exceeds observations")
    if "seasonal_naive" in models and (seasonal_period is None or seasonal_period<1): raise ValueError("seasonal_period required for seasonal_naive")
    records=[]
    for end in range(initial_train, len(s)-horizon+1, step):
        train=s.iloc[:end]; test=s.iloc[end:end+horizon]
        for name in models:
            try:
                if name=="naive": pred=np.repeat(train.iloc[-1],horizon)
                elif name=="drift":
                    slope=(train.iloc[-1]-train.iloc[0])/(len(train)-1); pred=train.iloc[-1]+slope*np.arange(1,horizon+1)
                elif name=="seasonal_naive":
                    if len(train)<seasonal_period: raise ValueError("insufficient seasonal history")
                    pred=np.resize(train.iloc[-seasonal_period:].to_numpy(),horizon)
                elif name=="ets":
                    kwargs={"trend":"add","initialization_method":"estimated"}
                    if seasonal_period and len(train)>=2*seasonal_period: kwargs.update(seasonal="add",seasonal_periods=seasonal_period)
                    fit=ExponentialSmoothing(train,**kwargs).fit(optimized=True); pred=fit.forecast(horizon).to_numpy()
                elif name=="arima":
                    fit=ARIMA(train,order=(1,1,1),enforce_stationarity=False,enforce_invertibility=False).fit(); pred=fit.forecast(horizon).to_numpy()
                else: raise ValueError(f"unknown model {name}")
                m=_metrics(test,pred); m.update({"origin":int(end),"model":name}); records.append(m)
            except Exception as exc:
                records.append({"origin":int(end),"model":name,"error":str(exc)})
    frame=pd.DataFrame(records)
    successful=frame[frame["error"].isna()] if "error" in frame else frame
    if successful.empty: raise ValueError("No forecasting model completed any backtest")
    summary=(successful.groupby("model")[['mae','rmse','mape_pct','smape_pct']].mean(numeric_only=True).sort_values("rmse").reset_index())
    return {"folds":frame.to_dict(orient="records"),"summary":summary.to_dict(orient="records"),"winner_by_rmse":str(summary.iloc[0]["model"])}
