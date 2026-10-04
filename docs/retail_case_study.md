# Real-World Scale Validation: UCI Online Retail II

## Why this dataset

The UCI Online Retail II dataset contains **1,067,371 real transactions** from a UK-based registered non-store online retailer between 2009-12-01 and 2011-12-09. It includes invoice number, product, quantity, invoice date, unit price, customer ID and country. UCI classifies it as business data with classification/regression/clustering tasks and publishes it under CC BY 4.0. See the official UCI record: https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii

## Churn definition

This dataset does not provide a churn label. We therefore create a **forecastable behavioral target from real transaction history**:

> A customer is churned at snapshot date *t* when they had positive-quantity purchasing activity during the preceding observation window but make no positive-quantity purchase during the next 90 days.

The target is created strictly from future transactions, while features use only transactions before the snapshot date.

## Leakage controls

- No future transactions enter feature construction.
- The target window starts at the snapshot date.
- Train/validation/test are separated chronologically.
- The probability threshold is chosen on validation only.
- The final model is refit on train+validation.
- The final test period is evaluated once.
- Refund/cancellation records are not treated as positive purchases.

## Scale strategy

The raw XLSX is approximately 43.5 MB. The pipeline converts it once to compressed Parquet and then uses DuckDB for feature construction. This avoids repeatedly loading the full workbook into memory and makes SQL-style analytical processing practical.

## Important interpretation limit

This is behavioral churn prediction, not causal inference. A high predicted churn probability means the customer's observed transaction pattern resembles customers who subsequently became inactive; it does not prove that a particular retention action will prevent churn.
