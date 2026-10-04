# Performance and scalability testing

The benchmark harness measures the generic profiler at 10K, 100K and 1M rows. The benchmark dataset is deterministic synthetic data and is **not** used to claim business performance.

Run:

```bash
python scripts/benchmark.py
```

For a production capacity claim, rerun on the target CPU/RAM/storage profile and retain the generated JSON alongside the release. Do not compare numbers across materially different environments without recording the environment metadata.

Large-file API limits are enforced at 100 MB by default. The API reads uploads in bounded chunks rather than trusting a client-supplied `Content-Length` alone.
