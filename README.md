# Customer Revenue & Churn Intelligence Platform — v4.2

**Production-hardened universal analytics platform for Business Analytics, BI, Data Analytics and Data Science.**

> **Core idea:** turn messy tabular data into defensible business insight through a governed workflow: **ingest → profile → quality-gate → analyze → model → explain → report → serve → monitor**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-67%20passed-success)](tests/)
[![Version](https://img.shields.io/badge/version-4.2.0-informational)](pyproject.toml)

---

## 1. What this project actually is

This repository is **not just a churn model** and it is not a collection of disconnected notebooks.

It is a reusable analytics workbench with a curated customer-revenue/churn use case. The same engine can accept a new CSV, Excel or Parquet dataset and take it through profiling, data quality, statistical analysis, machine learning, time-series analysis, forecasting, explainability, reporting and API delivery.

The platform is deliberately evidence-driven:

- descriptive analysis is not presented as causal inference;
- prediction is not presented as causation;
- validation respects time ordering when the data is temporal;
- joins are checked for cardinality and row explosion;
- model features are checked for leakage and missing requirements;
- test data is used for reporting, not model selection;
- recommendations are derived from observed data rather than invented narratives.

### The business question

For a customer/revenue organization, the platform helps answer questions such as:

- Who are the highest-value customers?
- Which customer segments are growing or declining?
- Where is revenue or margin concentrated?
- Which customers show churn risk?
- What factors are associated with churn or revenue outcomes?
- Are observed differences statistically credible and practically important?
- What is likely to happen next in a time series?
- Which observations look anomalous?
- How should a model be evaluated, explained and monitored after deployment?

---

## 2. End-to-end architecture

```text
                         ┌─────────────────────────┐
                         │ CSV / Excel / Parquet   │
                         │ Multiple tabular tables │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Ingestion + Profiling   │
                         │ schema / types / IDs    │
                         │ dates / PII hints      │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Data Quality + Contract │
                         │ nulls / duplicates      │
                         │ outliers / constraints  │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
              ┌───────────────────┐      ┌────────────────────┐
              │ SQL / Join Layer  │      │ Analytics Layer    │
              │ DuckDB / SQL      │      │ stats / RFM / TS   │
              │ cardinality guard │      │ anomaly / survival │
              └─────────┬─────────┘      └─────────┬──────────┘
                        │                          │
                        └────────────┬─────────────┘
                                     ▼
                         ┌─────────────────────────┐
                         │ ML + Forecasting        │
                         │ CV / temporal split     │
                         │ calibration / threshold │
                         │ leakage-safe features   │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             Explainability      Reporting         Batch Scoring
             SHAP / permutation  Excel / Power BI  model bundles
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │ Governance + Monitoring │
                         │ registry / lineage      │
                         │ drift / Prometheus      │
                         └────────────┬────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │ FastAPI + Streamlit     │
                         │ Docker + Grafana        │
                         └─────────────────────────┘
```

For the full technical explanation, read **[`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md)**.

---

## 3. Main capabilities

### Data engineering and quality

- CSV, TSV, XLSX/XLS and Parquet ingestion
- schema and type inference
- date, ID and target candidate detection
- missingness, duplicates, cardinality and outlier diagnostics
- data-quality scoring and recommendations
- explicit data contracts
- invalid-type / invalid-date checks
- conservative multi-table join discovery
- one-to-one, one-to-many, many-to-one and many-to-many validation
- join explosion protection

### Business analytics

- customer/revenue profiling
- RFM segmentation
- retention and survival analysis
- revenue and customer concentration
- cohort-style analysis
- anomaly detection
- statistical relationships and group comparisons
- executive summaries with explicit caveats

### Statistics

- Pearson, Spearman and Kendall correlations
- p-values
- Benjamini-Hochberg FDR correction
- Welch t-test
- effect sizes / Cohen's d
- bootstrap confidence intervals
- normality diagnostics

### Machine learning

Supports:

- binary classification
- multiclass classification
- regression
- cross-validation model selection
- chronological validation for temporal datasets
- rare-class safeguards
- leakage-safe preprocessing
- final model refitting after selection
- model artifact/bundle validation

Evaluation includes:

- ROC-AUC
- PR-AUC
- F1
- balanced accuracy
- Brier score / calibration
- confusion matrix
- MAE
- RMSE
- R²
- threshold optimization
- decision-curve / net-benefit analysis

### Explainability

- SHAP infrastructure
- permutation importance
- individual-observation explanations
- explicit distinction between predictive association and causation

### Time series and forecasting

- timestamp normalization
- duplicate timestamp handling
- frequency/spacing diagnostics
- regular vs irregular series detection
- rolling statistics
- ADF and KPSS stationarity diagnostics
- differencing diagnostics
- ACF/PACF
- Ljung-Box residual diagnostics
- Jarque-Bera diagnostics
- spectral/dominant-period analysis
- additive/multiplicative decomposition
- trend and seasonal strength
- robust rolling-MAD anomalies
- calendar and Fourier features
- lag features
- leakage-safe rolling features
- naive, drift and seasonal-naive baselines
- ETS and ARIMA
- leakage-aware lag/Ridge forecasting
- expanding-window backtesting
- recursive multi-step forecasting

### Serving, governance and operations

- FastAPI
- Streamlit
- guarded read-only SQL execution/validation
- API-key comparison using constant-time comparison
- upload-size protection
- model registry with immutable hashes
- champion/challenger workflow
- experiment tracking
- model cards
- dataset/model lineage
- drift monitoring
- Prometheus metrics
- Grafana dashboard
- Docker Compose
- CI/security workflow

### BI delivery

- Excel reporting
- Power BI fact/dimension/date-table exports
- relationship metadata
- DAX measures
- import instructions

### Optional AI analytics agent

The agent is provider-neutral and designed to work with an OpenAI-compatible interface. It can translate natural-language questions into a guarded analytics plan and read-only SQL. Responses are schema-validated; malformed model output is not silently converted into fabricated answers.

---

## 4. Curated case studies

### IBM Telco Customer Churn

A customer churn use case with approximately 7K customers. The project uses it to demonstrate customer profiling, churn modeling, segmentation, explainability and business interpretation.

### UCI Online Retail II

A large transactional retail dataset with more than one million transactions. The retail workflow constructs customer snapshots and future-looking churn targets while avoiding future transactions as predictors.

**Important:** this repository does not hard-code fabricated benchmark metrics. Run the pipelines to generate current metrics in your environment.

---

## 5. Reproducible local demos

Small public datasets are bundled under `data/samples/` so the universal engine can be exercised without downloading a large business dataset:

- `classification_breast_cancer.csv`
- `regression_diabetes.csv`

These are **engineering/demo fixtures**, not replacements for the customer/revenue case studies.

---

## 6. Quick start

### Create an environment

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Run the release smoke test

```bash
python scripts/smoke_test.py
```

### Run the full tests

```bash
pytest -q
```

### Run the performance benchmark

```bash
python scripts/benchmark.py --rows 10000 100000 1000000
```

The benchmark uses deterministic synthetic data and is intended for engineering regression testing, not business claims.

### Validate a release tree

```bash
python scripts/validate_release.py
```

### Run the dashboard

```bash
streamlit run app/streamlit_app.py
```

### Run the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Health endpoint:

```text
http://localhost:8000/health
```

Metrics:

```text
http://localhost:8000/metrics
```

---

## 7. Docker deployment

The Compose stack contains:

| Service | Purpose |
|---|---|
| `api` | FastAPI analytics/model-serving API |
| `dashboard` | Streamlit Universal Data Lab |
| `prometheus` | Metrics collection |
| `grafana` | Monitoring dashboards |

Start it with:

```bash
docker compose up --build
```

Then verify the API health endpoint before treating the stack as healthy.

**Deployment caveat:** the v4.2.0 audit environment did not have a Docker daemon, so Compose was structurally validated but not live-launched during the offline audit. Live container validation is part of the deployment phase.

See:

- [`docs/operations_runbook.md`](docs/operations_runbook.md)
- [`docs/productionization.md`](docs/productionization.md)
- [`docs/security.md`](docs/security.md)

---

## 8. Repository structure

```text
.
├── api/                    # FastAPI application
├── app/                    # Streamlit dashboard
├── configs/                # platform/model policies
├── data/samples/           # small reproducible public demo data
├── docker/                 # container and Prometheus configuration
├── docs/                   # architecture, methodology, operations, project guide
├── models/                 # model artifact location
├── reports/                # generated report location
├── scripts/                # smoke, benchmark, release validation
├── sql/                    # business and retail SQL
├── src/                    # core platform implementation
├── tests/                  # unit/integration/regression tests
├── Makefile                # common engineering commands
├── pyproject.toml          # package metadata/dependencies
├── requirements.txt        # installable dependency ranges
└── docker-compose.yml      # local service stack
```

---

## 9. Quality and release status

The v4.2.0 release was audited from the packaged ZIP, extracted into a fresh directory and checked again.

- **67 tests passed**
- **1 test skipped** because the audit environment lacked the optional Parquet execution engine
- smoke test passed
- 10K/100K/1M synthetic benchmark passed
- Python compilation passed
- wheel build passed with the available local build tooling
- release artifact scan passed
- ZIP integrity passed
- no Python cache/build artifacts in the release archive
- Docker Compose configuration parsed successfully
- release documentation is version-consistent with v4.2.0

The exact audit scope and limitations are documented in [`docs/audit_report.md`](docs/audit_report.md).

---

## 10. Reproducibility

The project records or supports:

- deterministic random seeds where applicable
- dataset hashes
- Git commit metadata
- Python/platform metadata
- model artifact hashes
- run metadata
- release manifests

The dependency specification uses bounded versions. A complete resolved lockfile should be generated in a connected environment/CI using the procedure in [`docs/dependency_locking.md`](docs/dependency_locking.md). The offline audit environment could not truthfully generate that lockfile.

---

## 11. Security posture

The project includes defensive controls for:

- read-only SQL validation
- destructive SQL rejection
- multiple-statement rejection
- SQL comment rejection
- `SELECT INTO`, locking and unsafe administrative command rejection
- guarded model features
- upload-size enforcement
- API-key constant-time comparison
- malformed AI-agent response rejection
- data-quality gates
- join explosion protection

This is an analytics application, not a security-certified production system. Perform organization-specific threat modeling, secrets management, authentication/authorization, network controls and penetration testing before exposing it publicly.

---

## 12. How this maps to real jobs

### Business Analyst

Requirements → business questions → KPI definitions → SQL → statistical reasoning → recommendations → stakeholder-ready reporting.

### Data Analyst

Data cleaning → EDA → quality checks → SQL/Pandas → statistics → visualization → business conclusions.

### BI Analyst

Data model → fact/dimension tables → relationships → DAX → Power BI-ready exports → executive monitoring.

### Data Scientist

Feature engineering → validation → model selection → calibration → explainability → error analysis → deployment → monitoring.

### Analytics Engineer

Reusable pipelines → data contracts → SQL → reproducibility → tests → lineage → governed outputs.

The strongest portfolio story is therefore **not “I built a churn model.”** It is:

> **“I built a governed analytics platform that takes raw tabular data from ingestion through business analysis, predictive modeling, explainability, reporting, serving and monitoring.”**

---

## 13. Recommended reading order

1. [`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md) — complete project explanation
2. [`docs/architecture.md`](docs/architecture.md) — technical architecture
3. [`docs/methodology.md`](docs/methodology.md) — analytical methodology
4. [`docs/business_case.md`](docs/business_case.md) — business framing
5. [`docs/model_card.md`](docs/model_card.md) — model governance
6. [`docs/operations_runbook.md`](docs/operations_runbook.md) — operations
7. [`docs/security.md`](docs/security.md) — security controls
8. [`docs/interview_story.md`](docs/interview_story.md) — interview preparation

---

## 14. Final note

This project intentionally contains more engineering than a typical portfolio notebook. That is deliberate: the objective is to demonstrate that analytics can be made **reproducible, testable, explainable and deployable**, not merely visually impressive.

At the same time, the platform does not claim that every dataset will automatically produce a valid business conclusion. Data quality, domain knowledge, causal design and deployment context still matter.

**Version:** 4.2.0  
**License:** see [`LICENSE`](LICENSE)
