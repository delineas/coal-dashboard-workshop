// Unit test: checks one pure function alone, with no server and no browser.
// It protects the GW labels of the KPI tiles and the country table.
import { describe, expect, test } from 'vitest'
import { formatSignedGw } from './format'

describe('formatSignedGw', () => {
  test('converts MW to GW with one decimal and a sign', () => {
    expect(formatSignedGw(1500)).toBe('+1.5 GW')
    expect(formatSignedGw(-250)).toBe('-0.3 GW')
  })

  test('shows no sign for zero', () => {
    expect(formatSignedGw(0)).toBe('0.0 GW')
  })
})
