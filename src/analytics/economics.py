import pandas as pd
from src.config import HIGH_RISK_THRESHOLD,RETENTION_OFFER_COST,EXPECTED_SAVED_MONTHS,GROSS_MARGIN_RATE

def add_risk_economics(df,prob_col='churn_probability'):
    x=df.copy()
    x['risk_band']=pd.cut(x[prob_col],[-.01,.30,.60,1.01],labels=['Low','Medium','High'])
    x['monthly_revenue_at_risk']=x['MonthlyCharges']*x[prob_col]
    x['gross_profit_at_risk_6m']=x[prob_col]*x['MonthlyCharges']*EXPECTED_SAVED_MONTHS*GROSS_MARGIN_RATE
    x['expected_offer_cost']=x[prob_col]*RETENTION_OFFER_COST
    x['expected_net_retention_value']=x['gross_profit_at_risk_6m']-x['expected_offer_cost']
    return x

def kpis(df):
    return {'customers':int(len(df)),'churn_rate':float(df.churn_flag.mean()),'monthly_revenue':float(df.MonthlyCharges.sum()),'revenue_at_risk':float(df.monthly_revenue_at_risk.sum()),'high_risk_customers':int((df.risk_band=='High').sum()),'high_risk_monthly_revenue':float(df.loc[df.risk_band=='High','MonthlyCharges'].sum()),'high_risk_expected_net_value':float(df.loc[df.risk_band=='High','expected_net_retention_value'].sum())}
