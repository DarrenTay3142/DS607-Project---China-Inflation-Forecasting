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

  - The CNY-aware ARMA(1,1) model materially reduced residual variation and
  estimated a significant positive CNY pressure effect, but residual
  autocorrelation remained concentrated at annual and annual-adjacent lags.
- A targeted comparison will therefore add either one seasonal AR term or
  one seasonal MA term to the CNY-aware SARIMAX model.
- Both seasonal terms will not initially be included together, to avoid
  recreating the near-cancelling seasonal AR-MA structure observed in the
  CNY-ignorant SARIMA.

- Headline internal validation used 25 monthly origins from December 2011
  through December 2013, with outcomes through December 2014.
- Both CNY-aware specifications generated valid forecasts at all 25 origins.
- The CNY-ignorant SARIMA generated valid forecasts at 23 of 25 origins.
  The September 2012 origin produced an economically invalid forecast path,
  and the December 2012 fit failed to converge.
- Accuracy comparisons among all three models were therefore calculated on
  the 23 common successful origins.
- The CNY-aware seasonal AR model performed best at the shortest horizons,
  while the CNY-aware seasonal MA model generally performed better at medium
  and longer horizons.
- The CNY-ignorant SARIMA performed best at longer horizons conditional on
  successful estimation, but had an 8 percent internal-origin failure rate.
- The CNY-aware SARIMAX with seasonal MA(1) errors is selected as the primary
  CNY-aware headline challenger because of its information criteria, residual
  adequacy, complete internal reliability, and medium-to-long-horizon
  performance.
- The equivalent CNY-aware seasonal AR(1) model is retained as a stability
  robustness specification because the selected seasonal MA root remains
  close to the invertibility boundary.

  - Core internal validation compared SARIMA(2,0,0)(1,0,1,12),
  SARIMA(1,0,1)(1,0,1,12), and SARIMA(0,0,2)(1,0,1,12).
- The models generated valid forecasts at 23, 24, and 25 of 25 internal
  origins respectively. Paired accuracy comparisons used the 22 origins
  common to all three models.
- SARIMA(1,0,1)(1,0,1,12) achieved the lowest MAE and RMSE at every
  highlighted horizon of 1, 3, 6, and 12 months, with its advantage generally
  increasing with horizon.
- SARIMA(1,0,1)(1,0,1,12) is selected as the primary core specification.
- SARIMA(0,0,2)(1,0,1,12) is retained as a reliability robustness
  specification because it generated valid forecasts at all internal origins.
- SARIMA(2,0,0)(1,0,1,12) is not selected despite leading full-development
  information criteria because it failed at two internal origins and produced
  weaker rolling forecast accuracy.
- All core candidates exhibited seasonal roots close to their stationarity
  or invertibility boundaries. Final evaluation will therefore continue to
  monitor convergence, root validity, and complete-path plausibility.

## Completed development-stage model selection

### Headline inflation

- The recursive five-year operational benchmark was compared with the
  CNY-ignorant SARIMA and two CNY-aware SARIMAX specifications on the
  23 internal origins successful for every model.
- The CNY-aware seasonal AR specification produced the lowest one-month
  forecast error.
- The operational benchmark produced the lowest RMSE at horizons 2 through
  12 and the lowest MAE at the principal medium and longer horizons.
- The CNY-ignorant SARIMA failed to produce a valid forecast trajectory at
  two of 25 attempted internal origins.
- Both CNY-aware specifications produced valid forecasts at all 25 origins.
- The operational benchmark remains the development-stage headline leader.
- SARIMAX(1,0,1)(0,0,1,12), with month indicators, CNY pressure, and
  post-CNY normalisation regressors, is locked as the primary CNY-aware
  headline challenger.
- The equivalent seasonal AR(1) specification is retained as a stability
  robustness model.
- The conventional CNY-ignorant SARIMA remains in the final model ladder
  despite its internal instability.

### Core inflation

- The recursive operational benchmark and three shortlisted SARIMA models
  were compared on the 22 internal origins successful for every statistical
  model.
- SARIMA(1,0,1)(1,0,1,12) produced the lowest MAE and RMSE at all highlighted
  horizons of 1, 3, 6, and 12 months.
- Its accuracy advantage over the operational benchmark increased with
  forecast horizon.
- SARIMA(1,0,1)(1,0,1,12) is locked as the primary core challenger.
- SARIMA(0,0,2)(1,0,1,12) is retained as a reliability robustness model.
- All fitted statistical models remain subject to strict convergence,
  stationarity, invertibility, finite-path, and positive-index checks.

### Final evaluation rule

- No model architecture, CNY phase definition, highlighted horizon, loss
  function, or estimation-window rule will be changed after examining
  forecasts originating after December 2014.
- Final evaluation uses expanding-window monthly re-estimation.
- Forecast origins run from December 2014 through August 2024.
- Complete outcomes are available through August 2026.
- Statistical models will be compared on common successful origins.
- Estimation failures will also be reported separately as a model-reliability
  outcome.