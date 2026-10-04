# Model Card — Customer Churn Intelligence

## Intended use
Prioritize customer-retention analysis and operational investigation. Predictions are risk scores, not causal estimates of who will churn because of an intervention.

## Data
Two tracks are supported:
1. IBM Telco Customer Churn: explicit historical churn label.
2. UCI Online Retail II: temporal behavioral benchmark with a constructed 90-day no-purchase target.

## Target
For the retail track, `churn_90d = 1` means no qualifying purchase occurs during the 90 days following the snapshot date.

## Validation
Temporal train/validation/test splits are required for the retail benchmark. Hyperparameters are selected without the final test period. The decision threshold is selected on validation data.

## Metrics
Report ROC-AUC and PR-AUC for ranking; precision, recall and F1 at the selected threshold; Brier/log loss for probabilistic quality.

## Limitations
- Public sample data is not production customer data.
- The retail churn definition is a business-case operational definition, not a contractual customer-status definition.
- No causal claim is supported.
- Calibration and drift must be rechecked after deployment.
- Retention economics depend on actual margin, intervention cost and incremental treatment effect.
