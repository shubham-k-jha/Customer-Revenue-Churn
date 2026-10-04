from fastapi.testclient import TestClient
from api.main import app

def test_health():
    r=TestClient(app).get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_generic_profile_csv():
    r = TestClient(app).post('/data/profile', files={'file': ('sample.csv', b'a,b,target\n1,x,0\n2,y,1\n3,x,0\n', 'text/csv')})
    assert r.status_code == 200
    body = r.json()
    assert body['rows'] == 3
    assert any(x['column'] == 'target' for x in body['target_candidates'])


def test_invalid_upload_returns_client_error():
    r = TestClient(app).post('/data/profile', files={'file': ('sample.txt', b'hello', 'text/plain')})
    assert r.status_code == 400


def test_time_series_endpoint_json_safe():
    from fastapi.testclient import TestClient
    from api.main import app
    import pandas as pd
    import numpy as np
    c=TestClient(app)
    dates=pd.date_range("2024-01-01",periods=40,freq="D")
    values=(100+np.arange(40)*0.2+5*np.sin(2*np.pi*np.arange(40)/7)).tolist()
    r=c.post("/analytics/time-series",json={"data":[{"date":str(d.date()),"value":v} for d,v in zip(dates,values)],"date_col":"date","value_col":"value","seasonal_period":7})
    assert r.status_code==200
    assert "decomposition" in r.json()

def test_deep_timeseries_endpoint():
    from fastapi.testclient import TestClient
    from api.main import app
    import pandas as pd
    dates=pd.date_range('2024-01-01',periods=40,freq='D')
    data=[{'date':d.isoformat(),'value':float(i+10)} for i,d in enumerate(dates)]
    r=TestClient(app).post('/analytics/time-series/deep',json={'data':data,'date_col':'date','value_col':'value','seasonal_period':7})
    assert r.status_code==200, r.text
    assert 'stationarity' in r.json()
