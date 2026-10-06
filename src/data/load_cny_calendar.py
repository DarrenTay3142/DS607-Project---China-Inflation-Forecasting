"""Load and validate the Chinese New Year calendar."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "year",
    "chinese_new_year",
}

EARLIEST_CNY_MONTH = 1
EARLIEST_CNY_DAY = 21
LATEST_CNY_MONTH = 2
LATEST_CNY_DAY = 20


def load_cny_calendar(
    file_path: Path,
    start_year: int | None = None,
    end_year: int | None = None,
) -> pd.DataFrame:
    """Load and validate Chinese New Year dates.

    Parameters
    ----------
    file_path:
        Path to the source CSV. Lines beginning with ``#`` are treated
        as source documentation and ignored during parsing.
    start_year:
        Optional first year to retain.
    end_year:
        Optional final year to retain.

    Returns
    -------
    pandas.DataFrame
        A validated table containing ``year`` and ``cny_date``.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Chinese New Year calendar not found: {file_path}"
        )

    calendar = pd.read_csv(
        file_path,
        comment="#",
        dtype={
            "year": "int64",
        },
    )

    missing_columns = REQUIRED_COLUMNS.difference(calendar.columns)

    if missing_columns:
        formatted_columns = ", ".join(sorted(missing_columns))

        raise ValueError(
            "The following required CNY calendar columns are missing: "
            f"{formatted_columns}"
        )

    calendar = calendar[
        [
            "year",
            "chinese_new_year",
        ]
    ].copy()

    calendar = calendar.rename(
        columns={
            "chinese_new_year": "cny_date",
        }
    )

    calendar["cny_date"] = pd.to_datetime(
        calendar["cny_date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    calendar = calendar.sort_values("year").reset_index(drop=True)

    validate_cny_calendar(calendar)

    if start_year is not None:
        calendar = calendar.loc[
            calendar["year"] >= start_year
        ].copy()

    if end_year is not None:
        calendar = calendar.loc[
            calendar["year"] <= end_year
        ].copy()

    if calendar.empty:
        raise ValueError(
            "No CNY calendar observations remain after year filtering."
        )

    if start_year is not None and end_year is not None:
        expected_years = pd.Index(
            range(start_year, end_year + 1),
            name="year",
        )

        actual_years = pd.Index(
            calendar["year"],
            name="year",
        )

        missing_years = expected_years.difference(actual_years)

        if not missing_years.empty:
            formatted_years = ", ".join(
                str(year) for year in missing_years
            )

            raise ValueError(
                "The filtered CNY calendar is missing years: "
                f"{formatted_years}"
            )

    return calendar.reset_index(drop=True)


def validate_cny_calendar(calendar: pd.DataFrame) -> None:
    """Validate the structure and calendar logic of CNY dates."""
    if calendar.empty:
        raise ValueError("The CNY calendar contains no observations.")

    if calendar["year"].duplicated().any():
        duplicate_years = (
            calendar.loc[
                calendar["year"].duplicated(keep=False),
                "year",
            ]
            .astype(str)
            .unique()
        )

        raise ValueError(
            "Duplicate CNY calendar years found: "
            f"{', '.join(duplicate_years)}"
        )

    if calendar["cny_date"].isna().any():
        raise ValueError(
            "The CNY calendar contains missing dates."
        )

    year_mismatch = (
        calendar["cny_date"].dt.year
        != calendar["year"]
    )

    if year_mismatch.any():
        mismatched_rows = calendar.loc[
            year_mismatch,
            ["year", "cny_date"],
        ]

        raise ValueError(
            "Some CNY dates do not match their stated Gregorian year:\n"
            f"{mismatched_rows.to_string(index=False)}"
        )

    date_is_valid = (
        (
            calendar["cny_date"].dt.month
            == EARLIEST_CNY_MONTH
        )
        & (
            calendar["cny_date"].dt.day
            >= EARLIEST_CNY_DAY
        )
    ) | (
        (
            calendar["cny_date"].dt.month
            == LATEST_CNY_MONTH
        )
        & (
            calendar["cny_date"].dt.day
            <= LATEST_CNY_DAY
        )
    )

    if not date_is_valid.all():
        invalid_rows = calendar.loc[
            ~date_is_valid,
            ["year", "cny_date"],
        ]

        raise ValueError(
            "CNY dates must fall between January 21 "
            "and February 20:\n"
            f"{invalid_rows.to_string(index=False)}"
        )