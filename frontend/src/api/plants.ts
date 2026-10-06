import type { Change } from '../change'

export interface PlantUnit {
  tracker_id: string
  name: string
  mw: number
  status_2017: string | null
  status_2023: string | null
  start_year: string
  retired_year: string
  technology: string
  comparable: boolean
}

export interface PlantDetail {
  id: string
  name: string
  country: string
  subnational_unit: string
  owner: string
  parent: string
  lat: number | null
  lon: number | null
  wiki_url: string
  mw17: number
  mw23: number
  cmp17: number
  cmp23: number
  change: Change | null
  units: PlantUnit[]
}

export function plantApi(id: string): string {
  return `/api/plants/${encodeURIComponent(id)}`
}

export function plantPath(id: string): string {
  return `/plant/${encodeURIComponent(id)}`
}

export function notComparableReason(unit: PlantUnit): string {
  if (unit.status_2017 === null) {
    const start = unit.start_year ? `It started in ${unit.start_year}` : 'It has no start year'
    return `GEM added this unit to the tracker after 2017. ${start}, so its 2017 status is unknown.`
  }
  return 'GEM removed this unit from the tracker after 2017. Its 2023 status is unknown.'
}
