"""Tests for CPI index reconstruction."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.load_ceic import load_cpi_series
from src.features.reconstruct_index import (
    add_reconstructed_indices,
    calculate_monthly_rate,
    calculate_yoy_rate,
    reconstruct_index,
)


DATA_PATH = Path("data/raw/china_cpi.csv")


def test_reconstruct_index_with_known_values():
    """A simple sequence should produce known compounded index values."""
    dates = pd.date_range("2020-01-01", periods=4, freq="MS")

    monthly_rate = pd.Series(
        [0.0, 1.0, -0.5, 2.0],
        index=dates,
    )

    reconstructed = reconstruct_index(monthly_rate)

    expected = pd.Series(
        [
            100.0,
            101.0,
            101.0 * 0.995,
            101.0 * 0.995 * 1.02,
        ],
        index=dates,
        name="reconstructed_index",
    )

    pd.testing.assert_series_equal(
        reconstructed,
        expected,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_reconstructed_index_reproduces_monthly_rates():
    """The reconstructed index should reproduce all monthly inputs."""
    cpi = load_cpi_series(DATA_PATH)

    headline_index = reconstruct_index(
        cpi["headline_mom_published"]
    )

    reconstructed_mom = calculate_monthly_rate(headline_index)

    comparison = pd.concat(
        [
            cpi["headline_mom_published"],
            reconstructed_mom,
        ],
        axis=1,
    ).dropna()

    pd.testing.assert_series_equal(
        comparison["headline_mom_published"],
        comparison["reconstructed_mom"],
        check_names=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10,
    )


def test_reconstructed_core_index_reproduces_monthly_rates():
    """The core reconstruction should reproduce its monthly inputs."""
    cpi = load_cpi_series(DATA_PATH)

    core_index = reconstruct_index(
        cpi["core_mom_published"]
    )

    reconstructed_mom = calculate_monthly_rate(core_index)

    comparison = pd.concat(
        [
            cpi["core_mom_published"],
            reconstructed_mom,
        ],
        axis=1,
    ).dropna()

    pd.testing.assert_series_equal(
        comparison["core_mom_published"],
        comparison["reconstructed_mom"],
        check_names=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10,
    )


def test_yoy_calculation_has_twelve_initial_missing_values():
    """A year-on-year rate requires twelve preceding monthly intervals."""
    dates = pd.date_range("2020-01-01", periods=24, freq="MS")
    index_level = pd.Series(range(100, 124), index=dates)

    yoy_rate = calculate_yoy_rate(index_level)

    assert yoy_rate.iloc[:12].isna().all()
    assert yoy_rate.iloc[12:].notna().all()


def test_missing_month_raises_error():
    """The reconstruction must not compound silently across a missing month."""
    dates = pd.to_datetime(
        [
            "2020-01-01",
            "2020-02-01",
            "2020-04-01",
        ]
    )

    monthly_rate = pd.Series(
        [0.1, 0.2, 0.3],
        index=dates,
    )

    with pytest.raises(ValueError, match="missing months"):
        reconstruct_index(monthly_rate)


def test_nonpositive_base_value_raises_error():
    """A reconstructed price index must have a positive base."""
    dates = pd.date_range("2020-01-01", periods=3, freq="MS")
    monthly_rate = pd.Series([0.1, 0.2, 0.3], index=dates)

    with pytest.raises(ValueError, match="must be positive"):
        reconstruct_index(monthly_rate, base_value=0)


def test_full_reconstruction_adds_expected_columns():
    """The complete transformation should add indices and diagnostics."""
    cpi = load_cpi_series(DATA_PATH)
    reconstructed = add_reconstructed_indices(cpi)

    expected_columns = {
        "headline_index_reconstructed",
        "core_index_reconstructed",
        "headline_yoy_reconstructed",
        "core_yoy_reconstructed",
        "headline_yoy_discrepancy",
        "core_yoy_discrepancy",
    }

    assert expected_columns.issubset(reconstructed.columns)


def test_common_sample_has_no_missing_monthly_observations():
    """Headline and core monthly series should be complete from 2006 onward."""
    cpi = load_cpi_series(DATA_PATH)

    common_sample = cpi.loc["2006-01-01":]

    assert common_sample[
        [
            "headline_mom_published",
            "core_mom_published",
        ]
    ].notna().all().all()