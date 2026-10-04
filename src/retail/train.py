import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from src.retail.config import SNAPSHOTS_PARQUET, MODEL

TARGET = 'churn_90d'
DROP = {'customer_id','snapshot_date','last_purchase_date','churn_90d','retained_90d'}

def load():
    import duckdb
    return duckdb.read_parquet(SNAPSHOTS_PARQUET.as_posix()).df()

def time_split(df):
    dates = sorted(df.snapshot_date.unique())
    if len(dates) < 6:
        raise ValueError('Need at least 6 monthly snapshots for temporal train/validation/test splits')
    n = len(dates)
    train_end, valid_end = dates[max(1, int(n*0.60)-1)], dates[max(2, int(n*0.80)-1)]
    train = df[df.snapshot_date <= train_end]
    valid = df[(df.snapshot_date > train_end) & (df.snapshot_date <= valid_end)]
    test = df[df.snapshot_date > valid_end]
    return train, valid, test

def make_model(X):
    cat = X.select_dtypes(include=['object','string']).columns.tolist()
    num = X.select_dtypes(exclude=['object','string']).columns.tolist()
    prep = ColumnTransformer([
        ('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), num),
        ('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat),
    ])
    return Pipeline([('prep', prep), ('model', LogisticRegression(max_iter=2000, class_weight='balanced'))])

def train():
    df = load()
    train, valid, test = time_split(df)
    Xtr = train.drop(columns=list(DROP), errors='ignore'); ytr = train[TARGET]
    Xv = valid.drop(columns=list(DROP), errors='ignore'); yv = valid[TARGET]
    Xt = test.drop(columns=list(DROP), errors='ignore'); yt = test[TARGET]

    model = make_model(Xtr)
    model.fit(Xtr, ytr)
    pv = model.predict_proba(Xv)[:,1]
    # Threshold chosen only on validation data using F1.
    thresholds = [i/100 for i in range(10,91)]
    best_t = max(thresholds, key=lambda t: __import__('sklearn').metrics.f1_score(yv, (pv>=t).astype(int)))

    # Refit on train+validation, then evaluate once on future test period.
    final = make_model(pd.concat([Xtr, Xv], ignore_index=True))
    final.fit(pd.concat([Xtr, Xv], ignore_index=True), pd.concat([ytr, yv], ignore_index=True))
    pt = final.predict_proba(Xt)[:,1]
    metrics = {
        'validation_threshold': best_t,
        'test_roc_auc': roc_auc_score(yt, pt),
        'test_pr_auc': average_precision_score(yt, pt),
        'test_brier': brier_score_loss(yt, pt),
        'test_log_loss': log_loss(yt, pt),
        'train_rows': len(train), 'validation_rows': len(valid), 'test_rows': len(test),
        'train_end': str(train.snapshot_date.max()), 'validation_end': str(valid.snapshot_date.max()), 'test_end': str(test.snapshot_date.max()),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final, MODEL)
    (MODEL.parent / 'retail_metrics.json').write_text(json.dumps(metrics, indent=2))
    return metrics

if __name__ == '__main__':
    print(json.dumps(train(), indent=2))
