"""Recursive five-year calendar-month inflation benchmark."""

from dataclasses import dataclass

import pandas as pd

from src.features.reconstruct_index import validate_monthly_series


@dataclass
class BenchmarkResult:
    """Outputs from one operational-benchmark forecast vintage."""

    forecast: pd.DataFrame
    audit: pd.DataFrame


def forecast_operational_benchmark(
    monthly_rate: pd.Series,
    index_level: pd.Series,
    forecast_origin: str | pd.Timestamp,
    horizon: int = 24,
    window_years: int = 5,
) -> BenchmarkResult:
    """Generate one recursive calendar-month benchmark forecast.

    At each future month, the forecast equals the arithmetic mean of the
    latest five entries for the same calendar month. Those entries may
    include forecasts generated earlier in the same forecast trajectory.

    Parameters
    ----------
    monthly_rate:
        Observed month-on-month inflation rates in percentage points.
    index_level:
        Reconstructed CPI index corresponding to the observed monthly rates.
    forecast_origin:
        Latest observed month available to the forecaster.
    horizon:
        Number of months to forecast.
    window_years:
        Number of matching calendar-month observations used in each mean.

    Returns
    -------
    BenchmarkResult
        A forecast table and an input-level audit table.
    """
    if horizon < 1:
        raise ValueError("The forecast horizon must be at least one month.")

    if window_years < 1:
        raise ValueError("The averaging window must be at least one year.")

    monthly_rate = validate_monthly_series(monthly_rate)
    index_level = index_level.sort_index().dropna().astype(float)

    if not isinstance(index_level.index, pd.DatetimeIndex):
        raise TypeError("The index level series must use a DatetimeIndex.")

    forecast_origin = pd.Timestamp(forecast_origin)

    if forecast_origin not in monthly_rate.index:
        raise ValueError(
            f"The forecast origin {forecast_origin:%Y-%m} "
            "is absent from the monthly rate series."
        )

    if forecast_origin not in index_level.index:
        raise ValueError(
            f"The forecast origin {forecast_origin:%Y-%m} "
            "is absent from the reconstructed index."
        )

    if not monthly_rate.index.equals(index_level.index):
        raise ValueError(
            "The monthly rate and index level series must have "
            "identical dates."
        )

    observed_monthly_rate = monthly_rate.loc[:forecast_origin].copy()
    observed_index = index_level.loc[:forecast_origin].copy()

    # Temporary extended series for this forecast origin only.
    extended_monthly_rate = observed_monthly_rate.copy()
    extended_index = observed_index.copy()

    forecast_rows = []
    audit_rows = []

    for horizon_number in range(1, horizon + 1):
        target_date = forecast_origin + pd.DateOffset(
            months=horizon_number
        )

        matching_month = extended_monthly_rate[
            extended_monthly_rate.index.month == target_date.month
        ]

        selected_inputs = matching_month.tail(window_years)

        if len(selected_inputs) < window_years:
            raise ValueError(
                f"Only {len(selected_inputs)} observations are available "
                f"for calendar month {target_date.month}; "
                f"{window_years} are required."
            )

        monthly_forecast = selected_inputs.mean()

        previous_date = target_date - pd.DateOffset(months=1)
        previous_index = extended_index.loc[previous_date]

        index_forecast = previous_index * (
            1 + monthly_forecast / 100
        )

        # Append forecasts before moving to the next horizon. This is what
        # makes the method recursive from the second forecast year onward.
        extended_monthly_rate.loc[target_date] = monthly_forecast
        extended_index.loc[target_date] = index_forecast

        denominator_date = target_date - pd.DateOffset(months=12)
        denominator_index = extended_index.loc[denominator_date]

        yoy_forecast = (
            index_forecast / denominator_index - 1
        ) * 100

        forecast_rows.append(
            {
                "forecast_origin": forecast_origin,
                "target_date": target_date,
                "horizon": horizon_number,
                "mom_forecast": monthly_forecast,
                "index_forecast": index_forecast,
                "yoy_forecast": yoy_forecast,
            }
        )

        for input_rank, (input_date, input_rate) in enumerate(
            selected_inputs.items(),
            start=1,
        ):
            audit_rows.append(
                {
                    "forecast_origin": forecast_origin,
                    "target_date": target_date,
                    "horizon": horizon_number,
                    "input_rank": input_rank,
                    "input_date": input_date,
                    "input_rate": input_rate,
                    "input_type": (
                        "observed"
                        if input_date <= forecast_origin
                        else "forecast"
                    ),
                    "mom_forecast": monthly_forecast,
                }
            )

    forecast = pd.DataFrame(forecast_rows)
    audit = pd.DataFrame(audit_rows)

    return BenchmarkResult(
        forecast=forecast,
        audit=audit,
    )