# AI-Induced Distribution Shift in Google Trends: Implications for GDP Nowcasting

## What is this project about?

The OECD Weekly Tracker uses Google Trends search data to nowcast weekly GDP growth for 46 countries. It relies on the intuition that search intensity for economically relevant terms, such as bankruptcy, unemployment benefits, and mortgage, reflects real economic conditions.

This project investigates whether AI-powered search tools are systematically changing how people use Google, and whether this is degrading the quality of GDP nowcasts that depend on Google Trends data.

## The core problem

AI chatbots are replacing Google as the first place people go for information. If this shift is concentrated in the same categories the OECD tracker relies on, the tracker's signal erodes, not because the economy changed, but because the measurement instrument changed.

This is a **distribution shift**: the data-generating process for Google Trends is being disrupted by a technological shock that has nothing to do with the economy.

## Research design

The project has five main phases:

| Phase | Question |
|-------|----------|
| 0 | Does the AI adoption proxy behave as expected? (validation) |
| 1 | Are economic Google Trends series actually shifting? (descriptive) |
| 2 | Does substitute AI predict shifts while placebo AI does not? (identification) |
| 3 | Which categories and search types are most affected? (heterogeneity) |
| 4 | Does the shift degrade GDP nowcasting performance? (nowcasting) |

### Identification strategy

Three orthogonal contrasts separate AI-induced measurement shift from confounders:

1. **Platform (substitute vs. placebo AI):** ChatGPT and Perplexity route queries *away* from Google. Gemini routes *through* Google. If substitute AI erodes GTrends but placebo does not, the effect is specific to measurement disruption, not general changes in economic behavior.

2. **Content (GDP-relevant vs. non-relevant):** Some categories carry strong GDP signal (bankruptcy, unemployment). Others have high AI substitutability but low GDP relevance (translation, coding, recipes). If only GDP-relevant categories erode, the tracker is specifically threatened.

3. **Timing (lagged treatment + pre-trends):** Last month's AI adoption predicts this month's GTrends, ruling out reverse causality. Parallel pre-trends before November 2022 rule out selection bias.

## Key data sources

- **Google Trends:** ~215 economic categories, MSA-level (US) and country-level, monthly and weekly, 2020–2026
- **OECD Quarterly National Accounts:** Real GDP growth (y-o-y) for 38 OECD members
- **BLS LAUS:** Monthly state-level unemployment
- **Census ACS:** MSA-level demographics (median age, education)
- **EF English Proficiency Index:** Cross-country moderator. AI tools work better in English, so higher proficiency leads to stronger substitution effects.

### AI search terms

| Type | Examples | Mechanism |
|------|----------|-----------|
| Substitute | ChatGPT, Perplexity AI, Claude AI | Route queries away from Google |
| Placebo | Gemini AI, Google Bard | Route through Google infrastructure |

## Expected outputs

1. Proxy validation showing AI adoption patterns are consistent across time and geography
2. Time series figures showing structural breaks in economic Google Trends series
3. Main result: negative effect of substitute AI on economic GTrends, with placebo near zero
4. Category-level vulnerability scores (β coefficient × Shapley importance)
5. Rolling-origin nowcasting evaluation: RMSE comparison pre-AI (2019–2022) vs. post-AI (2023–2026)
6. Policy recommendation: reweighted tracker that down-weights vulnerable categories

## Technical stack

- **Data:** `pytrends`, OECD SDMX API, BLS LAUS, Census ACS
- **Analysis:** `linearmodels` (panel regression with two-way clustered SEs), `statsmodels` (HAC SEs, mixed effects), `lightgbm` (gradient boosting for nowcasting), `strucchange` (structural break detection)
- **Visualization:** matplotlib, seaborn

## Why this matters beyond the OECD tracker

This project serves as a **template** for evaluating measurement stability of any alternative-data nowcasting input. Any instrument whose data-generating process is susceptible to technological disruption faces the same class of problem, such as satellite imagery when sensor technology changes, payments data when crypto adoption shifts transaction channels, and shipping data when supply chains restructure.

The framework here, which involves structural break detection, substitute versus placebo identification, nowcasting degradation testing, and remediation, generalizes to all of them. Google Trends and AI search substitution are the case study; the methodology is the transferable contribution.

## Status

Implementation is ongoing. All phases described in `GSearch-dist-shift-IMPL_v3.md`.

## Reference

Woloszko, N. (2020). "Tracking Economic Growth in Real Time with Weekly Indicators." *OECD Economic Department Working Papers* No. 1634.