from __future__ import annotations
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


def _series(df, date_col, value_col):
    if date_col not in df or value_col not in df: raise KeyError(f'{date_col}/{value_col} must exist')
    x=df[[date_col,value_col]].copy(); x[date_col]=pd.to_datetime(x[date_col],errors='coerce',utc=True,format='mixed'); x[value_col]=pd.to_numeric(x[value_col],errors='coerce')
    x=x.dropna().groupby(date_col,as_index=False)[value_col].sum().sort_values(date_col)
    if len(x)<20: raise ValueError('At least 20 observations are required for forecasting')
    return x


def seasonal_naive_backtest(df,date_col,value_col,horizon=7,season=7):
    if horizon<1 or season<1: raise ValueError('horizon and season must be positive')
    x=_series(df,date_col,value_col)
    if len(x)<season+horizon+5: raise ValueError('Not enough observations for seasonal backtest')
    train=x.iloc[:-horizon].copy(); test=x.iloc[-horizon:]
    if len(train)<season: raise ValueError('Not enough training observations for seasonal baseline')
    pred=np.resize(train[value_col].to_numpy()[-season:],horizon)
    return {'metrics':{'mae':float(mean_absolute_error(test[value_col],pred)),'rmse':float(mean_squared_error(test[value_col],pred)**0.5)},'actual':test.reset_index(drop=True),'predicted':pd.Series(pred,name=value_col)}


def backtest_ridge(df,date_col,value_col,horizon=7,lags=14):
    """Evaluate a lag model with a genuinely recursive multi-step forecast.

    The previous implementation constructed lag features for the held-out horizon
    from the observed future values. That is valid for one-step-ahead scoring but
    leaks future observations when horizon > 1. This implementation predicts one
    step, appends that prediction to the history, and uses it for the next step.
    """
    if horizon<1 or lags<1: raise ValueError('horizon and lags must be positive')
    x=_series(df,date_col,value_col)
    if len(x)<=horizon+lags+10: raise ValueError('Not enough observations for lag model')
    values=x[value_col].to_numpy(dtype=float)
    train_values=values[:-horizon]
    test_values=values[-horizon:]
    cols=[f'lag_{i}' for i in range(1,lags+1)]
    rows=[]
    for end in range(lags,len(train_values)):
        rows.append({f'lag_{i}':train_values[end-i] for i in range(1,lags+1)} | {'target':train_values[end]})
    train_frame=pd.DataFrame(rows)
    model=Ridge(alpha=1.0).fit(train_frame[cols],train_frame['target'])
    history=list(train_values)
    pred=[]
    for _ in range(horizon):
        features=pd.DataFrame([{f'lag_{i}':history[-i] for i in range(1,lags+1)}])
        yhat=float(model.predict(features)[0])
        pred.append(yhat); history.append(yhat)
    pred_arr=np.asarray(pred,float)
    return {'model':model,'metrics':{'mae':float(mean_absolute_error(test_values,pred_arr)),'rmse':float(mean_squared_error(test_values,pred_arr)**0.5)},'actual':x.iloc[-horizon:].reset_index(drop=True),'predicted':pd.Series(pred_arr,name=value_col),'lags':lags,'forecast_mode':'recursive_multi_step'}
