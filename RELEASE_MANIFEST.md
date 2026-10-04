# Release Manifest — 4.2.0

## Release theme

Production hardening: reproducibility, validation, performance regression testing, CI quality gates and portfolio-grade documentation.

## Included

- Universal CSV/TSV/XLSX/XLS/Parquet analytics engine
- Data quality, contracts, profiling and conservative multi-table joins
- Classification, multiclass classification and regression
- Leakage-safe chronological validation and cross-validation model selection
- Calibration, threshold optimization, explainability and statistical inference
- Deep time-series diagnostics and forecasting/backtesting
- Retention/survival, segmentation and anomaly detection
- Excel and Power BI exports
- Governed API, batch scoring, registry, lineage and monitoring
- Optional read-only SQL/LLM analytics agent
- Docker Compose, Prometheus and Grafana configuration
- CI and secret scanning
- Telco churn and UCI Online Retail II pipelines
- Bundled scikit-learn public demo datasets
- `scripts/smoke_test.py`
- `scripts/benchmark.py`
- `scripts/validate_release.py`
- Reproducibility/performance/dependency-locking documentation

## Validation

- **67 passed, 1 skipped**
- Smoke test: PASS
- 10K/100K/1M benchmark: PASS
- Python compilation: PASS
- Wheel build: PASS using the audited environment's installed build tooling
- Release artifact scan: PASS
- Parquet test skip is environment-limited because the audit environment cannot resolve/install the Parquet engine.
- Complete dependency lockfile is intentionally absent from this offline audit build; connected CI is configured to generate and verify it rather than committing a fabricated lock.
