import os
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import PROCESSED


def load():
    url=os.getenv('POSTGRES_URL')
    if not url:
        raise RuntimeError('POSTGRES_URL is not set')
    df=pd.read_csv(PROCESSED/'customer_clean.csv')
    engine=create_engine(url)
    rename={'customerID':'customer_id','SeniorCitizen':'senior_citizen','Partner':'partner','Dependents':'dependents','PhoneService':'phone_service','MultipleLines':'multiple_lines','InternetService':'internet_service','OnlineSecurity':'online_security','OnlineBackup':'online_backup','DeviceProtection':'device_protection','TechSupport':'tech_support','StreamingTV':'streaming_tv','StreamingMovies':'streaming_movies','Contract':'contract','PaperlessBilling':'paperless_billing','PaymentMethod':'payment_method','MonthlyCharges':'monthly_charges','TotalCharges':'total_charges','Churn':'churn'}
    out=df.rename(columns=rename)
    out.to_sql('customers',engine,if_exists='replace',index=False,method='multi')
    with engine.connect() as c:
        print(c.execute(text('SELECT COUNT(*) FROM customers')).scalar())

if __name__=='__main__': load()
