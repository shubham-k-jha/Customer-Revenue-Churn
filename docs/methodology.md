# Methodology

## Split strategy
A stratified 80/20 train/test split is used. The test set is held out until final evaluation. Cross-validation is performed only on the training portion.

## Preprocessing
Numeric variables use median imputation and scaling. Categorical variables use most-frequent imputation and one-hot encoding. All transformations are inside the sklearn pipeline, so they are fitted only on training folds.

## Models
1. Logistic Regression — interpretable baseline.
2. Random Forest — nonlinear benchmark.
3. XGBoost — planned/optional boosted-tree challenger when the environment supports it. XGBoost provides a sklearn-compatible classification interface. citeturn0search1turn0search4

## Metrics
ROC-AUC measures ranking discrimination; average precision/PR-AUC is included because churn is the minority class. Precision, recall and F1 are reported at explicit thresholds. Brier score and log loss are included for probability quality. scikit-learn documents ROC-AUC and average precision as distinct classification metrics. citeturn0search6turn0search14turn0search18

## Threshold
0.50 is a reporting baseline, not a business truth. A validation-derived F1 threshold is recorded separately. A production deployment should instead optimize a documented business cost/utility function using company-specific intervention cost, saved-margin value and contact capacity.

## Explainability
Feature importance or SHAP can explain model behavior. They do not establish that changing a feature will cause churn to change.

## Causal limitation
This dataset is observational and snapshot-based. It does not contain randomized retention treatments or longitudinal customer histories. Therefore the project can prioritize risk, but cannot claim that an intervention will prevent churn.
