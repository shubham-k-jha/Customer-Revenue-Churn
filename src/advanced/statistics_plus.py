from __future__ import annotations

import numpy as np
from scipy import stats


def _finite_1d(values, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError(f"{name} must contain at least one finite observation")
    return arr


def two_sample_effect(a, b):
    a = _finite_1d(a, "Group A")
    b = _finite_1d(b, "Group B")
    if len(a) < 2 or len(b) < 2:
        raise ValueError("At least two observations per group are required")
    t, p = stats.ttest_ind(a, b, equal_var=False)
    pooled = np.sqrt(
        ((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
        / (len(a) + len(b) - 2)
    )
    d = (a.mean() - b.mean()) / pooled if pooled > 0 else 0.0
    return {
        "welch_t": float(t),
        "p_value": float(p),
        "cohens_d": float(d),
        "n_a": int(len(a)),
        "n_b": int(len(b)),
    }


def bootstrap_mean_difference(a, b, n_boot=5000, seed=42):
    a = _finite_1d(a, "Group A")
    b = _finite_1d(b, "Group B")
    if n_boot < 1:
        raise ValueError("n_boot must be at least 1")

    rng = np.random.default_rng(seed)
    observed = float(a.mean() - b.mean())
    diffs = np.empty(int(n_boot), dtype=float)
    for i in range(int(n_boot)):
        diffs[i] = (
            rng.choice(a, len(a), replace=True).mean()
            - rng.choice(b, len(b), replace=True).mean()
        )
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {
        "difference": observed,
        "ci_low": float(lo),
        "ci_high": float(hi),
        "bootstrap_samples": int(n_boot),
    }
