# Feature Specification: Flag the countries with a large capacity change

**Feature Branch**: `feature/flag-large-capacity-change`

**Created**: 2026-10-13

**Status**: Draft

**Input**: Issue #7 "T7 · Flag the countries with a large capacity change". Reporter: energy policy analyst (internal user). Request: "Every quarter I write a short note about the countries where coal capacity moved the most. Today I sort the country table by change and read it row by row. I want the dashboard to flag the countries with a large change in comparable capacity, up or down, so that I see them first. When I open a flagged country, I want to see which plants caused the change."

**Base spec**: [`docs/spec.md`](../spec.md). This spec uses the terms of section 3 (comparable capacity, Δ MW, Δ %, plant change). It does not change the data rules of section 4.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the flagged countries first on the overview (Priority: P1)

The analyst opens the overview. The country table shows a flag on each country with a large change in comparable capacity, up or down. At page load, the table sorts by the size of the change, so the flagged countries are the first rows. The analyst does not read the full table row by row.

**Why this priority**: This is the main request. It removes the manual sort and the row-by-row reading. It gives value without the other stories.

**Independent Test**: Open `/`. Make sure that the flagged countries are the first rows of the country table and that each one shows the flag. Make sure that no other country shows the flag.

**Acceptance Scenarios**:

1. **Given** the user opens `/`, **When** the page loads, **Then** the country table sorts by |Δ MW|, largest first, and the rows with a flag come before the rows without a flag.
2. **Given** a country with |Δ MW| at or above the threshold and a decrease (for example, `United Kingdom`, −10,332 MW), **When** the country table shows the country, **Then** the row shows the flag with the direction "down".
3. **Given** a country with |Δ MW| at or above the threshold and an increase (for example, `Pakistan`, +7,418 MW), **When** the country table shows the country, **Then** the row shows the flag with the direction "up".
4. **Given** a country with |Δ MW| below the threshold (for example, `Kazakhstan`, +28 MW), **When** the country table shows the country, **Then** the row does not show the flag.
5. **Given** the user is on `/`, **When** the user clicks a column header, **Then** the table sorts by that column as before, and the flags stay on the same countries.

---

### User Story 2 - See the plants that caused the change of a flagged country (Priority: P2)

The analyst opens a flagged country from the overview. The country page shows the flag and the reason. The plant table sorts by the size of the plant change at page load, so the plants that caused the country change are the first rows.

**Why this priority**: The analyst needs the plant names to write the note. The data is already on the country page, but the analyst must sort it manually. This story depends on the flag of story 1 only for the header; the default sort gives value without it.

**Independent Test**: Open `/country/United Kingdom`. Make sure that the page shows the flag and that the first rows of the plant table are the plants with the largest |plant Δ MW|.

**Acceptance Scenarios**:

1. **Given** the user opens the page of a flagged country (for example, `/country/United Kingdom`), **When** the page loads, **Then** the page shows the flag, the direction and the country Δ MW near the country KPIs.
2. **Given** the user opens `/country/United Kingdom`, **When** the page loads, **Then** the plant table sorts by |plant Δ MW|, largest first, and the first row is `Drax power station` (−2,640 MW).
3. **Given** two plants with the same |plant Δ MW| (for example, `Cottam power station` and `Fiddler's Ferry power station`, both −2,000 MW), **When** the plant table sorts by |plant Δ MW|, **Then** the plants sort by name.
4. **Given** the user opens the page of a country that is not flagged (for example, `/country/Kazakhstan`), **When** the page loads, **Then** the page does not show the flag, and the plant table uses the same default sort.

---

### User Story 3 - Show only the flagged countries (Priority: P3)

The analyst wants a short list for the quarterly note. A control on the overview hides the countries that are not flagged. The analyst can show all countries again.

**Why this priority**: Story 1 already puts the flagged countries first. This filter makes the list shorter, but it is not necessary for the main task.

**Independent Test**: On `/`, turn on the filter. Make sure that the table shows only the flagged countries and that the count is correct. Turn off the filter. Make sure that the table shows all countries.

**Acceptance Scenarios**:

1. **Given** the user is on `/`, **When** the user turns on "Flagged only", **Then** the country table shows only the flagged countries, and the table subtitle shows their count.
2. **Given** the filter is on, **When** the user turns it off, **Then** the country table shows all countries again.
3. **Given** the filter is on, **When** the page loads again, **Then** the filter is off (see FR-010).

---

### Edge Cases

- A country with |Δ MW| equal to the threshold is flagged. The comparison is "at or above".
- A country with a large snapshot change but a small comparable change (large coverage change) is not flagged. The flag uses Δ MW only, never `mw_2023 - mw_2017` or coverage MW.
- A country with `cmp_2017 = 0` and `cmp_2023 > 0` ("new", for example, `Panama`) is flagged if `cmp_2023` is at or above the threshold. Δ % is null for this country, so the rule must not use Δ %.
- A country that is "phased out" (for example, `Portugal`, −1,878 MW) is flagged only if |Δ MW| is at or above the threshold.
- A country with Δ MW = 0 (trend `flat`) is never flagged.
- A flagged country can have plants that changed in the opposite direction (for example, `United Kingdom` has 7 plants that shrank or retired and 2 plants that grew). The plant table shows both directions. It does not hide plants.
- Plants with the change `coverage` have plant Δ MW = 0. They go to the end of the default sort.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST flag a country when |Δ MW| is at or above the threshold. Δ MW is `cmp_2023 - cmp_2017` (base spec section 3).
- **FR-002**: The threshold MUST be one fixed value for all countries: [NEEDS CLARIFICATION: threshold value not specified. Proposal: 5,000 MW. With the current data, 5,000 MW flags 13 countries, and 1,000 MW flags 32 countries. A rule that also needs |Δ %| ≥ 25 % flags 21 countries but does not flag `China` (+192,254 MW, +21.5 %) or `India`, which are the two largest increases.]
- **FR-003**: The flag MUST give the direction: "up" for Δ MW > 0, "down" for Δ MW < 0.
- **FR-004**: `GET /api/countries` and `GET /api/countries/{name}` MUST return the field `flagged` (boolean) for each country. The UI MUST use this field and MUST NOT calculate the flag again.
- **FR-005**: The overview country table MUST show the flag on each flagged country, with its direction.
- **FR-006**: At page load, the overview country table MUST sort by |Δ MW|, largest first. The user can sort by other columns as before (base spec AC-UI-2).
- **FR-007**: The country page MUST show the flag, the direction and Δ MW near the country KPIs when the country is flagged.
- **FR-008**: At page load, the country plant table MUST sort by |plant Δ MW| (`|cmp23 - cmp17|`), largest first, then by plant name. This applies to all countries, flagged or not.
- **FR-009**: The overview MUST have a "Flagged only" control that shows only the flagged countries in the country table.
- **FR-010**: The "Flagged only" control MUST be off at page load. The app does not keep its value in the URL (base spec section 10: no URL state).
- **FR-011**: The flag MUST NOT change the KPIs, the bar chart or the map.
- **FR-012**: The change legend in the sidebar MUST explain the flag: "Flagged: comparable change of [threshold] MW or more, up or down."

### Key Entities *(include if feature involves data)*

- **Country flag**: A property of a country. It is true when |Δ MW| is at or above the threshold. It has a direction (up or down) that is the same as the country trend. The API calculates it from the existing country totals. The ETL and the database do not change.
- **Flag threshold**: One value in MW. It is the same for all countries and all users.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At page load of `/`, all flagged countries are in the first rows of the country table, with no click.
- **SC-002**: From the overview, the analyst opens a flagged country and reads its 3 plants with the largest change in 2 clicks or fewer, with no column sort.
- **SC-003**: The analyst makes the list of flagged countries and their top 3 plants in less than 10 minutes. Today the analyst reads all 82 countries row by row.
- **SC-004**: The flag count in the UI is equal to the number of countries with `flagged = true` in `GET /api/countries`.
- **SC-005**: `npx moon run :test :lint :build` passes (base spec AC-GEN-2).

## Assumptions

- The analyst is the only target user. The threshold is fixed. A threshold that the user can change is out of scope.
- "Large change" means a large absolute change in comparable MW. The analyst writes about where capacity "moved the most", so an absolute rule fits better than a rule with Δ %. A small country with a large Δ % and a small Δ MW (for example, `Senegal`, +125 MW, +416.7 %) is not flagged.
- The flag uses comparable capacity only, as the issue says. Coverage change is not a real change (base spec section 4.6).
- "Which plants caused the change" means the plants with the largest |plant Δ MW|. The spec does not add a share or a contribution percentage for each plant, because plants with opposite directions make a share hard to read.
- The plant table already lists the plants of the country with their change (base spec section 6.3 and AC-UI-7). This feature changes only its default sort.
- The data has two releases only (2017 and 2023). "Every quarter" is the analyst's writing schedule. It does not mean new data each quarter.
- Tests follow base spec section 8: pytest for the API field `flagged`; `build` and `lint` for the frontend.
- Out of scope: a flag on the map or on the bar chart, a flag for plants, alerts or notifications, data export of the flagged list.
