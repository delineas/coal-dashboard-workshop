# Spec: coal capacity dashboard, 2017 vs 2023

## 1. Goal

The dashboard compares operating coal capacity by country in 2017 and in 2023. It shows the trend for each country, the details of each plant, and a map of the plants.

## 2. Data sources

| File | Release | Rows | Row = |
|---|---|---|---|
| `data/Global-Coal-Plant-Tracker-Jan-2017.csv` | GEM, January 2017 | 12,219 | one unit |
| `data/Global-Coal-Plant-Tracker-July-2023.csv` | GEM, July 2023 | 13,785 | one unit |

Both files start with a UTF-8 BOM. Numbers can contain thousands separators (`8,272`). Some fields contain line breaks, so the number of lines is larger than the number of rows.

**Tracker coverage changed between the two releases.** GEM added units that operated before 2017 but were not in the 2017 file, and removed units from the 2017 file. A unit that is not in one file did not necessarily start or stop operation. The comparison rules in section 4.6 separate real change from coverage change.

## 3. Definitions

| Term | Definition |
|---|---|
| Unit | One row of a CSV file. The key is `Tracker ID`. |
| Plant | A group of units. The key is `GEM location ID` (2023). Section 4.5 gives the rules for 2017-only units. |
| Operating capacity | The sum of `Capacity (MW)` for units with the status `operating` in that year. |
| Snapshot total (`mw_2017`, `mw_2023`) | The operating capacity of all units in the file of that year. It is equal to the GEM published total. |
| Comparable unit | A unit that is in both files, or a unit that is only in the 2023 file and has a `Start year` of 2017 or later. See section 4.6. |
| Comparable capacity (`cmp_2017`, `cmp_2023`) | The operating capacity of the comparable units only. |
| Country Δ MW | `cmp_2023 - cmp_2017`. This is the real change. |
| Coverage change MW | `(mw_2023 - mw_2017) - Δ MW`. This is the effect of units that GEM added to or removed from the tracker. |
| Country Δ % | `Δ MW / cmp_2017 × 100`. It is null when `cmp_2017 = 0`. The UI shows "new" if `cmp_2023 > 0`, and "not comparable" if `cmp_2023 = 0`. It shows "phased out" if `cmp_2017 > 0` and `cmp_2023 = 0`. |
| Country trend | `up` if Δ MW > 0, `down` if Δ MW < 0, `flat` if Δ MW = 0. |
| Plant change | See section 4.6. |

## 4. Data rules (ETL)

### 4.1 Process

- A Python script reads `data/*.csv` and writes `backend/coal.sqlite`.
- The moon task `backend:etl` runs the script.
- The tasks `backend:dev` and `backend:test` depend on `backend:etl`.
- Git ignores the `.sqlite` file.

### 4.2 Status

- The ETL converts all status values to lower case.

### 4.3 Country names

The ETL changes these 2017 names to the 2023 names:

| 2017 | 2023 |
|---|---|
| `Turkey` | `Türkiye` |
| `FYROM` | `North Macedonia` |
| `Swaziland` | `Eswatini` |
| `Democratic Republic of Congo` | `DR Congo` |
| `Bosnia & Herzegovina` | `Bosnia and Herzegovina` |

- `Jordan` and `Reunion` occur only in 2017. They are in an explicit allow list.
- Any other 2017 country that is not in the 2023 data and not in the map is an error.

### 4.3.1 Country of a unit

- A unit that is in the 2023 file uses its 2023 country **for both years**. The 2017 country of that unit is ignored.
- A unit that is only in the 2017 file uses its 2017 country, after the name map above.
- Reason: some units changed country between the releases (16 units `China` → `Hong Kong`, 1 unit `France` → `Guadeloupe`, 1 unit `Belgium` → `Russia`). If each year used its own country, `Hong Kong` would show as "new" although its plants operated in 2017, and the country totals would not agree with the plant table of the country page.
- The plant country is the country of its units. All units of a plant have the same country.

### 4.4 Bad rows

- The ETL discards 2017 rows with an empty status or an empty capacity (200 rows).
- For a duplicate `Tracker ID` in 2017, the ETL keeps the first row and discards the others.
- The ETL prints a summary of the discarded rows.
- Units without coordinates count in the totals. They do not show on maps.

### 4.5 Unit and plant matching

- The ETL matches units across years with `Tracker ID`.
- A unit that occurs in one year only is included. For the other year, the UI shows "not tracked".
- A unit that occurs in 2023 belongs to the plant of its `GEM location ID`.
- A 2017-only unit gets the `GEM location ID` of a sibling unit. A sibling unit has the same 2017 `Plant` and country, and occurs in 2023.
- If a 2017-only unit has no sibling unit, the ETL groups it by the 2017 (`Plant`, country). The plant ID is `L17-` + the first 8 hex characters of the SHA-1 of `<Plant>|<country>`.
- Plant name: the 2023 column `Plant ` (with a trailing space). For `L17-*` plants, the 2017 column `Plant`.

### 4.6 Comparable units and plant change

Each unit gets the flag `comparable`:

| Unit is in | Condition | `comparable` | Reason |
|---|---|---|---|
| both files | — | yes | Both releases give its status. |
| 2023 file only | `Start year` ≥ 2017 | yes | It started after the 2017 release. In 2017 it had 0 MW operating. |
| 2023 file only | `Start year` < 2017 or empty | no | GEM added it to the tracker later. Its 2017 status is unknown. |
| 2017 file only | — | no | GEM removed it from the tracker. The 2023 release still lists retired units, so its absence does not mean retirement. |

- Data check: 381 units (35,360 MW) operate in 2023, are only in the 2023 file, and started before 2017. 375 units (43,726 MW) operate in 2017 and are only in the 2017 file. Without this rule, these units would show as new and retired capacity.
- Snapshot totals (`mw_2017`, `mw_2023`) include all units. Δ MW, Δ %, trend and plant change use comparable units only.

For each plant, the ETL calculates:

- `mw17`, `mw23`: the snapshot operating MW of all its units.
- `cmp17`, `cmp23`: the operating MW of its comparable units.

The plant change compares `cmp17` and `cmp23` exactly:

| Change | Rule |
|---|---|
| `new` | `cmp17 = 0` and `cmp23 > 0` |
| `retired` | `cmp17 > 0` and `cmp23 = 0` |
| `grew` | `cmp23 > cmp17 > 0` |
| `shrank` | `cmp17 > cmp23 > 0` |
| `unchanged` | `cmp17 = cmp23 > 0` |
| `coverage` | `cmp17 = cmp23 = 0`, and `mw17 > 0` or `mw23 > 0` |
| none | `mw17 = mw23 = 0` |

- `coverage` means: the plant operates in one release, but none of its operating units can be compared. There are 183 such plants in the 2023 location IDs (for example, `L104985` Stepnogorsk power station, Kazakhstan).
- A plant with no change (0 MW in both years) does not show on maps or in lists.
- The route `/plant/:id` still shows the plant.

## 5. API (FastAPI)

| Method and path | Response |
|---|---|
| `GET /api/countries` | List of countries: `name, mw_2017, mw_2023, cmp_2017, cmp_2023, delta_mw, coverage_mw, pct_change, trend`. |
| `GET /api/countries/{name}` | Country KPIs and the list of plants of the country that have a change. |
| `GET /api/plants/map?country=` | Plants that have a change and coordinates: `id, name, lat, lon, mw17, mw23, cmp17, cmp23, change`. One response, no pagination. `country` is optional. |
| `GET /api/plants/{id}` | Plant record and its units. Each unit has the field `comparable`. |

- An unknown country or plant ID returns HTTP 404.
- Countries with 0 MW in both years are not in the response.

## 6. Frontend

### 6.1 Stack

- React, Tailwind, React Router, Recharts, react-leaflet v5, leaflet.markercluster.
- UI text in English. Number format en-US.

### 6.2 Visual direction

- Reference: prototype C, "Clean product dashboard".
- Left sidebar with Overview, country search and the change legend. On screens narrower than 1024px, the sidebar becomes a top bar with a menu button.
- Font: Inter with tabular numerals. Brand color: indigo.
- Change colors: `new` = dark orange, `grew` = light orange, `retired` = dark blue, `shrank` = light blue, `unchanged` = gray, `coverage` = white fill with a gray outline (legend label: "Tracker coverage change").
- Data source label: "Data: GEM, Jan 2017 and July 2023".

### 6.3 Routes

- `/`: global KPIs, a sortable country table, a diverging bar chart of Δ MW for the top 20 countries by |Δ MW|, and the global map.
  - KPIs: MW 2017 (snapshot), MW 2023 (snapshot), Δ MW (comparable) with Δ %, and coverage change MW.
  - Country table columns: Country, MW 2017, MW 2023, Δ MW, Δ %, Coverage, Trend. MW 2017 and MW 2023 are snapshot totals.
  - A short note under the KPIs explains: "Δ compares only units that both releases can compare. Coverage shows units that GEM added to or removed from the tracker."
- `/country/:name`: breadcrumb, country KPIs (same set as the overview), the map fitted to the country, and a sortable plant table (Plant, MW 2017, MW 2023, Δ MW, Change). The plant Δ MW is `cmp23 - cmp17`.
- `/plant/:id`: breadcrumb, plant header, mini-map, unit table and a link to the GEM wiki. The unit table has a column "Comparable" (yes / no). A unit with "no" shows a tooltip with the reason from section 4.6.

### 6.4 Map

- One circle for each plant. The radius is proportional to `sqrt(max(mw17, mw23))`.
- Mode selector: `2017`, `2023`, `Change`. The default is `Change`.
- Markers that are near each other make a cluster. The cluster icon is a donut that shows the share of each change class, with the plant count in the center.
- A popup shows the plant name, MW 2017 → MW 2023 and a link to the plant page.
- The map shows a legend.

## 7. Acceptance criteria

### 7.1 ETL

**AC-ETL-1: Operating totals**
- Given the two CSV files in `data/`
- When the ETL runs
- Then the global operating capacity is 1,965,448 MW for 2017 and 2,095,083 MW for 2023.

**AC-ETL-2: Country names**
- Given a unit that is only in the 2017 file, with the country `Turkey`
- When the ETL runs
- Then the unit belongs to the country `Türkiye`.

**AC-ETL-3: Unknown country**
- Given a 2017 fixture row with a country that is not in the 2023 data, not in the map and not in the allow list
- When the ETL tests run
- Then the test fails and shows the country name.

**AC-ETL-4: Bad rows**
- Given a 2017 row with an empty status, and two rows with the same `Tracker ID`
- When the ETL runs
- Then the ETL discards the empty row and the second duplicate row
- And the ETL prints the number of discarded rows for each reason.

**AC-ETL-5: Sibling plant**
- Given a 2017-only unit whose 2017 `Plant` and country are the same as those of a unit that occurs in 2023
- When the ETL runs
- Then the 2017-only unit belongs to the `GEM location ID` of that 2023 unit.

**AC-ETL-6: Synthetic plant ID**
- Given a 2017-only unit with no sibling unit
- When the ETL runs two times
- Then the unit belongs to a plant with an ID that starts with `L17-`
- And the ID is the same after each run.

**AC-ETL-7: Plant change**
- Given a plant whose comparable units have 0 MW operating in 2017 and 600 MW operating in 2023
- When the ETL runs
- Then the plant change is `new`.

**AC-ETL-8: Units without coordinates**
- Given an operating unit without latitude and longitude
- When the ETL runs
- Then the unit capacity is in the country total
- And the plant is not in the response of `GET /api/plants/map`.

**AC-ETL-9: Unit added to the tracker later**
- Given the unit `G113594` (Czech Republic, 30 MW, operating in 2023, `Start year` 2001, not in the 2017 file)
- When the ETL runs
- Then the unit is not comparable
- And its 30 MW are in `mw_2023` of Czech Republic, but not in `cmp_2023` or Δ MW.

**AC-ETL-10: Unit built after 2017**
- Given the unit `G114937` (China, 50 MW, operating in 2023, `Start year` 2022, not in the 2017 file)
- When the ETL runs
- Then the unit is comparable
- And its 50 MW are in `cmp_2023` and in Δ MW of China.

**AC-ETL-11: Unit removed from the tracker**
- Given the unit `G110459` (South Korea, 50 MW, operating in 2017, not in the 2023 file)
- When the ETL runs
- Then the unit is not comparable
- And its 50 MW are in `mw_2017` of South Korea, but not in `cmp_2017` or Δ MW.

**AC-ETL-12: Global comparable change**
- Given the two CSV files in `data/`
- When the ETL runs
- Then the global comparable capacity is 1,921,722 MW for 2017 and 2,054,880 MW for 2023
- And the global Δ MW is +133,158 MW (+6.9 %)
- And the global coverage change is −3,523 MW.

**AC-ETL-13: Unit that changed country**
- Given the 16 units that are `China` in the 2017 file and `Hong Kong` in the 2023 file
- When the ETL runs
- Then these units count for `Hong Kong` in both years
- And `Hong Kong` has `mw_2017` = 6,608 MW and `mw_2023` = 6,112 MW
- And `China` has `mw_2017` = 914,619 MW.

**AC-ETL-14: Plant with coverage change only**
- Given the plant `L104985` (Stepnogorsk power station, Kazakhstan), which operates in 2023 and has no comparable operating unit
- When the ETL runs
- Then the plant change is `coverage`.

### 7.2 API

**AC-API-1: Country list**
- Given the database is loaded
- When the client sends `GET /api/countries`
- Then the response contains 82 countries
- And each country has the fields `mw_2017, mw_2023, cmp_2017, cmp_2023, delta_mw, coverage_mw, pct_change, trend`
- And no country has 0 MW in both years.

**AC-API-2: Δ % with no 2017 capacity**
- Given a country with `cmp_2017` = 0 (for example, `Panama`)
- When the client sends `GET /api/countries`
- Then `pct_change` for that country is `null`.

**AC-API-3: Map filter**
- Given the database is loaded
- When the client sends `GET /api/plants/map?country=India`
- Then all plants in the response have the country `India`
- And all plants have coordinates and a change.

**AC-API-4: Not found**
- Given a plant ID that does not exist
- When the client sends `GET /api/plants/{id}`
- Then the response status is 404.

**AC-API-5: Plant with no operating capacity**
- Given a plant with 0 MW operating in both years
- When the client sends `GET /api/plants/{id}`
- Then the response status is 200 and the response contains the plant units.

### 7.3 Overview page

**AC-UI-1: KPIs**
- Given the user opens `/`
- When the page loads
- Then the page shows 1,965.4 GW for 2017, 2,095.1 GW for 2023, +133.2 GW (+6.9 %) for Δ, and −3.5 GW for the coverage change
- And the page shows the note that explains Δ and coverage.

**AC-UI-2: Table sort**
- Given the user is on `/`
- When the user clicks the column header "Δ %"
- Then the table sorts by Δ % and the rows with "new" or "not comparable" are at the end.

**AC-UI-3: Δ % labels**
- Given a country with `cmp_2017` = 0 and `cmp_2023` > 0 (for example, `Panama`)
- When the country table shows the country
- Then the Δ % cell shows "new".
- Given a country with `cmp_2017` > 0 and `cmp_2023` = 0 (for example, `Portugal`)
- When the country table shows the country
- Then the Δ % cell shows "phased out".
- Given a country with `cmp_2017` = 0 and `cmp_2023` = 0 (for example, `Reunion`)
- When the country table shows the country
- Then the Δ % cell shows "not comparable".

**AC-UI-4: Bar chart**
- Given the user is on `/`
- When the page loads
- Then the bar chart shows 20 countries, sorted by |Δ MW|
- And bars for an increase and bars for a decrease go in opposite directions.

**AC-UI-5: Country search**
- Given the user types "Ind" in the sidebar search
- When the user presses Enter
- Then the app opens the page of the first country that matches.

### 7.4 Country page

**AC-UI-6: Country navigation**
- Given the user is on `/`
- When the user clicks "India" in the country table
- Then the app opens `/country/India`
- And the map fits to the plants of India.

**AC-UI-7: Plant table**
- Given the user is on `/country/India`
- When the page loads
- Then the plant table shows Plant, MW 2017, MW 2023, Δ MW and Change
- And plants with 0 MW in both years are not in the table.

### 7.5 Plant page

**AC-UI-8: Plant detail**
- Given the user opens `/plant/<id>` for a plant with coordinates
- When the page loads
- Then the page shows the name, country, subnational unit, owner, parent, MW 2017, MW 2023, Δ and the change badge
- And a mini-map with one marker
- And a link "Open in GEM wiki".

**AC-UI-9: Unit table**
- Given a plant with a unit that occurs only in 2023
- When the user opens the plant page
- Then the column "Status 2017" for that unit shows "not tracked"
- And the column "Comparable" shows "yes" if the unit started in 2017 or later, and "no" in other cases.

**AC-UI-10: Breadcrumb**
- Given the user is on a plant page
- When the user clicks the country in the breadcrumb
- Then the app opens the country page.

**AC-UI-11: Unknown route item**
- Given the user opens `/plant/<id>` or `/country/<name>` with a value that does not exist
- When the page loads
- Then the page shows a "Not found" message and a link to the overview.

### 7.6 Map

**AC-MAP-1: Change mode**
- Given the map is in the `Change` mode
- When the map shows a plant with the change `retired`
- Then the circle color is dark blue.

**AC-MAP-2: Year mode**
- Given the user selects the mode `2017`
- When the map updates
- Then plants with 0 MW in 2017 are not on the map
- And the circle size uses the 2017 MW.

**AC-MAP-3: Cluster icon**
- Given the map is zoomed out on Asia
- When plants make a cluster
- Then the cluster icon is a donut with the share of each change class
- And the center shows the plant count.

**AC-MAP-4: Popup**
- Given the user clicks a plant circle
- When the popup opens
- Then the popup shows the name, MW 2017 → MW 2023 and a link to the plant page.

**AC-MAP-5: Coverage plants**
- Given the map is in the `Change` mode
- When the map shows a plant with the change `coverage` (for example, `L104985`)
- Then the circle has a white fill and a gray outline
- And the legend shows the label "Tracker coverage change".

### 7.7 General

**AC-GEN-1: Narrow screen**
- Given a screen width of 390 px
- When the user opens any route
- Then the page does not scroll horizontally
- And the sidebar is a top bar with a menu button.

**AC-GEN-2: Quality checks**
- Given the code on the feature branch
- When the developer runs `npx moon run :test :lint :build`
- Then all tasks pass.

## 8. Tests

- pytest for the ETL with small fixture CSV files: country names, unit matching, plant grouping, bad rows.
- pytest for the API with `TestClient`.
- Frontend: `build` and `lint` only.

## 9. Delivery

- [`docs/plan.md`](plan.md) gives the steps and their branches. Step 1 is a walking skeleton.
- After user approval, merge each branch into `main` with `--no-ff`.
- Small atomic commits, Conventional Commits, no signature lines.

## 10. Out of scope

- Years other than 2017 and 2023, and time series with more than two points.
- Reconstruction of the 2017 status of non-comparable units from the 2023 columns `Start year` and `Year retired`. These units stay out of Δ MW.
- Capacity that is not `operating`: construction, permitted, pre-permit, announced, shelved, mothballed, cancelled. These statuses show only in the unit table of a plant.
- Plants with 0 MW operating in both years on maps and in lists.
- Tolerance for small capacity changes (re-ratings). The change classification uses exact values.
- Clusters or segments of plants (age, technology, size, k-means).
- CO2, heat rate, capacity factor, coal type and other technical columns.
- Region and subregion views or filters.
- Map loading by bounding box, and server-side pagination.
- URL state for table sort and map mode.
- Dark mode.
- UI languages other than English.
- Data export (CSV, PDF, images).
- User accounts, authentication and data editing.
- Frontend unit tests and end-to-end tests.
- Deployment, hosting and CI.

## 11. Open items

- **Map tiles:** CARTO basemaps show "API KEY REQUIRED" on `localhost` and `file://`. Select a tile provider before `feature/plant-map`.
