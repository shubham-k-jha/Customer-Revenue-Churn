from pathlib import Path
import joblib, pandas as pd
from src.monitoring.metrics import PredictionMonitor

def score(input_path, output_path, model_path='artifacts/model_bundle.joblib'):
    b=joblib.load(model_path); df=pd.read_csv(input_path)
    ids=df['customerID'] if 'customerID' in df else pd.Series(range(len(df)))
    X=df.drop(columns=['customerID','Churn','churn_flag'],errors='ignore').reindex(columns=b['features'],fill_value=None)
    p=b['model'].predict_proba(X)[:,1]
    out=df.copy(); out['churn_probability']=p; out['risk_band']=pd.cut(p,[-.01,.30,.60,1.01],labels=['Low','Medium','High'])
    out['monthly_revenue_at_risk']=out['MonthlyCharges']*p
    out.to_csv(output_path,index=False)
    PredictionMonitor().log([{'probability':float(x),'risk_band':str(r)} for x,r in zip(p,out['risk_band'])])
    return Path(output_path)
