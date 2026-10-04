import numpy as np, pandas as pd

def test_multiclass_generic(tmp_path):
    from sklearn.datasets import load_iris
    from src.universal.model import train_generic
    d=load_iris(as_frame=True).frame
    r=train_generic(d,'target',task='classification',artifact_path=tmp_path/'m.joblib')
    assert r['winner'] in {'logistic','random_forest','xgboost'}
    assert len(r['comparison'])>=2

def test_join_suggestions():
    from src.advanced.multitable import suggest_joins
    a=pd.DataFrame({'id':[1,2,3],'v':[4,5,6]}); b=pd.DataFrame({'customer_id':[2,3,4],'x':[8,9,10]})
    r=suggest_joins({'a':a,'b':b},min_overlap=.5)
    assert any(x.left_key=='id' and x.right_key=='customer_id' for x in r)

def test_rfm():
    from src.advanced.segmentation import rfm_segment
    d=pd.DataFrame({'customer':['a','a','b','b','c','c'],'date':pd.date_range('2025-01-01',periods=6),'amount':[10,20,30,40,50,60]})
    r=rfm_segment(d,'customer','date','amount',n_segments=2)
    assert {'recency','frequency','monetary','segment_id'}.issubset(r.columns)

def test_forecast():
    from src.advanced.forecast import lag_forecast
    d=pd.DataFrame({'date':pd.date_range('2025-01-01',periods=70),'value':np.arange(70,dtype=float)})
    r=lag_forecast(d,'date','value',horizon=5,lags=7)
    assert len(r['forecast'])==5 and r['metrics']['rmse']>=0

def test_agent_guard():
    from src.agent.orchestrator import AnalyticsAgent
    from src.agent.provider import LLMProvider
    class P(LLMProvider):
        def complete(self,messages,**kwargs): return '{"intent":"revenue","steps":["aggregate"],"sql":"SELECT SUM(revenue) FROM sales","caveats":[]}'
    p=AnalyticsAgent(P()).plan('revenue',{'sales':['revenue']})
    assert p.intent=='revenue'


def test_rfm_single_customer_and_invalid_segments():
    from src.advanced.segmentation import rfm_segment
    d=pd.DataFrame({'customer':['a','a'],'date':pd.to_datetime(['2025-01-01','2025-01-02']),'amount':[10,20]})
    r=rfm_segment(d,'customer','date','amount',n_segments=4)
    assert len(r)==1 and r.loc[0,'segment_id']==0
    import pytest
    with pytest.raises(ValueError): rfm_segment(d,'customer','date','amount',n_segments=0)


def test_bootstrap_rejects_empty_and_invalid_boot_count():
    from src.advanced.statistics_plus import bootstrap_mean_difference
    import pytest
    with pytest.raises(ValueError): bootstrap_mean_difference([], [1,2])
    with pytest.raises(ValueError): bootstrap_mean_difference([1,2], [3,4], n_boot=0)


def test_forecast_preserves_observed_spacing():
    from src.advanced.forecast import lag_forecast
    d=pd.DataFrame({'date':pd.date_range('2025-01-05',periods=70,freq='W'),'value':np.arange(70,dtype=float)})
    r=lag_forecast(d,'date','value',horizon=3,lags=7)
    assert r['forecast']['date'].iloc[1]-r['forecast']['date'].iloc[0] == pd.Timedelta(days=7)


def test_generic_model_rejects_zero_predictors(tmp_path):
    from src.universal.model import train_generic
    import pytest
    d=pd.DataFrame({'constant':[1]*40,'target':[0,1]*20})
    with pytest.raises(ValueError, match='No usable predictor'):
        train_generic(d,'target',task='classification',artifact_path=tmp_path/'m.joblib')


def test_agent_validates_plan_types():
    from src.agent.orchestrator import AnalyticsAgent
    from src.agent.provider import LLMProvider
    import pytest
    class P(LLMProvider):
        def complete(self,messages,**kwargs): return '{"intent":"x","steps":"not-a-list","sql":null,"caveats":[]}'
    with pytest.raises(ValueError, match='steps'):
        AnalyticsAgent(P()).plan('q',{'t':['x']})
