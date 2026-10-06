# Plan: coal capacity dashboard, 2017 vs 2023

This plan implements [`docs/spec.md`](spec.md). It replaces the branch list in section 9 of the spec.

## 1. Approach

- **Step 1 is a walking skeleton.** It connects all layers for the main path of the spec: CSV files → ETL → SQLite → API → React page. Each layer has the minimum code. The skeleton stays as the base for all other steps.
- **Each other step adds one thing.** The step goes through all the layers that the thing needs (ETL, API, UI, tests), and ends with a visible or testable result.
- **No orphan code.** At the end of each step, all new code has a caller: each new ETL column goes to an API field, and each new API field goes to the UI (or to a test, if the spec defines it only for the API). A step does not add code "for a later step".
- **Refactor in place.** When a step needs a different structure, it changes the existing code. It does not add a second path next to the old one.

## 2. Rules for each step

- All steps use one branch, `feature/coal-dashboard`, from `main`. (This replaces the earlier rule of one branch for each step.) The branch names in section 5 are step names only.
- Small atomic commits, Conventional Commits, no signature lines.
- Before the merge, all these checks pass:
  - `npx moon run :test :lint :build` (AC-GEN-2).
  - The "Test at the end" list of the step.
  - From step 7: no horizontal scroll at 390 px on all routes that exist (AC-GEN-1).
- Each step ends with a commit that the checks pass on. After user approval, merge the branch into `main` with `--no-ff` at the end.

## 3. Decisions for this plan

The spec does not give these details. The plan uses these values. Change them before the related step if necessary.

| Topic | Value | Step |
|---|---|---|
| SQLite file | `backend/coal.sqlite` (the base project uses `app.sqlite`) | 1 |
| ETL module | `backend/app/etl.py`, run as `python -m app.etl` | 1 |
| Input for the `L17-` hash | `<2017 Plant>|<country after the name map>` | 10 |
| Two or more possible sibling plants | Use the smallest `GEM location ID` (3 units) | 10 |
| Search order in the sidebar | Alphabetical. "Ind" opens `India`. | 12 |
| Global KPIs | The frontend calculates them from `GET /api/countries`. No new endpoint. | 5 |

## 4. Open decisions

| Topic | Latest moment |
|---|---|
| Map tile provider (CARTO shows "API KEY REQUIRED"), its attribution, and an API key in `.env` if necessary | Before step 14 |

## 5. Steps

### Step 1: Walking skeleton — `feature/walking-skeleton`

Goal: the country comparison works from the CSV files to the browser.

- **Base:** copy `backend/`, `frontend/`, `.moon/`, `package.json` and `package-lock.json` from `../basecamp-tool`. Remove `/api/hello` and its test. Update `README.md`, the project names and the page title. Add `.moon/cache/` and `*.egg-info/` to `.gitignore`.
- **ETL:** `app/etl.py` reads the two CSV files (UTF-8 BOM, thousands separators), converts status to lower case, and skips rows without a numeric capacity. It sums the `operating` capacity by country for each year, with the country of each file. It writes the table `country_capacity(name, mw_2017, mw_2023)` to `backend/coal.sqlite`.
- **Moon:** add the task `backend:etl`. `backend:dev` and `backend:test` depend on it. Set `DB_PATH` to `coal.sqlite`.
- **API:** `GET /api/countries` returns `name, mw_2017, mw_2023`, sorted by `mw_2023` descending. It does not return countries with 0 MW in both years.
- **UI:** `App.tsx` gets the list and shows a table: Country, MW 2017, MW 2023, with en-US number format.
- **Tests:** an ETL test with a fixture CSV pair (3 to 5 rows). An API test on the real database.

Test at the end:
- `npx moon run :test :lint :build` passes.
- The sum of `mw_2017` is 1,965,448 MW and the sum of `mw_2023` is 2,095,083 MW (AC-ETL-1).
- `npx moon run backend:dev` and `frontend:dev`, then open `http://localhost:5173`: the table shows real data.
- Known limit: `Turkey` and `Türkiye` show as two rows. Step 2 fixes this.

### Step 2: Country names — `feature/country-names`

Goal: each country shows as one row.

- **ETL:** the name map and the allow list from section 4.3 of the spec. The ETL stops with an error that gives the name of an unknown 2017 country.
- **Tests:** the name map (AC-ETL-2) and the unknown-country error with a fixture (AC-ETL-3).

Test at the end:
- AC-ETL-2, AC-ETL-3 pass.
- In the browser, `Türkiye` shows once and `Turkey` does not show.

### Step 3: Unit table — `feature/unit-table`

Goal: the country totals come from one unit table, with the bad-row rules and the country of each unit.

- **ETL:** a table `units` with one row for each `Tracker ID`: country (section 4.3.1 of the spec), `status_2017`, `mw_2017`, `status_2023`, `mw_2023`. Discard bad 2017 rows and duplicates (section 4.4), and print the summary. `country_capacity` is now a SQL aggregate of `units`. The old direct sum is removed.
- **Tests:** bad rows (AC-ETL-4), the country of a unit (AC-ETL-13), the country list (AC-API-1, without the new fields).

Test at the end:
- AC-ETL-1 still passes. AC-ETL-4, AC-ETL-13 pass.
- `GET /api/countries` returns 82 countries.
- In the browser, `Hong Kong` shows 6,608 MW for 2017 and 6,112 MW for 2023.
- `npx moon run backend:etl` prints the discarded rows for each reason.

### Step 4: Comparable change — `feature/comparable-change`

Goal: the country table shows the real change and the coverage change.

- **ETL:** the flag `comparable` on each unit (section 4.6 of the spec).
- **API:** `GET /api/countries` adds `cmp_2017, cmp_2023, delta_mw, coverage_mw, pct_change, trend`.
- **UI:** the table adds the columns Δ MW, Δ %, Coverage and Trend. Δ % shows "new", "phased out" or "not comparable" (section 3 of the spec).
- **Tests:** AC-ETL-9 to AC-ETL-12, AC-API-1 (all fields), AC-API-2.

Test at the end:
- The tests above pass.
- In the browser: `Panama` shows "new", `Portugal` shows "phased out", `Reunion` shows "not comparable" (AC-UI-3).

### Step 5: Overview KPIs — `feature/overview-kpis`

Goal: the page shows the global numbers and explains Δ and coverage.

- **UI:** four KPI tiles above the table: MW 2017, MW 2023, Δ MW with Δ %, coverage change. The values are in GW. The note from section 6.3 of the spec is under the tiles.

Test at the end:
- The page shows 1,965.4 GW, 2,095.1 GW, +133.2 GW (+6.9 %) and −3.5 GW, and the note (AC-UI-1).

### Step 6: Table sort — `feature/country-table-sort`

Goal: the user can sort the country table.

- **UI:** a sortable table component. A click on a column header sorts by that column. A second click changes the direction. Null Δ % values are always at the end.

Test at the end:
- A click on "Δ %" sorts the table, and "new" and "not comparable" rows are at the end (AC-UI-2).

### Step 7: App shell — `feature/app-shell`

Goal: the page has the visual direction of prototype C.

- **UI:** a layout with the left sidebar (product name, "Overview" link, data source label "Data: GEM, Jan 2017 and July 2023"). Below 1024 px, the sidebar becomes a top bar with a menu button. Inter with tabular numerals, indigo brand color. The KPI tiles and the table use the card style of the prototype.

Test at the end:
- At 1400 px, the page has the sidebar. At 390 px, it has a top bar with a menu button, and no horizontal scroll (AC-GEN-1 for `/`).

### Step 8: Δ bar chart — `feature/delta-bar-chart`

Goal: the overview shows the 20 largest changes.

- **UI:** add Recharts. A diverging bar chart of Δ MW for the 20 countries with the largest |Δ MW|. Increases and decreases go in opposite directions.

Test at the end:
- The chart shows 20 countries sorted by |Δ MW| (AC-UI-4).

### Step 9: Country page — `feature/country-page`

Goal: the user can open a page for each country.

- **API:** `GET /api/countries/{name}` returns the country KPIs (the fields of the country list). An unknown name returns 404.
- **UI:** add React Router. The route `/country/:name` shows a breadcrumb and the KPI tiles (the same component as the overview). The country names in the overview table are links. An unknown name shows "Not found" with a link to the overview.
- **Tests:** the endpoint and its 404.

Test at the end:
- A click on "India" in the overview opens `/country/India` with the KPIs of India (AC-UI-6, without the map).
- `/country/Atlantis` shows "Not found" (AC-UI-11 for countries).

### Step 10: Plants on the country page — `feature/country-plants`

Goal: the country page lists its plants.

- **ETL:** a table `plants` (section 4.5 of the spec): `GEM location ID`, sibling units, `L17-` IDs, plant name, country, coordinates, owner, parent, subnational unit, wiki URL. Each unit gets its plant ID. Each plant gets `mw17, mw23, cmp17, cmp23`.
- **API:** `GET /api/countries/{name}` adds the list of plants with operating capacity in one year or more.
- **UI:** a sortable plant table on the country page (Plant, MW 2017, MW 2023, Δ MW), with the table component of step 6.
- **Tests:** AC-ETL-5, AC-ETL-6, and the plant list of a country.

Test at the end:
- AC-ETL-5, AC-ETL-6 pass.
- `/country/India` shows the plant table, without plants with 0 MW in both years.

### Step 11: Plant change — `feature/plant-change`

Goal: each plant shows its change class.

- **ETL:** the plant change from section 4.6 of the spec, including `coverage`.
- **API:** the plant list adds `change`.
- **UI:** a Change column with a colored badge (colors from section 6.2 of the spec). The change legend shows in the sidebar.
- **Tests:** AC-ETL-7, AC-ETL-14.

Test at the end:
- AC-ETL-7, AC-ETL-14 pass.
- `/country/India` shows the columns Plant, MW 2017, MW 2023, Δ MW and Change (AC-UI-7).
- `/country/Kazakhstan` shows Stepnogorsk power station with the badge "Tracker coverage change".

### Step 12: Country search — `feature/country-search`

Goal: the user can find a country from the sidebar.

- **UI:** a search field in the sidebar. It filters the country list while the user types. Enter opens the first match in alphabetical order.

Test at the end:
- Type "Ind" and push Enter: the app opens `/country/India` (AC-UI-5).

### Step 13: Plant page — `feature/plant-page`

Goal: the user can open the details of each plant.

- **API:** `GET /api/plants/{id}` returns the plant record and its units, with `comparable` for each unit. An unknown ID returns 404.
- **UI:** the route `/plant/:id` with the breadcrumb Overview › Country › Plant, the header (name, country, subnational unit, owner, parent, MW 2017, MW 2023, Δ, change badge), the unit table (Unit, MW, Status 2017, Status 2023, Start year, Retired year, Technology, Comparable) and the link "Open in GEM wiki". A missing status shows "not tracked". "Comparable: no" has a tooltip with the reason. The plant names in the country table are links. An unknown ID shows "Not found".
- **Tests:** AC-API-4, AC-API-5.

Test at the end:
- AC-API-4, AC-API-5 pass.
- A plant page shows all header fields and the link (AC-UI-8, without the mini-map).
- A unit that is only in 2023 shows "not tracked" and the correct "Comparable" value (AC-UI-9).
- The country in the breadcrumb opens the country page (AC-UI-10).
- An unknown plant ID shows "Not found" (AC-UI-11).

### Step 14: Global map — `feature/plant-map`

Requires: the tile provider decision (section 4).

Goal: the overview shows all plants on a map.

- **API:** `GET /api/plants/map` returns the plants with a change and coordinates (section 5 of the spec).
- **UI:** add Leaflet and react-leaflet. A map component on the overview: one circle for each plant, radius from `sqrt(max(mw17, mw23))`, color from the change class, popup with the name, MW 2017 → MW 2023 and a link to the plant page, and a legend.
- **Tests:** AC-ETL-8 (a plant without coordinates is not in the response).

Test at the end:
- AC-ETL-8 passes.
- A `retired` plant is dark blue (AC-MAP-1). A `coverage` plant has a white fill and a gray outline, and the legend shows "Tracker coverage change" (AC-MAP-5).
- A click on a circle opens the popup, and its link opens the plant page (AC-MAP-4).

### Step 15: Country map — `feature/country-map`

Goal: the country page shows its plants on a map.

- **API:** `GET /api/plants/map` adds the optional filter `country`.
- **UI:** the map component of step 14 on the country page. The map fits to the plants of the country.
- **Tests:** AC-API-3.

Test at the end:
- AC-API-3 passes.
- `/country/India` shows a map that fits to India (AC-UI-6, complete).

### Step 16: Plant mini-map — `feature/plant-mini-map`

Goal: the plant page shows the location of the plant.

- **UI:** the map component of step 14 in a small size with one marker on the plant page. A plant without coordinates shows the text "Location unavailable".

Test at the end:
- A plant with coordinates shows the mini-map with one marker (AC-UI-8, complete).

### Step 17: Map mode — `feature/map-mode`

Goal: the user can see the map for one year.

- **UI:** a segmented control `2017`, `2023`, `Change` (default `Change`). In a year mode, the circles use the MW of that year, and plants with 0 MW in that year are hidden.

Test at the end:
- In the mode `2017`, plants with 0 MW in 2017 are not on the map and the circle size uses the 2017 MW (AC-MAP-2).

### Step 18: Map clusters — `feature/map-clusters`

Goal: the map stays readable with about 2,900 plants.

- **UI:** add leaflet.markercluster in a small `useMap` wrapper. The cluster icon is an SVG donut with the share of each change class and the plant count in the center.

Test at the end:
- Zoomed out on Asia, the clusters show the donut and the count (AC-MAP-3).
- The map stays responsive when the user pans and zooms on the overview.

## 6. Acceptance criteria by step

| Step | Criteria |
|---|---|
| 1 | AC-ETL-1, AC-GEN-2 |
| 2 | AC-ETL-2, AC-ETL-3 |
| 3 | AC-ETL-4, AC-ETL-13, AC-API-1 (part) |
| 4 | AC-ETL-9, AC-ETL-10, AC-ETL-11, AC-ETL-12, AC-API-1, AC-API-2, AC-UI-3 |
| 5 | AC-UI-1 |
| 6 | AC-UI-2 |
| 7 | AC-GEN-1 |
| 8 | AC-UI-4 |
| 9 | AC-UI-6 (part), AC-UI-11 (part) |
| 10 | AC-ETL-5, AC-ETL-6 |
| 11 | AC-ETL-7, AC-ETL-14, AC-UI-7 |
| 12 | AC-UI-5 |
| 13 | AC-API-4, AC-API-5, AC-UI-8 (part), AC-UI-9, AC-UI-10, AC-UI-11 |
| 14 | AC-ETL-8, AC-MAP-1, AC-MAP-4, AC-MAP-5 |
| 15 | AC-API-3, AC-UI-6 |
| 16 | AC-UI-8 |
| 17 | AC-MAP-2 |
| 18 | AC-MAP-3 |

All 37 criteria of the spec have a step.
