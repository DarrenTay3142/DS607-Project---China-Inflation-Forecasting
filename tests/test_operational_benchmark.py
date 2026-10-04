"""Tests for the recursive operational inflation benchmark."""

from pathlib import Path

import pandas as pd

from src.data.load_ceic import load_cpi_series
from src.features.reconstruct_index import (
    add_reconstructed_indices,
    reconstruct_index,
)
from src.models.operational_benchmark import (
    forecast_operational_benchmark,
)


DATA_PATH = Path("data/raw/china_cpi.csv")


def make_synthetic_data():
    """Create simple complete monthly data for controlled testing."""
    dates = pd.date_range(
        "2014-01-01",
        "2019-12-01",
        freq="MS",
    )

    # The rate changes systematically by year and calendar month,
    # making selected inputs easy to verify.
    monthly_rate = pd.Series(
        [
            (date.year - 2014) + date.month / 100
            for date in dates
        ],
        index=dates,
        name="monthly_rate",
    )

    index_level = reconstruct_index(monthly_rate)

    return monthly_rate, index_level


def test_benchmark_returns_requested_horizon():
    """The benchmark should return 24 monthly forecasts."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    assert len(result.forecast) == 24
    assert result.forecast["horizon"].tolist() == list(
        range(1, 25)
    )


def test_forecast_dates_begin_after_origin():
    """The first target should be one month after the forecast origin."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    assert (
        result.forecast.iloc[0]["target_date"]
        == pd.Timestamp("2020-01-01")
    )

    assert (
        result.forecast.iloc[-1]["target_date"]
        == pd.Timestamp("2021-12-01")
    )


def test_each_forecast_uses_five_inputs():
    """Every forecast month should use exactly five values."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    input_counts = result.audit.groupby("horizon").size()

    assert (input_counts == 5).all()
    assert len(result.audit) == 24 * 5


def test_first_year_uses_observed_inputs_only():
    """Horizons 1 to 12 should use only historical observations."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    first_year_audit = result.audit[
        result.audit["horizon"] <= 12
    ]

    assert (
        first_year_audit["input_type"] == "observed"
    ).all()


def test_horizon_thirteen_uses_first_recursive_forecast():
    """January 2021 should include the January 2020 forecast."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    horizon_one = result.forecast.loc[
        result.forecast["horizon"] == 1,
        "mom_forecast",
    ].iloc[0]

    horizon_thirteen_inputs = result.audit[
        result.audit["horizon"] == 13
    ]

    forecast_inputs = horizon_thirteen_inputs[
        horizon_thirteen_inputs["input_type"] == "forecast"
    ]

    assert len(forecast_inputs) == 1

    assert (
        forecast_inputs.iloc[0]["input_date"]
        == pd.Timestamp("2020-01-01")
    )

    assert abs(
        forecast_inputs.iloc[0]["input_rate"] - horizon_one
    ) < 1e-12


def test_horizon_thirteen_average_is_recursive():
    """The month-13 forecast should equal its five audited inputs."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    audited_mean = (
        result.audit.loc[
            result.audit["horizon"] == 13,
            "input_rate",
        ].mean()
    )

    forecast_value = result.forecast.loc[
        result.forecast["horizon"] == 13,
        "mom_forecast",
    ].iloc[0]

    assert abs(audited_mean - forecast_value) < 1e-12


def test_input_series_are_not_modified():
    """Generating a forecast must not mutate the observed data."""
    monthly_rate, index_level = make_synthetic_data()

    original_monthly_rate = monthly_rate.copy()
    original_index_level = index_level.copy()

    forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    pd.testing.assert_series_equal(
        monthly_rate,
        original_monthly_rate,
    )

    pd.testing.assert_series_equal(
        index_level,
        original_index_level,
    )


def test_forecast_index_reproduces_monthly_forecasts():
    """Forecast index movements should equal forecast monthly rates."""
    monthly_rate, index_level = make_synthetic_data()

    result = forecast_operational_benchmark(
        monthly_rate=monthly_rate,
        index_level=index_level,
        forecast_origin="2019-12-01",
        horizon=24,
    )

    starting_index = index_level.loc["2019-12-01"]

    extended_index = pd.concat(
        [
            pd.Series(
                [starting_index],
                index=[pd.Timestamp("2019-12-01")],
            ),
            result.forecast.set_index("target_date")[
                "index_forecast"
            ],
        ]
    )

    implied_monthly_rate = (
        extended_index.pct_change(fill_method=None) * 100
    ).iloc[1:]

    expected_monthly_rate = (
        result.forecast.set_index("target_date")[
            "mom_forecast"
        ]
    )

    pd.testing.assert_series_equal(
        implied_monthly_rate,
        expected_monthly_rate,
        check_names=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10,
    )


def test_real_headline_forecast_runs_for_twenty_four_months():
    """The benchmark should run on the actual headline CPI data."""
    cpi = load_cpi_series(DATA_PATH)
    cpi = add_reconstructed_indices(cpi)

    common_sample = cpi.loc["2006-01-01":].dropna(
        subset=[
            "headline_mom_published",
            "headline_index_reconstructed",
        ]
    )

    result = forecast_operational_benchmark(
        monthly_rate=common_sample[
            "headline_mom_published"
        ],
        index_level=common_sample[
            "headline_index_reconstructed"
        ],
        forecast_origin="2020-12-01",
        horizon=24,
    )

    assert len(result.forecast) == 24
    assert len(result.audit) == 120
    assert result.forecast.notna().all().all()