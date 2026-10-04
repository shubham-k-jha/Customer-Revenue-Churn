import pytest
import numpy as np, pandas as pd
from src.advanced.deep_timeseries import clean_series, regularize, stationarity, lag_features, calendar_features, robust_outliers, trend_seasonality_strength
from src.advanced.forecasting_deep import expanding_backtest
from src.advanced.statistical_depth import normality, pairwise_correlations, bootstrap_ci
from src.advanced.anomaly import iqr_flags, isolation_flags
from src.advanced.feature_engineering import safe_ratios, winsorize


def seasonal_df(n=96):
    d=pd.date_range('2020-01-01',periods=n,freq='D')
    t=np.arange(n); y=100+0.15*t+10*np.sin(2*np.pi*t/7)+np.random.default_rng(1).normal(0,1,n)
    return pd.DataFrame({'date':d,'y':y})


def test_deep_ts_regularize_and_stationarity():
    df=seasonal_df(); s=clean_series(df,'date','y'); r=regularize(s,'D'); assert len(r)==len(s); assert 'adf' in stationarity(r)


def test_lag_features_no_current_leakage():
    s=pd.Series(np.arange(20,dtype=float)); x=lag_features(s,[1,2],[3]); assert pd.isna(x.iloc[0,0]); assert x.loc[3,'roll_mean_3']==1.0


def test_calendar_and_outlier_and_strength():
    df=seasonal_df(); feats=calendar_features(df.date,[7],2); assert {'month','day_of_week','sin_7_1'}.issubset(feats.columns)
    flags=robust_outliers(df.y,7); assert 'is_outlier' in flags
    assert trend_seasonality_strength(df.y,7)['seasonal_strength']>=0


def test_forecast_backtest_baselines():
    df=seasonal_df(); result=expanding_backtest(clean_series(df,'date','y'),horizon=7,initial_train=56,step=7,seasonal_period=7)
    assert result['summary']; assert result['winner_by_rmse'] in {'naive','drift','seasonal_naive','ets','arima'}


def test_stats_and_multiple_testing():
    rng=np.random.default_rng(2); df=pd.DataFrame({'a':rng.normal(size=100),'b':rng.normal(size=100),'c':rng.normal(size=100)})
    assert normality(df.a)['n']==100; corr=pairwise_correlations(df); assert 'q_value_bh' in corr; assert bootstrap_ci(df.a,n_boot=100)['ci_low'] < bootstrap_ci(df.a,n_boot=100)['ci_high']


def test_anomaly_and_features():
    s=pd.Series([1,1,1,1,10]); assert iqr_flags(s).is_anomaly.iloc[-1]
    x=pd.DataFrame({'a':np.arange(30,dtype=float),'b':np.arange(30,dtype=float)+1}); assert isolation_flags(x)['rows_scored']==30
    df=pd.DataFrame({'a':[10,20],'b':[2,4]}); assert safe_ratios(df,'a','b').tolist()==[5,5]; assert winsorize(pd.Series([1,2,100]),.1,.9).max()<100


def test_multiclass_xgboost_final_refit_if_available(tmp_path):
    from sklearn.datasets import load_iris
    from src.universal.model import train_generic
    d=load_iris(as_frame=True).frame
    summary=train_generic(d,'target',task='classification',artifact_path=tmp_path/'m.joblib')
    assert summary['task']=='classification'

def test_recursive_forecast_does_not_use_future_observations():
    from src.advanced.forecasting_suite import backtest_ridge
    base=seasonal_df(80)
    altered=base.copy(); altered.loc[altered.index[-5:],'y'] += 100000
    a=backtest_ridge(base,'date','y',horizon=5,lags=7)
    b=backtest_ridge(altered,'date','y',horizon=5,lags=7)
    assert np.allclose(a['predicted'].to_numpy(), b['predicted'].to_numpy())
    assert a['forecast_mode']=='recursive_multi_step'


def test_survival_parses_numeric_string_events_correctly():
    from src.advanced.survival import kaplan_meier
    r=kaplan_meier([1,2,3], ['1','0','1'])
    assert r['events'].tolist()==[1,0,1]
    with pytest.raises(ValueError):
        kaplan_meier([1,2,3], ['yes','no','yes'])


def test_survival_rejects_negative_duration_and_bad_horizon():
    from src.advanced.survival import kaplan_meier, retention_curve
    with pytest.raises(ValueError):
        kaplan_meier([-1,2,3],[1,0,1])
    with pytest.raises(ValueError):
        retention_curve([1,2,3],[1,0,1],[-1,2])


def test_constant_time_series_is_reported_not_crashed():
    from src.advanced.time_series_analysis import TimeSeriesConfig, analyze_time_series
    d=pd.DataFrame({'date':pd.date_range('2024-01-01',periods=30,freq='D'),'value':1.0})
    r=analyze_time_series(d,TimeSeriesConfig('date','value'))
    assert r['stationarity']['constant_series'] is True
    assert r['dominant_periods']==[]


def test_safe_join_enforces_declared_relationship_and_row_cap():
    from src.advanced.multitable import safe_join
    left=pd.DataFrame({'id':[1,1,2],'x':[1,2,3]}); right=pd.DataFrame({'id':[1,1,2],'y':[4,5,6]})
    with pytest.raises(ValueError): safe_join(left,right,'id','id',relationship='one-to-one')
    with pytest.raises(ValueError): safe_join(left,right,'id','id',max_output_rows=2)
