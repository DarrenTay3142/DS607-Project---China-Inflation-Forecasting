"""Tests for the expanding-window validation engine."""

import numpy as np
import pandas as pd

from src.evaluation.internal_validation import (
    ModelSpecification,
    run_expanding_internal_validation,
)


def make_test_series():
    """Create a nondegenerate complete synthetic monthly series."""
    dates = pd.date_range(
        "2000-01-01",
        "2008-12-01",
        freq="MS",
    )

    rng = np.random.default_rng(607)

    seasonal_component = (
        0.15
        * np.sin(
            2
            * np.pi
            * np.arange(len(dates))
            / 12
        )
    )

    innovations = rng.normal(
        loc=0.0,
        scale=0.05,
        size=len(dates),
    )

    monthly_values = np.empty(len(dates))
    monthly_values[0] = 0.2 + seasonal_component[0]

    for position in range(1, len(dates)):
        monthly_values[position] = (
            0.08
            + 0.45 * monthly_values[position - 1]
            + seasonal_component[position]
            + innovations[position]
        )

    monthly_rate = pd.Series(
        monthly_values,
        index=dates,
        name="monthly_rate",
    )

    growth_factors = 1 + monthly_rate / 100

    reconstructed_index = pd.Series(
        100 * growth_factors.cumprod(),
        index=dates,
        name="reconstructed_index",
    )

    published_yoy = pd.Series(
        (
            reconstructed_index
            / reconstructed_index.shift(12)
            - 1
        )
        * 100,
        index=dates,
        name="published_yoy",
    )

    return (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    )


def make_specification():
    """Return the common synthetic-model specification."""
    return ModelSpecification(
        label="Synthetic AR(1)",
        order=(1, 0, 0),
        seasonal_order=(0, 0, 0, 0),
        trend="c",
        uses_exog=False,
    )


def test_internal_validation_returns_all_origins_and_horizons():
    """The engine should return one row per origin and horizon."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    result = run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    expected_origins = 13
    expected_forecasts = expected_origins * 12

    assert len(result.fitting) == expected_origins
    assert result.fitting["converged"].all()
    assert result.fitting["error_message"].eq("").all()

    assert len(result.forecasts) == expected_forecasts

    assert result.forecasts["horizon"].min() == 1
    assert result.forecasts["horizon"].max() == 12

    assert (
        result.forecasts["forecast_origin"].nunique()
        == expected_origins
    )


def test_internal_validation_uses_expanding_window():
    """Training observations should increase by one each month."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    result = run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    increments = (
        result.fitting[
            "training_observations"
        ]
        .diff()
        .dropna()
    )

    assert increments.eq(1).all()


def test_internal_validation_does_not_modify_inputs():
    """The validation process must not mutate the input series."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    original_monthly_rate = monthly_rate.copy()
    original_index = reconstructed_index.copy()
    original_yoy = published_yoy.copy()

    run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
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


def test_internal_validation_outputs_are_finite():
    """Successful forecasts should contain only finite values."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    result = run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
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


def test_internal_validation_metrics_have_expected_counts():
    """Every horizon should have one forecast per successful origin."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    result = run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    assert (
        result.metrics["forecast_count"] == 13
    ).all()

    assert result.metrics["horizon"].tolist() == list(
        range(1, 13)
    )

def test_successful_origins_have_complete_horizons():
    """Every stored origin should contain the full forecast path."""
    (
        monthly_rate,
        reconstructed_index,
        published_yoy,
    ) = make_test_series()

    result = run_expanding_internal_validation(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        specification=make_specification(),
        first_origin="2005-12-01",
        final_origin="2006-12-01",
        horizon=12,
    )

    rows_per_origin = (
        result.forecasts.groupby(
            "forecast_origin"
        )
        .size()
    )

    assert rows_per_origin.eq(12).all()