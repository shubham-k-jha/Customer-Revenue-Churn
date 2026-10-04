# God-level Platform Architecture

## Product contract

The repository is a reusable tabular Data Science and Business Intelligence workbench. It accepts CSV/TSV/XLSX/XLS/Parquet, profiles the data, runs quality gates, supports supervised classification/regression, supports chronological validation when a date column is selected, generates Excel output, exposes safe API endpoints, and retains a curated churn/retention case study.

## Core principles

1. **Evidence before conclusions.** Every business claim should trace to data, SQL/statistics, or a model artifact.
2. **No test leakage.** Model selection happens on development cross-validation; final test metrics are reporting only.
3. **Time matters.** Explicit date selection triggers chronological holdout and TimeSeriesSplit.
4. **No blind target inference.** Ambiguous numeric targets require explicit task selection.
5. **No unrestricted SQL.** Natural-language SQL must pass read-only validation before execution.
6. **No causal overclaiming.** Predictive association and causal effects are separate claims.
7. **Reproducibility.** Dataset/model hashes, code version and environment metadata are tracked.
8. **Production observability.** Data quality, drift, latency and errors should be monitored.

## Agent architecture

`User -> Planner -> Profiler/Quality -> SQL/Stats/ML tools -> Validation -> Evidence store -> Excel/Dashboard/Report`.

The LLM is an orchestrator, not an authority. Tool boundaries enforce SQL safety, file limits and deterministic validation.

## Model governance

Champion/challenger selection should be driven by predeclared business metrics. Models are registered with artifact hashes and metadata. Production promotion should require a validation report and an approved model card.

## Deployment

Docker Compose provides API, dashboard, Prometheus and Grafana. MLflow is supported as an optional experiment backend; the repository's JSONL tracker remains available when MLflow is not installed.
