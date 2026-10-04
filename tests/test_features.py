import pandas as pd
from src.features.build import build_features

def test_feature_builder():
    df=pd.DataFrame({
      'customerID':['A'],'tenure':[6],'MonthlyCharges':[50.0],'TotalCharges':[300.0],
      'Contract':['Month-to-month'],'PaymentMethod':['Electronic check'],'InternetService':['Fiber optic'],
      'Partner':['No'],'Dependents':['No'],'PhoneService':['Yes'],'PaperlessBilling':['Yes'],
      'OnlineSecurity':['No'],'OnlineBackup':['Yes'],'DeviceProtection':['No'],'TechSupport':['No'],'StreamingTV':['Yes'],'StreamingMovies':['No'],
      'churn_flag':[1],'Churn':['Yes'],'gender':['Female'],'SeniorCitizen':[0],'MultipleLines':['No']
    })
    x=build_features(df)
    assert x.loc[0,'is_new_customer']==1
    assert x.loc[0,'service_count']==2
    assert x.loc[0,'is_month_to_month']==1
