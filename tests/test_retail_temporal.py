import pandas as pd
from src.retail.train import time_split

def test_temporal_split_has_no_overlap():
    rows=[]
    for i, d in enumerate(pd.date_range('2020-01-01', periods=9, freq='MS')):
        for c in range(2):
            rows.append({'snapshot_date':d,'customer_id':c,'churn_90d':c%2})
    df=pd.DataFrame(rows)
    tr, va, te=time_split(df)
    assert tr.snapshot_date.max() < va.snapshot_date.min()
    assert va.snapshot_date.max() < te.snapshot_date.min()

def test_target_is_binary():
    df=pd.DataFrame({'churn_90d':[0,1,0,1]})
    assert set(df.churn_90d.unique()) == {0,1}
