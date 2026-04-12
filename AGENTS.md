# AI-Induced Distribution Shift in Google Trends: Implications for GDP Nowcasting

## Implementation Guide (v5, final)

---

## 1. Motivation

The OECD Weekly Tracker (Woloszko 2020, 2024) nowcasts weekly GDP growth for 46 countries using ~215 Google Trends categories as inputs to a neural network. The identifying assumption is that search intensity for economically informative categories (e.g., "bankruptcy," "unemployment benefits," "mortgage") reflects real economic behavior.

AI-powered search tools (ChatGPT, Perplexity, Gemini, Copilot) are changing who searches on Google, how often, and for what. If this shift is systematic and correlated with the categories the tracker relies on, the tracker's signal-to-noise ratio degrades, not because the economy changed, but because the instrument did.

This project investigates whether AI adoption is inducing a distribution shift in Google Trends series, whether that shift is concentrated in categories that matter for GDP nowcasting, and whether it degrades nowcasting performance.

Beyond the OECD tracker, the analysis serves as a template for evaluating measurement stability of any alternative-data nowcasting input. Any instrument whose data-generating process is susceptible to technological disruption, such as satellite imagery when sensor technology changes, payments data when crypto adoption shifts transaction channels, and shipping data when supply chains restructure, faces the same class of problem. The framework here (structural break detection, lagged treatment with pre-trends, content-axis heterogeneity, nowcasting degradation test, remediation) generalizes to all of them. Google Trends and AI search substitution are the case study; the methodology is the transferable contribution.

---

## 2. Research Design

Five phases, plus two case-study extensions. Each phase produces standalone output.

| Phase | Question | Unit | Key data |
|-------|----------|------|----------|
| 0 | Validation: Does the AI proxy behave as expected? (temporal, cross-sectional) | US MSA × month | GTrends AI terms, Census ACS |
| 1 | Descriptive: Are economic GTrends shifting? | Country × week | GTrends economic categories |
| 2 | Identification: Does lagged AI adoption predict declines in economic GTrends? | US MSA × month | GTrends (AI + econ), BLS unemployment |
| 3 | Heterogeneity: Which categories and what type of search activity are most affected? | Category × MSA × month | Phase 2 by category |
| 4 | Nowcasting: Does the shift degrade GDP nowcasting? | Country × quarter | GTrends, OECD QNA |
| Ext. A | Mechanism: Is erosion concentrated in peak AI-usage hours? | Country × hour (pilot) | Hourly GTrends, short windows |
| Ext. B | Natural experiments: Do ChatGPT outages cause GTrends to spike? | Country × hour (pilot) | Hourly GTrends, Downdetector logs |

**Identification strategy, two axes:**

The project exploits two orthogonal contrasts to separate AI-induced measurement shift from confounders:

1. **Temporal axis (lagged treatment + pre-trends):** AI adoption last month predicting GTrends changes this month rules out reverse causality. Parallel pre-trends before Nov 2022 rule out selection. This is the core of Phase 2.

2. **Content axis (GDP-relevant vs. non-relevant categories):** If AI disproportionately erodes categories that carry GDP signal (bankruptcy, unemployment benefits) vs. categories with high AI substitutability but low GDP relevance (roleplaying, creative writing, cooking recipes), the tracker is specifically threatened. If erosion is uniform, the problem is general but less targeted. Core of Phase 3.

A complementary within-Google test exploits AI Overviews rollout: the initial user query remains in GTrends, but AI-generated fan-out queries are filtered. If AI Overviews reduce follow-up searches, SVI declines even without users leaving Google. This is detectable via structural break tests around the AI Overviews rollout (mid-2024 US, varies by country). Used as robustness, not primary identification.

---

## 3. Data

### 3.1 Google Trends

**Source:** `pytrends` + `tenacity` (exponential backoff, 4 to 6 hour budget for ~3,000 queries).

**SVI normalization:** 0 to 100, normalized within each query. Cross-category comparisons require joint queries (up to 5 terms) or independent normalization.

**Geography:** Country-level for all countries. US sub-national: Google provides MSA-level data (~200+ metros). Smaller MSAs face suppression of low-volume searches. Pull all available; create suppression indicator (SVI < 5); run sensitivity restricted to top-100 MSAs.

**Temporal resolution:** Monthly MSA-level for Phases 0 to 3 (2020 to 2026). Weekly country-level for Phases 1 and 4 (stitched from overlapping 5-year windows). Hourly country-level for Extensions A and B (short windows only).

**AI search terms:**

| Group | Terms | Mechanism |
|-------|-------|-----------|
| Substitute ($AI^{sub}$) | ChatGPT (primary); Perplexity AI, Claude AI, Gemini AI (sensitivity) | Route queries away from Google or reduce measured search volume |

Use ChatGPT alone as the primary substitute specification. Add Perplexity, Claude, and Gemini as sensitivity checks. Pull all four AI search terms at both MSA and country level. Aggregate substitute terms via PCA (if 1st component explains greater than 60 percent variance) or normalized average; retain individual series for sensitivity. The Bard series is too noisy from the rebranding transition to stitch reliably.

**Economic categories** (top-12 by Shapley importance from tracker repo; see Section 3.7): drawn from Woloszko (2020) Annex B sector groupings. Use the Annex B search term strings directly in pytrends rather than reverse-engineering category IDs. Representative terms by sector:

| Sector | Example search terms |
|--------|----------------------|
| Labor markets | "unemployment benefits", "jobs", "job listings", "recruitment" |
| Housing | "real estate agency", "mortgage", "home insurance" |
| Business services | "venture capital", "bankruptcy", "credit and lending" |
| Consumption | "restaurants", "travel", "vehicle brands" |
| Industrial | "maritime transport", "agricultural equipment", "freight" |
| Uncertainty | "economic crisis", "recession" |
| Poverty | "food bank" |

Note: "travel" and "food and drink" appear in both the consumption sector and the non-economic diagnostic set. Assign each term to exactly one group before analysis; do not let overlap contaminate the Phase 3b comparison.

**Non-economic diagnostic categories** (high AI substitutability, low GDP relevance): roleplaying, creative writing, cooking recipes. These three are well-documented AI substitution targets. Per OpenRouter's State of AI report, roleplaying and creative writing are among the top use cases by volume; cooking recipes similarly displaces food blogs. They carry little GDP signal. If AI erodes these but not economic categories, the tracker is safe. If both erode, the problem is general. If only economic categories erode, the mechanism is something specific about economic information-seeking.

**Reference:** OpenRouter. "State of AI Report." https://openrouter.ai/state-of-ai


### 3.2 OECD Quarterly National Accounts (QNA)

Quarterly real GDP growth (y-o-y, seasonally adjusted) for 38 OECD members via SDMX REST API (dataflow `OECD.SDD.NAD`; exact ID to verify via API). Country codes harmonized via ISO alpha-2 → alpha-3 lookup.


### 3.3 BLS LAUS

Monthly state-level unemployment (seasonally adjusted), merged to MSAs via MSA→state mapping. Controls for actual economic conditions. Data from flat files in `data/raw/`.


### 3.4 Census ACS (Phase 0)

MSA-level demographics: median age, % bachelor's degree. Used for cross-sectional proxy validation. Pulled via Census API with key stored in `.env`.


### 3.5 EF English Proficiency Index (Phase 4)

Annual country-level English proficiency scores (~100 countries). Used as cross-country moderator: AI tools work better in English, so higher English proficiency → stronger AI substitution → larger GTrends erosion. Free, publicly available.


### 3.6 Merge Summary

**Phases 0 to 3:** GTrends (MSA by month) left join BLS (state by month, via MSA to state) left join Census ACS (MSA, static). Join on MSA ID by year-month.

**Phase 4:** GTrends (country × week → quarterly mean) ← QNA (country × quarter) ← EF EPI (country, annual). Join on ISO-3 × year-quarter.


### 3.7 Shapley Values for Category Prioritization

The OECD Weekly Tracker repo contains Shapley value pickle files (`weekly_shap.pkl`, `monthly_shap.pkl`). Load these to rank all categories by their contribution to tracker predictions. Use the top-12 by Shapley value as the primary economic category set. This anchors category selection to empirically measured importance rather than manual judgment. The paper (Woloszko 2020) reports only sector-level aggregates; the pickle files have category-level values needed for the vulnerability score in Phase 3c and leave-one-out analysis in Phase 4.

---

## 4. Analysis

### Structural Prerequisites

**Response:** Level or change of economic SVI. Continuous, Gaussian baseline. Log-transform if residuals show skew.

**Hierarchical structure:** Observations nested in MSAs/countries over time. Two-way clustered SEs (MSA + month) as default; mixed effects if heterogeneity analysis (Phase 2, Step 3) warrants.

**Causal direction:** AI adoption may correlate with economic conditions (distressed areas adopt AI more). Two protections: (a) lagged treatment as primary specification throughout, (b) pre-trend test confirms parallel trends before Nov 2022. See DAG below.

**DAG:**

```
Economy_mt → GTrends_mt^econ    (real economic signal, controlled via BLS UE)
Economy_mt → AI_mt^sub          (distress drives AI interest, confounder)
AI_mt^sub  → GTrends_mt^econ    (substitution, our hypothesis)
```

If the confounder path (Economy → AI → GTrends) dominates, the effect of $AI^{sub}$ on GTrends should be confounded. Lagged treatment ($AI_{t-1}$) blocks contemporaneous reverse causality. Pre-trends before Nov 2022 test whether faster-adopting MSAs were already on different GTrends trajectories.


### Phase 0: Proxy Validation

*0a.* Temporal: AI series near-zero before Nov 2022, sharp rise after.

*0b.* Cross-sectional: Regress MSA-level mean $AI^{sub}$ on Census demographics, separately for 2023, 2024, 2025 (stability test). Use median age and % college only (avoid collinearity). Expect: younger and more educated MSAs adopt more.

*0c.* Internal consistency: Aggregate MSA-level to national; compare to country-level pull.


### Phase 1: Descriptive

*1a.* Plot weekly SVI for priority economic categories in US, UK, DE, FR, JP (2018 to 2026) with LOWESS smoother. Mark Nov 2022 and May 2024.

*1b.* Zivot-Andrews (1992) test for unit root with endogenous structural break (via `arch`). If trend-stationary: break date and magnitude from ZA output. If unit-root: first-difference and test for break in $\Delta SVI$ via multiple change-point detection with HC standard errors (`ruptures`).

*1c.* Simple parametric complement:

$$GTrends_{c,t}^{econ} = \alpha + \rho \cdot GTrends_{c,t-1}^{econ} + \beta \cdot PostAI_t + \varepsilon_t$$

Newey-West HAC SEs. Country-by-country for major economies; panel with country FE for robustness.


### Phase 2: Identification

Staggered DID exploiting differential AI adoption across MSAs. With MSA and time FE, beta is identified from within-MSA, within-period variation in AI adoption, comparing faster-adopting MSAs to slower ones, not estimating the aggregate effect.

**Primary specification (lagged treatment):**

$$GTrends_{m,t}^{econ} = \lambda_m + \mu_t + \beta \cdot AI_{m,t-1}^{sub} + \gamma \cdot UE_{s(m),t} + \varepsilon_{m,t}$$

Two-way clustered SEs (MSA, month). Lagged AI addresses reverse causality: adoption last month cannot be caused by GTrends changes this month.

**Pre-analysis checks:**
- Pre-trend test: do high-adoption MSAs show differential economic GTrends trajectories before Nov 2022?

**Granger-style robustness:**

$$\Delta GTrends_{m,t}^{econ} = \lambda_m + \mu_t + \rho \cdot \Delta GTrends_{m,t-1}^{econ} + \beta \cdot AI_{m,t-1}^{sub} + \gamma \cdot UE_{s(m),t} + \varepsilon_{m,t}$$

Does lagged AI predict GTrends *changes* beyond what past GTrends changes predict?

**Model escalation:**

- **Step 1:** Pooled OLS, baseline, no structural assumptions. Establishes direction and magnitude before fixed effects.
- **Step 2:** Two-way FE (MSA plus month), controls for time-invariant MSA traits and common temporal shocks. Identifies effect from within-MSA variation over time. **Headline result.**
- **Step 3:** Heterogeneity and mechanism. Regress:

$$GTrends_{m,t}^{econ} = \lambda_m + \mu_t + \beta_1 \cdot AI_{m,t-1}^{sub} + \beta_2 \cdot (AI_{m,t-1}^{sub} \times X_m) + \gamma \cdot UE_{s(m),t} + \varepsilon_{m,t}$$

where X_m equals MSA demographics (median age, percent college). If beta_2 is statistically significant and economically meaningful, estimate mixed effects with random slopes on $AI^{sub}$ to recover MSA-specific treatment effects. Random slopes are justified only if the interaction signals substantively different responses across metros, not as a default. With approximately 48 obs per MSA, random slopes are at the boundary of reliable estimation. Report shrinkage diagnostic (mean shrinkage factor, range of BLUPs).

- **Step 4:** Nonlinearity diagnostic. After Step 3, examine residuals from the preferred specification. Run: (i) partial residual plot of $AI^{sub}$, look for systematic curvature (e.g., concave at high adoption, linear elsewhere); (ii) RESET test (quadratic terms), if p less than 0.10, nonlinearity plausible; (iii) AIC/BIC comparison: linear versus GAM (penalized log-likelihood). If RESET rejects linearity and GAM improves AIC substantially (greater than 5 points), report GAM results alongside linear as robustness. Lead with linear in narrative. GAM is diagnostic, not headline.

All specifications test the same underlying hypothesis from complementary angles. A finding that survives across specifications is robust; divergences are informative and discussed where relevant. Step 2 is the headline result; Steps 1, 3 to 4 serve as robustness and mechanism investigation.


### Phase 3: Category Heterogeneity

**3a. Economic categories:** Run Phase 2 Step 2 separately for each of the 12 economic categories. Rank by $|\hat{\beta}|$.

**3b. Non-economic diagnostic:** Run Phase 2 Step 2 on roleplaying, creative writing, and cooking recipes. Compare $\hat{\beta}^{econ}$ vs. $\hat{\beta}^{non\text{-}econ}$:

| | Economic | Non-economic |
|--|----------|--------------|
| **Substitute AI** | Core: erodes GDP signal? | Diagnostic: general or targeted? |

If $|\hat{\beta}^{econ}| > |\hat{\beta}^{non\text{-}econ}|$: tracker specifically threatened. If $|\hat{\beta}^{non\text{-}econ}| > |\hat{\beta}^{econ}|$: AI cannibalizes non-economic search, tracker relatively safe. If both large: general substitution.

As external validation for the roleplaying/creative writing categories: triangulate against category-specific usage data where available (e.g., chatbot usage reports, app store analytics). Strong substitution effects in these categories would support the diagnostic interpretation.

**3c. Vulnerability score:** $V_k = |\hat{\beta}_k| \times ShapleyImportance_k$, where Shapley importance is drawn from the category-level values in `weekly_shap.pkl` (not the sector-level aggregates in the paper). Scatter plot with categories labeled; upper-right = danger zone.


### Phase 4: Nowcasting Degradation

**Target:** Quarterly y-o-y real GDP growth from OECD QNA.

**Features:** Quarterly-mean SVI for 12 economic categories, pooled cross-country.

**Rolling-origin evaluation:** For each quarter q in 2019Q1 to 2026Q1, train on all data up to q minus 1, predict q. Compute 1-step-ahead RMSE separately for pre-AI (2019 to 2022) and post-AI (2023 to 2026).

| Scenario | Features | Purpose |
|----------|----------|---------|
| A | 12 economic categories | Baseline tracker |
| B | A + $AI^{sub}$ | Does AI adoption control improve post-AI fit? |
| C | A, full retrain each quarter | Does re-estimation recover performance? |

**Interpretation of Scenario B:** If RMSE(B) less than RMSE(A) post-AI, the GDP signal has not disappeared. It has *relocated* across platforms. The tracker needs supplementary inputs, not replacement. If RMSE(B) approximately equals RMSE(A), the degradation is not addressable by controlling for AI adoption. The structural break is deeper.

**Model escalation:** AR(1) + country FE as floor. GBT as main. If GBT degrades more than AR(1), the nonlinear signal the tracker exploits is what's breaking.

**Cross-country moderator:** Interact country-level RMSE increase with EF English Proficiency Index. Prediction: higher English proficiency → stronger AI substitution → larger degradation.

**Leave-one-category-out:** Drop each category, retrain, compare RMSE. Triangulate with Phase 3 vulnerability scores.

**Reweighted tracker:** Down-weight categories with high $V_k$. Does the reweighted model outperform equal-weighted post-AI? This is the constructive policy output.


### 4.X Analytical Caveats

- **No within-data placebo:** The original design proposed Gemini as a measurement placebo: same AI enthusiasm, but Gemini "routes through Google" and thus would not reduce GTrends measurement, while ChatGPT/Perplexity/Claude substitute away from Google. This fails because (a) Gemini app queries are chatbot interactions, not Google Searches—they never enter the Google Search query stream that Trends samples (source: Google Gemini API documentation, ai.google.dev/gemini-api/docs/google-search), and (b) Google Trends explicitly filters "searches made by Google products and services," which includes AI Overviews and AI Mode fan-out queries as well as Gemini's internal grounding queries (source: support.google.com/trends/answer/4365533). Both substitute AI and Gemini reduce GTrends measurement, just via different mechanisms—cross-platform exit vs. within-ecosystem filtering. A difference-in-magnitudes test ($\beta_1^{sub} \neq \beta_2^{plac}$) is possible in principle, but rests on a behavioral assumption about the degree of residual Google Search use among Gemini vs. ChatGPT users that is unobservable and hard to validate. The identification strategy therefore relies on lagged treatment with pre-trends (Phase 2) and the content axis (Phase 3), without a placebo. A within-Google structural break test around AI Overviews rollout (mid-2024 US) provides complementary evidence.

- **Random slopes borderline:** ~48 obs per MSA is tight for random slope estimation (Phase 2, Step 3). Report mean shrinkage factor and BLUP range to assess reliability; treat random slopes as exploratory if shrinkage is high.

- **MSA suppression:** GTrends suppresses low-volume searches (SVI < 5). Suppression indicator created in data pull (Section 3.1); primary sensitivity restricted to top-100 MSAs.

- **Within-Google erosion:** AI Overviews (launched May 2024 in the US) may reduce follow-up searches even for users who never leave Google. Since fan-out queries are filtered from GTrends, the measured SVI for a category could decline even without cross-platform substitution. This strengthens the overall thesis but complicates attribution to external AI tools specifically. Structural break tests around the AI Overviews rollout provide a complementary within-Google test.


### Extension A: Diurnal Pattern (mechanism test, run after main analysis)

If AI substitution is the mechanism, erosion should concentrate in hours of peak AI usage (work hours, evening). Pull hourly country-level GTrends for top 5 economic categories for a few representative weeks (one pre-AI in 2022, two post-AI in 2024 to 2025). US only. Approximately 45 queries. If the diurnal pattern is visible, produce a figure. If noisy, drop. Low cost to pilot.


### Extension B: ChatGPT Outages (natural experiment, run after main analysis)

ChatGPT has experienced several multi-hour global outages (documented on Downdetector, OpenAI status page, and X/social media). If economic GTrends spike during outages (users forced back to Google) and normalize after, that is direct evidence of real-time substitution.

**Data:** Downdetector historical logs or OpenAI status page for outage timing. Hourly GTrends for economic categories during outage windows (±24 hours).

**Design:** Event-study around each outage, with the outage period as treatment and adjacent hours as control. Multiple outages provide replication.

**Notes:** Some outages may affect other AI providers simultaneously (shared infrastructure, cloud provider issues). Outages specific to OpenAI are cleanest. Also check whether other providers (Anthropic, Perplexity) had independent outages. These would serve as additional natural experiments. The converse test (Anthropic outage, no GTrends spike, because Claude users are a smaller share) is a useful placebo.

**Feasibility:** Contingent on hourly GTrends data being non-noisy at country level for short windows. Pilot before committing.


### Extension C: Italy ChatGPT Ban (case study, contingent on data quality)

Italy banned ChatGPT March 31 to April 28, 2023. If Italian economic GTrends recovered during the ban relative to other OECD countries and dropped again after, that is evidence from an exogenous policy shock.

**Design:** DID with one treated unit (Italy) and 37 controls, weekly data. Inference via permutation (assign fake bans to each control country, compare Italy's effect to placebo distribution) or synthetic control.

**Status:** Suggestive extension. Run only after main analysis is complete. Data quality concern: a single country-month with potentially noisy weekly GTrends may not yield a detectable effect. Worth a pilot pull of Italian GTrends for 2 to 3 economic categories in Q1 to Q2 2023 to assess feasibility before committing.

---

## 5. Technical Stack

| Component | Tool |
|-----------|------|
| Package management | `uv` |
| Google Trends | `pytrends` + `tenacity` |
| OECD SDMX | `requests` |
| BLS LAUS | flat files in `data/raw/` |
| Census ACS | `census` package via API (key in `.env`) |
| Shapley values | `pickle` |
| Panel regression | `linearmodels` (FE, two-way clustering) |
| Mixed effects | `statsmodels.MixedLM` |
| Structural breaks | `arch` (Zivot-Andrews), `ruptures` (change-point detection) |
| HAC SEs | `statsmodels` (Newey-West) |
| GAM | `pygam` |
| GBT | `lightgbm` |
| PCA | `scikit-learn` |
| API key management | `python-dotenv` |
| Visualization | `matplotlib`, `seaborn` |

---

## 6. Repo Structure

```
google-trends-ai-shift/
├── README.md
├── .env (gitignored; contains CENSUS_API_KEY)
├── pyproject.toml / uv.lock / .python-version / .gitignore
├── src/
│   ├── 00_gtrends_ai/pull.py
│   ├── 01_gtrends_econ/pull.py
│   ├── 02_qna/pull.py
│   ├── 03_bls/process.py
│   ├── 04_census/pull.py
│   ├── 05_panel_msa/build.py
│   ├── 06_panel_country/build.py
│   ├── 10_validation/run.py
│   ├── 11_breaks/run.py
│   ├── 12_panel/run.py
│   ├── 13_heterogeneity/run.py
│   ├── 14_nowcasting/run.py
│   ├── 20_diurnal/run.py
│   ├── 21_outages/run.py
│   ├── 22_italy/run.py
│   ├── utils/ (gtrends.py, sdmx.py, crosswalks.py)
│   └── figures/
├── data/ (gitignored: raw/, interim/, processed/)
├── output/ (gitignored)
└── notebooks/ (gitignored)
```

---

## 7. Open Questions

**Data (resolve before implementation):**
- [x] QNA SDMX dataflow ID: confirmed under `OECD.SDD.NAD` (verify exact ID via API)
- [x] 215 categories confirmed from paper (paragraph 16), selected from 1,200 available
- [x] 33 topics confirmed (paragraph 16)
- [x] Shapley pickle files loaded; top-12 to extract by mean importance
- [x] Gemini routing: resolved — not a valid placebo; see Section 4.X
- [ ] `pytrends` MSA-level suppression rates (pilot: 3 categories × 50 MSAs)
- [x] BLS LAUS: flat files downloaded to `data/raw/`
- [x] Census ACS: API key obtained; stored in `.env`

**Methodology (resolve during analysis):**
- [ ] Substitute index aggregation (PCA vs. average vs. ChatGPT alone)
- [ ] Pre-trend test: parallel trends before Nov 2022?
- [ ] Within-Google structural break around AI Overviews rollout (mid-2024) as complementary test

---

## 8. Expected Outputs

1. Proxy validation (cross-sectional, stable across years)
2. Descriptive time series with LOWESS and structural breaks
3. Main result: $\hat{\beta}$ on $AI^{sub}$ with two-way FE and pre-trend test (headline)
4. Granger robustness: lagged AI predicts GTrends changes
5. Pre-trend figure: parallel trends before Nov 2022
6. Content-axis comparison: economic vs. non-economic categories
7. Category vulnerability scatter ($|\hat{\beta}| \times$ Shapley importance)
8. Nowcasting degradation: rolling-origin RMSE pre-AI versus post-AI, scenarios A to C
9. Leave-one-out decomposition
10. Reweighted tracker performance