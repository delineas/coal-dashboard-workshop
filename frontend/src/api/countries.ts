import type { Change } from '../change'

export type Trend = 'up' | 'down' | 'flat'

export interface Country {
  name: string
  mw_2017: number
  mw_2023: number
  cmp_2017: number
  cmp_2023: number
  delta_mw: number
  coverage_mw: number
  pct_change: number | null
  trend: Trend
}

export const countriesApi = '/api/countries'

export function countryApi(name: string): string {
  return `/api/countries/${encodeURIComponent(name)}`
}

export function countryPath(name: string): string {
  return `/country/${encodeURIComponent(name)}`
}

export interface PlantSummary {
  id: string
  name: string
  subnational_unit: string
  mw17: number
  mw23: number
  cmp17: number
  cmp23: number
  change: Change
}

export interface CountryDetail extends Country {
  plants: PlantSummary[]
}
