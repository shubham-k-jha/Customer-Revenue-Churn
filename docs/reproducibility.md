# Reproducibility standard

The platform uses `uv.lock` as the authoritative full dependency lock. `requirements.txt` remains a human-readable compatibility specification.

## Fresh environment

```bash
uv sync --frozen
uv run python scripts/smoke_test.py
```

The smoke test uses deterministic, bundled scikit-learn public datasets and exercises profiling, classification, regression, API health, upload profiling and SQL guardrails.

Every analytical run should record the dataset hash, code revision, Python/platform information and configuration. The governance lineage utilities provide those fields for model/report artifacts.

## Release rule

A release is not considered valid unless:

1. the lockfile is present and frozen installation succeeds;
2. the full test suite passes (except explicitly documented optional-environment skips);
3. the smoke test passes;
4. release validation finds no caches/build artifacts;
5. the package can be built from a clean checkout;
6. generated benchmark results are clearly marked synthetic and are not presented as business outcomes.
