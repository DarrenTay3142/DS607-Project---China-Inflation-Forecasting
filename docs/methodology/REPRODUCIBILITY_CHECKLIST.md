# Reproducibility Checklist

This checklist verifies that the mainland China inflation forecasting project can be understood, rerun, and audited from the submitted repository.

Complete every applicable item before the final GitHub submission and presentation. Items already verified on 31 October 2026 are marked as complete. Items requiring the final repository, notebook, licensing, or presentation review remain open.

---

# 1. Repository contents

- [x] `README.md` is present at the repository root and reflects the final project.
- [x] `AI_USAGE.md` is present and complete.
- [x] `CONTRIBUTIONS.md` is present and complete.
- [x] `requirements.txt` is present and contains pinned direct dependencies.
- [x] `docs/methodology/DATA_DICTIONARY.md` is complete.
- [x] `docs/methodology/DECISION_REGISTER.md` reflects the final methodology and findings.
- [x] `notebooks/README.md` lists the five final notebooks in execution order.
- [x] Obsolete notebooks, unrelated exercises, temporary scripts, and duplicate files have been removed.
- [x] No temporary notebook checkpoint directories are tracked.
- [x] No local cache directories are tracked.
- [x] No editor, operating-system, or environment artefacts are tracked.

Useful checks:

```bash
git status
git ls-files
```

---

# 2. Licensed data protection

- [x] The unchanged licensed CEIC extract is stored locally at:

```text
data/raw/china_cpi.csv
```

- [x] `data/raw/china_cpi.csv` is excluded by `.gitignore`.
- [x] The licensed CEIC extract is not tracked by Git.
- [ ] No reformatted copy of the licensed observations is tracked elsewhere.
- [x] No credentials, passwords, API keys, access tokens, `.env` files, or account screenshots are present.
- [ ] Processed outputs have been reviewed to ensure that they do not reproduce the licensed source dataset in full.
- [x] Public Chinese New Year calendar data are clearly distinguished from licensed CEIC data.
- [x] Licensing and access instructions are documented in `data/README.md`, the root `README.md`, and the data dictionary.

Verify with:

```bash
git ls-files data/raw
git check-ignore -v data/raw/china_cpi.csv
```

Expected result:

- `git ls-files data/raw` does not list `china_cpi.csv`.
- `git check-ignore` identifies the applicable ignore rule.

If the extract was previously tracked, remove it from the Git index without deleting the local copy:

```bash
git rm --cached data/raw/china_cpi.csv
```

- [ ] Repository history has been checked if licensed data were ever pushed remotely.

---

# 3. Source metadata

- [x] All four CEIC series names are recorded.
- [x] All four CEIC series identifiers are recorded.
- [x] All four CEIC SR codes are recorded.
- [x] Raw CEIC units are recorded.
- [x] Standardised project units are recorded.
- [x] Source coverage is recorded.
- [x] Source organisation is recorded.
- [x] CEIC extraction date is recorded as 4 October 2026.
- [x] The latest source update shown in the extract is distinguished from the extraction date.
- [x] The COVID-19 source remark on the core YoY series is documented.
- [ ] The public Chinese New Year calendar source is documented with sufficient attribution.
- [x] Chinese New Year calendar coverage is documented.

---

# 4. Environment and dependencies

- [x] The tested Python version is recorded as `3.14.7`.
- [x] Required direct packages are listed in `requirements.txt`.
- [x] Direct package versions are pinned.
- [x] Unused direct dependencies have been removed.
- [x] The active project environment satisfies all pinned requirements.
- [x] `ipykernel` is explicitly included for notebook execution.
- [x] The project was executed and validated in the project-specific .venv.
- [x] Each submitted notebook is saved using the project virtual-environment kernel.
- [x] No notebook relies on an unrecorded globally installed package.
- [x] No code depends on a machine-specific absolute path.

Pinned environment:

```text
Python==3.14.7
numpy==2.5.3
pandas==3.0.6
scipy==1.18.1
statsmodels==0.15.0
matplotlib==3.11.2
jupyter==1.1.1
ipykernel==7.4.0
pytest==9.1.1
```

Installation check:

```bash
python -m pip install -r requirements.txt
```

---

# 5. Paths and project structure

- [x] All project paths are relative to the repository root.
- [x] Each notebook locates or validates the repository root consistently.
- [x] Data paths point to documented locations.
- [x] Output directories are created programmatically where needed.
- [x] File and directory names use consistent capitalisation.
- [x] No code references a personal home directory, Desktop path, cloud-synchronisation path, or temporary directory.
- [x] No notebook depends on an undocumented file outside the repository structure.

Search for likely absolute paths:

```bash
grep -R "/Users/" notebooks src tests
grep -R "C:\\" notebooks src tests
grep -R "/home/" notebooks src tests
```

Review any matches before submission. References appearing only in saved error tracebacks should also be removed by rerunning the affected notebooks cleanly.

---

# 6. Randomness and seeds

The principal project analysis uses deterministic model fitting and does not rely on random simulation for its reported results.

- [x] The principal submitted analysis does not depend on stochastic simulation or random resampling.
- [x] No stochastic procedure is retained in the final submitted analysis; a random seed is therefore not applicable.
- [x] No resampling or simulation result is retained in the final submitted analysis.
- [x] Unrelated randomised exercises are excluded from the project analysis.

A meaningless seed should not be added to deterministic code merely to satisfy the checklist.

---

# 7. Automated tests

- [x] The complete automated test suite passes from the repository root.
- [x] Data-loader tests pass.
- [x] CPI reconstruction tests pass.
- [x] Chinese New Year calendar-loader tests pass.
- [x] CNY phase-allocation tests pass.
- [x] Operational-benchmark tests pass.
- [x] Expanding-window evaluation tests pass.
- [x] Complete forecast-path checks pass.
- [x] Nonfinite-value checks pass.
- [x] Stationarity and invertibility validity checks pass.
- [x] Economically invalid index-path checks pass.

Final command and result:

```bash
python -m pytest -q
```

```text
66 passed in 2.03s
```

---

# 8. Notebook inventory and execution order

The final notebooks must appear and run in this order:

```text
01_data_audit.ipynb
02_operational_benchmark.ipynb
03_sarima_development.ipynb
04_final_evaluation.ipynb
05_results_and_inference.ipynb
```

For each notebook:

- [x] Select the project `.venv` kernel.
- [x] Restart the kernel.
- [x] Run all cells from top to bottom.
- [x] Confirm that no cell raises an exception.
- [x] Confirm that no notebook depends on an earlier notebook's in-memory state.
- [x] Confirm that displayed assertions pass.
- [x] Confirm that cell execution numbers are sequential.
- [x] Save the notebook with the intended executed outputs.
- [x] Remove obsolete debugging output and old tracebacks.
- [x] Confirm that licensed raw observations are not displayed unnecessarily.
- [x] Confirm that mathematical notation renders correctly.
- [x] Confirm that figure titles, labels, legends, units, and notes are readable.
- [x] Confirm that Markdown interpretations match the executed numerical results.

---

# 9. Notebook 01: data audit

- [x] The loader returns the four expected published CPI columns.
- [x] The index is a unique, increasing monthly `DatetimeIndex`.
- [x] Dates are standardised to month start.
- [x] All project inflation fields are numeric.
- [x] Series availability dates match the data dictionary.
- [x] The common headline-and-core MoM sample begins in January 2006.
- [x] Reconstructed index paths contain no invalid values.
- [x] Reconstructed YoY inflation follows the published YoY series coherently.
- [x] Discrepancy is defined as reconstructed minus published.
- [x] Reconstruction discrepancies are interpreted as possible rounding effects rather than automatically as data errors.
- [x] The reconstruction-discrepancy summary is exported to `outputs/tables/`.
- [x] The reconstruction-audit figure is exported to `outputs/figures/`.

Expected curated outputs:

```text
outputs/tables/01_reconstruction_discrepancy_summary.csv
outputs/figures/01_cpi_reconstruction_audit.png
```

---

# 10. Notebook 02: operational benchmark

- [x] The benchmark uses the preceding five same-calendar-month values.
- [x] The benchmark forecasts MoM inflation.
- [x] Monthly forecasts compound into a valid index path.
- [x] The index path converts into YoY forecasts correctly.
- [x] Horizon 1 uses only observations available at the forecast origin.
- [x] Forecasts beyond 12 months use earlier recursive benchmark forecasts where required.
- [x] No future realised CPI value enters a historical forecast.
- [x] The information-set audit correctly labels observed and forecast inputs.
- [x] The error convention is actual minus forecast.
- [x] Single-origin metrics are labelled as illustrative rather than final.
- [x] The benchmark-recursion audit is exported to `outputs/tables/`.
- [x] The illustrative benchmark forecast is exported to `outputs/figures/`.

Expected curated outputs:

```text
outputs/tables/02_benchmark_recursion_audit.csv
outputs/figures/02_benchmark_forecast_example.png
```

---

# 11. Notebook 03: model development

- [x] The development sample is January 2006 through December 2014.
- [x] No post-December 2014 outcome is used for model selection.
- [x] Candidate-order restrictions match the decision register.
- [x] AICc and BIC calculations are reviewed.
- [x] Failed and warning-producing fits remain visible.
- [x] Parameter estimates and confidence intervals are displayed correctly.
- [x] AR and MA root moduli are interpreted correctly.
- [x] Residual ACF and Ljung-Box diagnostics are reviewed.
- [x] Seasonal differencing is documented as investigated but not retained.
- [x] CNY pressure and normalisation phases match the final definitions.
- [x] CNY phase allocations sum to one separately within each phase and year.
- [x] Month indicators omit January as the reference category.
- [x] Internal validation uses only development-period outcomes.
- [x] Internal accuracy comparisons use common successful origins.
- [x] Parameter and root stability are reviewed.
- [x] Final model specifications match the decision register.
- [x] No development decision is revised using final-evaluation outcomes.
- [x] The CNY monthly-allocation figure is exported.
- [x] The locked model-specification table is exported.
- [x] The internal-validation reliability table is exported, if retained in the final output set.

Expected curated outputs:

```text
outputs/figures/03_cny_monthly_allocations.png
outputs/tables/03_locked_model_specifications.csv
outputs/tables/03_internal_validation_reliability.csv
```

Optional development figure, if retained:

```text
outputs/figures/03_core_development_rmse.png
```

---

# 12. Notebook 04: final evaluation

- [x] First forecast origin is December 2014.
- [x] Last forecast origin is August 2024.
- [x] Maximum horizon is 24 months.
- [x] Last realised target is August 2026.
- [x] There are 117 attempted origins.
- [x] Model specifications match those locked in Notebook 03.
- [x] CNY phase definitions remain unchanged.
- [x] Models use expanding-window estimation.
- [x] Every model uses only information available at its forecast origin.
- [x] Future CNY regressor values are deterministic calendar information.
- [x] Complete-path validity checks are applied.
- [x] Failed fits and warnings are recorded.
- [x] Headline paired comparisons use 104 common successful origins.
- [x] Core paired comparisons use 104 common successful origins.
- [x] Benchmark forecasts are restricted to the same paired origins.
- [x] Every compared model has the same number of errors at each paired horizon.
- [x] Reliability is reported separately across all attempted origins.
- [x] Mean error, MAE, and RMSE use the documented error convention.
- [x] Saved forecast and fitting panels match the displayed results.
- [x] Headline and core final RMSE figures are exported.
- [x] The final model-reliability figure is exported.
- [x] The final reliability table is exported.
- [x] Selected-horizon headline and core metric tables are exported.
- [x] The best-model-by-horizon table is exported.

Expected curated outputs:

```text
outputs/figures/04_headline_final_rmse.png
outputs/figures/04_core_final_rmse.png
outputs/figures/04_final_model_reliability.png
outputs/tables/04_final_reliability_summary.csv
outputs/tables/04_headline_selected_horizon_metrics.csv
outputs/tables/04_core_selected_horizon_metrics.csv
outputs/tables/04_best_model_by_horizon.csv
```

Full reproducibility artefacts should remain under `data/processed/` rather than being duplicated as publication-ready outputs.

---

# 13. Notebook 05: inference

- [x] The LR-test sample is January 2006 through December 2014.
- [x] Both models use the same 108 observations.
- [x] Both models use the same intercept treatment.
- [x] Both models use the same 11 month indicators.
- [x] Both models use the same nonseasonal SARIMA order.
- [x] Both models use the same seasonal SARIMA order.
- [x] The unrestricted model adds exactly two CNY regressors.
- [x] Both models converge.
- [x] All fitted parameters are finite.
- [x] The unrestricted log likelihood is not below the restricted log likelihood.
- [x] The LR statistic is calculated as:

$$
LR
=
2\left(
\ell_U-
\ell_R
\right).
$$

- [x] Degrees of freedom equal two.
- [x] The p-value is reported clearly.
- [x] The formal conclusion refers to improvement in maximised likelihood.
- [x] The conclusion does not claim that the LR test establishes improved forecasting.
- [x] The near-invertibility caveat is documented.
- [x] The signs and confidence intervals of both CNY coefficients are checked.
- [x] Exported inference tables match the displayed results.
- [x] The likelihood-ratio table is exported.
- [x] The matched model-comparison table is exported.
- [x] The coefficient-results table is exported.
- [x] The coefficient-estimate figure is exported.

Expected curated outputs:

```text
outputs/tables/05_cny_likelihood_ratio_test.csv
outputs/tables/05_cny_lr_model_comparison.csv
outputs/tables/05_cny_coefficient_results.csv
outputs/figures/05_cny_coefficient_estimates.png
```

---

# 14. Output regeneration and review

- [x] Curated figure and table export code is included in the notebooks.
- [x] All final figures regenerate from a clean notebook run.
- [x] All final tables regenerate from a clean notebook run.
- [x] Final figures are stored under `outputs/figures/`.
- [x] Final tables are stored under `outputs/tables/`.
- [ ] The presentation PDF is stored under `outputs/presentation/`.
- [x] Figure and table filenames are descriptive and stable.
- [x] All README links to figures and tables resolve correctly.
- [x] No final output depends on a manually edited number that differs from code output.
- [x] Reported values use consistent rounding.
- [x] Reported units are percentage points where appropriate.
- [x] Tables state whether they use all attempted origins or common successful origins.
- [x] Curated figures and tables have received a licensing review.

---

# 15. Documentation consistency

- [x] The root README describes the final five-notebook workflow.
- [x] The root README identifies the final model ladder.
- [x] The root README reports the correct sample dates.
- [x] The root README reports the correct final findings.
- [x] `notebooks/README.md` matches the actual notebook sequence.
- [x] `DATA_DICTIONARY.md` matches the documented project fields.
- [x] `DECISION_REGISTER.md` distinguishes final, completed, and superseded decisions.
- [x] `AI_USAGE.md` describes actual assistance and verification procedures.
- [x] `CONTRIBUTIONS.md` identifies responsibility for data, coding, analysis, figures, slides, and review.
- [x] No file refers to the abandoned AR-model, random-forest, or MODWT-hybrid ladder as current.
- [x] No file refers to the superseded one-regressor CNY design as current.
- [x] No file describes the unrelated permutation-test exercise as part of this project.
- [x] Model names and orders are consistent across notebooks and documentation.
- [x] The terms MoM, YoY, MAE, RMSE, SARIMA, SARIMAX, and CNY are defined on first use where needed.
- [x] Python `3.14.7` and the pinned `requirements.txt` are documented in the root README.

---

# 16. Presentation checks

- [x] The presentation is approximately 8–10 minutes.
- [x] The presentation states the research question.
- [x] The presentation identifies the licensed CEIC data source.
- [x] The presentation explains the operational benchmark.
- [x] The presentation summarises the development and final-evaluation separation.
- [x] The presentation includes the principal headline result.
- [x] The presentation includes the principal core result.
- [x] The presentation includes the likelihood-ratio result.
- [x] The presentation distinguishes explanatory fit from forecasting performance.
- [x] The presentation reports fitting reliability.
- [x] The presentation includes the main limitations.
- [x] The presentation provides a practical takeaway.
- [x] The presenter can explain the modelling choices without reading from the slides.
- [x] The presenter can explain stationarity, invertibility, roots, nuisance parameters, and the LR-test caveat.
- [x] The slide deck has been exported to PDF.
- [x] The presentation PDF is stored at:

```text
outputs/presentation/DS607_GP_01084382_slides.pdf
```

- [x] The editable PowerPoint is stored at:

```text
outputs/presentation/DS607_GP_01084382_slides.pptx
```

---

# 17. Final repository and submission audit

- [x] The GitHub repository URL is ready.
- [x] The student author is listed correctly.
- [x] The repository states that this is individual MDSE course work completed with instructor approval.
- [x] The final presentation PDF is present.
- [x] The repository was reviewed successfully in its remote GitHub form before the final presentation files were added.
- [x] The final presentation files have been checked in the remote GitHub repository after the presentation commit.
- [x] Markdown tables and equations render correctly on GitHub.
- [x] All repository links work.
- [x] No licensed data appear in the remote repository.
- [x] No credentials or local paths appear in the remote repository.
- [x] The final commit has a descriptive message.
- [x] The repository and presentation have been submitted through the required eLearn location.
- [x] A personal portfolio entry will be completed after submission and will identify the work as individual course work.

---

# 18. Final sign-off

## Validation record

```text
Final validation date: 8 November 2026
Python version: 3.14.7
Environment file: requirements.txt
Dependency validation: All pinned requirements satisfied
Automated test result: 66 passed in 2.08s
Notebook rerun result: All five notebooks completed successfully from clean kernels
Licensed-data Git check: Passed; raw CEIC extract ignored and not tracked
Presentation PDF check: Passed; final PDF and editable PowerPoint stored under outputs/presentation/
Final reviewer: Darren TAY Teck Yong
```

## Sign-off declaration

- [x] I have verified that the pinned project dependencies are installed.
- [x] I have run the complete automated test suite successfully.
- [x] I have rerun and reviewed all submitted notebooks.
- [x] I have verified that the repository does not expose licensed raw data or credentials.
- [x] I understand and can explain the statistical methods, results, and limitations.
- [x] I accept responsibility for the final repository and presentation.
