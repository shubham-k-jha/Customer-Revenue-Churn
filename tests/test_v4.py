import json
import numpy as np
import pandas as pd


def test_forecasting_suite_and_spacing():
    from src.advanced.forecasting_suite import seasonal_naive_backtest, backtest_ridge
    d=pd.DataFrame({'date':pd.date_range('2025-01-01',periods=80,freq='W'),'value':np.sin(np.arange(80)/4)+10})
    a=seasonal_naive_backtest(d,'date','value',horizon=5,season=4)
    b=backtest_ridge(d,'date','value',horizon=5,lags=7)
    assert a['metrics']['rmse'] >= 0 and b['metrics']['mae'] >= 0


def test_survival_curve():
    from src.advanced.survival import kaplan_meier, retention_curve
    km=kaplan_meier([1,2,3,4],[1,0,1,1])
    assert km.iloc[0].survival_probability < 1
    r=retention_curve([1,2,3,4],[1,0,1,1],[1,3])
    assert len(r)==2 and r.iloc[0].retention_probability >= r.iloc[1].retention_probability


def test_data_contract():
    from src.governance.data_contracts import validate_contract
    d=pd.DataFrame({'id':[1,2,3],'status':['ok','ok','bad'],'amount':[10,20,30]})
    c={'required_columns':['id','status'],'columns':{'id':{'unique':True},'status':{'allowed_values':['ok']},'amount':{'min':0}}}
    r=validate_contract(d,c)
    assert r['status']=='fail' and any(i['rule']=='allowed_values' for i in r['issues'])


def test_powerbi_export(tmp_path):
    from src.bi.powerbi_export import export_powerbi_package
    d=pd.DataFrame({'date':pd.date_range('2025-01-01',periods=3),'customer':['a','b','a'],'sales':[1,2,3]})
    out=export_powerbi_package(d,tmp_path/'pbi','date',['customer'],{'Total Sales':'SUM(fact_table[sales])'})
    assert (out/'fact_table.csv').exists() and (out/'dim_customer.csv').exists() and (out/'measures.dax').exists()
    assert 'Total Sales' in (out/'measures.dax').read_text()


def test_batch_score_regression(tmp_path):
    from src.universal.model import train_generic
    from src.production.batch_score_generic import score
    d=pd.DataFrame({'x':np.arange(50),'target':np.arange(50)*2.0+1})
    bundle=tmp_path/'m.joblib'; train_generic(d,'target',task='regression',artifact_path=bundle)
    inp=tmp_path/'in.csv'; d.drop(columns=['target']).to_csv(inp,index=False)
    out=score(inp,tmp_path/'out.csv',bundle)
    assert out.exists() and 'prediction' in pd.read_csv(out).columns


def test_executive_insights_are_evidence_based():
    from src.reporting.executive import generate_executive_insights
    d=pd.DataFrame({'date':pd.date_range('2025-01-01',periods=3),'region':['A','A','B'],'sales':[10,20,5]})
    r=generate_executive_insights(d,'date','sales','region')
    assert len(r['insights'])>=2 and r['caveats']

def test_survival_boolean_and_numeric_events():
    from src.advanced.survival import kaplan_meier
    r=kaplan_meier([1,2,3],[True,False,True])
    assert r['survival_probability'].iloc[-1] == 0.0

def test_safe_join_relationship_success():
    from src.advanced.multitable import safe_join
    left=pd.DataFrame({'id':[1,2],'x':[10,20]}); right=pd.DataFrame({'id':[1,2,2],'y':[1,2,3]})
    out=safe_join(left,right,'id','id',relationship='one-to-many')
    assert len(out)==3


def test_batch_score_rejects_missing_feature(tmp_path):
    from src.universal.model import train_generic
    from src.production.batch_score_generic import score
    d=pd.DataFrame({'x':np.arange(40),'z':np.arange(40)*3,'target':np.arange(40)*2.0+1})
    bundle=tmp_path/'m.joblib'; train_generic(d,'target',task='regression',artifact_path=bundle)
    inp=tmp_path/'in.csv'; d[['x','target']].drop(columns=['target']).to_csv(inp,index=False)
    try:
        score(inp,tmp_path/'out.csv',bundle)
    except ValueError as exc:
        assert 'missing required model features' in str(exc)
    else:
        raise AssertionError('missing feature should fail schema validation')

def test_target_ranker_avoids_sequential_identifier():
    from src.universal.profile import rank_target_candidates
    d=pd.DataFrame({'record_code':np.arange(50),'signal':[0,1]*25,'value':np.arange(50,dtype=float)})
    ranked=rank_target_candidates(d)
    assert ranked[0]['column']=='signal'
    assert all(x['column']!='record_code' for x in ranked[:1])
