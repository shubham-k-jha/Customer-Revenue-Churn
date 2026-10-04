# Deep Analytics Layer

The platform separates descriptive analytics from inference and prediction.

## Time-series methodology

1. Parse and aggregate timestamps deterministically.
2. Detect spacing irregularity before choosing models.
3. Regularize only when the analyst explicitly supplies a frequency.
4. Inspect rolling statistics, ADF and KPSS jointly; one stationarity test is not treated as proof.
5. Inspect ACF/PACF and Ljung-Box residual diagnostics.
6. Detect robust outliers without deleting them automatically.
7. Quantify trend/seasonal strength after decomposition.
8. Engineer lag/rolling/Fourier features with an explicit one-step shift to prevent target leakage.
9. Compare naive, drift and seasonal-naive baselines before complex models.
10. Use expanding-window backtesting for forecasting model selection.

## Statistical methodology

- Welch tests for unequal-variance two-group comparisons.
- Effect sizes alongside p-values.
- Bootstrap confidence intervals for sampling uncertainty.
- Spearman/Pearson/Kendall correlations as appropriate.
- Benjamini-Hochberg FDR correction for multiple pairwise tests.
- Normality diagnostics are treated as diagnostics, not as an automatic gatekeeper for analysis.

## Anomaly detection

IQR is a transparent univariate rule. Isolation Forest is a multivariate detector. Neither automatically means an observation is erroneous; analysts must distinguish data-quality errors from genuine rare events.

## Modeling principle

Complex models do not automatically win. Every forecasting experiment includes simple baselines, and temporal validation is used when time ordering matters.
