# Decision Register

## Decided
- Mainland China
- Headline and core CPI targets
- Forecast horizon up to 24 months
- Five-year calendar-month operational benchmark
- Python implementation
- CEIC source data

## Provisional
- Model ladder: benchmark, AR, SARIMA, optional advanced challenger
- Published year-on-year inflation as the evaluation outcome
- Reconstructed normalised index for coherent forecast paths

## Open
- Primary loss function
- Evaluation start date
- Expanding versus rolling estimation
- Bootstrap design
- Practical-equivalence threshold

## Decided

- Primary model-development sample: January 2006 to December 2014
- Common development sample for headline and core CPI
- Final forecast origins: December 2014 to August 2024
- 117 complete forecast vintages through the 24-month horizon
- Expanding-window coefficient estimation
- SARIMA orders selected once and fixed during final evaluation
- Post-December 2014 observations excluded from model development
- SARIMA specification search uses only January 2006 to December 2014.
- Model form: SARIMA(p,0,q)(P,0,Q,12) with a constant.
- Candidate orders: p,q in {0,1,2}; P,Q in {0,1}.
- Complexity restriction: p + q + P + Q <= 4.
- Model selection hierarchy:
  1. successful and numerically valid estimation;
  2. competitive AICc and BIC;
  3. adequate residual diagnostics;
  4. internal time-series cross-validation as a selection aid;
  5. parsimony when competing models perform similarly.
- Internal cross-validation is part of model development and is not treated
  as an unbiased estimate of final out-of-sample performance.

  - Headline residual diagnostics showed significant remaining dependence near
  annual lags. The leading D=0 model also estimated seasonal AR and MA terms
  close to opposing unit-boundary values.
- A narrow D=1 headline specification check was therefore added during model
  development. This is intended to test whether explicit seasonal differencing
  provides a more stable representation than near-cancelling seasonal AR and
  MA terms.
- The D=1 amendment is limited to four predeclared specifications. No wider
  search will be conducted unless all four fail for a clearly documented
  technical reason.

- Headline model development will include a CNY-aware SARIMAX extension.
- The initial CNY specification uses fixed calendar-month indicators and one
  fractional moving-holiday regressor.
- The regressor allocates a predeclared 21-day CNY-affected window, from
  10 days before through 10 days after Chinese New Year, across the Gregorian
  months in which those days occur.
- Future CNY regressors are treated as known calendar information rather than
  forecast economic inputs.
- The CNY-ignorant SARIMA will remain in the model ladder as a comparator.
- More flexible pre-, during-, and post-holiday regressors will not be added
  unless the one-regressor specification provides a documented

  - The primary CNY-aware model uses two moving-holiday regressors.
- The CNY pressure phase runs from 14 days before through 14 days after
  Chinese New Year, inclusive.
- The post-CNY normalisation phase runs from 15 through 28 days after
  Chinese New Year, inclusive.
- Each phase is allocated fractionally across the Gregorian months in which
  its affected days fall.
- Pressure and normalisation coefficients are estimated freely without sign
  restrictions.