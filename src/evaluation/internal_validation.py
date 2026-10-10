"""Expanding-window internal validation for inflation forecasting models."""

from dataclasses import dataclass
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


@dataclass(frozen=True)
class ModelSpecification:
    """Fixed SARIMA or SARIMAX architecture."""

    label: str
    order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int]
    trend: str = "c"
    uses_exog: bool = False


@dataclass
class InternalValidationResult:
    """Forecast errors, fitting diagnostics, and summary metrics."""

    forecasts: pd.DataFrame
    fitting: pd.DataFrame
    metrics: pd.DataFrame


def _validate_model_inputs(
    monthly_rate: pd.Series,
    reconstructed_index: pd.Series,
    published_yoy: pd.Series,
    exog: pd.DataFrame | None,
) -> None:
    """Validate aligned monthly modelling inputs."""
    if not isinstance(monthly_rate.index, pd.DatetimeIndex):
        raise TypeError(
            "monthly_rate must use a DatetimeIndex."
        )

    if not monthly_rate.index.equals(
        reconstructed_index.index
    ):
        raise ValueError(
            "monthly_rate and reconstructed_index must "
            "have identical indexes."
        )

    if not monthly_rate.index.equals(published_yoy.index):
        raise ValueError(
            "monthly_rate and published_yoy must "
            "have identical indexes."
        )

    if not monthly_rate.index.is_unique:
        raise ValueError(
            "The modelling index contains duplicate dates."
        )

    expected_index = pd.date_range(
        monthly_rate.index.min(),
        monthly_rate.index.max(),
        freq="MS",
    )

    if not monthly_rate.index.equals(expected_index):
        raise ValueError(
            "The modelling data must form a continuous "
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

    if exog is not None:
        if not exog.index.equals(monthly_rate.index):
            raise ValueError(
                "exog and monthly_rate must have identical indexes."
            )

        if exog.isna().any().any():
            raise ValueError(
                "exog contains missing observations."
            )


def _minimum_root_modulus(roots) -> float:
    """Return the minimum root modulus or NaN if no roots exist."""
    roots = np.asarray(roots)

    if roots.size == 0:
        return np.nan

    return float(np.min(np.abs(roots)))


def _calculate_yoy_forecast(
    historical_index: pd.Series,
    forecast_index: pd.Series,
) -> pd.Series:
    """Calculate YoY forecasts from observed and forecast index levels."""
    combined_index = pd.concat(
        [
            historical_index,
            forecast_index,
        ]
    )

    combined_index = combined_index[
        ~combined_index.index.duplicated(keep="last")
    ].sort_index()

    yoy_forecast = (
        combined_index
        / combined_index.shift(12)
        - 1
    ) * 100

    yoy_forecast = yoy_forecast.reindex(
        forecast_index.index
    )

    yoy_forecast.name = "yoy_forecast"

    return yoy_forecast


def run_expanding_internal_validation(
    monthly_rate: pd.Series,
    reconstructed_index: pd.Series,
    published_yoy: pd.Series,
    specification: ModelSpecification,
    first_origin,
    final_origin,
    horizon: int = 12,
    exog: pd.DataFrame | None = None,
    maxiter: int = 500,
) -> InternalValidationResult:
    """Run expanding-window internal validation for one model.

    At every forecast origin, coefficients are estimated using only
    observations available through that origin. Model orders remain fixed.

    An origin contributes forecasts only if estimation converges and the
    complete forecast trajectory is finite and mechanically valid.
    """
    if horizon < 1:
        raise ValueError(
            "horizon must be at least one month."
        )

    monthly_rate = monthly_rate.asfreq("MS").astype(float)

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

    if exog is not None:
        exog = exog.asfreq("MS").astype(float)

    _validate_model_inputs(
        monthly_rate=monthly_rate,
        reconstructed_index=reconstructed_index,
        published_yoy=published_yoy,
        exog=exog,
    )

    if specification.uses_exog and exog is None:
        raise ValueError(
            f"{specification.label} requires exogenous regressors."
        )

    if not specification.uses_exog and exog is not None:
        raise ValueError(
            f"{specification.label} does not use exogenous regressors."
        )

    first_origin = pd.Timestamp(first_origin)
    final_origin = pd.Timestamp(final_origin)

    origins = pd.date_range(
        first_origin,
        final_origin,
        freq="MS",
    )

    forecast_rows = []
    fitting_rows = []

    for origin in origins:
        if origin not in monthly_rate.index:
            raise ValueError(
                f"Forecast origin {origin:%Y-%m} is absent."
            )

        target_dates = pd.date_range(
            origin + pd.DateOffset(months=1),
            periods=horizon,
            freq="MS",
        )

        unavailable_dates = target_dates.difference(
            monthly_rate.index
        )

        if not unavailable_dates.empty:
            formatted_dates = ", ".join(
                date.strftime("%Y-%m")
                for date in unavailable_dates
            )

            raise ValueError(
                "Forecast targets extend beyond available data: "
                f"{formatted_dates}"
            )

        training_rate = monthly_rate.loc[:origin]

        training_exog = None
        future_exog = None

        if specification.uses_exog:
            training_exog = exog.loc[:origin]
            future_exog = exog.loc[target_dates]

        warning_messages = []

        minimum_ar_root = np.nan
        minimum_ma_root = np.nan
        finite_parameters = False
        converged = False

        try:
            with warnings.catch_warnings(
                record=True
            ) as captured:
                warnings.simplefilter("always")

                model = SARIMAX(
                    endog=training_rate,
                    exog=training_exog,
                    order=specification.order,
                    seasonal_order=(
                        specification.seasonal_order
                    ),
                    trend=specification.trend,
                    enforce_stationarity=True,
                    enforce_invertibility=True,
                )

                fitted = model.fit(
                    disp=False,
                    maxiter=maxiter,
                )

                warning_messages = [
                    str(item.message)
                    for item in captured
                ]

            converged = bool(
                fitted.mle_retvals.get(
                    "converged",
                    False,
                )
            )

            if not converged:
                raise RuntimeError(
                    "Maximum-likelihood estimation did not "
                    "converge."
                )

            finite_parameters = bool(
                np.isfinite(fitted.params).all()
            )

            if not finite_parameters:
                raise RuntimeError(
                    "The fitted model contains nonfinite "
                    "parameters."
                )

            minimum_ar_root = _minimum_root_modulus(
                fitted.arroots
            )

            minimum_ma_root = _minimum_root_modulus(
                fitted.maroots
            )

            if (
                np.isfinite(minimum_ar_root)
                and minimum_ar_root <= 1.0
            ):
                raise RuntimeError(
                    "The fitted AR process is not stationary."
                )

            if (
                np.isfinite(minimum_ma_root)
                and minimum_ma_root <= 1.0
            ):
                raise RuntimeError(
                    "The fitted MA process is not invertible."
                )

            forecast_result = fitted.get_forecast(
                steps=horizon,
                exog=future_exog,
            )

            mom_forecast = pd.Series(
                np.asarray(
                    forecast_result.predicted_mean,
                    dtype=float,
                ),
                index=target_dates,
                name="mom_forecast",
            )

            if not np.isfinite(mom_forecast).all():
                raise RuntimeError(
                    "The model generated nonfinite monthly "
                    "forecasts."
                )

            growth_factors = (
                1 + mom_forecast / 100
            )

            if not np.isfinite(growth_factors).all():
                raise RuntimeError(
                    "The model generated nonfinite growth "
                    "factors."
                )

            if (growth_factors <= 0).any():
                raise RuntimeError(
                    "The model generated a monthly forecast "
                    "implying a nonpositive price index."
                )

            origin_index = float(
                reconstructed_index.loc[origin]
            )

            with np.errstate(
                over="raise",
                invalid="raise",
            ):
                cumulative_growth = (
                    growth_factors.cumprod()
                )

                index_forecast = pd.Series(
                    origin_index * cumulative_growth,
                    index=target_dates,
                    name="index_forecast",
                    dtype=float,
                )

            if not np.isfinite(index_forecast).all():
                raise RuntimeError(
                    "The model generated nonfinite index "
                    "forecasts."
                )

            yoy_forecast = _calculate_yoy_forecast(
                historical_index=(
                    reconstructed_index.loc[:origin]
                ),
                forecast_index=index_forecast,
            )

            if not np.isfinite(yoy_forecast).all():
                raise RuntimeError(
                    "The model generated nonfinite "
                    "year-on-year forecasts."
                )

            actual_yoy = published_yoy.loc[
                target_dates
            ]

            if not np.isfinite(actual_yoy).all():
                raise RuntimeError(
                    "The realised year-on-year series contains "
                    "nonfinite values."
                )

            forecast_error = (
                actual_yoy - yoy_forecast
            )

            if not np.isfinite(forecast_error).all():
                raise RuntimeError(
                    "The model generated nonfinite forecast "
                    "errors."
                )

            absolute_error = forecast_error.abs()

            with np.errstate(
                over="raise",
                invalid="raise",
            ):
                squared_error = forecast_error.pow(2)

            if not np.isfinite(squared_error).all():
                raise RuntimeError(
                    "The model generated nonfinite squared "
                    "forecast errors."
                )

            # Store this origin temporarily. Nothing is appended to the
            # final table until every horizon passes validation.
            origin_forecast_rows = []

            for horizon_number, target_date in enumerate(
                target_dates,
                start=1,
            ):
                origin_forecast_rows.append(
                    {
                        "model": specification.label,
                        "forecast_origin": origin,
                        "target_date": target_date,
                        "horizon": horizon_number,
                        "mom_forecast": float(
                            mom_forecast.loc[target_date]
                        ),
                        "index_forecast": float(
                            index_forecast.loc[target_date]
                        ),
                        "yoy_forecast": float(
                            yoy_forecast.loc[target_date]
                        ),
                        "yoy_actual": float(
                            actual_yoy.loc[target_date]
                        ),
                        "forecast_error": float(
                            forecast_error.loc[target_date]
                        ),
                        "absolute_error": float(
                            absolute_error.loc[target_date]
                        ),
                        "squared_error": float(
                            squared_error.loc[target_date]
                        ),
                    }
                )

            forecast_rows.extend(
                origin_forecast_rows
            )

            fitting_rows.append(
                {
                    "model": specification.label,
                    "forecast_origin": origin,
                    "training_observations": len(
                        training_rate
                    ),
                    "converged": converged,
                    "finite_parameters": (
                        finite_parameters
                    ),
                    "warning_count": len(
                        warning_messages
                    ),
                    "warnings": " | ".join(
                        warning_messages
                    ),
                    "minimum_ar_root_modulus": (
                        minimum_ar_root
                    ),
                    "minimum_ma_root_modulus": (
                        minimum_ma_root
                    ),
                    "seasonal_ar_estimate": (
                        fitted.params.get(
                            "ar.S.L12",
                            np.nan,
                        )
                    ),
                    "seasonal_ma_estimate": (
                        fitted.params.get(
                            "ma.S.L12",
                            np.nan,
                        )
                    ),
                    "cny_pressure_estimate": (
                        fitted.params.get(
                            "cny_pressure",
                            np.nan,
                        )
                    ),
                    "cny_normalisation_estimate": (
                        fitted.params.get(
                            "cny_normalisation",
                            np.nan,
                        )
                    ),
                    "ordinary_ar_1_estimate": (
                        fitted.params.get(
                            "ar.L1",
                            np.nan,
                        )
                    ),
                    "ordinary_ma_1_estimate": (
                        fitted.params.get(
                            "ma.L1",
                            np.nan,
                        )
                    ),
                    "error_message": "",
                }
            )

        except Exception as error:
            fitting_rows.append(
                {
                    "model": specification.label,
                    "forecast_origin": origin,
                    "training_observations": len(
                        training_rate
                    ),
                    "converged": converged,
                    "finite_parameters": (
                        finite_parameters
                    ),
                    "warning_count": len(
                        warning_messages
                    ),
                    "warnings": " | ".join(
                        warning_messages
                    ),
                    "minimum_ar_root_modulus": (
                        minimum_ar_root
                    ),
                    "minimum_ma_root_modulus": (
                        minimum_ma_root
                    ),
                    "seasonal_ar_estimate": np.nan,
                    "seasonal_ma_estimate": np.nan,
                    "cny_pressure_estimate": np.nan,
                    "cny_normalisation_estimate": np.nan,
                    "ordinary_ar_1_estimate": np.nan,
                    "ordinary_ma_1_estimate": np.nan,
                    "error_message": (
                        f"{type(error).__name__}: {error}"
                    ),
                }
            )

    forecasts = pd.DataFrame(forecast_rows)
    fitting = pd.DataFrame(fitting_rows)

    if not forecasts.empty:
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
            forecasts[
                numeric_columns
            ].to_numpy()
        ).all():
            raise RuntimeError(
                "Internal validation produced nonfinite "
                "forecast results."
            )

    if forecasts.empty:
        metrics = pd.DataFrame(
            columns=[
                "model",
                "horizon",
                "forecast_count",
                "mean_error",
                "mae",
                "rmse",
            ]
        )
    else:
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

        metrics = metrics.drop(
            columns="mse"
        )

    return InternalValidationResult(
        forecasts=forecasts,
        fitting=fitting,
        metrics=metrics,
    )