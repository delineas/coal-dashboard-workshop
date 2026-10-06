# basecamp-tool

Empty starting point for a training exercise. The stack is connected end to end
and has no features: React + Tailwind frontend, FastAPI backend, SQLite database.
The page calls `GET /api/hello` and shows "Hello world".

## Setup

Backend (Python 3.11+):

    python3 -m venv .venv
    .venv/bin/pip install -e "backend[dev]"

Frontend and workspace tools (Node 20.19+, required by Vite 8):

    npm install
    cd frontend && npm install

## Monorepo

The repository is a [moon](https://moonrepo.dev) workspace with two projects:
`backend` and `frontend`. The workspace config is in `.moon/workspace.yml`. Each
project declares its tasks in its own `moon.yml`. Moon caches task results and
runs only what changed.

## Run

    npx moon run backend:dev
    npx moon run frontend:dev

Open http://localhost:5173

## Test

    npx moon run :test :lint :build
