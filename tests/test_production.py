import pandas as pd
from src.monitoring.metrics import population_stability_index
from src.production.batch_score import score

def test_psi_identical_zero():
    x=[1,2,3,4,5,6,7,8,9,10]
    assert population_stability_index(x,x) < 1e-9

def test_batch_schema(tmp_path):
    src=tmp_path/'input.csv'; out=tmp_path/'out.csv'
    pd.DataFrame({'customerID':['x'],'MonthlyCharges':[10.0],'TotalCharges':[100.0],'tenure':[10], 'churn_flag':[0]}).to_csv(src,index=False)
    # Requires a trained artifact; schema test is intentionally skipped if absent.
    import os
    if os.path.exists('artifacts/model_bundle.joblib'):
        score(src,out); assert 'churn_probability' in pd.read_csv(out).columns


def test_psi_detects_out_of_reference_range():
    import numpy as np
    from src.monitoring.drift import psi
    assert psi(np.arange(100,dtype=float),np.arange(100,200,dtype=float))>0
