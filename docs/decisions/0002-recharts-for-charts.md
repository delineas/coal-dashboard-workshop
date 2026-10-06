# 0002. Use Recharts for charts

- Status: accepted
- Date: 2026-10-06
- Reversible: yes, with low effort. One component (`DeltaBarChart`) uses Recharts.

## Context

The overview needs a diverging bar chart of Δ MW for the top 20 countries (spec section 6.3). The spec names Recharts in the stack.

## Decision

Add `recharts` to the frontend. Use it for the bar chart.

## Consequences

- The chart is declarative React code with a tooltip and labels.
- The production bundle grows from about 220 kB to about 580 kB (174 kB gzip). Vite shows its "chunks larger than 500 kB" warning. Lazy loading of routes can reduce the first load later if necessary.

## Alternatives

- Inline SVG without a library: no bundle cost, but more code for axes, labels and tooltips.
- A heavier library (ECharts, Plotly): more features than the dashboard needs.
