"""Tests for the Chinese New Year calendar loader."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.load_cny_calendar import (
    load_cny_calendar,
    validate_cny_calendar,
)


CALENDAR_PATH = Path(
    "data/external/chinese_new_year_dates.csv"
)


def test_cny_calendar_file_exists():
    """The public CNY calendar should be committed locally."""
    assert CALENDAR_PATH.exists()


def test_cny_calendar_has_expected_columns():
    """The cleaned calendar should contain only year and CNY date."""
    calendar = load_cny_calendar(CALENDAR_PATH)

    assert calendar.columns.tolist() == [
        "year",
        "cny_date",
    ]


def test_cny_calendar_has_complete_source_range():
    """The downloaded calendar should cover 1900 through 2100."""
    calendar = load_cny_calendar(CALENDAR_PATH)

    assert calendar["year"].min() == 1900
    assert calendar["year"].max() == 2100
    assert len(calendar) == 201


def test_cny_calendar_has_unique_years():
    """Each Gregorian year should appear exactly once."""
    calendar = load_cny_calendar(CALENDAR_PATH)

    assert calendar["year"].is_unique


def test_cny_calendar_dates_match_years():
    """Every CNY date should occur in its stated Gregorian year."""
    calendar = load_cny_calendar(CALENDAR_PATH)

    assert (
        calendar["cny_date"].dt.year
        == calendar["year"]
    ).all()


def test_project_period_is_complete():
    """The project requires an uninterrupted 2006-2030 calendar."""
    calendar = load_cny_calendar(
        CALENDAR_PATH,
        start_year=2006,
        end_year=2030,
    )

    assert calendar["year"].tolist() == list(
        range(2006, 2031)
    )

    assert len(calendar) == 25


@pytest.mark.parametrize(
    ("year", "expected_date"),
    [
        (2006, "2006-01-29"),
        (2007, "2007-02-18"),
        (2008, "2008-02-07"),
        (2012, "2012-01-23"),
        (2014, "2014-01-31"),
        (2020, "2020-01-25"),
        (2024, "2024-02-10"),
        (2026, "2026-02-17"),
        (2030, "2030-02-03"),
    ],
)
def test_known_cny_dates(year, expected_date):
    """Selected historically relevant dates should match."""
    calendar = load_cny_calendar(CALENDAR_PATH)

    actual_date = calendar.loc[
        calendar["year"] == year,
        "cny_date",
    ].iloc[0]

    assert actual_date == pd.Timestamp(expected_date)


def test_missing_requested_year_raises_error(
    tmp_path,
):
    """Filtering should detect a missing required year."""
    incomplete_path = tmp_path / "incomplete_calendar.csv"

    incomplete_path.write_text(
        (
            "year,chinese_new_year\n"
            "2006,2006-01-29\n"
            "2008,2008-02-07\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="missing years: 2007",
    ):
        load_cny_calendar(
            incomplete_path,
            start_year=2006,
            end_year=2008,
        )


def test_duplicate_year_raises_error():
    """The validator should reject duplicate Gregorian years."""
    invalid_calendar = pd.DataFrame(
        {
            "year": [2006, 2006],
            "cny_date": pd.to_datetime(
                [
                    "2006-01-29",
                    "2006-01-29",
                ]
            ),
        }
    )

    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        validate_cny_calendar(invalid_calendar)


def test_out_of_range_date_raises_error():
    """A date outside January 21-February 20 is invalid."""
    invalid_calendar = pd.DataFrame(
        {
            "year": [2006],
            "cny_date": pd.to_datetime(
                ["2006-03-01"]
            ),
        }
    )

    with pytest.raises(
        ValueError,
        match="January 21",
    ):
        validate_cny_calendar(invalid_calendar)