from __future__ import annotations

from dataclasses import dataclass
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose


@dataclass(frozen=True)
class DeepTSConfig:
    date_col: str
    value_col: str
    frequency: str | None = None
    seasonal_period: int | None = None
    rolling_window: int = 7
    max_lags: int = 24
    outlier_z: float = 3.5


def clean_series(df: pd.DataFrame, date_col: str, value_col: str, agg: str = "sum") -> pd.Series:
    if date_col not in df.columns or value_col not in df.columns:
        raise KeyError(f"{date_col!r} and {value_col!r} must exist")
    if agg not in {"sum", "mean", "median", "first", "last"}:
        raise ValueError("agg must be sum, mean, median, first or last")
    x = df[[date_col, value_col]].copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce", utc=True, format="mixed")
    x[value_col] = pd.to_numeric(x[value_col], errors="coerce")
    x = x.dropna().sort_values(date_col)
    if x.empty:
        raise ValueError("No valid date/value observations remain")
    grouped = getattr(x.groupby(date_col)[value_col], agg)().sort_index()
    if len(grouped) < 12:
        raise ValueError("At least 12 valid observations are required")
    return grouped.astype(float)


def regularize(series: pd.Series, frequency: str, fill: str = "interpolate") -> pd.Series:
    if frequency not in {"D", "W", "MS", "ME", "QS", "QE", "H"}:
        raise ValueError("Unsupported frequency; use D/W/MS/ME/QS/QE/H")
    out = series.asfreq(frequency)
    if fill == "interpolate":
        out = out.interpolate(method="time")
    elif fill == "ffill":
        out = out.ffill()
    elif fill == "zero":
        out = out.fillna(0.0)
    elif fill != "none":
        raise ValueError("fill must be interpolate, ffill, zero or none")
    return out


def _safe_float(x):
    return None if x is None or not np.isfinite(float(x)) else float(x)


def stationarity(series: pd.Series) -> dict:
    y = series.dropna().to_numpy(dtype=float)
    if len(y) < 12:
        raise ValueError("At least 12 observations are required for stationarity tests")
    if np.ptp(y) == 0:
        return {
            "constant_series": True,
            "adf_error": "ADF is undefined for a constant series",
            "kpss_error": "KPSS is undefined for a constant series",
        }
    out = {"constant_series": False}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            a = adfuller(y, autolag="AIC")
            out["adf"] = {"statistic": float(a[0]), "p_value": float(a[1]), "used_lags": int(a[2]), "n_obs": int(a[3]), "stationary_5pct": bool(a[1] < .05)}
        except Exception as e:
            out["adf_error"] = str(e)
        try:
            k = kpss(y, regression="c", nlags="auto")
            out["kpss"] = {"statistic": float(k[0]), "p_value": float(k[1]), "used_lags": int(k[2]), "stationary_5pct": bool(k[1] >= .05)}
        except Exception as e:
            out["kpss_error"] = str(e)
    return out


def difference_diagnostics(series: pd.Series, max_d: int = 2) -> list[dict]:
    if max_d < 0 or max_d > 2:
        raise ValueError("max_d must be between 0 and 2")
    rows = []
    for d in range(max_d + 1):
        y = series.diff(d).dropna() if d else series.dropna()
        if len(y) < 12:
            break
        st = stationarity(y)
        rows.append({"difference_order": d, "adf_p_value": st.get("adf", {}).get("p_value"), "kpss_p_value": st.get("kpss", {}).get("p_value"), "adf_stationary": st.get("adf", {}).get("stationary_5pct"), "kpss_stationary": st.get("kpss", {}).get("stationary_5pct")})
    return rows


def residual_diagnostics(residuals: pd.Series, lags: int = 12) -> dict:
    y = pd.Series(residuals, dtype=float).dropna()
    if len(y) < 10:
        raise ValueError("At least 10 residual observations are required")
    if float(y.std(ddof=0)) == 0.0:
        return {"ljung_box": {"lag": 0, "statistic": 0.0, "p_value": 1.0, "white_noise_5pct": True}, "jarque_bera": {"statistic": 0.0, "p_value": 1.0, "normal_5pct": True}, "mean": float(y.mean()), "std": 0.0}
    nlags = min(max(1, lags), max(1, len(y)//4))
    lb = acorr_ljungbox(y, lags=[nlags], return_df=True)
    jb = stats.jarque_bera(y)
    return {
        "ljung_box": {"lag": nlags, "statistic": float(lb["lb_stat"].iloc[0]), "p_value": float(lb["lb_pvalue"].iloc[0]), "white_noise_5pct": bool(lb["lb_pvalue"].iloc[0] >= .05)},
        "jarque_bera": {"statistic": float(jb.statistic), "p_value": float(jb.pvalue), "normal_5pct": bool(jb.pvalue >= .05)},
        "mean": float(y.mean()), "std": float(y.std(ddof=1)),
    }


def robust_outliers(series: pd.Series, window: int = 7, threshold: float = 3.5) -> pd.DataFrame:
    if window < 3 or threshold <= 0:
        raise ValueError("window must be >=3 and threshold must be positive")
    s = pd.Series(series, dtype=float)
    med = s.rolling(window, center=True, min_periods=max(3, window//2)).median()
    mad = (s-med).abs().rolling(window, center=True, min_periods=max(3, window//2)).median()
    robust_z = 0.67448975 * (s-med) / mad.replace(0, np.nan)
    fallback = (s-s.median()) / (s.std(ddof=0) or 1.0)
    robust_z = robust_z.fillna(fallback)
    return pd.DataFrame({"value": s, "robust_z": robust_z, "is_outlier": robust_z.abs() >= threshold}, index=s.index)


def trend_seasonality_strength(series: pd.Series, period: int) -> dict:
    if period < 2 or len(series) < 2 * period:
        raise ValueError("Need at least two complete seasonal cycles")
    result = seasonal_decompose(series, model="additive", period=period, extrapolate_trend="freq")
    var_resid = float(np.nanvar(result.resid))
    var_detrended = float(np.nanvar(result.observed - result.trend))
    var_deseasonalized = float(np.nanvar(result.observed - result.seasonal))
    trend_strength = max(0.0, min(1.0, 1.0 - var_resid / var_detrended)) if var_detrended > 0 else 0.0
    season_strength = max(0.0, min(1.0, 1.0 - var_resid / var_deseasonalized)) if var_deseasonalized > 0 else 0.0
    return {"trend_strength": float(trend_strength), "seasonal_strength": float(season_strength), "period": int(period)}


def calendar_features(dates: pd.Series, fourier_periods: list[int] | None = None, harmonics: int = 2) -> pd.DataFrame:
    if harmonics < 1:
        raise ValueError("harmonics must be positive")
    d = pd.to_datetime(dates, utc=True, errors="coerce", format="mixed")
    if d.isna().any():
        raise ValueError("dates contains unparseable values")
    out = pd.DataFrame(index=d.index)
    out["year"] = d.dt.year.astype(int)
    out["quarter"] = d.dt.quarter.astype(int)
    out["month"] = d.dt.month.astype(int)
    out["week"] = d.dt.isocalendar().week.astype(int).to_numpy()
    out["day_of_week"] = d.dt.dayofweek.astype(int)
    out["day_of_year"] = d.dt.dayofyear.astype(int)
    out["is_month_start"] = d.dt.is_month_start.astype(int)
    out["is_month_end"] = d.dt.is_month_end.astype(int)
    for p in fourier_periods or []:
        if p < 2:
            raise ValueError("Fourier periods must be >=2")
        t = np.arange(len(d), dtype=float)
        for k in range(1, harmonics + 1):
            out[f"sin_{p}_{k}"] = np.sin(2*np.pi*k*t/p)
            out[f"cos_{p}_{k}"] = np.cos(2*np.pi*k*t/p)
    return out


def lag_features(series: pd.Series, lags: list[int], rolling_windows: list[int] | None = None) -> pd.DataFrame:
    if not lags or any(int(l) < 1 for l in lags):
        raise ValueError("lags must contain positive integers")
    s = pd.Series(series, dtype=float)
    out = pd.DataFrame({f"lag_{int(l)}": s.shift(int(l)) for l in lags}, index=s.index)
    for w in rolling_windows or []:
        if int(w) < 2:
            raise ValueError("rolling windows must be >=2")
        # shift before rolling to prevent current-target leakage
        r = s.shift(1).rolling(int(w), min_periods=int(w))
        out[f"roll_mean_{int(w)}"] = r.mean()
        out[f"roll_std_{int(w)}"] = r.std()
        out[f"roll_min_{int(w)}"] = r.min()
        out[f"roll_max_{int(w)}"] = r.max()
    return out


def full_diagnostics(series: pd.Series, seasonal_period: int | None = None, rolling_window: int = 7, max_lags: int = 24) -> dict:
    s = pd.Series(series, dtype=float).dropna()
    if len(s) < 12:
        raise ValueError("At least 12 observations are required")
    from src.advanced.time_series_analysis import infer_frequency, autocorrelation, dominant_periods
    out = {"frequency": infer_frequency(s), "stationarity": stationarity(s), "differencing": difference_diagnostics(s), "residual_diagnostics": residual_diagnostics(s.diff().dropna(), min(max_lags, 12)), "outliers": robust_outliers(s, rolling_window).tail(100).reset_index().to_dict(orient="records"), "dominant_periods": dominant_periods(s) if len(s) >= 16 else [], "autocorrelation": autocorrelation(s, max_lags)}
    if seasonal_period:
        out["seasonality"] = trend_seasonality_strength(s, seasonal_period)
    return out
