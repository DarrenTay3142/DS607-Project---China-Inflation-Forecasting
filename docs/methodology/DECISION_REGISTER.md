# Decision Register

This register records the final methodological decisions, completed analytical findings, superseded proposals, and remaining administrative tasks for the mainland China inflation forecasting project.

The project was completed individually by Darren TAY Teck Yong with instructor approval.

## Status definitions

- **Decided:** final methodological or project decision.
- **Completed finding:** empirical result established by the executed analysis.
- **Superseded or rejected:** an earlier proposal or investigated branch that is not part of the final design.
- **Open administrative item:** publication or submission work that does not alter the statistical analysis.

---

# 1. Research scope

## Decided

- The project studies monthly mainland China consumer price inflation.
- The two forecast targets are:
  - headline CPI inflation;
  - core CPI inflation excluding food and energy.
- Published month-on-month inflation is the modelling input.
- Forecast month-on-month rates are compounded into reconstructed CPI index paths.
- Forecast index paths are converted into year-on-year inflation forecasts.
- Published year-on-year inflation is the final evaluation outcome.
- Forecast horizons run from 1 through 24 months.
- The analysis is implemented in Python.
- CPI data are obtained from CEIC Data through the Singapore Management University Libraries subscription.
- Chinese New Year dates are obtained from a documented public calendar source.
- Licensed CEIC observations are maintained locally and excluded from the public repository.

## Final research questions

### Forecasting question

Do parsimonious seasonal time-series models produce practically meaningful improvements in out-of-sample forecasts of mainland China’s headline and core CPI inflation relative to a five-year calendar-month operational benchmark?

### Explanatory-inference question

Holding fixed Gregorian month effects and a matched SARIMA error specification constant, do Chinese New Year pressure and post-CNY normalisation regressors jointly improve the maximised likelihood of the headline month-on-month inflation model?

## Interpretation rule

- Forecast accuracy and explanatory likelihood answer different questions.
- A variable may improve the fitted likelihood without improving multi-step forecast accuracy.
- Forecast accuracy, fitting reliability, and explanatory inference are reported separately.

---

# 2. Data and transformation design

## Decided

- The common headline-and-core modelling history begins in January 2006.
- The local CEIC extract ends in August 2026.
- The licensed extract was downloaded on 4 October 2026.
- Four published series are used:
  - headline year-on-year inflation;
  - headline month-on-month inflation;
  - core year-on-year inflation;
  - core month-on-month inflation.
- Dates are standardised to a monthly, month-start `DatetimeIndex`.
- CEIC relative-index values centred on 100 are converted into percentage-point inflation rates by subtracting 100.
- Missing observations before a source series begins are not imputed.
- Headline and core reconstructed indices are normalised analytical objects rather than official CPI index series.
- Discrepancy is defined as:

$$
d_t
=
\widehat{\pi}_t^{\mathrm{YoY}}
-
\pi_t^{\mathrm{YoY,published}}.
$$

- Small reconstruction discrepancies are expected because published month-on-month rates are rounded.
- Published year-on-year inflation remains the authoritative evaluation outcome.

## Index reconstruction

For monthly inflation $m_t$:

$$
P_t
=
P_{t-1}
\left(
1+\frac{m_t}{100}
\right).
$$

Reconstructed year-on-year inflation is:

$$
\widehat{\pi}_t^{\mathrm{YoY}}
=
100
\left(
\frac{P_t}{P_{t-12}}
-1
\right).
$$

## Completed findings

- Both reconstructed index paths are coherent and positive over the project sample.
- Reconstructed year-on-year inflation follows the timing and direction of the corresponding published series.
- Small differences remain because rounded monthly releases do not exactly reproduce official year-on-year calculations.
- The reconstruction is suitable for converting forecast monthly rates into multi-horizon year-on-year forecasts.

---

# 3. Sample separation

## Decided

### Development sample

```text
January 2006 to December 2014
