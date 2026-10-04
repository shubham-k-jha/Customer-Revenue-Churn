# Interview Story

**Problem:** Analysts repeatedly receive heterogeneous business datasets and spend time profiling, cleaning, querying, modeling and packaging results.

**Solution:** A reusable Data Science Workbench that accepts common tabular formats, performs quality checks, supports supervised ML with leakage-safe validation, generates Excel and dashboard outputs, and exposes governed APIs.

**Technical depth:** Python, Pandas, SQL, DuckDB/PostgreSQL, scikit-learn, XGBoost, SHAP, FastAPI, Streamlit, Docker, CI/CD, monitoring and model governance.

**Key design decision:** The platform never treats automatic inference as ground truth. Ambiguous targets require user confirmation, dates trigger chronological evaluation, and SQL is validated before execution.

**Production story:** Model artifacts are hashed and registered, runs record dataset/code metadata, drift can be monitored, and Prometheus/Grafana are available for service observability.
