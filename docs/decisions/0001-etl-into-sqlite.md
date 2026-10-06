# 0001. Load the CSV data into SQLite with a build-time ETL

- Status: accepted
- Date: 2026-10-06
- Reversible: yes, with medium effort. The API reads only SQL tables. To change the storage, change the ETL output and the queries in `app/main.py`.

## Context

The data is two static CSV files (12,219 and 13,785 rows). The rules to match units across releases, to normalize countries and to classify change are complex. The API must answer in milliseconds, and the tests must find errors in the rules.

## Decision

- A Python script (`backend/app/etl.py`) reads `data/*.csv`, applies all data rules of the spec, and writes `backend/coal.sqlite`.
- The API only runs SQL queries on that file. It does not read the CSV files.
- The moon task `backend:etl` runs the script. `backend:dev` and `backend:test` depend on it. Git ignores the database file.

## Consequences

- All data rules are in one module that tests can run on small fixture files.
- The database is a build output. A change in the CSV files or in the ETL needs a new run of `backend:etl`. Moon does this automatically through the task inputs.
- The API tests use the real database, so they also check the real totals of the spec.

## Alternatives

- Read the CSV files into memory when the API starts: simpler, but the rules and the queries mix in the API code.
- A static JSON file for the frontend without a backend: no API to test, and the base project already has FastAPI and SQLite.
