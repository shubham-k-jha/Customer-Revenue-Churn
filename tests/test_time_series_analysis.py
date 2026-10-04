import numpy as np
import pandas as pd
import pytest

from src.advanced.time_series_analysis import (
    TimeSeriesConfig, analyze_time_series, decomposition, dominant_periods,
    infer_frequency, stationarity_test,
)


def make_series(n=60, freq="D"):
    d = pd.date_range("2024-01-01", periods=n, freq=freq)
    y = 100 + np.arange(n) * 0.2 + 8 * np.sin(2*np.pi*np.arange(n)/7)
    return pd.DataFrame({"date": d, "value": y})


def test_time_series_diagnostics():
    r = analyze_time_series(make_series(), TimeSeriesConfig("date", "value", seasonal_period=7))
    assert r["frequency"]["irregular"] is False
    assert len(r["autocorrelation"]["acf"]) > 2
    assert "stationary_at_5pct" in r["stationarity"]
    assert set(r["decomposition"].columns) == {"observed", "trend", "seasonal", "resid"}


def test_monthly_frequency_and_irregularity():
    d = pd.DataFrame({"date": pd.to_datetime(["2024-01-01","2024-02-01","2024-04-01","2024-05-01"]), "value":[1,2,3,4]})
    from src.advanced.time_series_analysis import prepare_series
    # Frequency inference is also useful for short diagnostic inputs.
    r = infer_frequency(pd.Series([1.,2.,3.,4.], index=pd.to_datetime(["2024-01-01","2024-02-01","2024-04-01","2024-05-01"])))
    assert r["median_seconds"] > 20*86400
    assert r["irregular"] is True


def test_decomposition_guards():
    with pytest.raises(ValueError):
        decomposition(make_series(10).set_index("date")["value"], 7)
    bad = make_series(40); bad["value"] = -bad["value"]
    with pytest.raises(ValueError):
        decomposition(bad.set_index("date")["value"], 7, model="multiplicative")


def test_spectral_analysis_guard():
    with pytest.raises(ValueError):
        dominant_periods(pd.Series(np.arange(10), index=pd.date_range("2024-01-01", periods=10)))
