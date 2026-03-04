# Tasks: E-Commerce Analytics Dashboard

**Input**: Design documents from `specs/001-ecommerce-dashboard/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/functions.md ✅, quickstart.md ✅

**Tests**: Included — plan.md §Technical Context explicitly specifies pytest unit tests for `load_data` and all aggregation functions; constitution §5 requires them.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in all descriptions

## Path Conventions

All source code lives at repository root (single-file Streamlit app):

- `dashboard.py` — single entry point, all functions
- `requirements.txt` — dependency manifest for Streamlit Cloud
- `tests/test_dashboard.py` — pytest unit tests
- `data/sales-data.csv` — READ ONLY, do not modify

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the three project files from scratch — the app skeleton, the test skeleton, and the dependency manifest.

- [x] T001 [P] Create `requirements.txt` at repo root with pinned versions: `streamlit>=1.32`, `pandas>=2.2`, `plotly>=5.20`
- [x] T002 [P] Create `tests/test_dashboard.py` with imports (`import pandas as pd`, `import pytest`, `from dashboard import load_data, calculate_kpis, prepare_trend_data, prepare_category_data, prepare_region_data`) and a single placeholder `test_placeholder` that passes
- [x] T003 Create `dashboard.py` at repo root with: imports (`import streamlit as st`, `import pandas as pd`, `import plotly.graph_objects as go`), `st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")`, stub definitions (`pass`) for all 8 functions (`load_data`, `calculate_kpis`, `prepare_trend_data`, `prepare_category_data`, `prepare_region_data`, `build_trend_chart`, `build_category_chart`, `build_region_chart`, `main`), and `if __name__ == "__main__": main()`

---

## Phase 2: Foundational (Blocking Prerequisite — Data Loading)

**Purpose**: `load_data()` is consumed by every user story. No story can be built until this function is correct.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Write pytest unit tests for `load_data()` in `tests/test_dashboard.py`: (a) happy path — calling `load_data("data/sales-data.csv")` returns a DataFrame with all 8 columns and 482 rows; (b) `FileNotFoundError` path — calling with a nonexistent path does not raise an exception (error is handled internally); (c) date coercion — DataFrame returned has `date` column of dtype `datetime64`
- [x] T005 Implement `load_data(filepath: str = "data/sales-data.csv") -> pd.DataFrame` in `dashboard.py`: add `@st.cache_data` decorator; load with `pd.read_csv(filepath, parse_dates=["date"])`; validate all 8 required columns present (raise `st.error()` + `st.stop()` on mismatch); parse dates with `pd.to_datetime(errors="coerce")`; count and drop NaT rows with `st.warning(f"{n} row(s) with invalid dates excluded")`; wrap file load in `try/except FileNotFoundError` and `except Exception` calling `st.error()` + `st.stop()` per `contracts/functions.md`

**Checkpoint**: `pytest tests/ -v` should show `test_placeholder` passing and all `load_data` tests passing before proceeding.

---

## Phase 3: User Story 1 — KPI Overview at a Glance (Priority: P1) 🎯 MVP

**Goal**: Display Total Sales (currency-formatted) and Total Orders (integer) as two prominent KPI cards that appear immediately on page load with no user interaction.

**Independent Test**: Open `http://localhost:8501` in a fresh browser tab. Two `st.metric` cards appear — one labelled "Total Sales" showing ~$650K–$700K formatted as `$XXX,XXX.XX`, one labelled "Total Orders" showing `482`. No clicks required.

- [x] T006 [P] [US1] Write pytest unit tests for `calculate_kpis()` in `tests/test_dashboard.py`: (a) given a 3-row test DataFrame, `total_orders` equals 3; (b) `total_sales` equals the sum of the `total_amount` column as a float; (c) both keys `"total_sales"` and `"total_orders"` are present in the returned dict
- [x] T007 [US1] Implement `calculate_kpis(df: pd.DataFrame) -> dict` in `dashboard.py`: return `{"total_sales": float(df["total_amount"].sum()), "total_orders": len(df)}` — pure function, no side effects, per `contracts/functions.md`
- [x] T008 [US1] Implement KPI section in `main()` in `dashboard.py`: add `st.title("ShopSmart Sales Dashboard")`; call `load_data()` wrapped in `try/except` with `st.error()` + `st.stop()`; call `calculate_kpis(df)`; render a `st.columns(2)` row — left column: `st.metric("Total Sales", f"${kpis['total_sales']:,.2f}")`, right column: `st.metric("Total Orders", f"{kpis['total_orders']:,}")`

**Checkpoint**: Run `streamlit run dashboard.py`. Dashboard title and both KPI cards appear. Total Orders = 482, Total Sales in range $650,000–$700,000.

---

## Phase 4: User Story 2 — Sales Trend Over Time (Priority: P2)

**Goal**: Display a full-width interactive Plotly line chart showing monthly sales totals with hover tooltips, so growth patterns are visible at a glance.

**Independent Test**: With dashboard open and KPI cards visible, scroll to the sales trend chart. X-axis shows 12 month labels (Jan–Dec 2024), Y-axis shows sales totals, hovering over any point reveals exact month and sales value.

- [ ] T009 [P] [US2] Write pytest unit tests for `prepare_trend_data()` in `tests/test_dashboard.py`: (a) output has columns `month` and `sales`; (b) rows are sorted ascending by `month`; (c) with a dataset spanning >30 days, grouping produces one row per calendar month; (d) with a dataset spanning ≤30 days, grouping produces one row per day
- [ ] T010 [US2] Implement `prepare_trend_data(df: pd.DataFrame) -> pd.DataFrame` in `dashboard.py`: compute date range as `df["date"].max() - df["date"].min()`; use `freq="MS"` if range > 30 days, else `freq="D"`; apply `df.groupby(pd.Grouper(key="date", freq=freq))["total_amount"].sum().reset_index()`; rename columns to `month` and `sales`; sort ascending by `month`; return result — pure function per `contracts/functions.md`
- [ ] T011 [US2] Implement `build_trend_chart(trend_df: pd.DataFrame) -> go.Figure` in `dashboard.py`: create `go.Figure` with `go.Scatter(x=trend_df["month"], y=trend_df["sales"], mode="lines+markers")`; set title "Sales Trend Over Time", X-axis label "Month", Y-axis label "Total Sales ($)"; configure hover template to show month and `$%{y:,.2f}`; return Figure without calling any `st.*` functions per `contracts/functions.md`
- [ ] T012 [US2] Add trend chart to `main()` in `dashboard.py` after the KPI row: call `prepare_trend_data(df)` and `build_trend_chart(trend_df)`; render with `st.plotly_chart(fig, use_container_width=True)`

**Checkpoint**: Dashboard now shows title + KPI row + full-width trend line chart. Hovering a point shows exact month and sales value.

---

## Phase 5: User Story 3 — Sales Breakdown by Category (Priority: P3)

**Goal**: Display a sorted bar chart showing all five product categories by total sales, descending, with interactive tooltips.

**Independent Test**: With data loaded, locate the category bar chart. All 5 categories appear, sorted so the highest-revenue category is leftmost. Hovering over a bar shows category name and exact sales total.

- [ ] T013 [P] [US3] Write pytest unit tests for `prepare_category_data()` in `tests/test_dashboard.py`: (a) output columns are `category` and `sales`; (b) rows are sorted descending by `sales`; (c) all categories present in the input DataFrame appear in the output (none filtered); (d) `sales` value for each category equals the sum of `total_amount` for that category's rows
- [ ] T014 [US3] Implement `prepare_category_data(df: pd.DataFrame) -> pd.DataFrame` in `dashboard.py`: `df.groupby("category")["total_amount"].sum().reset_index().rename(columns={"total_amount": "sales"}).sort_values("sales", ascending=False).reset_index(drop=True)`; return result — pure function per `contracts/functions.md`
- [ ] T015 [US3] Implement `build_category_chart(cat_df: pd.DataFrame) -> go.Figure` in `dashboard.py`: create `go.Figure` with `go.Bar(x=cat_df["category"], y=cat_df["sales"])`; set title "Sales by Category"; configure hover template to show category name and `$%{y:,.2f}`; return Figure without calling any `st.*` functions or re-sorting input data per `contracts/functions.md`

**Checkpoint**: With category function + chart builder complete, US3 is independently testable. `pytest tests/ -v` all pass. The chart builder can be verified by temporarily calling it in `main()` before the full US4 layout task.

---

## Phase 6: User Story 4 — Sales Breakdown by Region (Priority: P3)

**Goal**: Display a sorted bar chart showing all four geographic regions by total sales, descending, with interactive tooltips — placed side-by-side with the category chart.

**Independent Test**: With data loaded, locate the regional bar chart. All 4 regions appear (North, South, East, West), sorted descending. Hovering over a bar shows region name and exact sales total.

- [ ] T016 [P] [US4] Write pytest unit tests for `prepare_region_data()` in `tests/test_dashboard.py`: (a) output columns are `region` and `sales`; (b) rows are sorted descending by `sales`; (c) all regions present in the input DataFrame appear in the output; (d) `sales` value for each region equals the sum of `total_amount` for that region's rows
- [ ] T017 [US4] Implement `prepare_region_data(df: pd.DataFrame) -> pd.DataFrame` in `dashboard.py`: `df.groupby("region")["total_amount"].sum().reset_index().rename(columns={"total_amount": "sales"}).sort_values("sales", ascending=False).reset_index(drop=True)`; return result — pure function per `contracts/functions.md`
- [ ] T018 [US4] Implement `build_region_chart(region_df: pd.DataFrame) -> go.Figure` in `dashboard.py`: create `go.Figure` with `go.Bar(x=region_df["region"], y=region_df["sales"])`; set title "Sales by Region"; configure hover template to show region name and `$%{y:,.2f}`; return Figure without calling any `st.*` functions or re-sorting input data per `contracts/functions.md`
- [ ] T019 [US4] Add two-column bar chart row to `main()` in `dashboard.py` after the trend chart: create `col1, col2 = st.columns(2)`; in `col1` call `prepare_category_data(df)`, `build_category_chart(cat_df)`, `st.plotly_chart(fig, use_container_width=True)`; in `col2` call `prepare_region_data(df)`, `build_region_chart(region_df)`, `st.plotly_chart(fig, use_container_width=True)`

**Checkpoint**: Full dashboard complete. Layout matches plan.md wireframe: title → KPI row → trend chart → category|region row. All four user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation, deployment readiness, and final correctness check.

- [ ] T020 [P] Run full test suite in `tests/test_dashboard.py` with `pytest tests/ -v` and confirm all tests pass with zero failures or warnings
- [ ] T021 Validate dashboard locally against `quickstart.md` expected values: run `streamlit run dashboard.py`, open `http://localhost:8501`, confirm Total Orders = 482, Total Sales in range $650,000–$700,000, top category visible, all 4 regions shown
- [ ] T022 Verify deployment readiness: confirm `requirements.txt` is at repo root (not in a subdirectory), `data/sales-data.csv` is committed and not in `.gitignore`, `dashboard.py` is at repo root — all three conditions required per `research.md` Streamlit Community Cloud deployment decision

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **User Story phases (Phase 3–6)**: All depend on Foundational (Phase 2) completion
  - US1 (P1): implement first — its data load is consumed by all other stories
  - US2 (P2): implement after US1 (reuses `df` from `main()`)
  - US3 and US4 (both P3): implement after US2; they are mutually independent
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P2)**: Can start after Phase 2 — reuses `df` loaded in `main()`, independent of US1
- **US3 (P3)**: Can start after Phase 2 — independent of US2
- **US4 (P3)**: Can start after Phase 2 — independent of US2 and US3; T019 layout task requires both US3 and US4 functions

### Within Each User Story

- Test tasks ([P]) should be written before implementation (TDD: confirm tests fail first)
- Data preparation function before chart builder function
- Chart builder function before adding to `main()`

### Parallel Opportunities

- T001 and T002 (Phase 1) can run in parallel — different files
- T006 and T007 (Phase 3, US1) can run in parallel — different files
- T009 and T010 (Phase 4, US2) can run in parallel — different files
- T013 and T014 (Phase 5, US3) can run in parallel — different files
- T016 and T017 (Phase 6, US4) can run in parallel — different files
- T020 and T021 (Phase 7) can run in parallel — independent validation steps
- US3 (Phase 5) and US4 (Phase 6) can run in parallel if two developers are available

---

## Parallel Example: User Story 1

```bash
# In Phase 3, launch T006 and T007 simultaneously (different files):
Task T006: Write calculate_kpis tests in tests/test_dashboard.py
Task T007: Implement calculate_kpis in dashboard.py

# Then sequentially:
Task T008: Wire calculate_kpis into main() in dashboard.py
```

## Parallel Example: User Stories 3 & 4

```bash
# After Phase 2 + Phase 4 complete, two developers can split:
Developer A: T013 → T014 → T015  (prepare_category_data + build_category_chart)
Developer B: T016 → T017 → T018  (prepare_region_data + build_region_chart)

# Then join for T019:
Task T019: Add two-column chart row to main() in dashboard.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T005) — **required before any story**
3. Complete Phase 3: User Story 1 (T006–T008)
4. **STOP and VALIDATE**: `streamlit run dashboard.py` — KPI cards show correct values
5. Deploy to Streamlit Community Cloud if demo-ready

### Incremental Delivery

1. Setup + Foundational → data loads correctly
2. **+US1** → KPI cards visible → MVP deploy/demo
3. **+US2** → trend chart added → richer demo
4. **+US3** → category chart added
5. **+US4** → region chart added, layout complete → production deploy
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With two developers:
1. Together: Complete Setup (Phase 1) + Foundational (Phase 2)
2. Together: Complete US1 (Phase 3) — single unit of work
3. Dev A: US2 (Phase 4); Dev B: can start US3 prep
4. Dev A + Dev B: US3 and US4 in parallel (Phases 5–6)
5. Together: T019 layout merge, Phase 7 polish

---

## Notes

- `[P]` tasks involve different files and have no mutual dependencies — safe to run in parallel
- `[Story]` label maps each task to a specific user story for Jira traceability
- `tests/test_dashboard.py` tests are unit tests only — no Streamlit UI is started during tests
- `data/sales-data.csv` is READ ONLY — do not modify it at any point
- `main()` is built incrementally: T008 adds KPI section, T012 adds trend chart, T019 adds bar chart row
- Commit after each phase checkpoint to maintain a working state at each increment
