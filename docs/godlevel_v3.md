# God-level v3 base architecture

## Product flow

`Upload → Profile → Quality Gate → Join/Model → Validate → Explain → BI/Excel → Monitor`

## Agent contract

The LLM is an orchestrator, not the source of truth. It can propose an analysis plan and read-only SQL. SQL passes through the existing destructive-statement/multiple-statement guard before it can be used. The agent must surface caveats and cannot claim observational causality.

## Multi-table design

`src/advanced/multitable.py` scores candidate keys using overlap and uniqueness. Suggestions are never executed automatically. A user or application must explicitly select a join key and join type.

## Modeling design

The universal engine supports:
- binary classification
- multiclass classification
- regression
- chronological validation when a date column is supplied

Model selection is performed on development cross-validation; the held-out test period remains reporting-only.

## Analytics extensions

- RFM segmentation
- lag forecasting baseline
- Welch's t-test + Cohen's d
- bootstrap confidence intervals

These are deliberately conservative primitives intended to be composed into business workflows rather than marketed as autonomous scientific discovery.

## Recruiter demonstration

The strongest demo sequence is:
1. Upload a real CSV/XLSX/Parquet dataset.
2. Inspect schema, quality and possible PII.
3. Select a target or ask the analytics agent for a plan.
4. Run leakage-aware modeling.
5. Inspect CV comparison and test metrics separately.
6. Generate Excel management output.
7. Explain the result and limitations.
8. Show API/monitoring endpoints.
