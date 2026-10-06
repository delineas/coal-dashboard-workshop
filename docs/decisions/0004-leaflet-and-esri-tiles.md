# 0004. Draw the map with react-leaflet and Esri World Light Gray tiles

- Status: accepted
- Date: 2026-10-06
- Reversible: yes. The tile provider is two constants in `PlantMap.tsx`. The map library is used only in `PlantMap.tsx` (and later in the cluster wrapper).

## Context

The spec asks for a plant map with Leaflet, react-leaflet and leaflet.markercluster (decided in the questions round). The spec named CARTO Positron tiles, but CARTO now returns an "API KEY REQUIRED" image for requests without a key. A check with `curl` gave the same watermark tile with and without a `localhost` referer. This was an open item of the spec.

## Decision

- Add `leaflet`, `react-leaflet` and `@types/leaflet`.
- Use the Esri "World Light Gray Base" tiles (`server.arcgisonline.com/.../Canvas/World_Light_Gray_Base`), with the attribution "Tiles © Esri — Esri, DeLorme, NAVTEQ". They need no key and have a light gray style like Positron, so the change colors stay clear.
- Draw plants as `CircleMarker` with `preferCanvas`, because about 2,900 SVG circles are slow.

## Consequences

- No API key and no `.env` file for the map.
- The Esri terms allow this use for development and non-commercial use with attribution. A commercial deployment needs an ArcGIS account or another provider. Deployment is out of scope.
- The bundle grows to about 784 kB (235 kB gzip).

## Alternatives

- CARTO with an API key: the original choice, but it needs an account and a secret.
- OpenStreetMap standard tiles: no key, but a colorful style that competes with the change colors, and a usage policy that forbids heavy use.
