from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def rfm_segment(
    df: pd.DataFrame,
    customer_col: str,
    date_col: str,
    amount_col: str,
    n_segments: int = 4,
) -> pd.DataFrame:
    """Create RFM features and deterministic KMeans segments.

    Segment IDs are identifiers, not quality rankings. For fewer than two
    customers, clustering is undefined, so the single customer is assigned
    segment 0 rather than crashing. Requested segment counts are clipped to
    the number of customers.
    """
    for c in (customer_col, date_col, amount_col):
        if c not in df.columns:
            raise KeyError(c)
    if n_segments < 1:
        raise ValueError("n_segments must be at least 1")

    x = df[[customer_col, date_col, amount_col]].copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce", utc=True, format="mixed")
    x[amount_col] = pd.to_numeric(x[amount_col], errors="coerce")
    x = x.dropna(subset=[customer_col, date_col, amount_col])
    if x.empty:
        raise ValueError("No usable rows for RFM")

    ref = x[date_col].max() + pd.Timedelta(days=1)
    r = (
        x.groupby(customer_col)
        .agg(
            recency=(date_col, lambda s: int((ref - s.max()).days)),
            frequency=(date_col, "count"),
            monetary=(amount_col, "sum"),
        )
        .reset_index()
    )

    if len(r) == 1:
        r["segment_id"] = 0
        return r

    n_segments = min(int(n_segments), len(r))
    z = StandardScaler().fit_transform(r[["recency", "frequency", "monetary"]])
    r["segment_id"] = KMeans(
        n_clusters=n_segments, n_init=20, random_state=42
    ).fit_predict(z)
    return r
