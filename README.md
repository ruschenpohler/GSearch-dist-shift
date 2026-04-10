# AI-Induced Distribution Shift in Google Trends: Implications for GDP Nowcasting

## What is this project about?

The OECD Weekly Tracker uses Google Trends search data to nowcast weekly GDP growth for 46 countries. It relies on the intuition that search intensity for economically relevant terms, such as bankruptcy, unemployment benefits, and mortgage, reflects real economic conditions.

This project investigates whether AI-powered search tools are systematically changing how people use Google, and whether this is degrading the quality of GDP nowcasts that depend on GTrends data.

## The core problem

AI chatbots are replacing Google as the first place people go for information. If this shift is concentrated in the same categories the OECD tracker relies on, the tracker's signal erodes, not because the economy changed, but because the measurement instrument changed.

This is a **distribution shift**: the data-generating process for GTrends is being disrupted by technology independent of (or not fully dependent on) the economy.

## Research design

The project has five main phases:

| Phase | Question |
|-------|----------|
| 0 | Does the AI adoption proxy behave as expected? (validation) |
| 1 | Are economic GTrends series actually shifting? (descriptive) |
| 2 | Does substitute AI predict shifts while placebo AI does not? (identification) |
| 3 | Which categories and search types are most affected? (heterogeneity) |
| 4 | Does the shift degrade GDP nowcasting performance? (nowcasting) |

### Identification strategy

Three orthogonal contrasts separate AI-induced measurement shift from confounders:

1. **Platform (substitute vs. placebo AI):** ChatGPT, Claude, Perplexity, etc. route queries *away* from Google, Gemini routes queries *through* Google. The general logic is that if substitute AI erodes GTrends but placebo does not, the effect is specific to measurement disruption, not general changes in economic behavior.

2. **Content (GDP-relevant vs. non-relevant):** Some categories carry strong GDP signal (bankruptcy, unemployment). Others have high AI substitutability but low GDP relevance (roleplaying, creative writing, cooking recipes). I.e., if only GDP-relevant categories erode, the tracker is specifically threatened.

3. **Timing (lagged treatment + pre-trends):** We further restrict alternative channels of causation by adding lagged AI adoption. we also test for parallel pre-trends before November 2022 to minimize the impact of selection bias.

## Key data sources

- **GTrends:** ~215 economic categories, MSA-level (US) and country-level, monthly and weekly, 2020–2026
- **OECD Quarterly National Accounts:** Real GDP growth (y-o-y) for 38 OECD members
- **BLS LAUS:** Monthly state-level unemployment
- **Census ACS:** MSA-level demographics (median age, education)
- **EF English Proficiency Index:** Cross-country moderator. AI tools work better in English, so higher proficiency leads to stronger substitution effects.


## Expected outputs

1. Proxy validation showing AI adoption patterns are consistent across time and geography
2. Time series figures showing structural breaks in economic GTrends series
3. Main result: negative effect of substitute AI on economic GTrends, with placebo near zero
4. Category-level vulnerability scores (β coefficient × Shapley importance)
5. Rolling-origin nowcasting evaluation: RMSE comparison pre-AI (2019–2022) vs. post-AI (2023–2026)
6. Potential policy recommendation could be a reweighted tracker that down-weights vulnerable categories

## Technical stack

- **Data:** `pytrends`, OECD SDMX API, BLS LAUS, Census ACS
- **Analysis:** `linearmodels` (panel regression with two-way clustered SEs), `statsmodels` (HAC SEs, mixed effects), `lightgbm` (gradient boosting for nowcasting), `strucchange` (structural break detection)
- **Visualization:** matplotlib, seaborn

## Why this matters beyond the OECD tracker

I see this project as more of a **template** for evaluating measurement stability of alternative-data nowcasting input per se. Not as necessarily confined to GTrends. Any instrument whose data-generating process is susceptible to technological disruption faces the same class of problem, such as satellite imagery when sensor technology changes, payments data when crypto adoption shifts transaction channels, and shipping data when supply chains restructure.

GTrends are interesting simply because they are widely used in nowcasting and because the impact seems first-order with AI tools replacing (and for a good part having replaced) search. In some sense, GTrends and AI search substitution are a case study, but the methodology is a portable contribution.

## Reference

Woloszko, N. (2020). "Tracking Economic Growth in Real Time with Weekly Indicators." *OECD Economic Department Working Papers* No. 1634.