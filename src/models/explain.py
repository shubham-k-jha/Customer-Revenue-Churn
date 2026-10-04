from pathlib import Path
import joblib, pandas as pd

def explain_global(data_path='data/processed/model_dataset.csv', model_path='artifacts/model_bundle.joblib', output='artifacts/explainability.csv', max_rows=2000):
    b=joblib.load(model_path); df=pd.read_csv(data_path).head(max_rows); X=df.drop(columns=['customerID','Churn','churn_flag'],errors='ignore').reindex(columns=b['features'],fill_value=None)
    try:
        import shap
        transformed=b['model'].named_steps['prep'].transform(X)
        estimator=b['model'].named_steps['model']
        names=b['model'].named_steps['prep'].get_feature_names_out()
        if hasattr(estimator,'coef_'): values=estimator.coef_[0]
        else:
            explainer=shap.TreeExplainer(estimator); values=explainer.shap_values(transformed); values=values[1] if isinstance(values,list) else values
            values=abs(values).mean(axis=0)
        out=pd.DataFrame({'feature':names,'importance':abs(values)}).sort_values('importance',ascending=False)
    except Exception as e:
        out=pd.DataFrame({'feature':b['features'],'importance':[None]*len(b['features'])}); Path(output).with_suffix('.error.txt').write_text(str(e))
    out.to_csv(output,index=False); return out
