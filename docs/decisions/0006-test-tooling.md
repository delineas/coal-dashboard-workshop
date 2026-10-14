# 0006. Add one tool for each type of test

- Status: accepted
- Date: 2026-10-14
- Reversible: yes, with low effort. Each tool is a dev dependency with its own test files. To remove a tool, remove the dependency and its files.

## Context

The backend has integration tests with pytest. The frontend has no tests (issue #5). The course shows each type of test with one real example in this repository.

## Decision

- Frontend unit and characterization tests: `vitest`. It reads `vite.config.ts`, so it needs no extra configuration.
- End-to-end tests: `@playwright/test`. Playwright starts the backend and the frontend servers itself.
- Property-based tests: `hypothesis` in the backend dev dependencies.
- Mutation tests: `mutmut` with a configuration in `backend/pyproject.toml`. It is not in the dev dependencies, because a person runs it by hand, not every test run.
- Architecture tests: no new tool. The backend uses `ast` from the standard library. The frontend uses `vitest` and `node:fs`.

## Consequences

- `npm test` in `frontend/` runs the unit, characterization, regression and architecture tests in less than a second.
- The end-to-end test needs a browser (`npx playwright install chromium`) and the database file (`moon run backend:etl`).
- The fitness and regression tests are expected failures (`xfail` / `test.fails`) until someone fixes issues #6 and #1.

## Alternatives

- Jest for the frontend: it needs a separate transform configuration for TypeScript and Vite.
- Cypress for end-to-end: heavier, and it does not start two servers as easily.
- dependency-cruiser for the frontend architecture rule: a new dependency for one rule that a short test can check.
