export interface Country {
  name: string
  mw_2017: number
  mw_2023: number
}

export async function fetchCountries(): Promise<Country[]> {
  const response = await fetch('/api/countries')
  if (!response.ok) throw new Error(`API error ${response.status}`)
  return response.json()
}
