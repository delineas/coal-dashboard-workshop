import type { Country } from './api/countries'

const mwFormat = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })
const signedMwFormat = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0, signDisplay: 'exceptZero' })
const pctFormat = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1, signDisplay: 'exceptZero' })

export function formatMw(value: number): string {
  return mwFormat.format(value)
}

export function formatSignedMw(value: number): string {
  return signedMwFormat.format(value)
}

export function formatPctChange(country: Pick<Country, 'pct_change' | 'cmp_2023'>): string {
  if (country.pct_change === null) return country.cmp_2023 > 0 ? 'new' : 'not comparable'
  if (country.cmp_2023 === 0) return 'phased out'
  return `${pctFormat.format(country.pct_change)} %`
}

export const trendSymbol = { up: '↑', down: '↓', flat: '=' } as const
