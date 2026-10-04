"""Load and validate the CEIC China CPI CSV extract."""

from pathlib import Path

import pandas as pd


HEADLINE_YOY = "CN: Consumer Price Index"
CORE_YOY = "CN: CPI: Core (excl. Food & Energy)"
HEADLINE_MOM = "CN: Consumer Price Index: MoM"
CORE_MOM = "CN: CPI: MoM: Core (excl. Food & Energy)"

REQUIRED_SERIES = [
    HEADLINE_YOY,
    CORE_YOY,
    HEADLINE_MOM,
    CORE_MOM,
]


def find_first_observation_row(file_path: Path) -> int:
    """Return the zero-based CSV row containing the first monthly observation."""
    raw = pd.read_csv(
        file_path,
        header=None,
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )

    first_column = raw.iloc[:, 0].str.strip()

    date_mask = first_column.str.fullmatch(
        r"(0[1-9]|1[0-2])/\d{4}",
        na=False,
    )

    matching_rows = raw.index[date_mask]

    if matching_rows.empty:
        raise ValueError(
            "No monthly observation row in MM/YYYY format was found."
        )

    return int(matching_rows[0])


def read_ceic_metadata(file_path: Path) -> pd.DataFrame:
    """Read the CEIC metadata rows and return metadata by series name."""
    first_observation_row = find_first_observation_row(file_path)

    metadata_raw = pd.read_csv(
        file_path,
        header=None,
        nrows=first_observation_row,
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )

    series_names = metadata_raw.iloc[0, 1:].str.strip()
    metadata = metadata_raw.iloc[1:, :].copy()

    metadata_labels = metadata.iloc[:, 0].str.strip()
    metadata_values = metadata.iloc[:, 1:]

    metadata_values.index = metadata_labels
    metadata_values.columns = series_names

    return metadata_values.T


def read_ceic_observations(file_path: Path) -> pd.DataFrame:
    """Read the dated observation section from the CEIC export."""
    first_observation_row = find_first_observation_row(file_path)

    observations = pd.read_csv(
        file_path,
        header=0,
        skiprows=range(1, first_observation_row),
        low_memory=False,
    )

    date_column = observations.columns[0]

    observations = observations.rename(columns={date_column: "date"})
    observations["date"] = pd.to_datetime(
        observations["date"],
        format="%m/%Y",
        errors="coerce",
    )

    observations = observations.dropna(subset=["date"])
    observations = observations.set_index("date").sort_index()

    return observations


def validate_required_series(observations: pd.DataFrame) -> None:
    """Raise an error if any required CPI series is absent."""
    missing_series = [
        series
        for series in REQUIRED_SERIES
        if series not in observations.columns
    ]

    if missing_series:
        formatted_missing = "\n".join(
            f"- {series}" for series in missing_series
        )

        raise ValueError(
            "The following required CEIC series are missing:\n"
            f"{formatted_missing}"
        )


def load_cpi_series(file_path: Path) -> pd.DataFrame:
    """Load and transform the four required headline and core CPI series."""
    observations = read_ceic_observations(file_path)
    validate_required_series(observations)

    cpi = observations[REQUIRED_SERIES].copy()

    cpi = cpi.rename(
        columns={
            HEADLINE_YOY: "headline_yoy_relative",
            CORE_YOY: "core_yoy_relative",
            HEADLINE_MOM: "headline_mom_relative",
            CORE_MOM: "core_mom_relative",
        }
    )

    cpi = cpi.apply(pd.to_numeric, errors="coerce")

    cpi["headline_yoy_published"] = (
        cpi["headline_yoy_relative"] - 100
    )
    cpi["core_yoy_published"] = (
        cpi["core_yoy_relative"] - 100
    )
    cpi["headline_mom_published"] = (
        cpi["headline_mom_relative"] - 100
    )
    cpi["core_mom_published"] = (
        cpi["core_mom_relative"] - 100
    )

    final_columns = [
        "headline_yoy_published",
        "headline_mom_published",
        "core_yoy_published",
        "core_mom_published",
    ]

    return cpi[final_columns]
