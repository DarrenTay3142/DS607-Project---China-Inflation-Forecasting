"""Tests for the CEIC China CPI ingestion module."""

from pathlib import Path

import pandas as pd

from src.data.load_ceic import (
    CORE_MOM,
    CORE_YOY,
    HEADLINE_MOM,
    HEADLINE_YOY,
    find_first_observation_row,
    load_cpi_series,
    read_ceic_metadata,
    read_ceic_observations,
)


DATA_PATH = Path("data/raw/china_cpi.csv")


def test_raw_data_file_exists():
    """The licensed CEIC extract must be available locally."""
    assert DATA_PATH.exists()


def test_first_observation_row_is_found():
    """The loader should find the first monthly observation."""
    first_row = find_first_observation_row(DATA_PATH)

    assert isinstance(first_row, int)
    assert first_row > 0


def test_required_series_are_present():
    """All four headline and core series should be available."""
    observations = read_ceic_observations(DATA_PATH)

    required = {
        HEADLINE_YOY,
        CORE_YOY,
        HEADLINE_MOM,
        CORE_MOM,
    }

    assert required.issubset(observations.columns)


def test_metadata_matches_expected_units():
    """CEIC units should match the expected moving-base relatives."""
    metadata = read_ceic_metadata(DATA_PATH)

    assert metadata.loc[HEADLINE_YOY, "Unit"] == "Prev Year=100"
    assert metadata.loc[CORE_YOY, "Unit"] == "Prev Year=100"
    assert metadata.loc[HEADLINE_MOM, "Unit"] == "Prev Mth=100"
    assert metadata.loc[CORE_MOM, "Unit"] == "Prev Mth=100"


def test_cpi_output_has_expected_columns():
    """The cleaned data should have four percentage-rate columns."""
    cpi = load_cpi_series(DATA_PATH)

    expected_columns = [
        "headline_yoy_published",
        "headline_mom_published",
        "core_yoy_published",
        "core_mom_published",
    ]

    assert cpi.columns.tolist() == expected_columns


def test_cpi_index_is_monthly_and_unique():
    """Observation dates should be ordered and unique."""
    cpi = load_cpi_series(DATA_PATH)

    assert isinstance(cpi.index, pd.DatetimeIndex)
    assert cpi.index.is_monotonic_increasing
    assert cpi.index.is_unique


def test_latest_observation_is_august_2026():
    """The uploaded CEIC extract should end in August 2026."""
    cpi = load_cpi_series(DATA_PATH)

    assert cpi.index.max() == pd.Timestamp("2026-08-01")


def test_relative_to_percentage_conversion():
    """A relative of 100.8 should become an inflation rate of 0.8%."""
    cpi = load_cpi_series(DATA_PATH)

    august_2026 = cpi.loc[pd.Timestamp("2026-08-01")]

    assert abs(august_2026["headline_yoy_published"] - 0.8) < 1e-12
    assert abs(august_2026["headline_mom_published"] - 0.4) < 1e-12