import pandas as pd
from src.data.quality import load_and_validate

def test_zero_tenure_blank_total_charges_preserved(tmp_path):
    p=tmp_path/'x.csv'
    pd.DataFrame([{
      "customerID":"A","gender":"Female","SeniorCitizen":0,"Partner":"No","Dependents":"No","tenure":0,"PhoneService":"No","MultipleLines":"No phone service","InternetService":"No","OnlineSecurity":"No internet service","OnlineBackup":"No internet service","DeviceProtection":"No internet service","TechSupport":"No internet service","StreamingTV":"No internet service","StreamingMovies":"No internet service","Contract":"Month-to-month","PaperlessBilling":"No","PaymentMethod":"Mailed check","MonthlyCharges":20,"TotalCharges":"","Churn":"No"
    }]).to_csv(p,index=False)
    df=load_and_validate(p)
    assert len(df)==1
    assert df.loc[0,'TotalCharges']==0
    assert df.loc[0,'total_charges_missing']==1


def test_quality_empty_dataset_fails():
    import pandas as pd
    from src.platform.quality import DataQualityEngine
    r=DataQualityEngine().run(pd.DataFrame({'x':[]}))
    assert r['status']=='fail' and r['issues'][0]['rule']=='empty_dataset'
