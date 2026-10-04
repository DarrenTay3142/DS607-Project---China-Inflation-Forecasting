"""Reconstruct normalised CPI indices from published monthly changes."""

import pandas as pd


def validate_monthly_series(monthly_rate: pd.Series) -> pd.Series:
    """Validate and return a chronologically ordered monthly rate series."""
    if not isinstance(monthly_rate.index, pd.DatetimeIndex):
        raise TypeError("The monthly rate series must use a DatetimeIndex.")

    monthly_rate = monthly_rate.sort_index().dropna().astype(float)

    if monthly_rate.empty:
        raise ValueError("The monthly rate series contains no observations.")

    if not monthly_rate.index.is_unique:
        raise ValueError("The monthly rate series contains duplicate dates.")

    expected_dates = pd.date_range(
        start=monthly_rate.index.min(),
        end=monthly_rate.index.max(),
        freq="MS",
    )

    missing_dates = expected_dates.difference(monthly_rate.index)

    if not missing_dates.empty:
        formatted_dates = ", ".join(
            date.strftime("%Y-%m") for date in missing_dates
        )

        raise ValueError(
            "The monthly rate series contains missing months: "
            f"{formatted_dates}"
        )

    if (monthly_rate <= -100).any():
        raise ValueError(
            "Monthly inflation cannot be less than or equal to -100%."
        )

    return monthly_rate


def reconstruct_index(
    monthly_rate: pd.Series,
    base_value: float = 100.0,
) -> pd.Series:
    """Construct a normalised index from monthly percentage changes.

    The first observed month is assigned the supplied base value. Each
    subsequent index value is obtained by applying that month's published
    month-on-month percentage change to the preceding index value.
    """
    monthly_rate = validate_monthly_series(monthly_rate)

    if base_value <= 0:
        raise ValueError("The base index value must be positive.")

    growth_factor = 1 + monthly_rate / 100

    reconstructed_index = growth_factor.copy()
    reconstructed_index.iloc[0] = base_value

    if len(reconstructed_index) > 1:
        reconstructed_index.iloc[1:] = (
            growth_factor.iloc[1:].cumprod() * base_value
        )

    reconstructed_index.name = "reconstructed_index"

    return reconstructed_index


def calculate_monthly_rate(index_level: pd.Series) -> pd.Series:
    """Calculate month-on-month percentage changes from an index."""
    monthly_rate = index_level.pct_change(fill_method=None) * 100
    monthly_rate.name = "reconstructed_mom"

    return monthly_rate


def calculate_yoy_rate(index_level: pd.Series) -> pd.Series:
    """Calculate year-on-year percentage changes from an index."""
    yoy_rate = index_level.pct_change(
        periods=12,
        fill_method=None,
    ) * 100

    yoy_rate.name = "reconstructed_yoy"

    return yoy_rate


def add_reconstructed_indices(cpi: pd.DataFrame) -> pd.DataFrame:
    """Add reconstructed headline and core CPI indices and annual rates."""
    required_columns = {
        "headline_mom_published",
        "core_mom_published",
    }

    missing_columns = required_columns.difference(cpi.columns)

    if missing_columns:
        formatted_columns = ", ".join(sorted(missing_columns))

        raise ValueError(
            "The following required columns are missing: "
            f"{formatted_columns}"
        )

    result = cpi.copy()

    result["headline_index_reconstructed"] = reconstruct_index(
        result["headline_mom_published"]
    )

    result["core_index_reconstructed"] = reconstruct_index(
        result["core_mom_published"]
    )

    result["headline_yoy_reconstructed"] = calculate_yoy_rate(
        result["headline_index_reconstructed"]
    )

    result["core_yoy_reconstructed"] = calculate_yoy_rate(
        result["core_index_reconstructed"]
    )

    result["headline_yoy_discrepancy"] = (
        result["headline_yoy_reconstructed"]
        - result["headline_yoy_published"]
    )

    result["core_yoy_discrepancy"] = (
        result["core_yoy_reconstructed"]
        - result["core_yoy_published"]
    )

    return result