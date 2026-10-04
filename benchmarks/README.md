# Performance benchmark

`python scripts/benchmark.py` profiles deterministic synthetic tabular datasets at 10K, 100K and 1M rows. These rows are **not business benchmark data**; they exist only to measure scalability and catch accidental performance regressions.

Results are written to `reports/benchmarks/latest.json` and are intentionally not hard-coded into marketing claims. Compare runs on the same Python/dependency lock and hardware.
