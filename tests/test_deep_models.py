import numpy as np, pandas as pd
from src.models.deep_evaluation import classification_report_deep, optimize_threshold, calibration_diagnostics, decision_curve
from src.analytics.cohort import retention_cohort


def test_deep_classification_evaluation():
    y=np.array([0,0,0,1,1,1]); p=np.array([.1,.2,.4,.55,.8,.9])
    r=classification_report_deep(y,p,.5); assert 0<=r['f1']<=1 and 'roc_auc' in r
    best=optimize_threshold(y,p); assert .05<=best['threshold']<=.95
    assert calibration_diagnostics(y,p)['bins_returned']>=2
    assert not decision_curve(y,p).empty


def test_cohort_retention():
    d=pd.DataFrame({'customer':[1,1,2,2,3],'date':['2024-01-01','2024-02-01','2024-01-03','2024-03-01','2024-02-01']})
    r=retention_cohort(d,'customer','date'); assert not r['retention'].empty; assert np.isclose(r['retention'].iloc[0,0],1)
