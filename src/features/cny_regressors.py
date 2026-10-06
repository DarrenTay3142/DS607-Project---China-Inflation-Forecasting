"""Construct monthly Chinese New Year moving-holiday regressors."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class CNYRegressorResult:
    """Monthly regressors and their day-level allocation audit."""

    monthly: pd.DataFrame
    audit: pd.DataFrame


def _normalise_month_start(value) -> pd.Timestamp:
    """Convert a date-like value to its monthly starting date."""
    timestamp = pd.Timestamp(value)

    return timestamp.to_period("M").to_timestamp()


def _count_inclusive_days(
    interval_start: pd.Timestamp,
    interval_end: pd.Timestamp,
    month_start: pd.Timestamp,
) -> int:
    """Count interval days falling within a given Gregorian month."""
    month_end = month_start + pd.offsets.MonthEnd(0)

    overlap_start = max(interval_start, month_start)
    overlap_end = min(interval_end, month_end)

    if overlap_start > overlap_end:
        return 0

    return int((overlap_end - overlap_start).days + 1)


def _allocate_phase_to_months(
    cny_year: int,
    phase_name: str,
    phase_start: pd.Timestamp,
    phase_end: pd.Timestamp,
) -> list:
    """Allocate one holiday phase fractionally across months."""
    total_days = int((phase_end - phase_start).days + 1)

    if total_days <= 0:
        raise ValueError(
            f"{phase_name} must contain at least one day."
        )

    first_month = phase_start.to_period("M").to_timestamp()
    final_month = phase_end.to_period("M").to_timestamp()

    affected_months = pd.date_range(
        start=first_month,
        end=final_month,
        freq="MS",
    )

    rows = []

    for month_start in affected_months:
        affected_days = _count_inclusive_days(
            interval_start=phase_start,
            interval_end=phase_end,
            month_start=month_start,
        )

        if affected_days == 0:
            continue

        rows.append(
            {
                "cny_year": cny_year,
                "phase": phase_name,
                "month": month_start,
                "phase_start": phase_start,
                "phase_end": phase_end,
                "affected_days": affected_days,
                "total_phase_days": total_days,
                "fraction": affected_days / total_days,
            }
        )

    allocated_days = sum(
        row["affected_days"] for row in rows
    )

    if allocated_days != total_days:
        raise ValueError(
            f"{phase_name} allocation for {cny_year} is incomplete: "
            f"{allocated_days} of {total_days} days allocated."
        )

    return rows


def build_cny_regressors(
    cny_calendar: pd.DataFrame,
    start_date,
    end_date,
    pressure_days_before: int = 14,
    pressure_days_after: int = 14,
    normalisation_start_day: int = 15,
    normalisation_end_day: int = 28,
) -> CNYRegressorResult:
    """Build monthly pressure and normalisation CNY regressors.

    The primary specification defines:

    - pressure phase:
      CNY minus 14 days through CNY plus 14 days;
    - normalisation phase:
      CNY plus 15 days through CNY plus 28 days.

    Each phase is allocated across months according to the fraction of
    affected days falling within each Gregorian month.

    Parameters
    ----------
    cny_calendar:
        Validated table containing ``year`` and ``cny_date``.
    start_date:
        First monthly date to include.
    end_date:
        Final monthly date to include.
    pressure_days_before:
        Number of days before CNY included in the pressure phase.
    pressure_days_after:
        Number of days after CNY included in the pressure phase.
    normalisation_start_day:
        First day after CNY included in normalisation.
    normalisation_end_day:
        Final day after CNY included in normalisation.

    Returns
    -------
    CNYRegressorResult
        Monthly fractional regressors and a complete allocation audit.
    """
    required_columns = {
        "year",
        "cny_date",
    }

    missing_columns = required_columns.difference(
        cny_calendar.columns
    )

    if missing_columns:
        formatted_columns = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "The CNY calendar is missing columns: "
            f"{formatted_columns}"
        )

    if pressure_days_before < 0:
        raise ValueError(
            "pressure_days_before cannot be negative."
        )

    if pressure_days_after < 0:
        raise ValueError(
            "pressure_days_after cannot be negative."
        )

    if normalisation_start_day <= pressure_days_after:
        raise ValueError(
            "The normalisation phase must begin after "
            "the pressure phase ends."
        )

    if normalisation_end_day < normalisation_start_day:
        raise ValueError(
            "normalisation_end_day must be greater than or "
            "equal to normalisation_start_day."
        )

    start_date = _normalise_month_start(start_date)
    end_date = _normalise_month_start(end_date)

    if end_date < start_date:
        raise ValueError(
            "end_date must not be earlier than start_date."
        )

    monthly_index = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS",
    )

    monthly = pd.DataFrame(
        {
            "cny_pressure": 0.0,
            "cny_normalisation": 0.0,
        },
        index=monthly_index,
    )

    monthly.index.name = "date"

    calendar = cny_calendar.copy()

    calendar["cny_date"] = pd.to_datetime(
        calendar["cny_date"],
        errors="raise",
    )

    calendar = calendar.sort_values("year")

    relevant_calendar = calendar.loc[
        calendar["year"].between(
            start_date.year,
            end_date.year,
        )
    ].copy()

    if relevant_calendar.empty:
        raise ValueError(
            "No CNY dates overlap the requested monthly period."
        )

    expected_years = pd.Index(
        range(start_date.year, end_date.year + 1)
    )

    actual_years = pd.Index(
        relevant_calendar["year"]
    )

    missing_years = expected_years.difference(actual_years)

    if not missing_years.empty:
        formatted_years = ", ".join(
            str(year) for year in missing_years
        )

        raise ValueError(
            "The requested regressor period is missing CNY years: "
            f"{formatted_years}"
        )

    audit_rows = []

    for row in relevant_calendar.itertuples(index=False):
        cny_year = int(row.year)
        cny_date = pd.Timestamp(row.cny_date)

        pressure_start = (
            cny_date
            - pd.Timedelta(days=pressure_days_before)
        )

        pressure_end = (
            cny_date
            + pd.Timedelta(days=pressure_days_after)
        )

        normalisation_start = (
            cny_date
            + pd.Timedelta(days=normalisation_start_day)
        )

        normalisation_end = (
            cny_date
            + pd.Timedelta(days=normalisation_end_day)
        )

        if pressure_end >= normalisation_start:
            raise ValueError(
                f"CNY phases overlap in {cny_year}."
            )

        audit_rows.extend(
            _allocate_phase_to_months(
                cny_year=cny_year,
                phase_name="pressure",
                phase_start=pressure_start,
                phase_end=pressure_end,
            )
        )

        audit_rows.extend(
            _allocate_phase_to_months(
                cny_year=cny_year,
                phase_name="normalisation",
                phase_start=normalisation_start,
                phase_end=normalisation_end,
            )
        )

    audit = pd.DataFrame(audit_rows)

    for row in audit.itertuples(index=False):
        if row.month not in monthly.index:
            continue

        column_name = (
            "cny_pressure"
            if row.phase == "pressure"
            else "cny_normalisation"
        )

        monthly.loc[row.month, column_name] += row.fraction

    _validate_phase_allocations(
        audit=audit,
        start_year=start_date.year,
        end_year=end_date.year,
    )

    if (monthly < 0).any().any():
        raise ValueError(
            "CNY regressor fractions cannot be negative."
        )

    return CNYRegressorResult(
        monthly=monthly,
        audit=audit,
    )


def _validate_phase_allocations(
    audit: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> None:
    """Verify complete and non-overlapping annual phase allocations."""
    expected_index = pd.MultiIndex.from_product(
        [
            range(start_year, end_year + 1),
            ["pressure", "normalisation"],
        ],
        names=[
            "cny_year",
            "phase",
        ],
    )

    phase_sums = (
        audit.groupby(
            [
                "cny_year",
                "phase",
            ]
        )["fraction"]
        .sum()
        .reindex(expected_index)
    )

    if phase_sums.isna().any():
        missing_allocations = phase_sums[
            phase_sums.isna()
        ].index.tolist()

        raise ValueError(
            "Missing CNY phase allocations: "
            f"{missing_allocations}"
        )

    if not phase_sums.round(12).eq(1.0).all():
        invalid_sums = phase_sums.loc[
            ~phase_sums.round(12).eq(1.0)
        ]

        raise ValueError(
            "CNY phase fractions must sum to one by year:\n"
            f"{invalid_sums.to_string()}"
        )