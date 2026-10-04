from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


def lag_forecast(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    horizon: int = 7,
    lags: int = 14,
):
    """Leakage-aware lag baseline with spacing-aware future timestamps.

    Observations are aggregated by timestamp. The forecast horizon means
    future periods, not necessarily calendar days; the median observed time
    delta is used to extend irregular/weekly/monthly series safely.
    """
    if horizon < 1 or lags < 1:
        raise ValueError("horizon and lags must be at least 1")
    if date_col not in df.columns or value_col not in df.columns:
        raise KeyError("date_col/value_col must exist in the input dataframe")

    x = df[[date_col, value_col]].copy()
    x[date_col] = pd.to_datetime(
        x[date_col], errors="coerce", utc=True, format="mixed"
    )
    x[value_col] = pd.to_numeric(x[value_col], errors="coerce")
    x = (
        x.dropna()
        .sort_values(date_col)
        .groupby(date_col, as_index=False)[value_col]
        .sum()
    )
    if len(x) < max(40, lags + 10):
        raise ValueError("Not enough observations for forecasting baseline")

    deltas = x[date_col].diff().dropna().dt.total_seconds()
    positive_deltas = deltas[deltas > 0]
    if positive_deltas.empty:
        raise ValueError("Date column must contain at least two distinct timestamps")
    step = pd.to_timedelta(float(positive_deltas.median()), unit="s")

    for lag in range(1, lags + 1):
        x[f"lag_{lag}"] = x[value_col].shift(lag)
    x = x.dropna().reset_index(drop=True)
    cut = max(1, int(len(x) * 0.8))
    train, test = x.iloc[:cut], x.iloc[cut:]
    if test.empty:
        raise ValueError("Forecast holdout is empty; provide more observations")

    cols = [f"lag_{i}" for i in range(1, lags + 1)]
    model = Ridge(alpha=1.0).fit(train[cols], train[value_col])
    pred = model.predict(test[cols])

    # x is ordered with lag_1 = immediately previous observation.
    history = x[value_col].tolist()
    future = []
    for _ in range(horizon):
        row = pd.DataFrame([history[-lags:][::-1]], columns=cols)
        y = float(model.predict(row)[0])
        future.append(y)
        history.append(y)

    future_dates = [x[date_col].max() + step * (i + 1) for i in range(horizon)]
    return {
        "metrics": {
            "mae": float(mean_absolute_error(test[value_col], pred)),
            "rmse": float(mean_squared_error(test[value_col], pred) ** 0.5),
        },
        "forecast": pd.DataFrame({date_col: future_dates, value_col: future}),
        "frequency_seconds": float(step.total_seconds()),
    }
