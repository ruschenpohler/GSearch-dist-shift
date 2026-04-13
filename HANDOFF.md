# Project State — Handoff Document

**Date:** 2026-04-13
**Repo:** `https://github.com/ruschenpohler/GSearch-dist-shift.git`
**Branch:** master (9 commits ahead of origin)

---

## What's Done

### Infrastructure
- `pyproject.toml` with all dependencies (pinned `urllib3<2` for pytrends compat)
- All directories created per AGENTS.md Section 6
- `.gitignore` excludes `data/`, `output/`, `notebooks/`, `.env`, `*.pkl`, `AGENTS.md`

### AGENTS.md (v5, not tracked by git)
- Removed all Gemini/placebo references
- ID strategy: lagged treatment + pre-trends (temporal) and GDP-relevant vs non-relevant (content)
- Added Section 4.X analytical caveat with sourced evidence (Google Trends FAQ, Gemini API docs)
- Hybrid GTrends query strategy: 8 category IDs + 4 search terms (see category_mapping.py)
- Updated tech stack: arch + ruptures (not rpy2), python-dotenv, pyarrow

### Data
- **BLS state unemployment**: `data/raw/bls_state_unemployment.parquet` (30,600 rows, 51 states, 1976-2026)
- **ACS MSA demographics**: `data/raw/acs_msa_demographics.parquet` (2,779 rows, ~927 MSAs, years 2021-2023)
- **Shapley pickles**: `weekly_shap.pkl`, `monthly_shap.pkl` in project root (239 categories, top-12 extracted)
- **BLS flat files**: `data/raw/la.data.3.AllStatesS`, `la.series`, `la.area`, `la.measure`
- **Census API key**: `.env` file in root (not tracked by git)
- **OECD QNA GDP**: `data/raw/oecd_qna_gdp.parquet` (8,113 rows, 38 countries, 1947-Q2 to 2025-Q4)
- **EF EPI**: `data/raw/ef_epi.parquet` (123 countries, 2025 scores, 0-800 scale)
- **GTrends AI terms**: partial pulls exist (country monthly missing DE; country weekly complete for 5 countries)
- **GTrends econ categories**: pilot pull exists (5 countries × 15 categories × 75 months)

### Code (tested and working)
- `src/utils/gtrends.py` — pytrends wrapper with tenacity retry, cat= support, MSA/country/monthly/weekly pulls, SVI suppression flagging (< 5), proportional rescaling for weekly stitching
- `src/utils/crosswalks.py` — MSA-to-state mapping, FIPS codes, BLS loader, country codes, PILOT_MSA_GEOS (10), CENSUS_NAME_TO_PYTRENDS (50), get_pytrends_msa_codes() function
- `src/utils/category_mapping.py` — SHAPLEY_QUERIES (12 entries), NON_ECONOMIC_DIAGNOSTICS, ANNEX_B_GROUPS
- `src/utils/validation.py` — data validation module: GTrends suppression rates, zero rates, time gap checks, QNA validation, full raw-data report
- `src/00_gtrends_ai/pull.py` — refactored to use shared gtrends.py utilities; no more direct TrendReq calls
- `src/01_gtrends_econ/pull.py` — removed unused `pickle` import; uses PILOT_MSA_GEOS from crosswalks
- `src/02_qna/pull.py` — **fixed and tested**: switched from dead sdmx.oecd.org endpoint to working stats.oecd.org/SDMX-JSON API; filters in Python for B1GQ/Y/S1/PC/L/G1; includes ISO3→ISO2 mapping
- `src/03_bls/process.py` — BLS processing (tested, working)
- `src/04_census/pull.py` — ACS pull (tested, working)
- `src/04_census/pull_epi.py` — EF EPI pull from Wikipedia (123 countries, 2025; fallback to manual CSV)
- `src/utils/__init__.py`, all `__init__.py` stubs for remaining modules

### Key Decisions Made
1. **Gemini is not a valid placebo** — both substitute AI and Gemini reduce GTrends measurement (see AGENTS.md 4.X for sources)
2. **Category mapping is hybrid** — 8/12 use `cat=` with a broad query; 4/12 use free-text search
3. **"House price index"** → "Housing prices" as proxy (zero volume as exact term)
4. **urllib3<2** required for pytrends compatibility
5. **Census API key was invalid** — pulled without key (works, lower rate limit)
6. **OECD QNA**: API endpoint is `stats.oecd.org/SDMX-JSON/data/QNA/all` (not `sdmx.oecd.org`); B1GQ is the GDP code (not B1GS); TRANSACTION=B1GQ, ADJUSTMENT=Y, UNIT_MEASURE=PC, PRICE_BASE=L, TRANSFORMATION=G1
7. **Weekly stitching** uses proportional rescaling (not naive drop_duplicates); most recent window is reference, earlier windows rescaled by overlap ratio
8. **EPI data** sourced from Wikipedia (123 countries, 2025; no official CSV available)

### Known Data Issues
- GTrends AI monthly pull is missing DE (partial pull artifact) — will be fixed on re-pull
- SVI suppression rate is 84.5% for AI terms (expected: near-zero before Nov 2022) and 9.1% for econ categories
- QNA has sparse data for some countries (CHL, COL, CZE, EST, etc. have fewer observations)
- ACS `median_age` column appears to contain FIPS/MSA codes rather than actual median age (needs investigation on merge)

## What's NOT Done Yet (Next Steps)

### Data Pulls (long-running, rate-limited)
- [ ] Re-run GTrends pulls with updated code (`uv run python run_all_pulls.py`)
- [ ] Expand MSA pull from pilot (10) to 50 (use `get_pytrends_msa_codes()` in crosswalks.py)
- [ ] Later: expand MSA pull to ~200

### Code to Write
- [ ] `src/05_panel_msa/build.py` — merge GTrends + BLS + ACS by MSA-month
- [ ] `src/06_panel_country/build.py` — merge GTrends + QNA + EF EPI by country-quarter
- [ ] `src/10_validation/run.py` — Phase 0 (temporal, cross-sectional, internal consistency)
- [ ] `src/11_breaks/run.py` — Phase 1 (LOWESS, Zivot-Andrews, parametric)
- [ ] `src/12_panel/run.py` — Phase 2 (two-way FE, Granger, escalation)
- [ ] Remaining analysis scripts (13-14, 20-22)
- [ ] Investigate ACS `median_age` column (may contain MSA codes, not ages)

### Methodology Decisions Still Open
- [ ] Substitute index aggregation: PCA vs average vs ChatGPT alone
- [ ] Pre-trend test: parallel trends before Nov 2022
- [ ] Within-Google structural break around AI Overviews rollout (mid-2024)

## How to Resume

1. Re-run GTrends pulls: `uv run python run_all_pulls.py`
2. QNA and EPI data are done: `data/raw/oecd_qna_gdp.parquet` and `data/raw/ef_epi.parquet`
3. Run validation: `uv run python src/utils/validation.py`
4. Write `src/05_panel_msa/build.py` once GTrends data lands
5. Write `src/10_validation/run.py` for Phase 0

## Git Status
- 9 local commits ahead of origin (not pushed)
- AGENTS.md is in .gitignore (stays local, not tracked)
- Data files in `data/raw/` are gitignored (stay local)
- `.env` with Census API key is gitignored