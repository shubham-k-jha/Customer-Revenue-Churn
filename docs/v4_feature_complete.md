# V4 Deep Analytics & Production Platform

V4 is intended as a reusable analytics system, not a collection of isolated demos.

## Time-series analysis

- deterministic timestamp parsing and duplicate aggregation
- explicit regularization rather than silently inventing frequency
- spacing irregularity diagnostics
- rolling mean/std/min/max
- ADF and KPSS stationarity tests
- differencing diagnostics
- ACF/PACF
- Ljung-Box residual autocorrelation testing
- Jarque-Bera residual diagnostics
- spectral dominant-period detection
- additive seasonal decomposition
- trend/seasonal strength
- robust rolling-MAD outlier detection
- calendar features and Fourier terms
- leakage-safe lag/rolling features

## Forecasting

Forecast model selection uses expanding-window backtesting. Simple baselines are mandatory comparators:

- naive
- drift
- seasonal naive
- ETS
- ARIMA(1,1,1)

Metrics include MAE, RMSE, MAPE and SMAPE. A complex model is not considered successful merely because it has a good single holdout score.

## Statistical analysis

- Welch unequal-variance tests
- effect sizes
- bootstrap confidence intervals
- Pearson/Spearman/Kendall correlation
- Benjamini-Hochberg multiple-testing correction
- normality diagnostics

## Predictive evaluation

- threshold optimization
- precision/recall/F1/balanced accuracy
- ROC-AUC and PR-AUC
- Brier score and calibration curves
- decision-curve/net-benefit analysis

## Customer analytics

- RFM segmentation
- cohort retention
- Kaplan-Meier survival analysis where duration/event definitions are supplied

## Anomaly detection

- transparent IQR rules
- multivariate Isolation Forest

## Governance boundaries

The system does not equate statistical association with causation, an anomaly score with an error, or a predictive probability with a guaranteed outcome. Business semantics must be supplied or verified by the analyst.
