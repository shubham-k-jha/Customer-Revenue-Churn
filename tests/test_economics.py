import pandas as pd
from src.analytics.economics import add_risk_economics

def test_economics():
    df=pd.DataFrame({'MonthlyCharges':[100.0],'churn_flag':[1],'churn_probability':[.8]})
    x=add_risk_economics(df)
    assert x.loc[0,'monthly_revenue_at_risk']==80
    assert x.loc[0,'risk_band']=='High'
