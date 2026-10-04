# Forecasting Mainland China Inflation

DS607 Statistics for Data Science individual course project, completed with instructor approval.

## Research question

Do systematically estimated time-series models produce statistically and practically meaningful improvements in out-of-sample forecasts of mainland China's headline and core CPI inflation relative to a five-year calendar-month operational benchmark?

## Student author

Darren TAY Teck Yong

## Model ladder

1. Five-year calendar-month operational benchmark
2. Parsimonious autoregressive model
3. SARIMA model
4. Optional advanced challenger, such as random forest or a MODWT-based hybrid

## Data

The source data are licensed CEIC data accessed through Singapore Management University. Raw extracts are excluded from Git and must be placed in `data/raw/` by an authorised user.

## Repository structure

- `data/`: raw, interim, and processed data
- `notebooks/`: numbered analytical notebooks
- `src/`: reusable data, model, evaluation, and plotting code
- `tests/`: automated checks
- `outputs/`: final figures, tables, and presentation
- `docs/`: proposal and methodological documentation
