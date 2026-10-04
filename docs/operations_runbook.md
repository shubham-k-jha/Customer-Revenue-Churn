# Operations Runbook

## Daily/weekly checks
1. Check API `/health`.
2. Check `/monitoring` prediction volume and risk-rate changes.
3. Run data-quality validation before scoring.
4. Compare feature distributions against the reference population with PSI.
5. Review model version and artifact hash.
6. Review prediction queue for unexpected missingness or probability collapse.

## Retraining
Retrain when:
- material data drift is detected,
- business definition changes,
- model performance deteriorates on newly labeled outcomes,
- a scheduled governance review requires it.

Never replace a production artifact without recording the new model metadata and evaluation report.

## Rollback
1. Identify the previous registered model artifact.
2. Verify its SHA-256 hash.
3. Restore the model path/configuration.
4. Restart the API.
5. Verify `/model` and `/health`.
6. Record the incident and rollback reason.
