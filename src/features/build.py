import pandas as pd
from src.config import PROCESSED

YESNO=['Partner','Dependents','PhoneService','PaperlessBilling']
SERVICE_COLS=['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies']

def build_features(df):
    x=df.copy()
    x['tenure_years']=x['tenure']/12
    x['is_new_customer']=(x['tenure']<=12).astype('int8')
    x['is_long_tenure']=(x['tenure']>=48).astype('int8')
    x['estimated_annual_revenue']=x['MonthlyCharges']*12
    x['total_to_monthly_ratio']=x['TotalCharges']/x['MonthlyCharges'].replace(0,pd.NA)
    x['total_to_monthly_ratio']=x['total_to_monthly_ratio'].fillna(0)
    x['service_count']=sum(x[c].eq('Yes').astype(int) for c in SERVICE_COLS)
    x['has_any_addon']=(x['service_count']>0).astype('int8')
    x['is_month_to_month']=x['Contract'].eq('Month-to-month').astype('int8')
    x['electronic_check']=x['PaymentMethod'].eq('Electronic check').astype('int8')
    x['fiber_optic']=x['InternetService'].eq('Fiber optic').astype('int8')
    return x

def main():
    df=pd.read_csv(PROCESSED/'customer_clean.csv')
    build_features(df).to_csv(PROCESSED/'model_dataset.csv',index=False)
if __name__=='__main__': main()
