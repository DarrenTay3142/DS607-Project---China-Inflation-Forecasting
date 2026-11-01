# Contributions

This project was completed individually by **Darren TAY Teck Yong** with instructor approval.

The student author holds sole responsibility for the assessed work, including the research design, data handling, code execution, statistical analysis, interpretation, repository preparation, and presentation.

Generative AI assistance is disclosed separately in `AI_USAGE.md`. AI assistance does not constitute authorship or transfer responsibility for any part of the submitted work.

## Research question and project design

Darren TAY Teck Yong:

- proposed the study of mainland China headline and core CPI inflation;
- formulated the operational-benchmark and time-series forecasting comparison;
- developed the distinction between forecast accuracy, numerical reliability, and explanatory inference;
- discussed the project scope and tractability with the instructor;
- adopted the final likelihood-ratio test after confirming its suitability with the instructor;
- made or explicitly adopted all final methodological decisions.

## Data acquisition and licensing

Darren TAY Teck Yong:

- obtained the licensed CEIC data through authorised Singapore Management University access;
- selected and downloaded the required headline and core CPI series;
- maintained the licensed extract locally and outside the public repository;
- documented the source, access requirements, and redistribution restrictions;
- obtained and reviewed the public Chinese New Year calendar information;
- checked dates, frequencies, missing values, units, and series availability.

## Data engineering

Darren TAY Teck Yong:

- created and reviewed the CPI data-loading workflow;
- validated the monthly index, column schema, data types, and observation periods;
- reconstructed headline and core CPI index paths from published month-on-month inflation;
- compared reconstructed and published year-on-year inflation;
- reviewed discrepancies arising from compounding rounded monthly rates;
- created and audited the Chinese New Year pressure and post-CNY normalisation regressors;
- verified that the moving-holiday allocations were aligned with the monthly CPI data.

## Operational benchmark

Darren TAY Teck Yong:

- specified the five-year same-calendar-month operational benchmark;
- reviewed the recursive treatment of forecast horizons beyond 12 months;
- verified that historical forecasts used only information available at each forecast origin;
- inspected the monthly, reconstructed-index, and year-on-year forecast paths;
- reviewed benchmark forecast errors and evaluation metrics.

## Statistical modelling

Darren TAY Teck Yong:

- reviewed the exploratory time-series analysis;
- examined calendar-month patterns, ACFs, PACFs, and stationarity-test results;
- defined and ran the low-complexity SARIMA candidate searches;
- examined convergence, warnings, AICc, BIC, parameter estimates, and confidence intervals;
- reviewed AR stationarity and MA invertibility through polynomial roots;
- assessed residual autocorrelation and Ljung-Box diagnostics;
- investigated seasonal differencing and decided not to retain it as the principal headline solution;
- developed and reviewed the CNY-aware SARIMAX specifications;
- selected the model shortlist after considering fit, diagnostics, parsimony, stability, and forecast performance.

## Forecast validation and evaluation

Darren TAY Teck Yong:

- ran the internal expanding-window validation;
- reviewed repeated maximum-likelihood fits and forecast-path checks;
- examined parameter and root stability across forecast origins;
- locked the final specifications before opening the final evaluation results;
- ran the final expanding-window evaluation through 24-month horizons;
- reviewed convergence failures, warnings, and invalid origins;
- constructed and verified common successful-origin comparison samples;
- calculated and interpreted mean error, MAE, and RMSE;
- compared headline and core modelling results separately;
- treated numerical reliability as a model-quality outcome rather than silently discarding failed fits.

## Statistical inference

Darren TAY Teck Yong:

- formulated the joint null hypothesis for the two Chinese New Year regressors;
- verified that the restricted and unrestricted models were genuinely nested;
- fitted both models by maximum likelihood;
- checked that both models used identical observations, deterministic terms, and SARIMA error structures;
- verified the likelihood-ratio statistic, degrees of freedom, and p-value;
- interpreted the CNY coefficient estimates and confidence intervals;
- distinguished explanatory likelihood from out-of-sample forecast performance;
- reviewed the asymptotic limitation associated with the near-boundary seasonal MA nuisance parameter.

## Python implementation and testing

Darren TAY Teck Yong:

- created and maintained the project repository;
- executed all Python code in the student-controlled project environment;
- reviewed reusable functions in `src/`;
- ran and reviewed the automated tests;
- corrected coding, indexing, path, forecast-alignment, and output issues;
- restarted and reran the analytical notebooks;
- verified object shapes, indexes, labels, counts, and saved outputs;
- checked that licensed source data and credentials were excluded from version control.

## Figures, tables, and outputs

Darren TAY Teck Yong:

- generated and reviewed the project figures;
- reviewed the data-audit and model-diagnostic tables;
- generated the forecast-reliability and accuracy summaries;
- prepared the likelihood-ratio and coefficient tables;
- selected the results to be included in the repository and presentation;
- organised final derived outputs under the repository’s output folders.

## Documentation and repository preparation

Darren TAY Teck Yong:

- reviewed and edited all notebook explanations and interpretations;
- prepared the project README and repository navigation;
- documented the data restrictions and reproduction procedure;
- prepared `AI_USAGE.md` and this contribution statement;
- removed unrelated exercises and obsolete project material;
- checked mathematical notation, Markdown rendering, file paths, and notebook execution order;
- performed the final repository quality review.

## Presentation

Darren TAY Teck Yong is responsible for:

- selecting the presentation narrative and principal results;
- preparing and reviewing the slide deck;
- explaining the data, methods, results, and limitations;
- rehearsing the presentation within the required time;
- answering questions about the statistical methodology and findings.

## Review and academic responsibility

Darren TAY Teck Yong reviewed the final analytical results and remains solely responsible for:

- the accuracy of the submitted code and documentation;
- compliance with data-licensing restrictions;
- the methodological decisions;
- the statistical interpretations;
- the repository contents;
- the presentation materials;
- and the ability to explain and defend the project independently.

This repository is submitted as individual MDSE course work. Generative AI support is documented transparently in `AI_USAGE.md`.
