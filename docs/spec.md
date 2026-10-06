# Spec: coal capacity dashboard, 2017 vs 2023

## 1. Goal

The dashboard compares operating coal capacity by country in 2017 and in 2023. It shows the trend for each country, the details of each plant, and a map of the plants.

## 2. Data sources

| File | Release | Rows | Row = |
|---|---|---|---|
| `data/Global-Coal-Plant-Tracker-Jan-2017.csv` | GEM, January 2017 | 12,256 | one unit |
| `data/Global-Coal-Plant-Tracker-July-2023.csv` | GEM, July 2023 | 13,785 | one unit |

Both files start with a UTF-8 BOM. Numbers can contain thousands separators (`8,272`).

## 3. Definitions

| Term | Definition |
|---|---|
| Unit | One row of a CSV file. The key is `Tracker ID`. |
| Plant | A group of units. The key is `GEM location ID` (2023). Section 4.5 gives the rules for 2017-only units. |
| Operating capacity | The sum of `Capacity (MW)` for units with the status `operating` in that year. |
| Country Δ MW | `mw_2023 - mw_2017` |
| Country Δ % | `(mw_2023 - mw_2017) / mw_2017 × 100`. It is null when `mw_2017 = 0`. |
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

### 4.6 Plant change

The ETL compares the operating MW of the plant in 2017 (`mw17`) and in 2023 (`mw23`) exactly:

| Change | Rule |
|---|---|
| `new` | `mw17 = 0` and `mw23 > 0` |
| `retired` | `mw17 > 0` and `mw23 = 0` |
| `grew` | `mw23 > mw17 > 0` |
| `shrank` | `mw17 > mw23 > 0` |
| `unchanged` | `mw17 = mw23 > 0` |
| none | `mw17 = mw23 = 0` |

- A plant with no change (0 MW in both years) does not show on maps or in lists.
- The route `/plant/:id` still shows the plant.

## 5. API (FastAPI)

| Method and path | Response |
|---|---|
| `GET /api/countries` | List of countries: `name, mw_2017, mw_2023, delta_mw, pct_change, trend`. |
| `GET /api/countries/{name}` | Country KPIs and the list of plants of the country that have a change. |
| `GET /api/plants/map?country=` | Plants that have a change and coordinates: `id, name, lat, lon, mw17, mw23, change`. One response, no pagination. `country` is optional. |
| `GET /api/plants/{id}` | Plant record and its units. |

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
- Change colors: `new` = dark orange, `grew` = light orange, `retired` = dark blue, `shrank` = light blue, `unchanged` = gray.
- Data source label: "Data: GEM, Jan 2017 and July 2023".

### 6.3 Routes

- `/`: global KPIs, a sortable country table, a diverging bar chart of Δ MW for the top 20 countries by |Δ MW|, and the global map.
- `/country/:name`: breadcrumb, country KPIs, the map fitted to the country, and a sortable plant table.
- `/plant/:id`: breadcrumb, plant header, mini-map, unit table and a link to the GEM wiki.

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
- Given a 2017 unit with the country `Turkey`
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
- Given a plant with 0 MW operating in 2017 and 600 MW operating in 2023
- When the ETL runs
- Then the plant change is `new`.

**AC-ETL-8: Units without coordinates**
- Given an operating unit without latitude and longitude
- When the ETL runs
- Then the unit capacity is in the country total
- And the plant is not in the response of `GET /api/plants/map`.

### 7.2 API

**AC-API-1: Country list**
- Given the database is loaded
- When the client sends `GET /api/countries`
- Then the response contains 82 countries
- And no country has 0 MW in both years.

**AC-API-2: Δ % with no 2017 capacity**
- Given a country with 0 MW operating in 2017 and more than 0 MW in 2023 (for example, `Panama`)
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
- Then the page shows 1,965.4 GW for 2017, 2,095.1 GW for 2023 and +129.6 GW for the change.

**AC-UI-2: Table sort**
- Given the user is on `/`
- When the user clicks the column header "Δ %"
- Then the table sorts by Δ % and the rows with "new" are at the end.

**AC-UI-3: Δ % labels**
- Given a country with 0 MW in 2017 (for example, `Panama`)
- When the country table shows the country
- Then the Δ % cell shows "new".
- Given a country with 0 MW in 2023 (for example, `Portugal`)
- When the country table shows the country
- Then the Δ % cell shows "phased out".

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
- Then the plant table shows Plant, MW 2017, MW 2023, Δ and Change
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
- Then the column "Status 2017" for that unit shows "not tracked".

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

- Branches, in this sequence:
  1. `feature/app-scaffold`
  2. `feature/data-etl`
  3. `feature/country-comparison`
  4. `feature/plant-map`
  5. `feature/plant-detail`
- After user approval, merge each branch into `main` with `--no-ff`.
- Small atomic commits, Conventional Commits, no signature lines.

## 10. Out of scope

- Years other than 2017 and 2023, and time series with more than two points.
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
