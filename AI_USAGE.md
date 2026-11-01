# AI Usage Statement

Microsoft 365 Copilot was used as a disclosed project assistant throughout this individual DS607 course project.

Copilot supported research planning, statistical-design discussion, Python code drafting and review, debugging, methodological explanation, notebook documentation, repository organisation, writing, and quality assurance. Copilot did not independently obtain the licensed data, execute the analysis outside the student-controlled project environment, determine the final methodological decisions, or submit any project materials.

The student author selected the research question, obtained the data through authorised channels, executed and reviewed the analysis, examined all material outputs, decided whether to adopt or reject proposed methods, interpreted the results, consulted the instructor about project scope and inference, and remains responsible for all submitted work.

## Principles of use

AI assistance was used according to the following principles:

1. **Student control**
   The student author retained control over the research question, project scope, statistical design, code execution, methodological decisions, interpretation, and final presentation.

2. **Independent execution**
   All project code was run in the student author's local project environment. AI-generated code was not treated as valid merely because it executed.

3. **Verification against outputs**
   Proposed code and interpretations were checked against notebook outputs, object shapes, parameter estimates, diagnostics, forecast counts, error messages, and manually derived calculations where appropriate.

4. **Incremental review**
   Complex modelling steps were developed and reviewed incrementally. Errors were isolated and corrected before later stages were accepted.

5. **Course alignment**
   Statistical methods were connected to DS607 material, including maximum likelihood, restricted and unrestricted models, nuisance parameters, likelihood-ratio testing, degrees of freedom, and asymptotic reference distributions.

6. **Instructor oversight**
   The project proposal and subsequent scope concerns were discussed with the instructor. The likelihood-ratio test used for the Chinese New Year regressors was adopted after the instructor agreed that it was suitable for the project.

7. **Transparency about limitations**
   AI assistance was also used to identify and explain methodological limitations, including near-boundary seasonal MA roots, convergence failures, common-origin forecast comparisons, and the distinction between explanatory fit and out-of-sample forecast performance.

8. **No fabricated evidence**
   Project results were taken from executed code and observed outputs. Numerical results were not invented or simulated unless a task was explicitly identified as a separate learning exercise. Unrelated exercises were removed from the project repository.

## Areas of AI assistance

### Research planning and scope

Copilot assisted with:

- refining the forecasting and inference questions;
- separating explanatory inference from forecast evaluation;
- organising the work into development, final evaluation, and inference stages;
- discussing the tractability of the original project scope;
- preparing the proposal and reviewing the instructor's feedback;
- identifying which completed work remained relevant after scope discussions.

The student author decided to retain the broader, completed forecasting design after discussing feasibility with the instructor.

### Data engineering

Copilot assisted with drafting and reviewing code for:

- loading the local CEIC extract;
- validating dates, frequencies, column types, and missing values;
- reconstructing CPI index paths from published month-on-month inflation;
- converting reconstructed index paths into year-on-year inflation;
- loading and validating the public Chinese New Year calendar;
- constructing and auditing moving-holiday regressors.

The student author obtained the CEIC data through authorised SMU access and verified the resulting series, sample dates, and reconstruction discrepancies.

### Operational benchmark

Copilot assisted with:

- formalising the five-year same-calendar-month benchmark;
- implementing recursive forecasts beyond the first 12 months;
- auditing the information set at each horizon;
- defining forecast errors;
- checking monthly, index-level, and year-on-year transformations.

The student author ran the benchmark, examined its audit tables, and verified that future realised observations were not used.

### SARIMA and SARIMAX development

Copilot assisted with:

- drafting low-complexity candidate searches;
- calculating and interpreting AICc and BIC;
- reviewing ACF and PACF diagnostics;
- applying ADF and KPSS stationarity tests;
- checking convergence, warnings, AR roots, and MA roots;
- applying Ljung-Box residual diagnostics;
- investigating seasonal differencing;
- constructing fixed-month and Chinese New Year designs;
- organising internal expanding-window validation;
- comparing models on common successful origins.

The student author executed all searches, reviewed the results, and explicitly adopted the final shortlist. Models were not selected from an AI recommendation or information criterion alone.

### Final forecast evaluation

Copilot assisted with:

- implementing the locked expanding-window evaluation;
- validating complete 24-month forecast paths;
- recording failed and warning-producing origins;
- constructing paired common-origin samples;
- calculating mean error, MAE, and RMSE;
- interpreting headline and core results separately;
- distinguishing forecast accuracy from operational reliability.

The student author ran the final evaluation and checked the reported model counts, failure patterns, tables, and figures.

### Statistical inference

Copilot assisted with:

- formulating the joint null hypothesis for the two Chinese New Year regressors;
- constructing matched restricted and unrestricted SARIMAX models;
- calculating the likelihood-ratio statistic and p-value;
- interpreting the two restrictions and nuisance parameters;
- distinguishing the joint LR test from individual coefficient tests;
- explaining how near non-invertibility may weaken the finite-sample chi-square calibration;
- separating explanatory likelihood from forecasting performance.

The likelihood-ratio test was verified from the fitted log likelihoods:

$$
LR
=
2\left(\ell_U-\ell_R\right)
=
28.985.
$$

The student author inspected the fitted models, confirmed the nested comparison, checked the arithmetic, and remains responsible for the inferential interpretation.

### Code review and debugging

Copilot assisted with identifying or correcting issues involving:

- incomplete or truncated notebook cells;
- relative paths and project-root handling;
- DateTime indexes and monthly frequencies;
- model convergence and warning handling;
- matched forecast-origin samples;
- invalid or incomplete forecast paths;
- duplicated or outdated notebook content;
- Markdown and mathematical-notation rendering.

Corrections were rerun in the local environment rather than accepted from prose alone.

### Documentation and presentation

Copilot assisted with:

- drafting explanatory Markdown around code cells;
- reorganising the notebooks into reader-facing analytical narratives;
- preparing repository documentation;
- drafting the proposal;
- drafting report-ready interpretations;
- explaining technical concepts in preparation for presentation questions;
- identifying required repository files and submission checks.

The student author reviewed and edited the final wording and verified that the documentation matched the executed analysis.

## Usage log

The log records major phases of assistance rather than every individual prompt.

| Project phase | AI assistance | Student verification and responsibility |
|---|---|---|
| Project setup | Proposed repository structure, relative-path conventions, modules, tests, and notebook sequence | Created and managed the local repository; reviewed paths and structure; ran setup and tests |
| Proposal | Drafted and formatted the one-page proposal and licensing statement | Reviewed the proposal, supplied personal details, submitted it, and discussed feedback with the instructor |
| Data audit | Assisted with loader checks, schema validation, index reconstruction, and discrepancy interpretation | Obtained the licensed data, ran the notebook, checked dates and outputs, and reviewed reconstruction differences |
| Operational benchmark | Helped specify and implement the recursive five-year same-month benchmark | Ran the forecast example and audited the observed and recursively forecast inputs |
| Exploratory analysis | Supported plots, calendar-month summaries, ACF/PACF review, and stationarity testing | Examined the outputs and decided which questions required further investigation |
| SARIMA search | Drafted candidate-search and diagnostic code; explained information criteria and roots | Executed the search, reviewed invalid fits and warnings, and adopted the candidate shortlist |
| Seasonal-differencing investigation | Helped design and interpret a narrow seasonal-differencing branch | Ran and reviewed the branch and decided not to retain seasonal differencing as the main solution |
| CNY regressors | Helped formalise pressure and normalisation windows and audit their monthly allocation | Examined the public calendar dates, allocation tables, and plot; retained the documented definitions |
| CNY-aware SARIMAX | Assisted with deterministic design, SARIMA error search, residual diagnostics, and root checks | Ran the fits and retained a primary model and a separate root-robustness model |
| Internal validation | Helped implement repeated expanding-window estimation and common-origin metrics | Reviewed fitting failures, forecast counts, accuracy tables, and parameter stability |
| Final evaluation | Helped run locked models, benchmark comparisons, reliability summaries, MAE, RMSE, and bias analysis | Ran the full notebook, checked all model counts and principal numerical results, and did not reopen model selection |
| Likelihood-ratio test | Helped construct matched models, calculate the statistic, and explain the inferential result | Confirmed nesting, convergence, log likelihoods, degrees of freedom, coefficient estimates, and arithmetic |
| Methodological limitations | Explained near non-invertibility, unit-circle roots, nuisance parameters, and asymptotic caveats | Worked through the concepts, challenged unclear explanations, and adopted only interpretations understood and defensible |
| Notebook polish | Reorganised notebooks and drafted explanatory Markdown and conclusions | Reran the replacement notebooks and checked code execution, outputs, notation, and mathematical rendering |
| Repository preparation | Assisted with README, AI usage documentation, contribution documentation, and submission checklist | Reviews and approves final repository contents and remains responsible for submission |
| Presentation preparation | Assists with slide structure, technical explanations, anticipated questions, and timing | Selects final content, rehearses the explanation, and answers presentation questions independently |

## Examples of verification

The student author performed checks including:

- restarting kernels and running notebooks from top to bottom;
- confirming expected dates, observation counts, and monthly frequencies;
- comparing reconstructed and published inflation series;
- checking forecast-origin and target-date calculations;
- verifying that benchmark forecasts did not use unavailable future outcomes;
- reviewing convergence warnings and failed fits;
- confirming AR and MA root conditions;
- examining residual ACFs and Ljung-Box tests;
- checking common-origin counts before comparing forecast accuracy;
- manually verifying selected likelihood-ratio calculations;
- inspecting coefficient signs, confidence intervals, AIC, and BIC;
- checking the distinction between forecast errors and fitting failures;
- running automated tests;
- correcting Markdown equations when mathematical notation did not render correctly.

## Limitations of AI assistance

Generative AI can produce incorrect code, incomplete reasoning, unsuitable statistical recommendations, or polished explanations that overstate what the evidence establishes.

For that reason:

- AI-generated material was treated as a draft;
- statistical claims were checked against executed results;
- methodological recommendations were evaluated against the project design and course content;
- uncertain issues were discussed with the instructor where appropriate;
- final conclusions were limited to what the data and completed analyses support.

## Academic ownership

The student author remains responsible for:

- the research question;
- data access and licensing compliance;
- methodological decisions;
- code execution;
- statistical interpretation;
- repository contents;
- presentation materials;
- and all submitted conclusions.

The use of AI assistance does not transfer authorship, accountability, or the obligation to understand and explain the project.
