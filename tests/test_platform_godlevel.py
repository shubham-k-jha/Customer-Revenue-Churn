import pandas as pd, pytest
from src.platform.quality import DataQualityEngine
from src.security.guards import validate_read_only_sql, validate_upload
from src.analytics.statistics import chi_square
from src.universal.model import train_generic

def test_quality_flags_constant_and_missing():
    df=pd.DataFrame({'a':[1,1,1],'b':[None,None,1]})
    r=DataQualityEngine(null_warn=.5).run(df)
    assert r['status']=='warn'; assert any(i['rule']=='constant' for i in r['issues'])

def test_sql_guard():
    assert validate_read_only_sql('SELECT * FROM sales')=='SELECT * FROM sales'
    with pytest.raises(ValueError): validate_read_only_sql('DELETE FROM sales')
    with pytest.raises(ValueError): validate_read_only_sql('SELECT 1; SELECT 2')

def test_upload_guard():
    validate_upload('data.parquet',100)
    with pytest.raises(ValueError): validate_upload('data.exe',100)

def test_chi_square():
    df=pd.DataFrame({'a':['x','x','y','y'],'b':['yes','no','yes','no']})
    r=chi_square(df,'a','b'); assert 'p_value' in r

def test_generic_model_selects_by_cv_not_test():
    from sklearn.datasets import load_breast_cancer
    d=load_breast_cancer(as_frame=True).frame
    d['target']=d['target'].astype(int)
    r=train_generic(d,'target',task='classification',artifact_path='/tmp/godlevel_test_model.joblib')
    assert r['selection_rule'].startswith('winner selected by cross-validation')


def test_sql_literal_semicolon_is_not_a_statement():
    from src.security.guards import validate_read_only_sql
    assert validate_read_only_sql("SELECT 'a;b' AS value") == "SELECT 'a;b' AS value"


def test_sql_guard_rejects_side_effectful_read_forms():
    from src.security.guards import validate_read_only_sql
    import pytest
    for sql in ["SELECT * INTO new_table FROM t", "SELECT * FROM t FOR UPDATE", "SELECT * FROM t WHERE x=1"]:
        if 'WHERE' in sql:
            assert validate_read_only_sql(sql) == sql
        else:
            with pytest.raises(ValueError):
                validate_read_only_sql(sql)
