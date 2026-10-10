"""Internal validation for the recursive operational benchmark."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.models.operational_benchmark import (
    forecast_operational_benchmark,
)


@dataclass
class BenchmarkValidationResult:
    """Forecast-level and horizon-level benchmark results."""

    forecasts: pd.DataFrame
    metrics: pd.DataFrame


def _validate_aligned_monthly_inputs(
    monthly_rate: pd.Series,
    reconstructed_index: pd.Series,
    published_yoy: pd.Series,
) -> None:
    """Validate complete and aligned monthly input series."""
    series_collection = {
        "monthly_rate": monthly_rate,
        "reconstructed_index": reconstructed_index,
        "published_yoy": published_yoy,
    }

    for name, series in series_collection.items():
        if not isinstance(series.index, pd.DatetimeIndex):
            raise TypeError(
                f"{name} must use a DatetimeIndex."
            )

        if not series.index.is_unique:
            raise ValueError(
                f"{name} contains duplicate dates."
            )

        if not series.index.is_monotonic_increasing:
            raise ValueError(
                f"{name} must be chronologically ordered."
            )

    if not monthly_rate.index.equals(
        reconstructed_index.index
    ):
        raise ValueError(
            "monthly_rate and reconstructed_index must "
            "have identical indexes."
        )

    if not monthly_rate.index.equals(
        published_yoy.index
    ):
        raise ValueError(
            "monthly_rate and published_yoy must have "
            "identical indexes."
        )

    expected_index = pd.date_range(
        start=monthly_rate.index.min(),
        end=monthly_rate.index.max(),
        freq="MS",
    )

    if not monthly_rate.index.equals(expected_index):
        raise ValueError(
            "The input data must form a continuous "
            "monthly-start series."
        )

    if monthly_rate.isna().any():
        raise ValueError(
            "monthly_rate contains missing observations."
        )

    if reconstructed_index.isna().any():
        raise ValueError(
            "reconstructed_index contains missing observations."
        )


def _calculate_metrics(
    forecasts: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate horizon-level benchmark accuracy measures."""
    if forecasts.empty:
        return pd.DataFrame(
            columns=[
                "model",
                "horizon",
                "forecast_count",
                "mean_error",
                "mae",
                "rmse",
            ]
        )

    metrics = (
        forecasts.groupby(
            [
                "model",
                "horizon",
            ],
            as_index=False,
        )
        .agg(
            forecast_count=(
                "forecast_error",
                "count",
            ),
            mean_error=(
                "forecast_error",
                "mean",
            ),
            mae=(
                "absolute_error",
                "mean",
            ),
            mse=(
                "squared_error",
                "mean",
            ),
        )
    )

    metrics["rmse"] = np.sqrt(
        metrics["mse"]
    )

    return metrics.drop(
        columns="mse"
    )


def run_operational_benchmark_validation(
    monthly_rate: pd.Series,
    reconstructed_index: pd.Series,
    published_yoy: pd.Series,
    model_label: str,
    first_origin,
    final_origin,
    horizon: int = 12,
    window_years: int = 5,
) -> BenchmarkValidationResult:
    """Run recursive operational-benchmark internal validation.

    A separate temporary extended monthly series is created at every
    forecast origin. Forecast values generated for one origin never enter
    another origin's forecast calculation.
    """
    if horizon < 1:
        raise ValueError(
            "horizon must be at least one month."
        )

    if window_years < 1:
        raise ValueError(
            "window_years must be at least one."
        )

    monthly_rate = (
        monthly_rate
        .asfreq("MS")
        .astype(float)
    )

    reconstructed_index = (
        reconstructed_index
        .asfreq("MS")
        .astype(float)
    )

    published_yoy = (
        published_yoy
        .asfreq("MS")
        .astype(float)
    )

    _validate_aligned_monthly_inputs(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
    )

    first_origin = pd.Timestamp(first_origin)
    final_origin = pd.Timestamp(final_origin)

    origins = pd.date_range(
        start=first_origin,
        end=final_origin,
        freq="MS",
    )

    forecast_rows = []

    for origin in origins:
        if origin not in monthly_rate.index:
            raise ValueError(
                f"Forecast origin {origin:%Y-%m} is absent."
            )

        target_dates = pd.date_range(
            start=origin + pd.DateOffset(months=1),
            periods=horizon,
            freq="MS",
        )

        unavailable_dates = target_dates.difference(
            published_yoy.index
        )

        if not unavailable_dates.empty:
            formatted_dates = ", ".join(
                date.strftime("%Y-%m")
                for date in unavailable_dates
            )

            raise ValueError(
                "Forecast targets extend beyond available outcomes: "
                f"{formatted_dates}"
            )

        benchmark_result = forecast_operational_benchmark(
            monthly_rate=monthly_rate,
            index_level=reconstructed_index,
            forecast_origin=origin,
            horizon=horizon,
            window_years=window_years,
        )

        origin_forecast = (
            benchmark_result.forecast
            .set_index("target_date")
            .copy()
        )

        origin_forecast["yoy_actual"] = (
            published_yoy.loc[
                origin_forecast.index
            ]
        )

        origin_forecast["forecast_error"] = (
            origin_forecast["yoy_actual"]
            - origin_forecast["yoy_forecast"]
        )

        origin_forecast["absolute_error"] = (
            origin_forecast[
                "forecast_error"
            ].abs()
        )

        with np.errstate(
            over="raise",
            invalid="raise",
        ):
            origin_forecast["squared_error"] = (
                origin_forecast[
                    "forecast_error"
                ].pow(2)
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

        if not np.isfinite(
            origin_forecast[
                numeric_columns
            ].to_numpy()
        ).all():
            raise RuntimeError(
                f"The operational benchmark produced nonfinite "
                f"results at origin {origin:%Y-%m}."
            )

        origin_forecast = (
            origin_forecast.reset_index()
        )

        for row in origin_forecast.itertuples(
            index=False
        ):
            forecast_rows.append(
                {
                    "model": model_label,
                    "forecast_origin": origin,
                    "target_date": row.target_date,
                    "horizon": int(row.horizon),
                    "mom_forecast": float(
                        row.mom_forecast
                    ),
                    "index_forecast": float(
                        row.index_forecast
                    ),
                    "yoy_forecast": float(
                        row.yoy_forecast
                    ),
                    "yoy_actual": float(
                        row.yoy_actual
                    ),
                    "forecast_error": float(
                        row.forecast_error
                    ),
                    "absolute_error": float(
                        row.absolute_error
                    ),
                    "squared_error": float(
                        row.squared_error
                    ),
                }
            )

    forecasts = pd.DataFrame(
        forecast_rows
    )

    expected_rows = (
        len(origins) * horizon
    )

    if len(forecasts) != expected_rows:
        raise RuntimeError(
            "The operational benchmark did not produce "
            "a complete forecast panel."
        )

    rows_per_origin = (
        forecasts.groupby(
            "forecast_origin"
        )
        .size()
    )

    if not rows_per_origin.eq(horizon).all():
        raise RuntimeError(
            "At least one operational-benchmark origin "
            "has an incomplete forecast trajectory."
        )

    metrics = _calculate_metrics(
        forecasts
    )

    return BenchmarkValidationResult(
        forecasts=forecasts,
        metrics=metrics,
    )