// Characterization test: pins what formatPctChange returns TODAY. It does not say that this output is correct.
// It protects the Δ % labels while someone changes the rules (Refs #5). If a value changes on purpose, update it here.
import { expect, test } from 'vitest'
import { formatPctChange } from './format'

test.each([
  { pct_change: null, cmp_2023: 120, expected: 'new' },
  { pct_change: null, cmp_2023: 0, expected: 'not comparable' },
  { pct_change: -100, cmp_2023: 0, expected: 'phased out' },
  { pct_change: 12.345, cmp_2023: 500, expected: '+12.3 %' },
  { pct_change: -3.96, cmp_2023: 500, expected: '-4 %' },
  { pct_change: 0, cmp_2023: 500, expected: '0 %' },
  { pct_change: -0.04, cmp_2023: 500, expected: '0 %' },
  { pct_change: 250, cmp_2023: 500, expected: '+250 %' },
])('formatPctChange($pct_change, cmp_2023 $cmp_2023) returns "$expected"', ({ expected, ...country }) => {
  expect(formatPctChange(country)).toBe(expected)
})
