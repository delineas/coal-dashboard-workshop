# 0005. Cluster plants with leaflet.markercluster through one imperative layer component

- Status: accepted
- Date: 2026-10-06
- Reversible: yes. Only `PlantClusterLayer.tsx` uses the plugin. To remove clusters, render `CircleMarker` elements again in `PlantMap.tsx`.

## Context

The overview map shows about 2,900 plants. Without clusters, circles cover each other in China and India. The spec asks for leaflet.markercluster with a donut icon that shows the share of each change class.

## Decision

- Add `leaflet.markercluster` and `@types/leaflet.markercluster`. Do not add a React wrapper package: the available wrappers lag behind react-leaflet v5.
- `PlantClusterLayer` gets the map with `useMap()`, builds a `markerClusterGroup` with `L.circleMarker` layers in an effect, and removes the group in the effect cleanup. The change class goes in the marker options, and `iconCreateFunction` reads it to draw the donut.
- Popups use DOM elements. Their link calls the React Router `navigate`, so the app does not reload.
- The plugin uses the global `L` that Leaflet sets. `leaflet` must be imported before `leaflet.markercluster`.

## Consequences

- One rebuild of the cluster group each time the plant list or the map mode changes. With `chunkedLoading`, this is fast enough for about 2,900 plants.
- Popup content is plain DOM code, not JSX.
- Clusters end at zoom 9 (`disableClusteringAtZoom`), so single plants stay clickable.

## Alternatives

- `react-leaflet-cluster` or similar wrappers: less code, but one more dependency that must follow react-leaflet releases.
- Canvas circles without clusters: simpler, but the map is not readable at low zoom.
