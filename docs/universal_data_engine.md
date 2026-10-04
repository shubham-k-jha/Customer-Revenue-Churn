# Universal Data Engine

The project can operate in two modes:

1. **Domain mode** — the curated Telco churn and Online Retail II pipelines with business-specific feature engineering and temporal evaluation.
2. **Universal mode** — a schema-agnostic tabular engine for user-provided CSV, TSV, XLSX/XLS, and Parquet files.

## Supported formats

- `.csv`
- `.tsv`
- `.xlsx`
- `.xls`
- `.parquet` / `.pq`

Excel workbooks can also be inspected sheet-by-sheet using the IO helpers.

## Universal workflow

```text
Upload file
  -> format validation
  -> schema/profile
  -> missingness / cardinality / duplicate checks
  -> likely ID/date/target detection
  -> user confirms target and optional exclusions
  -> task inference: classification or regression
  -> leakage-safe preprocessing Pipeline
  -> model comparison
  -> holdout evaluation
  -> model artifact + JSON summary
```

## CLI

```bash
python -m src.universal.cli profile path/to/data.parquet
python -m src.universal.cli profile path/to/data.xlsx --sheet Sheet1

python -m src.universal.cli train path/to/data.csv --target churn
python -m src.universal.cli train path/to/data.parquet --target revenue --task regression --drop customer_id
```

## Important limitation

"Any dataset" cannot mean arbitrary unstructured data. Universal mode is designed for **tabular supervised ML**. The user must confirm the target when automatic detection is ambiguous. Domain-specific temporal forecasting, survival analysis, NLP, image models, causal inference, and multi-table relational modeling require specialized pipelines rather than blindly applying AutoML.

IDs and dates are treated as potentially dangerous predictors. The profiler flags them; the training CLI lets the user explicitly exclude them. High-cardinality categoricals should also be reviewed before training.

The preprocessing stack uses scikit-learn's `ColumnTransformer` and `Pipeline`, so numerical and categorical columns can receive separate transformations while learned preprocessing stays inside the model workflow. This is important for leakage control.

### Time-aware data

If a date column is selected, the engine sorts chronologically, holds out the latest 20% as the test period, and uses `TimeSeriesSplit` for cross-validation. This prevents future observations from being mixed into earlier training folds.
