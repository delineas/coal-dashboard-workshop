# coal-dashboard

The dashboard compares operating coal capacity by country in 2017 and in 2023, with the details and a map of each plant. The data is the Global Coal Plant Tracker from Global Energy Monitor (GEM).

- Spec: [`docs/spec.md`](docs/spec.md)
- Plan: [`docs/plan.md`](docs/plan.md)
- Decisions: [`docs/decisions/`](docs/decisions/)

Stack: React + Tailwind frontend, FastAPI backend, SQLite database. The stack started as a copy of `basecamp-tool`.

## Setup

Backend (Python 3.11+):

    python3 -m venv .venv
    .venv/bin/pip install -e "backend[dev]"

Frontend and workspace tools (Node 20.19+, required by Vite 8):

    npm install
    cd frontend && npm install

## Monorepo

The repository is a [moon](https://moonrepo.dev) workspace with two projects: `backend` and `frontend`. The workspace config is in `.moon/workspace.yml`. Each project declares its tasks in its own `moon.yml`.

## Data

The ETL reads `data/*.csv` and writes `backend/coal.sqlite`. Git ignores the database file.

    npx moon run backend:etl

The tasks `backend:dev` and `backend:test` run the ETL first.

## Run

    npx moon run backend:dev
    npx moon run frontend:dev

Open http://localhost:5173

## Test

    npx moon run :test :lint :build
