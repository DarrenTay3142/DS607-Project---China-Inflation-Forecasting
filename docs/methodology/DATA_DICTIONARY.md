# Data Dictionary

This document describes the source data, standardised variables, derived features, forecast outputs, and model-diagnostic fields used in the mainland China inflation forecasting project.

## 1. Data sources

### CPI data

The CPI series are obtained from **CEIC Data through the Singapore Management University Libraries subscription**.

The licensed source extract was downloaded on **4 October 2026** and is stored locally as:

```text
data/raw/china_cpi.csv
```

The extract is excluded from the public repository and must be obtained separately by an authorised user.

All four selected CPI series are:

- monthly;
- published for mainland China;
- sourced by CEIC from the National Bureau of Statistics of China;
- active in the CEIC database;
- available through August 2026 in the project extract.

### Chinese New Year calendar

Chinese New Year dates are obtained from a documented public calendar source and stored as:

```text
data/external/chinese_new_year_dates.csv
```

The calendar dates are deterministic and known in advance. They are used only to construct moving-holiday regressors.

## 2. Units and conventions

- Inflation rates are expressed in **percentage points**, not decimal proportions.
- Dates are standardised to the first day of each calendar month.
- Month-on-month inflation is abbreviated as **MoM**.
- Year-on-year inflation is abbreviated as **YoY**.
- Reconstructed index levels are normalised analytical series and are not official published CPI index levels.
- The common headline-and-core modelling history begins in January 2006.
- Forecast error is defined as:

$$
e_{T+h\mid T}
=
y_{T+h}
-
\widehat{y}_{T+h\mid T}.
$$

A negative forecast error therefore indicates that the forecast was above the published outcome.

---

# 3. Standardised CPI fields

The project loader selects four monthly mainland China CPI series from the local CEIC export and converts the CEIC relative-index values into inflation rates in percentage points.

| Project field | CEIC source series | CEIC series ID | SR code | Raw CEIC unit | Standardised unit | Source coverage |
|---|---|---|---|---|---|---|
| `headline_yoy_published` | `CN: Consumer Price Index` | `5724301 (CIEA)` | `SR568569` | `Prev Year=100` | Percentage points | January 1985 to August 2026 |
| `headline_mom_published` | `CN: Consumer Price Index: MoM` | `5716201 (CIAHJZ)` | `SR23496` | `Prev Mth=100` | Percentage points | January 1995 to August 2026 |
| `core_yoy_published` | `CN: CPI: Core (excl. Food & Energy)` | `143227301 (CIAHSV)` | `SR1903868` | `Prev Year=100` | Percentage points | January 2006 to August 2026 |
| `core_mom_published` | `CN: CPI: MoM: Core (excl. Food & Energy)` | `314418701 (CIAIEN)` | `SR5011464` | `Prev Mth=100` | Percentage points | January 2006 to August 2026 |

Additional source metadata:

- **Region:** China
- **Frequency:** Monthly
- **Source organisation:** National Bureau of Statistics of China
- **CEIC extraction date:** 4 October 2026
- **Latest source update shown in the export:** 9 September 2026
- **Last source observation:** August 2026

The project uses the common headline-and-core modelling period beginning in January 2006, even though the two headline series have longer source histories.

## Date field

| Field | Description | Source | Type | Coverage | Notes |
|---|---|---|---|---|---|
| `date` | Monthly observation date | CEIC export row labels | Monthly date | Varies by source series | Parsed from `MM/YYYY` and standardised to a unique, increasing month-start `DatetimeIndex` named `date` |

## Source-value transformation

The selected CEIC series are supplied as relative indexes centred on 100 rather than directly as percentage-point inflation rates.

For the year-on-year series:

$$
\pi_t^{\mathrm{YoY}}
=
R_t^{\mathrm{Prev\ Year}=100}
-100.
$$

For the month-on-month series:

$$
\pi_t^{\mathrm{MoM}}
=
R_t^{\mathrm{Prev\ Mth}=100}
-100.
$$

For example, a CEIC monthly relative value of $100.6$ is stored by the project as month-on-month inflation of

$$
100.6-100=0.6
$$

percentage points.

The standardised project columns therefore contain inflation rates in percentage points, not CEIC relative-index levels.

The exact source-column mapping is implemented in:

```text
src/data/load_ceic.py
```

## Source remarks

The CEIC export marks `CN: CPI: Core (excl. Food & Energy)` with a `[COVID-19-IMPACT]` series remark. This source metadata is retained as a documented caution but does not indicate that observations were manually adjusted by the project.

---

# 4. Reconstructed CPI fields

The project reconstructs normalised CPI index paths from the published month-on-month inflation rates.

For a month-on-month inflation rate $m_t$, the reconstructed index evolves according to:

$$
P_t
=
P_{t-1}
\left(
1+\frac{m_t}{100}
\right).
$$

The reconstructed year-on-year inflation rate is:

$$
\pi_t^{\mathrm{YoY,reconstructed}}
=
100
\left(
\frac{P_t}{P_{t-12}}
-1
\right).
$$

| Field | Description | Source | Unit | Coverage | Notes |
|---|---|---|---|---|---|
| `headline_index_reconstructed` | Normalised headline CPI index compounded from published headline MoM inflation | Derived from `headline_mom_published` | Index | From first usable headline MoM observation | Analytical index path; not an official published CPI index |
| `core_index_reconstructed` | Normalised core CPI index compounded from published core MoM inflation | Derived from `core_mom_published` | Index | From January 2006 | Analytical index path; not an official published CPI index |
| `headline_yoy_reconstructed` | Headline YoY inflation calculated from the reconstructed headline index | Derived | Percentage points | From the first month with a 12-month reconstructed comparison | Used to audit the monthly-to-annual transformation |
| `core_yoy_reconstructed` | Core YoY inflation calculated from the reconstructed core index | Derived | Percentage points | From the first month with a 12-month reconstructed comparison | Used to audit the monthly-to-annual transformation |
| `headline_yoy_discrepancy` | Reconstructed headline YoY minus published headline YoY | Derived | Percentage points | Where both series are available | Small differences are expected because published MoM values are rounded |
| `core_yoy_discrepancy` | Reconstructed core YoY minus published core YoY | Derived | Percentage points | Where both series are available | Small differences are expected because published MoM values are rounded |

The discrepancy fields are defined as:

$$
d_t
=
\widehat{\pi}_t^{\mathrm{YoY}}
-
\pi_t^{\mathrm{YoY,published}}.
$$

A non-zero discrepancy is not automatically a data error. Published month-on-month rates are rounded, while official year-on-year inflation may be calculated from higher-precision index values.

The reconstruction is implemented in:

```text
src/features/reconstruct_index.py
```

---

# 5. Chinese New Year calendar fields

The public Chinese New Year calendar file contains one dated holiday observation per year.

| Field | Description | Source | Unit or type | Coverage | Notes |
|---|---|---|---|---|---|
| `year` | Gregorian year associated with the Chinese New Year date | Public calendar source | Integer | 2006 through 2026 for the project | Must be unique within the calendar file |
| `cny_date` | Gregorian date of the first day of Chinese New Year | Public calendar source | Date | 2006 through 2026 | Converted to a date or timestamp by the project loader |

The calendar is loaded by:

```text
src/data/load_cny_calendar.py
```

---

# 6. Chinese New Year regressor fields

The project constructs two deterministic moving-holiday regressors from each Chinese New Year date.

## Pressure phase

The pressure phase covers the inclusive interval from 14 days before through 14 days after Chinese New Year. This is a 29-day interval.

## Normalisation phase

The normalisation phase covers the inclusive interval from 15 through 28 days after Chinese New Year. This is a 14-day interval.

Each phase is allocated fractionally across the Gregorian months containing its affected dates.

| Field | Description | Source | Unit | Range | Notes |
|---|---|---|---|---|---|
| `cny_pressure` | Fraction of the CNY pressure phase falling within a given Gregorian month | Derived from `cny_date` | Proportion | 0 to 1 | Monthly allocations sum to 1 within each CNY year |
| `cny_normalisation` | Fraction of the post-CNY normalisation phase falling within a given Gregorian month | Derived from `cny_date` | Proportion | 0 to 1 | Monthly allocations sum to 1 within each CNY year |

The regressors are constructed by:

```text
src/features/cny_regressors.py
```

## CNY allocation-audit fields

The regressor-building function also creates an audit table describing each monthly allocation.

| Field | Description | Unit or type | Notes |
|---|---|---|---|
| `cny_year` | Chinese New Year year associated with the phase | Integer | Identifies the annual holiday event |
| `phase` | CNY phase being allocated | Category | Identifies pressure or normalisation |
| `month` | Gregorian month receiving part of the phase | Monthly date | Stored using the project's monthly date convention |
| `affected_days` | Number of phase days falling within the month | Days | Integer count |
| `total_phase_days` | Total number of days in the relevant phase | Days | 29 for pressure and 14 for normalisation |
| `fraction` | Share of the phase allocated to the month | Proportion | Calculated as `affected_days / total_phase_days` |

---

# 7. Fixed month-indicator fields

The CNY-aware models include fixed Gregorian month effects.

| Field pattern | Description | Unit | Notes |
|---|---|---|---|
| `month_2` through `month_12` | Indicators for February through December | Binary | January is omitted as the reference category |

For month $m$:

$$
M_{m,t}
=
\begin{cases}
1, & \text{if observation }t\text{ occurs in month }m,\\
0, & \text{otherwise.}
\end{cases}
$$

The models also include an intercept, so omitting January avoids exact multicollinearity.

---

# 8. Operational-benchmark audit fields

The operational benchmark records the observations or recursively generated forecasts used to calculate each same-calendar-month average.

| Field | Description | Unit or type | Notes |
|---|---|---|---|
| `forecast_origin` | Last observed month before the forecast path begins | Monthly date | Defines the information set |
| `horizon` | Forecast horizon associated with the audited target | Months | Runs from 1 through 24 |
| `target_date` | Calendar month being forecast | Monthly date | Equal to origin plus horizon |
| `input_date` | Same-calendar-month date entering the five-year average | Monthly date | May precede or follow the forecast origin |
| `input_type` | Whether the benchmark input is observed or recursively forecast | Category | Expected values are `observed` and `forecast` |
| `input_value` | MoM inflation rate entering the average | Percentage points | Published rate or earlier benchmark forecast |

For horizons beyond 12 months, a benchmark input dated after the forecast origin must be an earlier recursively generated forecast rather than a realised future value.

---

# 9. Forecast-panel fields

The forecasting functions generate horizon-level output panels. Exact published-target column names differ between headline and core panels, but the principal fields are listed below.

| Field | Description | Unit or type | Notes |
|---|---|---|---|
| `model` | Model label | String | Identifies the benchmark, SARIMA, or SARIMAX specification |
| `forecast_origin` | Last month observed before the forecast path begins | Monthly date | The model may use information only through this date |
| `horizon` | Forecast horizon | Months | Runs from 1 through 24 |
| `target_date` | Calendar month being forecast | Monthly date | Equal to origin plus horizon |
| `mom_forecast` | Forecast published MoM inflation rate | Percentage points | Generated directly by the benchmark or statistical model |
| `index_forecast` | Reconstructed forecast CPI index level | Index | Obtained by recursively compounding monthly forecasts |
| `yoy_forecast` | Forecast YoY inflation implied by the reconstructed index path | Percentage points | Compared with the official published YoY target |
| `headline_yoy_published` | Realised official headline YoY inflation | Percentage points | Headline evaluation target |
| `core_yoy_published` | Realised official core YoY inflation | Percentage points | Core evaluation target |
| `forecast_error` | Published outcome minus forecast | Percentage points | Negative values indicate overforecasting |
| `absolute_error` | Absolute forecast error | Percentage points | Used to calculate MAE |
| `squared_error` | Squared forecast error | Squared percentage points | Used to calculate RMSE |

## Forecast-error metrics

For $N_h$ errors at horizon $h$:

$$
\mathrm{ME}_h
=
\frac{1}{N_h}
\sum_{i=1}^{N_h}
e_{i,h},
$$

$$
\mathrm{MAE}_h
=
\frac{1}{N_h}
\sum_{i=1}^{N_h}
\left|e_{i,h}\right|,
$$

and

$$
\mathrm{RMSE}_h
=
\sqrt{
\frac{1}{N_h}
\sum_{i=1}^{N_h}
e_{i,h}^{2}
}.
$$

---

# 10. Model-fitting diagnostic fields

The expanding-window evaluation records model reliability separately from forecast accuracy.

| Field | Description | Unit or type | Notes |
|---|---|---|---|
| `model` | Model label | String | Matches the forecast-panel model identifier |
| `forecast_origin` | Historical estimation endpoint | Monthly date | One row per attempted fit |
| `training_observations` | Number of observations used for estimation | Count | Increases under expanding-window evaluation |
| `converged` | Whether maximum-likelihood optimisation converged | Boolean | Non-converged fits are rejected |
| `finite_parameters` | Whether all fitted parameters are finite | Boolean | Required for a valid fit |
| `warning_count` | Number of fitting warnings | Count | Retained for diagnostic reporting |
| `warnings` | Fitting-warning messages | String | Empty when no warning is recorded |
| `minimum_ar_root_modulus` | Smallest modulus among fitted AR roots | Numeric | Values greater than 1 satisfy the root stationarity condition |
| `minimum_ma_root_modulus` | Smallest modulus among fitted MA roots | Numeric | Values greater than 1 satisfy the root invertibility condition |
| `error_message` | Error recorded when fitting or validation fails | String | Empty for successful fits |

A root modulus only slightly above one is formally valid but indicates proximity to the stationarity or invertibility boundary.

---

# 11. Likelihood-ratio output fields

The inference notebook exports a joint likelihood-ratio test and coefficient summary.

## LR-test table

| Field | Description | Unit or type |
|---|---|---|
| `restricted_log_likelihood` | Maximised log likelihood of the matched model without CNY regressors | Log-likelihood value |
| `unrestricted_log_likelihood` | Maximised log likelihood of the matched model with both CNY regressors | Log-likelihood value |
| `lr_statistic` | Twice the difference between unrestricted and restricted log likelihoods | Numeric |
| `degrees_of_freedom` | Number of restrictions imposed under the null | Count |
| `p_value` | Upper-tail probability under the conventional chi-square reference distribution | Probability |

The test statistic is:

$$
LR
=
2\left(
\ell_U-
\ell_R
\right).
$$

## CNY coefficient table

| Field | Description | Unit |
|---|---|---|
| `estimate` | Maximum-likelihood coefficient estimate | Percentage-point contribution for a full phase allocation |
| `standard_error` | Estimated coefficient standard error | Percentage points |
| `z_statistic` | Estimate divided by standard error | Unitless |
| `individual_p_value` | Two-sided individual coefficient-test p-value | Probability |
| `ci_lower` | Lower endpoint of the 95% confidence interval | Percentage points |
| `ci_upper` | Upper endpoint of the 95% confidence interval | Percentage points |

The project's principal inferential result is the joint likelihood-ratio test, not the individual coefficient tests.

---

# 12. Analysis periods

| Analysis stage | Start | End | Purpose |
|---|---|---|---|
| Available project extract | January 1985 for the longest headline series | August 2026 | Complete local CEIC extract across selected series |
| Common headline-and-core modelling history | January 2006 | August 2026 | Period with both headline and core MoM series available |
| Development sample | January 2006 | December 2014 | Identification, model development, diagnostics, and internal validation |
| Final forecast origins | December 2014 | August 2024 | Locked expanding-window evaluation |
| Final realised targets | January 2015 | August 2026 | Outcomes for forecast horizons up to 24 months |
| LR-test sample | January 2006 | December 2014 | Matched restricted and unrestricted likelihood comparison |
| CNY calendar coverage | 2006 | 2026 | Deterministic moving-holiday regressor construction |

The first final forecast origin is December 2014, and the first target is January 2015. December 2014 remains the final observed month in the information set for that first forecast.

---

# 13. Derived data files

The final evaluation and inference notebooks generate derived CSV outputs under:

```text
data/processed/
```

Expected outputs include:

```text
headline_final_forecasts_common_origins.csv
core_final_forecasts_common_origins.csv
headline_final_fitting_diagnostics.csv
core_final_fitting_diagnostics.csv
headline_cny_likelihood_ratio_test.csv
headline_cny_lr_model_comparison.csv
headline_cny_coefficient_results.csv
```

These files should be reviewed before publication to ensure that they contain derived model outputs rather than a reproducible copy of the licensed CEIC source observations.

Final publication-ready summaries should be placed under:

```text
outputs/tables/
outputs/figures/
```

---

# 14. Licensing and publication boundary

The following file is licensed and must not be committed to the public repository:

```text
data/raw/china_cpi.csv
```

The repository may contain:

- this data dictionary;
- access and reproduction instructions;
- code;
- the public Chinese New Year calendar;
- model parameters and diagnostics;
- aggregated forecast-evaluation metrics;
- derived figures and tables that do not reproduce the licensed source dataset.

Do not publish:

- the original CEIC extract;
- reformatted copies of its observations;
- credentials, access tokens, or restricted account information;
- processed files that allow the licensed source series to be reconstructed in full without a licensing review.

Before pushing the repository, verify:

```bash
git status
git ls-files data/raw
git check-ignore -v data/raw/china_cpi.csv
```

`git ls-files data/raw` must not list `china_cpi.csv`.
