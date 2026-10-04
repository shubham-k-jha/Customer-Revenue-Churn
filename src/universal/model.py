from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import average_precision_score, balanced_accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score, recall_score
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold, TimeSeriesSplit, cross_val_score
from sklearn.base import clone
from src.config import ARTIFACTS, RANDOM_STATE


def infer_task(y: pd.Series) -> str:
    n = y.nunique(dropna=True)
    if y.dtype == 'bool' or n <= 2:
        return 'classification'
    if pd.api.types.is_numeric_dtype(y) and n > 10:
        return 'regression'
    if pd.api.types.is_numeric_dtype(y):
        raise ValueError('Ambiguous numeric target: explicitly specify classification or regression.')
    return 'classification'


def _prepare(df, target, drop_columns=None):
    if target not in df.columns: raise ValueError(f'Target column {target!r} not found')
    X=df.drop(columns=[target]+(drop_columns or []), errors='ignore').copy()
    X=X.loc[:, X.nunique(dropna=False)>1]
    if X.shape[1] == 0:
        raise ValueError('No usable predictor columns remain after removing the target and constant columns.')
    cats=X.select_dtypes(include=['object','string','category','bool']).columns.tolist()
    nums=[c for c in X.columns if c not in cats]
    prep=ColumnTransformer([
        ('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),nums),
        ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cats)
    ], remainder='drop')
    return X, df[target].copy(), prep


def _encode_target(y):
    vals=list(pd.Series(y.dropna().unique()))
    if len(vals)<2: raise ValueError('Classification target must contain at least two classes')
    le=LabelEncoder(); encoded=le.fit_transform(y.astype(str))
    return pd.Series(encoded,index=y.index), {str(v):int(i) for i,v in enumerate(le.classes_)}


def _classification_models(prep):
    models={'logistic':Pipeline([('prep',prep),('model',LogisticRegression(max_iter=2500,class_weight='balanced',random_state=RANDOM_STATE))]),
            'random_forest':Pipeline([('prep',prep),('model',RandomForestClassifier(n_estimators=300,min_samples_leaf=2,class_weight='balanced_subsample',random_state=RANDOM_STATE,n_jobs=-1))])}
    try:
        from xgboost import XGBClassifier
        models['xgboost']=Pipeline([('prep',prep),('model',XGBClassifier(n_estimators=300,max_depth=5,learning_rate=.05,subsample=.85,colsample_bytree=.85,eval_metric='logloss',tree_method='hist',random_state=RANDOM_STATE,n_jobs=-1))])
    except ImportError: pass
    return models


def _regression_models(prep):
    models={'ridge':Pipeline([('prep',prep),('model',Ridge(alpha=1.0))]),
            'random_forest':Pipeline([('prep',prep),('model',RandomForestRegressor(n_estimators=300,min_samples_leaf=2,random_state=RANDOM_STATE,n_jobs=-1))])}
    try:
        from xgboost import XGBRegressor
        models['xgboost']=Pipeline([('prep',prep),('model',XGBRegressor(n_estimators=300,max_depth=5,learning_rate=.05,subsample=.85,colsample_bytree=.85,objective='reg:squarederror',tree_method='hist',random_state=RANDOM_STATE,n_jobs=-1))])
    except ImportError: pass
    return models


def train_generic(df,target,task=None,drop_columns=None,artifact_path=None,date_column=None):
    work=df.copy()
    if date_column:
        if date_column not in work: raise ValueError(f'Date column {date_column!r} not found')
        parsed=pd.to_datetime(work[date_column],errors='coerce',utc=True,format='mixed')
        if parsed.notna().mean()<.90: raise ValueError('Selected date column has <90% parseable values')
        work=work.assign(__date=parsed).sort_values('__date').reset_index(drop=True).drop(columns='__date')
        drop_columns=list(dict.fromkeys((drop_columns or [])+[date_column]))
    X,y,prep=_prepare(work,target,drop_columns)
    task=task or infer_task(y)
    if task not in {'classification','regression'}: raise ValueError('task must be classification or regression')
    if task=='classification':
        mask=y.notna(); X=X.loc[mask]; y,mapping=_encode_target(y.loc[mask])
    else:
        y=pd.to_numeric(y,errors='coerce'); mask=y.notna(); X=X.loc[mask]; y=y.loc[mask]
        mapping=None
    if len(X)<30: raise ValueError('At least 30 usable rows are required')
    if date_column:
        cut=int(len(X)*.80); X_train,X_test=X.iloc[:cut],X.iloc[cut:]; y_train,y_test=y.iloc[:cut],y.iloc[cut:]
        cv=TimeSeriesSplit(n_splits=5)
        split_strategy='chronological'
    elif task=='classification':
        class_counts=y.value_counts()
        min_class=int(class_counts.min())
        if min_class < 2:
            raise ValueError('Classification requires at least two observations in every class for a stratified train/test split.')
        n_splits=min(5,min_class)
        X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.20,stratify=y,random_state=RANDOM_STATE)
        cv=StratifiedKFold(n_splits=n_splits,shuffle=True,random_state=RANDOM_STATE); split_strategy=f'stratified_random_{n_splits}fold'
    else:
        X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.20,random_state=RANDOM_STATE)
        cv=KFold(5,shuffle=True,random_state=RANDOM_STATE); split_strategy='random'
    models=_classification_models(prep) if task=='classification' else _regression_models(prep)
    rows=[]
    for name,est in models.items():
        if task=='classification':
            fold_scores=[]
            for fold_train, fold_valid in cv.split(X_train, y_train):
                ytr=y_train.iloc[fold_train]; yv=y_train.iloc[fold_valid]
                if ytr.nunique() < 2:
                    continue
                fold_est=clone(est)
                if ytr.nunique() > 2 and name == 'xgboost':
                    try:
                        fold_est.named_steps['model'].set_params(objective='multi:softprob', num_class=int(ytr.nunique()), eval_metric='mlogloss')
                    except Exception:
                        pass
                try:
                    fold_est.fit(X_train.iloc[fold_train], ytr)
                    fold_pred=fold_est.predict(X_train.iloc[fold_valid])
                    fold_proba=fold_est.predict_proba(X_train.iloc[fold_valid])
                    if ytr.nunique()==2 and yv.nunique()==2:
                        score=float(roc_auc_score(yv,fold_proba[:,1]))
                    elif ytr.nunique()>2 and yv.nunique()>1 and set(yv.unique()).issubset(set(ytr.unique())):
                        score=float(roc_auc_score(yv,fold_proba,multi_class='ovr',average='weighted',labels=sorted(ytr.unique())))
                    else:
                        score=float(recall_score(yv,fold_pred,labels=sorted(ytr.unique()),average='macro',zero_division=0))
                    fold_scores.append(score)
                except Exception:
                    continue
            if not fold_scores:
                raise ValueError(f'Unable to obtain a valid cross-validation score for {name}; temporal folds may not contain enough classes.')
            cv_score=float(np.mean(fold_scores))
            est.fit(X_train,y_train); p=est.predict_proba(X_test); pred=est.predict(X_test)
            if y.nunique()==2:
                roc=float(roc_auc_score(y_test,p[:,1])) if y_test.nunique()==2 else None
                pr=float(average_precision_score(y_test,p[:,1])) if y_test.nunique()==2 else None
            else:
                roc=float(roc_auc_score(y_test,p,multi_class='ovr',average='weighted')) if y_test.nunique()>1 and set(y_test.unique()).issubset(set(y_train.unique())) else None
                try:
                    pr=float(average_precision_score(pd.get_dummies(y_test).reindex(columns=range(y.nunique()),fill_value=0),p,average='weighted')) if y_test.nunique()>1 else None
                except ValueError:
                    pr=None
            rows.append({'model':name,'cv_primary':cv_score,'test_roc_auc':roc,'test_pr_auc':pr,'test_f1_macro':float(f1_score(y_test,pred,labels=sorted(y_train.unique()),average='macro',zero_division=0)),'test_balanced_accuracy':float(recall_score(y_test,pred,labels=sorted(y_train.unique()),average='macro',zero_division=0))})
        else:
            cv_score=float(-cross_val_score(est,X_train,y_train,cv=cv,scoring='neg_root_mean_squared_error',n_jobs=-1).mean())
            est.fit(X_train,y_train); p=est.predict(X_test)
            rows.append({'model':name,'cv_primary_rmse':cv_score,'test_rmse':float(mean_squared_error(y_test,p)**.5),'test_mae':float(mean_absolute_error(y_test,p)),'test_r2':float(r2_score(y_test,p))})
    comparison=pd.DataFrame(rows).sort_values('cv_primary' if task=='classification' else 'cv_primary_rmse',ascending=task!='classification').reset_index(drop=True)
    winner=str(comparison.iloc[0]['model'])
    # Final artifact is refit on all usable data ONLY after winner selection. Test metrics remain untouched reporting metrics.
    final_model=models[winner]
    if task == 'classification' and y.nunique() > 2 and winner == 'xgboost':
        try:
            final_model.named_steps['model'].set_params(
                objective='multi:softprob',
                num_class=int(y.nunique()),
                eval_metric='mlogloss',
            )
        except Exception as exc:
            raise ValueError(f'Could not configure XGBoost for multiclass final refit: {exc}') from exc
    final_model = final_model.fit(X, y)
    bundle={'model':final_model,'task':task,'target':target,'features':X.columns.tolist(),'drop_columns':drop_columns or [],'date_column':date_column,'target_mapping':mapping,'feature_dtypes':{str(c):str(X[c].dtype) for c in X.columns},'version':'generic-v4','split_strategy':split_strategy,'selection_metric':'cv_roc_auc_or_ovr' if task=='classification' else 'cv_rmse'}
    artifact_path=Path(artifact_path or ARTIFACTS/'generic_model_bundle.joblib'); artifact_path.parent.mkdir(parents=True,exist_ok=True); joblib.dump(bundle,artifact_path)
    summary={'task':task,'target':target,'winner':winner,'rows':len(df),'usable_rows':len(X),'split_strategy':split_strategy,'selection_rule':'winner selected by cross-validation on development data; test set used only for final reporting','comparison':comparison.to_dict(orient='records'),'artifact':str(artifact_path)}
    artifact_path.with_suffix('.json').write_text(json.dumps(summary,indent=2))
    return summary
