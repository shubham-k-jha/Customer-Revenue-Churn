# Productionization Checklist

## Data
- Replace public sample with governed CRM source.
- Add a prediction timestamp and explicit future churn horizon.
- Build a longitudinal feature store so every feature is available before the prediction timestamp.
- Add schema/data-quality monitoring.

## Modeling
- Time-based validation rather than random split when production timestamps exist.
- Track drift in feature distributions and prediction probabilities.
- Calibrate probabilities on a validation set when probability accuracy matters.
- Refit on a controlled schedule and compare champion/challenger models.

## Decisioning
- Define contact capacity.
- Define intervention cost.
- Estimate saved contribution margin using controlled experiments.
- Measure incremental retention, not simply model accuracy.

## Governance
- Review protected/sensitive attributes and proxy risks.
- Document model version, data version, feature definitions and threshold.
- Log predictions and downstream actions.
- Add approval and rollback mechanisms.
