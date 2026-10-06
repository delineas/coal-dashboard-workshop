import type { Country } from '../api/countries'
import { formatGw, formatPctChange, formatSignedGw } from '../format'

function sum(countries: Country[], key: keyof Omit<Country, 'name' | 'pct_change' | 'trend'>): number {
  return countries.reduce((total, c) => total + c[key], 0)
}

function Tile({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <p className="text-xs font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
      {detail && <p className="mt-0.5 text-sm text-gray-500 tabular-nums">{detail}</p>}
    </div>
  )
}

export default function KpiTiles({ countries }: { countries: Country[] }) {
  const cmp2017 = sum(countries, 'cmp_2017')
  const cmp2023 = sum(countries, 'cmp_2023')
  const pctChange = cmp2017 > 0 ? ((cmp2023 - cmp2017) * 100) / cmp2017 : null

  return (
    <section>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Tile label="Operating 2017" value={formatGw(sum(countries, 'mw_2017'))} />
        <Tile label="Operating 2023" value={formatGw(sum(countries, 'mw_2023'))} />
        <Tile
          label="Δ (comparable units)"
          value={formatSignedGw(sum(countries, 'delta_mw'))}
          detail={formatPctChange({ pct_change: pctChange, cmp_2023: cmp2023 })}
        />
        <Tile label="Tracker coverage change" value={formatSignedGw(sum(countries, 'coverage_mw'))} />
      </div>
      <p className="mt-2 text-sm text-gray-500">
        Δ compares only units that both releases can compare. Coverage shows units that GEM added to or removed from
        the tracker.
      </p>
    </section>
  )
}
