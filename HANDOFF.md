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

### Code
- `src/utils/gtrends.py` — pytrends wrapper with tenacity retry, cat= support, MSA/country/monthly/weekly pull functions
- `src/utils/crosswalks.py` — MSA-to-state mapping, FIPS codes, BLS loader, country codes
- `src/utils/category_mapping.py` — SHAPLEY_QUERIES (12 entries: 8 category, 4 search term), NON_ECONOMIC_DIAGNOSTICS, ANNEX_B_GROUPS
- `src/00_gtrends_ai/pull.py` — AI terms pull (4 terms, country monthly/weekly, MSA monthly pilot)
- `src/01_gtrends_econ/pull.py` — Economic categories pull (pilot functions using hybrid category/term approach)
- `src/02_qna/pull.py` — OECD QNA via SDMX (not yet tested)
- `src/03_bls/process.py` — BLS processing (tested, working)
- `src/04_census/pull.py` — ACS pull (tested, working)
- `src/utils/__init__.py`, all `__init__.py` stubs for remaining modules

### Key Decisions Made
1. **Gemini is not a valid placebo** — both substitute AI and Gemini reduce GTrends measurement (see AGENTS.md 4.X for sources)
2. **Category mapping is hybrid** — Shapley names are GTrends category names, not search terms. 8/12 use `cat=` with a broad query; 4/12 use free-text search
3. **"House price index"** has zero search volume as exact term → "Housing prices" used as proxy
4. **urllib3<2** required for pytrends compatibility (`method_whitelist` removed in urllib3 2.x)
5. **Census API key was invalid** — pulled without key (works, lower rate limit)

## What's NOT Done Yet (Next Steps)

### Data Pulls (long-running, rate-limited)
- [ ] `uv run python run_all_pulls.py` — GTrends AI terms + economic categories (4-8 hours)
  - AI terms: country monthly (~5 min), country weekly (~25 min), MSA pilot (~5 min)
  - Economic categories: same structure but slower (15 individual queries per geography)
- [ ] `uv run python src/02_qna/pull.py` — OECD QNA GDP data (not yet tested)
- [ ] Expand MSA pull from pilot (10) to full scope (~200) — flagged for later

### Code to Write
- [ ] `src/05_panel_msa/build.py` — merge GTrends + BLS + ACS by MSA-month
- [ ] `src/06_panel_country/build.py` — merge GTrends + QNA + EF EPI by country-quarter
- [ ] `src/10_validation/run.py` — Phase 0 (temporal, cross-sectional, internal consistency)
- [ ] `src/11_breaks/run.py` — Phase 1 (LOWESS, Zivot-Andrews, parametric)
- [ ] `src/12_panel/run.py` — Phase 2 (two-way FE, Granger, escalation)
- [ ] Remaining analysis scripts (13-14, 20-22)

### Methodology Decisions Still Open
- [ ] Substitute index aggregation: PCA vs average vs ChatGPT alone
- [ ] Pre-trend test: parallel trends before Nov 2022
- [ ] Within-Google structural break around AI Overviews rollout (mid-2024)

## How to Resume

1. Start GTrends pulls: `uv run python run_all_pulls.py` (or individual scripts)
2. Pull QNA data: `uv run python src/02_qna/pull.py`
3. Check output files in `data/raw/` — should see parquet files appearing
4. Write `src/05_panel_msa/build.py` once GTrends data lands
5. Write `src/10_validation/run.py` for Phase 0

## Git Status
- 9 local commits ahead of origin (not pushed)
- AGENTS.md is in .gitignore (stays local, not tracked)
- Data files in `data/raw/` are gitignored (stay local)
- `.env` with Census API key is gitignored