"""Tests for Chinese New Year moving-holiday regressors."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.load_cny_calendar import load_cny_calendar
from src.features.cny_regressors import (
    build_cny_regressors,
)


CALENDAR_PATH = Path(
    "data/external/chinese_new_year_dates.csv"
)


@pytest.fixture
def cny_calendar():
    """Return the project CNY calendar."""
    return load_cny_calendar(
        CALENDAR_PATH,
        start_year=2006,
        end_year=2030,
    )


@pytest.fixture
def primary_regressors(cny_calendar):
    """Return the primary two-phase CNY specification."""
    return build_cny_regressors(
        cny_calendar=cny_calendar,
        start_date="2006-01-01",
        end_date="2030-12-01",
    )


def test_monthly_regressor_columns(primary_regressors):
    """The result should contain two fractional regressors."""
    assert primary_regressors.monthly.columns.tolist() == [
        "cny_pressure",
        "cny_normalisation",
    ]


def test_monthly_regressor_index(primary_regressors):
    """The monthly table should be continuous and monthly."""
    monthly = primary_regressors.monthly

    assert isinstance(monthly.index, pd.DatetimeIndex)
    assert monthly.index.freqstr == "MS"
    assert monthly.index.is_monotonic_increasing
    assert monthly.index.is_unique


def test_phase_fractions_sum_to_one_by_year(
    primary_regressors,
):
    """Every annual phase should be allocated completely."""
    phase_sums = (
        primary_regressors.audit.groupby(
            [
                "cny_year",
                "phase",
            ]
        )["fraction"]
        .sum()
    )

    assert phase_sums.round(12).eq(1.0).all()


def test_primary_phase_lengths(primary_regressors):
    """Primary pressure and normalisation lengths are fixed."""
    audit = primary_regressors.audit

    pressure_lengths = audit.loc[
        audit["phase"] == "pressure",
        "total_phase_days",
    ].unique()

    normalisation_lengths = audit.loc[
        audit["phase"] == "normalisation",
        "total_phase_days",
    ].unique()

    assert pressure_lengths.tolist() == [29]
    assert normalisation_lengths.tolist() == [14]


def test_2006_pressure_allocation(primary_regressors):
    """The 2006 pressure phase spans January and February."""
    audit = primary_regressors.audit

    allocation = audit.loc[
        (audit["cny_year"] == 2006)
        & (audit["phase"] == "pressure"),
        [
            "month",
            "affected_days",
            "fraction",
        ],
    ].reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "month": pd.to_datetime(
                [
                    "2006-01-01",
                    "2006-02-01",
                ]
            ),
            "affected_days": [
                17,
                12,
            ],
            "fraction": [
                17 / 29,
                12 / 29,
            ],
        }
    )

    pd.testing.assert_frame_equal(
        allocation,
        expected,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_2006_normalisation_is_in_february(
    primary_regressors,
):
    """The 2006 normalisation phase falls fully in February."""
    audit = primary_regressors.audit

    allocation = audit.loc[
        (audit["cny_year"] == 2006)
        & (audit["phase"] == "normalisation")
    ]

    assert len(allocation) == 1

    assert (
        allocation.iloc[0]["month"]
        == pd.Timestamp("2006-02-01")
    )

    assert allocation.iloc[0]["affected_days"] == 14
    assert abs(allocation.iloc[0]["fraction"] - 1.0) < 1e-12


def test_2007_pressure_spills_into_march(
    primary_regressors,
):
    """A late-February CNY should move pressure into March."""
    audit = primary_regressors.audit

    allocation = audit.loc[
        (audit["cny_year"] == 2007)
        & (audit["phase"] == "pressure"),
        [
            "month",
            "affected_days",
        ],
    ].reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "month": pd.to_datetime(
                [
                    "2007-02-01",
                    "2007-03-01",
                ]
            ),
            "affected_days": [
                25,
                4,
            ],
        }
    )

    pd.testing.assert_frame_equal(
        allocation,
        expected,
    )


def test_2012_pressure_spans_january_and_february(
    primary_regressors,
):
    """An early CNY should allocate pressure across two months."""
    audit = primary_regressors.audit

    allocation = audit.loc[
        (audit["cny_year"] == 2012)
        & (audit["phase"] == "pressure"),
        [
            "month",
            "affected_days",
        ],
    ].reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "month": pd.to_datetime(
                [
                    "2012-01-01",
                    "2012-02-01",
                ]
            ),
            "affected_days": [
                23,
                6,
            ],
        }
    )

    pd.testing.assert_frame_equal(
        allocation,
        expected,
    )


def test_regressors_are_zero_outside_affected_months(
    primary_regressors,
):
    """Ordinary months should have zero CNY fractions."""
    monthly = primary_regressors.monthly

    july_2010 = monthly.loc[
        pd.Timestamp("2010-07-01")
    ]

    assert july_2010["cny_pressure"] == 0.0
    assert july_2010["cny_normalisation"] == 0.0


def test_pressure_and_normalisation_do_not_overlap(
    primary_regressors,
):
    """No calendar day should belong to both phases."""
    audit = primary_regressors.audit

    phase_bounds = (
        audit.groupby(
            [
                "cny_year",
                "phase",
            ]
        )
        .agg(
            phase_start=("phase_start", "first"),
            phase_end=("phase_end", "first"),
        )
        .reset_index()
    )

    pressure = phase_bounds.loc[
        phase_bounds["phase"] == "pressure"
    ].set_index("cny_year")

    normalisation = phase_bounds.loc[
        phase_bounds["phase"] == "normalisation"
    ].set_index("cny_year")

    assert (
        pressure["phase_end"]
        < normalisation["phase_start"]
    ).all()


def test_invalid_overlapping_phase_definition_raises(
    cny_calendar,
):
    """Overlapping pressure and normalisation phases are invalid."""
    with pytest.raises(
        ValueError,
        match="must begin after",
    ):
        build_cny_regressors(
            cny_calendar=cny_calendar,
            start_date="2006-01-01",
            end_date="2030-12-01",
            pressure_days_after=14,
            normalisation_start_day=14,
        )


def test_missing_calendar_year_raises_error(
    cny_calendar,
):
    """All requested years must be present."""
    incomplete_calendar = cny_calendar.loc[
        cny_calendar["year"] != 2010
    ]

    with pytest.raises(
        ValueError,
        match="missing CNY years: 2010",
    ):
        build_cny_regressors(
            cny_calendar=incomplete_calendar,
            start_date="2006-01-01",
            end_date="2030-12-01",
        )