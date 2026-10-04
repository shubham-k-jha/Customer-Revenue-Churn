# Complete Project Guide — Customer Revenue & Churn Intelligence Platform v4.2

## 1. Executive overview

This project is a **universal tabular analytics and decision-support platform** with a customer revenue/churn case-study track.

It was designed around a practical problem: real organizations rarely hand an analyst a perfectly shaped dataset and ask for one isolated model. A real workflow starts with uncertain data, ambiguous business questions, multiple tables, missing values, inconsistent types and competing analytical approaches. The result must then be explainable to business users, reproducible by another analyst and operational enough to serve or monitor.

The platform therefore covers the lifecycle:

**raw data → ingestion → profiling → quality → contracts → SQL/joins → statistical analysis → feature engineering → validation → modeling/forecasting → evaluation → explanation → business reporting → API/dashboard → governance → monitoring**

The architecture is intentionally modular so the universal engine can be reused on datasets that have nothing to do with telecom churn.

---

## 2. The problem it solves

### Traditional portfolio project

A typical portfolio project looks like:

```text
CSV → Pandas → EDA → model → accuracy → notebook
```

That is useful for learning but weak evidence of production analytics ability.

### This project

The platform instead treats analytics as a controlled decision pipeline:

```text
Question
   ↓
Dataset discovery
   ↓
Schema + data quality
   ↓
Business definitions
   ↓
Safe transformations / joins
   ↓
Descriptive + inferential analysis
   ↓
Prediction / forecasting when justified
   ↓
Validation + uncertainty
   ↓
Explainability
   ↓
Business recommendation
   ↓
Report / API / dashboard
   ↓
Monitoring + governance
```

The important design choice is that **not every problem should become machine learning**. The platform supports simpler analytics first and adds predictive models where they provide incremental value.

---

## 3. Major architectural layers

### 3.1 Ingestion

The ingestion layer accepts common business tabular formats:

- CSV
- TSV
- XLSX/XLS
- Parquet

The objective is to normalize the input into an analysis-friendly representation without hiding important assumptions.

Key concerns:

- encoding
- file size
- missing values
- duplicate rows
- column types
- date parsing
- identifier candidates
- target candidates

---

### 3.2 Profiling

Profiling answers: **“What is actually in this dataset?”**

It examines:

- row/column counts
- data types
- missingness
- uniqueness/cardinality
- likely IDs
- likely dates
- likely target columns
- numerical summaries
- categorical distributions
- possible PII hints

This is deliberately separated from business interpretation. A column that looks like a target statistically is not automatically the correct business target.

---

### 3.3 Data quality

The quality layer prevents the rest of the pipeline from silently operating on broken assumptions.

Checks include:

- missingness
- duplicate records
- invalid dates
- unexpected types
- high-cardinality fields
- outliers
- constant columns
- contract violations
- suspicious distributions

The system can produce a quality score and recommendations, but the score is a diagnostic—not a universal measure of “good data.”

---

## 4. Data contracts

A data contract converts informal assumptions into executable rules.

Examples:

```text
customer_id must be present
customer_id should be unique
age must be within an allowed range
churn should be in {0, 1}
revenue should not be negative
required columns cannot exceed a null threshold
```

This matters because production analytics fails more often from **schema/data drift and broken assumptions** than from a lack of sophisticated algorithms.

---

## 5. Multi-table analytics

Business datasets are often relational rather than one flat table.

The platform therefore investigates candidate joins using:

- key overlap
- uniqueness
- candidate relationship type
- preview joins
- expected cardinality
- row-count changes

Supported relationship reasoning includes:

- one-to-one
- one-to-many
- many-to-one
- many-to-many

Many-to-many joins are especially dangerous because they can multiply rows and inflate revenue, counts or other metrics. The platform includes join explosion protection instead of silently accepting the result.

---

## 6. SQL layer and security

SQL is treated as a first-class analytics interface.

The guarded SQL path is designed for **read-only analytics**. It rejects destructive or administrative operations and unsafe patterns such as:

- `DROP`
- `DELETE`
- `UPDATE`
- `INSERT`
- `ALTER`
- `TRUNCATE`
- multiple statements
- comments used to alter parsing context
- `SELECT INTO`
- locking clauses
- administrative commands

Quoted strings are handled so legitimate text values are not incorrectly treated as SQL keywords.

The principle is simple: an analytics assistant should be able to query data without being allowed to mutate the database.

---

## 7. Business analytics layer

The platform contains reusable analytics that commonly appear in customer/revenue work.

### RFM segmentation

Customers can be segmented using:

- Recency
- Frequency
- Monetary value

This supports questions such as:

- Who are high-value active customers?
- Which customers are becoming inactive?
- Which groups need retention attention?

### Retention / survival

Kaplan-Meier analysis can estimate retention/survival curves when the dataset contains appropriate duration and event information.

The implementation validates event encoding and duration values rather than assuming that any binary-looking field is valid.

### Anomaly detection

Both statistical and model-based approaches are supported, including IQR-style detection and Isolation Forest.

The project explicitly distinguishes:

> **anomaly ≠ bad data**

An unusual transaction can be a legitimate high-value event, fraud, a data error or an emerging business pattern. Investigation is required.

---

## 8. Statistical analysis

The statistical layer supports relationships and group comparisons rather than blindly ranking correlations.

Included methods include:

- Pearson correlation
- Spearman correlation
- Kendall correlation
- p-values
- multiple-testing correction using Benjamini-Hochberg FDR
- Welch's t-test
- Cohen's d
- bootstrap confidence intervals
- normality diagnostics

The important business distinction is between:

```text
statistical significance
```

and

```text
practical/business significance
```

A tiny effect can be statistically significant in a huge dataset. A useful decision therefore needs effect size and business context, not only a p-value.

---

## 9. Machine-learning workflow

The ML system supports:

- binary classification
- multiclass classification
- regression

The general workflow is:

```text
Target definition
      ↓
Feature selection
      ↓
Train/validation/test design
      ↓
Preprocessing pipeline
      ↓
Cross-validation/model selection
      ↓
Hyperparameter/model comparison
      ↓
Final refit
      ↓
Held-out test evaluation
      ↓
Calibration/threshold analysis
      ↓
Explainability
      ↓
Model artifact + metadata
```

### Temporal leakage protection

If the data is time-dependent, random splitting can allow the future to influence the past.

The platform supports chronological validation and leakage-safe feature generation. This is critical for customer churn, finance, operations and forecasting use cases.

### Rare-class handling

Classification with very few positive examples can break ordinary cross-validation. The system checks class counts and adjusts validation logic instead of blindly requesting an impossible number of folds.

### Multiclass handling

The final multiclass XGBoost objective is configured consistently with the number of classes rather than relying on binary defaults.

---

## 10. Model evaluation

The platform deliberately avoids treating accuracy as the universal metric.

### Classification

Available metrics include:

- ROC-AUC
- PR-AUC
- F1
- balanced accuracy
- Brier score
- log loss/calibration-related diagnostics
- confusion matrix

For imbalanced churn problems, **PR-AUC and class-specific metrics** can be more informative than raw accuracy.

### Threshold selection

A probability model does not automatically tell the business which customers to classify as “at risk.” Threshold optimization allows the operating point to be selected according to the business trade-off between false positives and false negatives.

### Decision curve analysis

Net-benefit/decision-curve analysis can be used to evaluate whether using the model provides value over treating everyone or treating no one under a defined decision framework.

### Regression

- MAE
- RMSE
- R²

MAE is often easier to explain operationally, while RMSE penalizes large errors more heavily.

---

## 11. Explainability

The project supports:

- SHAP
- permutation importance
- individual prediction explanations

The key governance rule is:

> **A feature explaining a prediction does not prove that changing that feature will cause the outcome to change.**

For example, if contract type is strongly associated with churn predictions, the model does not prove that changing a customer's contract will causally prevent churn.

Causal claims require an appropriate causal design, such as randomized experimentation or a defensible quasi-experimental strategy.

---

## 12. Time-series analysis

The time-series subsystem is substantially deeper than simple rolling averages.

Diagnostics include:

- timestamp normalization
- duplicate timestamp aggregation
- frequency/spacing analysis
- regular/irregular classification
- rolling statistics
- ADF stationarity testing
- KPSS testing
- first/second differencing
- ACF/PACF
- Ljung-Box residual autocorrelation
- Jarque-Bera residual diagnostics
- spectral analysis
- additive/multiplicative decomposition
- trend strength
- seasonal strength
- robust rolling-MAD anomalies

Constant or degenerate series are handled explicitly so the system does not emit meaningless statistical results.

---

## 13. Forecasting

Forecasting models include:

- naive
- drift
- seasonal naive
- ETS
- ARIMA
- leakage-aware lag/Ridge model

Evaluation uses expanding-window/backtesting rather than simply fitting on all historical data and claiming the resulting forecast is validated.

The recursive forecasting implementation is specifically designed so future test values are not accidentally fed back into lag features during multi-step prediction.

This is an important distinction between a model that appears accurate in a notebook and one that approximates its actual deployment behavior.

---

## 14. Model governance

The platform includes model registry concepts for:

- champion/challenger models
- immutable SHA-256 hashes
- promotion/archive states
- model metadata
- lineage

A model should be reproducible and identifiable after deployment. Knowing only the filename `model.pkl` is not enough.

---

## 15. Experiment tracking and lineage

Run metadata can include:

- dataset hash
- Git commit
- Python version
- platform information
- run timestamp
- model metadata
- configuration

This makes it possible to answer:

> “Exactly what data, code and environment produced this result?”

That question becomes critical once analytics influences real decisions.

---

## 16. Monitoring

The project contains drift monitoring and Prometheus metrics.

The monitoring stack is:

```text
API
 ↓
Prometheus metrics
 ↓
Prometheus
 ↓
Grafana
```

Metrics cover API behavior and prediction activity, while drift monitoring provides a statistical signal that the input distribution may have changed.

A drift alert is **not automatically a model failure**. It means the distribution should be investigated.

---

## 17. API

FastAPI exposes health, metrics, model and analytics-related endpoints.

The API includes defensive behavior for:

- invalid uploads
- oversized uploads
- malformed content lengths
- invalid analytical inputs
- SQL safety
- model feature mismatches

Health should be checked separately from deeper analytical readiness.

---

## 18. Streamlit dashboard

The dashboard acts as the interactive Universal Data Lab.

Major workflow areas include:

- universal data profiling
- data quality
- multi-table analysis
- modeling
- segmentation
- forecasting
- AI agent
- deep time-series diagnostics

The dashboard is intended for exploration and communication. Production serving should use the API and governed model artifacts rather than treating the UI as the sole production interface.

---

## 19. Power BI and Excel

The project recognizes that many analytics outputs ultimately go to business users rather than Python environments.

Power BI exports can include:

- fact tables
- dimension tables
- date tables
- relationship metadata
- DAX measures
- import instructions

Excel reporting provides a familiar deliverable for stakeholders and operational teams.

---

## 20. AI analytics agent

The AI layer is deliberately constrained.

A natural-language question can become an analytics plan and read-only SQL request, but the system does not trust model-generated text blindly.

Controls include:

1. provider-neutral adapter;
2. structured response expectations;
3. schema validation;
4. read-only SQL guardrails;
5. explicit caveats;
6. no fabricated fallback answer when the model response is malformed.

The agent is therefore an **assistant to the analytics workflow**, not a replacement for validation.

---

## 21. Testing strategy

The repository has a broad regression suite covering:

- universal ingestion
- quality checks
- API behavior
- advanced analytics
- deep analytics
- ML edge cases
- time-series diagnostics
- retail temporal logic
- production behavior
- release hardening
- security boundaries

The v4.2.0 audit result was:

> **67 passed, 1 skipped**

The skipped test depends on an optional Parquet engine unavailable in the audit environment.

The project also includes:

```bash
python scripts/smoke_test.py
```

which performs a compact end-to-end sanity check.

---

## 22. Performance testing

The benchmark generates deterministic synthetic datasets at:

- 10,000 rows
- 100,000 rows
- 1,000,000 rows

It measures profiling throughput and is intended to detect performance regressions.

The v4.2.0 audit recorded approximately:

| Rows | Observed throughput |
|---:|---:|
| 10K | 1.04M rows/sec |
| 100K | 1.42M rows/sec |
| 1M | 1.16M rows/sec |

These numbers are environment-specific and should **not** be presented as a universal production SLA.

---

## 23. Reproducibility and dependency locking

The project keeps bounded dependency requirements and documents the connected-environment locking workflow.

A fully resolved lockfile was deliberately not fabricated during the offline audit because the environment could not resolve the package index and lacked several runtime packages.

In CI/connected development, generate the lockfile using the documented procedure and review dependency changes as part of release management.

---

## 24. Docker deployment

The Compose architecture contains:

```text
api
 ├── FastAPI
 └── analytics/model-serving

dashboard
 └── Streamlit

prometheus
 └── metrics collection

grafana
 └── monitoring visualization
```

The v4.2.0 offline audit validated the Compose configuration structurally but could not start Docker because the audit environment had no Docker daemon.

Therefore, live deployment remains a separate validation phase.

---

## 25. What is proven vs what is not

### Proven in the v4.2.0 audit

- source code compiles
- test suite passes except the documented optional Parquet skip
- smoke test passes
- synthetic benchmark passes
- wheel can be built with available tooling
- release package is internally clean
- ZIP round-trip is valid
- Docker Compose configuration parses
- release versioning is consistent

### Still requires deployment/internet-enabled validation

- live Docker containers
- Prometheus/Grafana integration
- Streamlit browser behavior
- external package installation from a clean machine
- complete dependency lock resolution
- real IBM Telco execution in the target environment
- full UCI Online Retail II download/execution
- cloud deployment
- production CPU/memory behavior
- external LLM provider integration

This distinction is intentional. A serious project should state what was actually tested.

---

## 26. How to use the project in an interview

### 30-second explanation

> “I built a universal analytics platform around a customer revenue and churn use case. It takes raw tabular data through profiling, quality checks, SQL and relational validation, statistical analysis, segmentation, leakage-safe ML and forecasting, then adds explainability, Power BI/Excel outputs, an API, monitoring and model governance. I also built tests, smoke checks and release validation so it behaves more like an engineering product than a notebook.”

### If asked why it is more than a churn project

> “Churn is the business case study, but the underlying engine is dataset-agnostic. I wanted the architecture to solve the broader analyst problem: starting from an unfamiliar dataset and producing defensible insight.”

### If asked about leakage

Explain temporal splits, leakage-safe rolling/lag features and recursive forecasting. Give a concrete example where future observations must not enter the feature vector.

### If asked about SHAP

Explain that SHAP helps attribute model predictions to input features, but it does not establish causality.

### If asked about statistical significance

Explain p-values, effect size, confidence intervals and multiple-testing correction, then connect the result to business materiality.

### If asked about production readiness

Discuss tests, contracts, artifact hashes, lineage, API validation, monitoring, Docker and CI—and clearly state what still requires live deployment validation.

---

## 27. Known limitations

This is a portfolio-grade engineering platform, not a universal automatic decision-maker.

Important limitations:

- automated target detection can be wrong;
- automated join discovery requires business validation;
- model performance depends on the supplied dataset;
- statistical significance does not establish causality;
- drift detection needs operational thresholds and investigation;
- AI-generated analytical plans still require validation;
- Docker/cloud deployment needs environment-specific security and infrastructure configuration;
- production authentication/authorization is not equivalent to a full enterprise IAM system;
- benchmark throughput depends on hardware and software versions.

The correct response to these limitations is **explicit governance**, not pretending they do not exist.

---

## 28. Final assessment

The project should now be treated as a **frozen v4.2 baseline** for deployment testing.

Do not keep adding algorithms before deployment. The next useful phase is to expose the system to:

1. a clean machine;
2. real datasets;
3. a live Docker environment;
4. browser/UI interaction;
5. actual API calls;
6. monitoring traffic;
7. realistic memory/CPU load;
8. deployment failure and recovery scenarios.

That is where the remaining engineering weaknesses—if any—will become visible.
