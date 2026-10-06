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

export async function fetchCountries(): Promise<Country[]> {
  const response = await fetch('/api/countries')
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}
