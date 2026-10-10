# 0003. Client-side routes with React Router and country names in URLs

- Status: accepted
- Date: 2026-10-06
- Reversible: partly. The router library is easy to change. The URL format (`/country/<name>`, `/plant/<id>`) is harder to change after people share links.

## Context

The spec defines three routes (`/`, `/country/:name`, `/plant/:id`) that people can share. The base project has one page and no router.

## Decision

- Add `react-router` and use `BrowserRouter` with path URLs (not hash URLs).
- Use the country name, URL-encoded, as the route parameter and as the API key (`/api/countries/{name}`).
- Load data per page with one small hook, `useApi(path)`, that gives `loading`, `ok`, `not-found` or `error`. A 404 from the API shows the "Not found" page.

## Consequences

- The Vite dev server returns `index.html` for unknown paths, so deep links work in development. A production host must do the same (deployment is out of scope).
- Country names with spaces, accents or apostrophes (`Côte d'Ivoire`, `Türkiye`) need URL encoding. `countryPath()` and `countryApi()` do this in one place.
- A rename of a country in a later GEM release breaks old links. An ISO code would be more stable, but the data has no ISO column.

## Alternatives

- Hash routes (`#/country/...`): work on any static host, but the URLs are less clean.
- ISO 3166 codes in URLs: more stable, but need a mapping table for about 110 names.
