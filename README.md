# 🚀 Customer Revenue & Churn Intelligence Platform

<p align="center">
  <strong>From raw tabular data to defensible business decisions.</strong>
</p>

<p align="center">
  A production-oriented analytics platform combining
  <strong>Business Analytics · BI · Statistics · Machine Learning · Forecasting · Explainability · Governance</strong>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-4.2.0-blue)
![Tests](https://img.shields.io/badge/Tests-67%20Passed-success)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker&logoColor=white)

</p>

---

## 🎯 What Is This?

**Customer Revenue & Churn Intelligence Platform** is a reusable analytics workbench designed to turn messy tabular data into **reproducible, testable, explainable and deployable business intelligence**.

It is deliberately more than a churn model.

The platform provides an end-to-end workflow:

```text
INGEST
   ↓
PROFILE
   ↓
QUALITY GATE
   ↓
ANALYZE
   ↓
MODEL
   ↓
EXPLAIN
   ↓
REPORT
   ↓
SERVE
   ↓
MONITOR
```

The same engine can work with **CSV, Excel and Parquet** data and support workflows ranging from business analysis and BI to machine learning and forecasting.

---

# 💼 Business Questions

The platform is designed around questions that matter to customer and revenue teams:

| Business Question | Analytics Capability |
|---|---|
| Who are our highest-value customers? | Customer & revenue profiling |
| Which segments are growing or declining? | Segmentation & trend analysis |
| Where is revenue concentrated? | Concentration analysis |
| Which customers show churn risk? | Churn modeling |
| What factors are associated with churn? | Statistical analysis + ML |
| Are observed differences credible? | Hypothesis testing + effect sizes |
| What is likely to happen next? | Time-series forecasting |
| Which observations are unusual? | Anomaly detection |
| Can model predictions be explained? | SHAP + permutation importance |
| Can the system be monitored after deployment? | Drift + metrics + governance |

---

# 🏗️ Platform Architecture

```text
                         ┌──────────────────────────┐
                         │ CSV / Excel / Parquet    │
                         │ Multiple Tabular Tables  │
                         └─────────────┬────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │ Ingestion & Profiling    │
                         │ Schema · Types · IDs     │
                         │ Dates · Target · PII     │
                         └─────────────┬────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │ Data Quality & Contracts  │
                         │ Nulls · Duplicates       │
                         │ Outliers · Constraints    │
                         └─────────────┬────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
              ┌────────────────────┐      ┌────────────────────┐
              │ SQL / Join Layer   │      │ Analytics Layer    │
              │ DuckDB / SQL       │      │ Stats · RFM · TS   │
              │ Cardinality Guard  │      │ Anomaly · Survival │
              └──────────┬─────────┘      └──────────┬─────────┘
                         │                           │
                         └─────────────┬─────────────┘
                                       ▼
                         ┌──────────────────────────┐
                         │ ML & Forecasting         │
                         │ CV · Temporal Splits     │
                         │ Calibration · Thresholds │
                         │ Leakage-Safe Features    │
                         └─────────────┬────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
             │Explainability│   │  Reporting  │   │Batch Scoring│
             │ SHAP / Perm. │   │Excel / BI   │   │Model Bundle │
             └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                    │                 │                  │
                    └─────────────────┼──────────────────┘
                                      ▼
                         ┌──────────────────────────┐
                         │ Governance & Monitoring  │
                         │ Registry · Lineage       │
                         │ Drift · Prometheus       │
                         └─────────────┬────────────┘
                                       ▼
                         ┌──────────────────────────┐
                         │ FastAPI · Streamlit      │
                         │ Docker · Grafana         │
                         └──────────────────────────┘
```

---

# ⚡ Core Capabilities

## 🧹 Data Engineering & Quality

- CSV, TSV, XLSX/XLS and Parquet ingestion
- Automatic schema and type inference
- Date, ID and target candidate detection
- Missingness diagnostics
- Duplicate detection
- Cardinality analysis
- Outlier diagnostics
- Data-quality scoring
- Explicit data contracts
- Invalid-type and invalid-date checks
- Conservative multi-table join discovery
- Join cardinality validation
- Join explosion protection

---

## 📊 Business Analytics

- Customer and revenue profiling
- RFM segmentation
- Retention analysis
- Survival analysis
- Revenue concentration
- Customer concentration
- Cohort-style analysis
- Anomaly detection
- Statistical group comparisons
- Executive summaries
- Explicit analytical caveats

---

## 📐 Statistical Analysis

The platform supports:

- Pearson correlation
- Spearman correlation
- Kendall correlation
- P-values
- Benjamini–Hochberg FDR correction
- Welch's t-test
- Cohen's d
- Bootstrap confidence intervals
- Normality diagnostics

The platform explicitly separates **association from causation**.

---

# 🤖 Machine Learning

Supported problem types:

- Binary classification
- Multiclass classification
- Regression

### Validation

- Cross-validation
- Chronological validation
- Leakage-safe preprocessing
- Rare-class safeguards
- Final model refitting
- Model artifact validation

### Evaluation

- ROC-AUC
- PR-AUC
- F1
- Balanced accuracy
- Brier score
- Calibration
- Confusion matrix
- MAE
- RMSE
- R²
- Threshold optimization
- Decision-curve / net-benefit analysis

---

# 🔍 Explainability

Model outputs are not treated as black boxes.

The platform provides infrastructure for:

- **SHAP**
- **Permutation importance**
- Individual-observation explanations
- Feature-level interpretation
- Predictive association analysis

> **Important:** model explainability does not establish causality.

---

# 📈 Time-Series & Forecasting

The forecasting layer includes:

### Diagnostics

- Timestamp normalization
- Duplicate timestamp handling
- Frequency/spacing diagnostics
- Regular vs irregular series detection
- Rolling statistics
- ADF stationarity test
- KPSS stationarity test
- Differencing diagnostics
- ACF/PACF
- Ljung–Box diagnostics
- Jarque–Bera diagnostics
- Spectral / dominant-period analysis
- Additive/multiplicative decomposition
- Trend strength
- Seasonal strength

### Forecasting

- Naive baseline
- Drift baseline
- Seasonal-naive baseline
- ETS
- ARIMA
- Leakage-aware lag/Ridge forecasting
- Expanding-window backtesting
- Recursive multi-step forecasting

### Feature Engineering

- Calendar features
- Fourier features
- Lag features
- Leakage-safe rolling features

---

# 🛡️ Governance & Production Controls

This platform treats analytics as an engineering system, not just a notebook.

### Model Governance

- Model registry
- Immutable model hashes
- Champion/challenger workflow
- Experiment tracking
- Model cards
- Dataset lineage
- Model lineage

### Monitoring

- Data drift monitoring
- Prometheus metrics
- Grafana dashboards

### Security Controls

- Read-only SQL validation
- Destructive SQL rejection
- Multiple-statement rejection
- SQL comment rejection
- Unsafe administrative command rejection
- Upload-size enforcement
- Constant-time API-key comparison
- Malformed AI-agent response rejection
- Data-quality gates
- Join explosion protection

---

# 📊 BI Delivery

The platform can generate BI-ready outputs including:

- Excel reports
- Power BI fact tables
- Dimension tables
- Date tables
- Relationship metadata
- DAX measures
- Power BI import instructions

---

# 🧠 Optional AI Analytics Agent

The platform includes an optional provider-neutral analytics agent designed around an **OpenAI-compatible interface**.

It can:

```text
Natural Language Question
          ↓
     Query Planning
          ↓
   Schema Validation
          ↓
   Guarded SQL Generation
          ↓
     Read-Only Query
          ↓
     Result Analysis
          ↓
   Business Explanation
```

The system validates model output rather than silently accepting malformed or fabricated responses.

---

# 🧪 Curated Case Studies

## 1. IBM Telco Customer Churn

Approximately 7K customers.

Demonstrates:

- Customer profiling
- Churn analysis
- Segmentation
- Predictive modeling
- Explainability
- Business interpretation

## 2. UCI Online Retail II

A large transactional retail dataset containing **more than one million transactions**.

The workflow constructs customer-level snapshots and future-looking churn targets while avoiding future transactions as predictors.

> The repository does **not** hard-code fabricated benchmark metrics. Run the pipelines in your environment to generate current metrics.

---

# 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data | Pandas, NumPy |
| SQL | DuckDB / SQL |
| Statistics | SciPy / statistical tooling |
| Machine Learning | Scikit-learn |
| Explainability | SHAP |
| Dashboard | Streamlit |
| API | FastAPI |
| BI | Excel / Power BI |
| Monitoring | Prometheus / Grafana |
| Deployment | Docker Compose |
| Testing | Pytest |
| Version Control | Git / GitHub |

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/shubham-k-jha/Customer-Revenue-Churn.git
cd Customer-Revenue-Churn
```

## 2. Create a virtual environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# ✅ Verify the Installation

### Smoke test

```bash
python scripts/smoke_test.py
```

### Full test suite

```bash
pytest -q
```

### Release validation

```bash
python scripts/validate_release.py
```

### Performance benchmark

```bash
python scripts/benchmark.py --rows 10000 100000 1000000
```

The project documentation identifies these as the reproducibility and release-validation commands.

---

# 🖥️ Run the Dashboard

```bash
streamlit run app/streamlit_app.py
```

Then open the local Streamlit URL shown in your terminal.

---

# 🔌 Run the API

In another terminal:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Health check

```text
http://localhost:8000/health
```

### Metrics

```text
http://localhost:8000/metrics
```



---

# 🐳 Docker

The Docker Compose stack contains:

| Service | Purpose |
|---|---|
| `api` | FastAPI analytics/model-serving API |
| `dashboard` | Streamlit analytics dashboard |
| `prometheus` | Metrics collection |
| `grafana` | Monitoring dashboards |

Start everything:

```bash
docker compose up --build
```

> **Note:** the v4.2.0 offline audit structurally validated the Compose configuration but did not live-launch Docker because a Docker daemon was unavailable in the audit environment. Live container validation should therefore be performed in the deployment environment.

---

# 📁 Repository Structure

```text
Customer-Revenue-Churn/
│
├── api/                    # FastAPI application
├── app/                    # Streamlit dashboard
│
├── configs/                # Platform & model policies
│
├── data/
│   └── samples/            # Reproducible demo datasets
│
├── docker/                 # Container & monitoring configuration
│
├── docs/                   # Architecture, methodology & operations
│
├── models/                 # Model artifact location
├── reports/                # Generated reports
│
├── scripts/                # Smoke, benchmark & release validation
│
├── sql/                    # Business & retail SQL
├── src/                    # Core platform implementation
├── tests/                  # Unit & integration tests
│
├── Makefile                # Common engineering commands
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies
└── docker-compose.yml      # Local service stack
```

The repository structure follows the v4.2 release structure documented in the project README.

---

# 🧪 Release Quality

The **v4.2.0** release was audited from the packaged ZIP and extracted into a fresh directory.

### Audit Results

| Check | Result |
|---|---|
| Tests | ✅ 67 passed |
| Optional Parquet test | ⚠️ 1 skipped |
| Smoke test | ✅ Passed |
| 10K benchmark | ✅ Passed |
| 100K benchmark | ✅ Passed |
| 1M benchmark | ✅ Passed |
| Python compilation | ✅ Passed |
| Wheel build | ✅ Passed |
| Release artifact scan | ✅ Passed |
| ZIP integrity | ✅ Passed |
| Docker Compose parsing | ✅ Passed |
| Version consistency | ✅ Passed |

The audit also confirmed that no Python cache/build artifacts were included in the release archive.

---

# 🔬 Reproducibility

The platform records or supports:

- Deterministic random seeds
- Dataset hashes
- Git commit metadata
- Python/platform metadata
- Model artifact hashes
- Run metadata
- Release manifests

The dependency specification uses bounded versions. A complete resolved lockfile should be generated in a connected environment or CI using the project's dependency-locking procedure.

---

# 🎯 Why This Project Matters

This project intentionally goes beyond a typical portfolio notebook.

It demonstrates the complete analytics lifecycle:

```text
Raw Data
   ↓
Data Engineering
   ↓
Quality Assurance
   ↓
Business Analysis
   ↓
Statistical Reasoning
   ↓
Machine Learning
   ↓
Explainability
   ↓
Forecasting
   ↓
Reporting
   ↓
API / Dashboard
   ↓
Governance
   ↓
Monitoring
```

The strongest way to describe the project is:

> **I built a governed analytics platform that takes raw tabular data from ingestion through business analysis, predictive modeling, explainability, reporting, serving and monitoring.**

---

# 💼 Career Relevance

### Business Analyst

```text
Requirements
→ Business Questions
→ KPI Definitions
→ SQL
→ Statistical Reasoning
→ Recommendations
→ Stakeholder Reporting
```

### Data Analyst

```text
Data Cleaning
→ EDA
→ Data Quality
→ SQL / Pandas
→ Statistics
→ Visualization
→ Business Conclusions
```

### BI Analyst

```text
Data Model
→ Fact / Dimension Tables
→ Relationships
→ DAX
→ Power BI Outputs
→ Executive Monitoring
```

### Data Scientist

```text
Feature Engineering
→ Validation
→ Model Selection
→ Calibration
→ Explainability
→ Error Analysis
→ Deployment
→ Monitoring
```

### Analytics Engineer

```text
Reusable Pipelines
→ Data Contracts
→ SQL
→ Testing
→ Reproducibility
→ Lineage
→ Governed Outputs
```

---

# 📚 Documentation

Recommended reading order:

1. **[Project Guide](docs/PROJECT_GUIDE.md)** — complete project explanation
2. **[Architecture](docs/architecture.md)** — technical architecture
3. **[Methodology](docs/methodology.md)** — analytical methodology
4. **[Business Case](docs/business_case.md)** — business framing
5. **[Model Card](docs/model_card.md)** — model governance
6. **[Operations Runbook](docs/operations_runbook.md)** — operations
7. **[Security](docs/security.md)** — security controls
8. **[Interview Story](docs/interview_story.md)** — interview preparation

---

# 🚧 Project Status & Active Development

**Version:** `4.2.0`

**Status:** 🟢 Working · 🧪 Actively Tested · 🚧 Continuously Improving

This project is **working and actively maintained**, but it is **not considered finished**.

Version `4.2.0` is a functional, tested release with a production-oriented architecture. However, I am continuing to experiment, test, refine and expand the platform to make it more robust, intelligent, scalable and useful for real-world analytics.

### 🔨 Current Development Focus

- 🔧 Improving existing analytics workflows
- 🧪 Expanding test coverage and edge-case handling
- ⚡ Improving performance and scalability
- 📊 Adding more advanced business analytics
- 🤖 Improving the optional AI analytics agent
- 📈 Expanding forecasting and time-series capabilities
- 🧠 Improving ML diagnostics and explainability
- 🛡️ Strengthening governance, validation and monitoring
- 🔄 Improving data-drift and model-drift detection
- 🔗 Expanding data lineage and reproducibility
- 🐳 Improving deployment and containerization
- 🎨 Improving the dashboard and user experience
- 📚 Expanding documentation, examples and practical use cases

### 🚀 What's Next

The platform will continue evolving through incremental releases.

The goal is not simply to add more features, but to continuously improve:

```text
Reliability
    ↓
Accuracy
    ↓
Performance
    ↓
Explainability
    ↓
Usability
    ↓
Production Readiness
```

> **This is a work in progress. I am continuously building, testing, fixing and improving the system rather than treating the current release as the final version.**

⭐ **If you find the project interesting, follow the repository and check back for future releases and improvements.**

---

# ⚠️ Important Limitations

This is an analytics application, **not a security-certified production system**.

Before exposing it publicly in a real organization, perform appropriate:

- Threat modeling
- Secrets management
- Authentication / authorization
- Network controls
- Security review
- Penetration testing
- Domain-specific validation

Automated analytics also does not guarantee valid business conclusions. **Data quality, domain knowledge, causal design and deployment context remain critical.**

---

# 📌 License

See [`LICENSE`](LICENSE).

---

<p align="center">
  <strong>Built to demonstrate that analytics can be reproducible, testable, explainable and deployable — not merely visually impressive.</strong>
</p>

<p align="center">
  <sub>Customer Revenue & Churn Intelligence Platform · v4.2.0</sub>
</p>
