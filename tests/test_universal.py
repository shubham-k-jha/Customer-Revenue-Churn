import pytest
import pandas as pd
from pathlib import Path
from src.universal.profile import profile_dataframe, rank_target_candidates
from src.universal.io import read_table
from src.universal.model import infer_task


def test_profile_and_target_detection():
    df = pd.DataFrame({"customer_id":[1,2,3,4], "age":[20,30,40,50], "churn":["No","Yes","No","Yes"]})
    p = profile_dataframe(df)
    assert p["rows"] == 4
    assert any(x["column"] == "churn" for x in rank_target_candidates(df))


def test_supported_csv_roundtrip(tmp_path):
    df = pd.DataFrame({"x":[1,2], "y":[0,1]})
    path = tmp_path / "data.csv"; df.to_csv(path, index=False)
    out = read_table(path)
    assert list(out.columns) == ["x", "y"]


def test_task_inference():
    assert infer_task(pd.Series([0,1,0,1])) == "classification"
    assert infer_task(pd.Series([float(i) for i in range(40)])) == "regression"


def test_parquet_roundtrip_when_engine_available(tmp_path):
    pytest = __import__('pytest')
    df = pd.DataFrame({'x':[1,2], 'target':[0,1]})
    path = tmp_path / 'data.parquet'
    try:
        df.to_parquet(path, index=False)
    except ImportError:
        pytest.skip('Parquet engine not installed in this execution environment')
    out = read_table(path)
    assert out.equals(df)

def test_time_aware_generic_training(tmp_path):
    from src.universal.model import train_generic
    dates = pd.date_range('2024-01-01', periods=40, freq='D')
    df = pd.DataFrame({'event_date': dates, 'x': range(40), 'target': [i % 2 for i in range(40)]})
    result = train_generic(df, 'target', task='classification', date_column='event_date', artifact_path=tmp_path/'time_model.joblib')
    assert result['task'] == 'classification'
    assert result['winner'] in {'logistic','random_forest','xgboost'}


def test_generic_classification_rejects_singleton_class():
    import pandas as pd
    from src.universal.model import train_generic
    df=pd.DataFrame({'x':range(30),'y':['a']*29+['b']})
    with pytest.raises(ValueError, match='at least two observations'):
        train_generic(df,'y',task='classification')
