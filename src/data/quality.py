import pandas as pd

REQUIRED=['customerID','gender','SeniorCitizen','Partner','Dependents','tenure','PhoneService','MultipleLines','InternetService','OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies','Contract','PaperlessBilling','PaymentMethod','MonthlyCharges','TotalCharges','Churn']

def load_and_validate(path):
    df=pd.read_csv(path)
    missing=set(REQUIRED)-set(df.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    df.columns=df.columns.str.strip()
    df['TotalCharges']=pd.to_numeric(df['TotalCharges'],errors='coerce')
    df['MonthlyCharges']=pd.to_numeric(df['MonthlyCharges'],errors='coerce')
    df['tenure']=pd.to_numeric(df['tenure'],errors='coerce')
    if df['customerID'].duplicated().any(): raise ValueError('Duplicate customer IDs detected')
    if not df['MonthlyCharges'].ge(0).all(): raise ValueError('Negative monthly charges')
    if not df['TotalCharges'].dropna().ge(0).all(): raise ValueError('Negative total charges')
    if not df['tenure'].between(0,72).all(): raise ValueError('Unexpected tenure range')
    if not df['Churn'].isin(['Yes','No']).all(): raise ValueError('Unexpected churn labels')
    # Blank TotalCharges are meaningful for zero-tenure records; retain them and impute to 0 for modeling.
    df['total_charges_missing']=df['TotalCharges'].isna().astype('int8')
    df['TotalCharges']=df['TotalCharges'].fillna(0.0)
    df['churn_flag']=df['Churn'].eq('Yes').astype('int8')
    return df

def quality_report(df):
    return {
      'rows':int(len(df)), 'columns':int(df.shape[1]), 'duplicate_ids':int(df.customerID.duplicated().sum()),
      'missing_total_charges':int(df.total_charges_missing.sum()), 'churn_rate':float(df.churn_flag.mean()),
      'monthly_revenue':float(df.MonthlyCharges.sum()), 'negative_monthly_charges':int((df.MonthlyCharges<0).sum())
    }
