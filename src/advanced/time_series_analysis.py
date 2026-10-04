from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.signal import periodogram
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose


@dataclass(frozen=True)
class TimeSeriesConfig:
    date_col: str
    value_col: str
    seasonal_period: int | None = None
    max_lags: int = 24
    rolling_window: int = 7


def prepare_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    """Validate, normalize, sort and aggregate a univariate time series."""
    if date_col not in df.columns or value_col not in df.columns:
        raise KeyError(f"{date_col}/{value_col} must exist")
    x = df[[date_col, value_col]].copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce", utc=True, format="mixed")
    x[value_col] = pd.to_numeric(x[value_col], errors="coerce")
    x = x.dropna().groupby(date_col, as_index=True)[value_col].sum().sort_index()
    if len(x) < 8:
        raise ValueError("At least 8 valid observations are required")
    if not x.index.is_monotonic_increasing or x.index.has_duplicates:
        raise ValueError("Time series index must be sorted and unique after aggregation")
    return x.astype(float)


def infer_frequency(series: pd.Series) -> dict:
    idx = pd.DatetimeIndex(series.index)
    if len(idx) < 2:
        raise ValueError("At least two timestamps are required")
    deltas = idx.to_series().diff().dropna().dt.total_seconds()
    positive = deltas[deltas > 0]
    if positive.empty:
        raise ValueError("Timestamps must contain positive spacing")
    median_seconds = float(positive.median())
    irregularity = float(positive.std(ddof=0) / median_seconds) if len(positive) > 1 else 0.0
    return {
        "median_seconds": median_seconds,
        "median_delta": str(pd.to_timedelta(median_seconds, unit="s")),
        "irregular": bool(irregularity > 0.05),
        "spacing_cv": irregularity,
        "observations": int(len(series)),
    }


def rolling_statistics(series: pd.Series, window: int = 7) -> pd.DataFrame:
    if window < 2:
        raise ValueError("rolling window must be at least 2")
    if len(series) < window:
        raise ValueError("rolling window exceeds the number of observations")
    return pd.DataFrame({
        "value": series,
        "rolling_mean": series.rolling(window).mean(),
        "rolling_std": series.rolling(window).std(),
        "rolling_min": series.rolling(window).min(),
        "rolling_max": series.rolling(window).max(),
    })


def stationarity_test(series: pd.Series) -> dict:
    if len(series) < 12:
        raise ValueError("At least 12 observations are recommended for ADF testing")
    values=series.to_numpy(dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("stationarity test requires finite observations")
    if np.ptp(values) == 0:
        return {"test":"Augmented Dickey-Fuller","constant_series":True,"statistic":None,"p_value":None,"used_lags":0,"n_obs":int(len(values)),"critical_values":{},"stationary_at_5pct":None}
    result = adfuller(values, autolag="AIC")
    return {
        "test": "Augmented Dickey-Fuller",
        "statistic": float(result[0]),
        "p_value": float(result[1]),
        "used_lags": int(result[2]),
        "n_obs": int(result[3]),
        "critical_values": {k: float(v) for k, v in result[4].items()},
        "stationary_at_5pct": bool(result[1] < 0.05),
    }


def autocorrelation(series: pd.Series, max_lags: int = 24) -> dict:
    if max_lags < 1:
        raise ValueError("max_lags must be positive")
    values=series.to_numpy(dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("autocorrelation requires finite observations")
    if np.ptp(values) == 0:
        return {"lags":[0],"acf":[1.0],"pacf":[1.0]}
    nlags = min(max_lags, len(series) // 2 - 1)
    if nlags < 1:
        raise ValueError("Not enough observations for autocorrelation")
    a = acf(series.to_numpy(dtype=float), nlags=nlags, fft=True)
    p = pacf(series.to_numpy(dtype=float), nlags=nlags, method="ywm")
    return {"lags": list(range(nlags + 1)), "acf": a.tolist(), "pacf": p.tolist()}


def dominant_periods(series: pd.Series, top_n: int = 5) -> list[dict]:
    if top_n < 1:
        raise ValueError("top_n must be positive")
    y = series.to_numpy(dtype=float)
    if len(y) < 16:
        raise ValueError("At least 16 observations are required for spectral analysis")
    y = y - np.mean(y)
    if np.ptp(y) == 0:
        return []
    freq, power = periodogram(y)
    mask = freq > 0
    freq, power = freq[mask], power[mask]
    if len(freq) == 0:
        return []
    order = np.argsort(power)[::-1][:top_n]
    return [{"frequency": float(freq[i]), "period_observations": float(1 / freq[i]), "power": float(power[i])} for i in order]


def decomposition(series: pd.Series, period: int, model: str = "additive") -> pd.DataFrame:
    if period < 2:
        raise ValueError("seasonal period must be at least 2")
    if model not in {"additive", "multiplicative"}:
        raise ValueError("model must be additive or multiplicative")
    if len(series) < 2 * period:
        raise ValueError("At least two complete seasonal cycles are required")
    if model == "multiplicative" and (series <= 0).any():
        raise ValueError("Multiplicative decomposition requires strictly positive values")
    result = seasonal_decompose(series, model=model, period=period, extrapolate_trend="freq")
    return pd.DataFrame({"observed": result.observed, "trend": result.trend, "seasonal": result.seasonal, "resid": result.resid})


def analyze_time_series(df: pd.DataFrame, config: TimeSeriesConfig) -> dict:
    series = prepare_series(df, config.date_col, config.value_col)
    out = {
        "frequency": infer_frequency(series),
        "summary": {
            "start": series.index.min().isoformat(),
            "end": series.index.max().isoformat(),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
        },
        "rolling": rolling_statistics(series, config.rolling_window).tail(100).reset_index(names=config.date_col),
        "stationarity": stationarity_test(series),
        "autocorrelation": autocorrelation(series, config.max_lags),
        "dominant_periods": dominant_periods(series),
    }
    if config.seasonal_period is not None:
        out["decomposition"] = decomposition(series, config.seasonal_period)
    return out
