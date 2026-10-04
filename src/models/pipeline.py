import json
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_curve,
    precision_score, recall_score, f1_score, brier_score_loss, log_loss
)
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
)
from src.config import PROCESSED, ARTIFACTS, RANDOM_STATE

TARGET='churn_flag'
ID_COLS=['customerID','Churn',TARGET]


def make_preprocessor(X):
    cats=X.select_dtypes(include=['object','string']).columns.tolist()
    nums=X.select_dtypes(exclude=['object','string']).columns.tolist()
    return ColumnTransformer([
      ('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),
      ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cats)
    ])


def candidates(X):
    prep=make_preprocessor(X)
    models={
      'logistic': (
        Pipeline([('prep',prep),('model',LogisticRegression(max_iter=3000,class_weight='balanced',random_state=RANDOM_STATE))]),
        {'model__C':[0.1,1.0,3.0]}
      ),
      'random_forest': (
        Pipeline([('prep',prep),('model',RandomForestClassifier(n_estimators=400,min_samples_leaf=3,class_weight='balanced_subsample',random_state=RANDOM_STATE,n_jobs=-1))]),
        {'model__max_depth':[None,6,12],'model__min_samples_leaf':[2,5]}
      )
    }
    try:
        from xgboost import XGBClassifier
        models['xgboost']=(
          Pipeline([('prep',prep),('model',XGBClassifier(
              n_estimators=400,max_depth=4,learning_rate=.05,subsample=.8,colsample_bytree=.8,
              objective='binary:logistic',eval_metric='logloss',tree_method='hist',
              random_state=RANDOM_STATE,n_jobs=-1
          ))]),
          {'model__max_depth':[3,4,6],'model__learning_rate':[.03,.05,.1],'model__subsample':[.8,1.0]}
        )
    except ImportError:
        pass
    return models


def metrics(y,p,threshold=.5):
    pred=(np.asarray(p)>=threshold).astype(int)
    return {
      'roc_auc':roc_auc_score(y,p),
      'pr_auc':average_precision_score(y,p),
      'brier':brier_score_loss(y,p),
      'log_loss':log_loss(y,p,labels=[0,1]),
      'precision':precision_score(y,pred,zero_division=0),
      'recall':recall_score(y,pred,zero_division=0),
      'f1':f1_score(y,pred,zero_division=0)
    }


def best_f1_threshold(y,p):
    precision,recall,thresholds=precision_recall_curve(y,p)
    if len(thresholds)==0: return .5
    f=2*precision[:-1]*recall[:-1]/np.maximum(precision[:-1]+recall[:-1],1e-12)
    return float(thresholds[int(np.nanargmax(f))])


def train():
    df=pd.read_csv(PROCESSED/'model_dataset.csv')
    X=df.drop(columns=ID_COLS,errors='ignore'); y=df[TARGET]
    # Three-way split: model selection -> threshold selection -> final test.
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.20,stratify=y,random_state=RANDOM_STATE)
    X_train,X_valid,y_train,y_valid=train_test_split(X_dev,y_dev,test_size=.25,stratify=y_dev,random_state=RANDOM_STATE)
    cv=StratifiedKFold(5,shuffle=True,random_state=RANDOM_STATE)

    rows=[]; candidates_fitted={}
    for name,(est,grid) in candidates(X_train).items():
        search=GridSearchCV(est,grid,scoring='average_precision',cv=cv,n_jobs=-1,refit=True,return_train_score=False)
        search.fit(X_train,y_train)
        p_valid=search.best_estimator_.predict_proba(X_valid)[:,1]
        threshold=best_f1_threshold(y_valid,p_valid)
        rows.append({
          'model':name,
          'cv_roc_auc':float(cross_val_score(search.best_estimator_,X_train,y_train,cv=cv,scoring='roc_auc',n_jobs=-1).mean()),
          'cv_pr_auc':float(search.best_score_),
          'validation_roc_auc':float(roc_auc_score(y_valid,p_valid)),
          'validation_pr_auc':float(average_precision_score(y_valid,p_valid)),
          'validation_f1_at_selected_threshold':float(f1_score(y_valid,(p_valid>=threshold).astype(int))),
          'selected_threshold':float(threshold)
        })
        candidates_fitted[name]=(search.best_estimator_,search.best_params_)

    comparison=pd.DataFrame(rows).sort_values(['cv_pr_auc','validation_pr_auc'],ascending=False).reset_index(drop=True)
    winner=str(comparison.loc[0,'model']); threshold=float(comparison.loc[0,'selected_threshold']); best_params=candidates_fitted[winner][1]

    # Rebuild the winning estimator with the selected hyperparameters and refit only after all decisions are complete.
    winning_estimator=candidates(X_dev)[winner][0].set_params(**best_params)
    winning_estimator.fit(X_dev,y_dev)
    p_test=winning_estimator.predict_proba(X_test)[:,1]

    test05=metrics(y_test,p_test,.5); testopt=metrics(y_test,p_test,threshold)
    summary={
      'winner':winner,
      'selection_metric':'cross_validated_average_precision_on_training_split',
      'selected_threshold_source':'validation_split',
      'selected_threshold':threshold,
      'best_params':best_params,
      'model_selection_rows':comparison.to_dict(orient='records'),
      'test_metrics_at_0_50':test05,
      'test_metrics_at_selected_threshold':testopt,
      'train_rows':int(len(y_train)),
      'validation_rows':int(len(y_valid)),
      'test_rows':int(len(y_test)),
      'test_evaluated_once_after_model_selection':True
    }
    joblib.dump({'model':winning_estimator,'threshold':threshold,'features':X.columns.tolist(),'winner':winner},ARTIFACTS/'model_bundle.joblib')
    comparison.to_csv(ARTIFACTS/'model_comparison.csv',index=False)
    (ARTIFACTS/'model_summary.json').write_text(json.dumps(summary,indent=2))
    return comparison,summary

if __name__=='__main__':
    result,summary=train(); print(result.to_string(index=False)); print(json.dumps(summary,indent=2))
