"""Tests for recursive operational-benchmark validation."""

import numpy as np
import pandas as pd

from src.evaluation.benchmark_validation import (
    run_operational_benchmark_validation,
)
from src.features.reconstruct_index import (
    reconstruct_index,
)


def make_benchmark_test_data():
    """Create complete synthetic monthly inflation data."""
    dates = pd.date_range(
        "2000-01-01",
        "2008-12-01",
        freq="MS",
    )

    seasonal_component = (
        0.2
        * np.sin(
            2
            * np.pi
            * np.arange(len(dates))
            / 12
        )
    )

    trend_component = (
        0.001
        * np.arange(len(dates))
    )

    monthly_rate = pd.Series(
        0.15
        + seasonal_component
        + trend_component,
        index=dates,
        name="monthly_rate",
    )

    reconstructed_index = reconstruct_index(
        monthly_rate
    )

    published_yoy = (
        reconstructed_index
        / reconstructed_index.shift(12)
        - 1
    ) * 100

    published_yoy.name = "published_yoy"

    return (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    )


def test_benchmark_validation_returns_complete_panel():
    """Each origin should contribute every requested horizon."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_benchmark_test_data()

    result = run_operational_benchmark_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        model_label="Synthetic benchmark",
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    expected_origins = 13

    assert len(result.forecasts) == (
        expected_origins * 12
    )

    assert (
        result.forecasts[
            "forecast_origin"
        ].nunique()
        == expected_origins
    )

    rows_per_origin = (
        result.forecasts.groupby(
            "forecast_origin"
        )
        .size()
    )

    assert rows_per_origin.eq(12).all()


def test_benchmark_validation_generates_all_horizons():
    """The result should contain horizons one through twelve."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_benchmark_test_data()

    result = run_operational_benchmark_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        model_label="Synthetic benchmark",
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    assert (
        result.forecasts["horizon"]
        .drop_duplicates()
        .sort_values()
        .tolist()
        == list(range(1, 13))
    )


def test_benchmark_validation_outputs_are_finite():
    """All stored benchmark outputs should be finite."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_benchmark_test_data()

    result = run_operational_benchmark_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        model_label="Synthetic benchmark",
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    numeric_columns = [
        "mom_forecast",
        "index_forecast",
        "yoy_forecast",
        "yoy_actual",
        "forecast_error",
        "absolute_error",
        "squared_error",
    ]

    assert np.isfinite(
        result.forecasts[
            numeric_columns
        ].to_numpy()
    ).all()


def test_benchmark_metrics_have_expected_counts():
    """Each horizon should have one result per origin."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_benchmark_test_data()

    result = run_operational_benchmark_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        model_label="Synthetic benchmark",
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    assert (
        result.metrics["forecast_count"]
        == 13
    ).all()


def test_benchmark_validation_does_not_mutate_inputs():
    """The benchmark validation must preserve its inputs."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_benchmark_test_data()

    original_monthly_rate = monthly_rate.copy()
    original_index = reconstructed_index.copy()
    original_yoy = published_yoy.copy()

    run_operational_benchmark_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        model_label="Synthetic benchmark",
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    pd.testing.assert_series_equal(
        monthly_rate,
        original_monthly_rate,
    )

    pd.testing.assert_series_equal(
        reconstructed_index,
        original_index,
    )

    pd.testing.assert_series_equal(
        published_yoy,
        original_yoy,
    )