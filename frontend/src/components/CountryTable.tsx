import { Link } from 'react-router'
import { countriesCsvApi, countryPath, type Country } from '../api/countries'
import { formatMw, formatPctChange, formatSignedMw, trendSymbol } from '../format'
import Card from './Card'
import SortableTable, { type Column } from './SortableTable'

const columns: Column<Country>[] = [
  {
    key: 'name',
    label: 'Country',
    sortValue: (c) => c.name,
    render: (c) => (
      <Link to={countryPath(c.name)} className="font-medium text-zinc-900 hover:text-brand-600">
        {c.name}
      </Link>
    ),
  },
  { key: 'mw_2017', label: 'MW 2017', align: 'right', sortValue: (c) => c.mw_2017, render: (c) => formatMw(c.mw_2017) },
  { key: 'mw_2023', label: 'MW 2023', align: 'right', sortValue: (c) => c.mw_2023, render: (c) => formatMw(c.mw_2023) },
  {
    key: 'delta_mw',
    label: 'Δ MW',
    align: 'right',
    sortValue: (c) => c.delta_mw,
    render: (c) => formatSignedMw(c.delta_mw),
  },
  { key: 'pct_change', label: 'Δ %', align: 'right', sortValue: (c) => c.pct_change, render: formatPctChange },
  {
    key: 'coverage_mw',
    label: 'Coverage',
    align: 'right',
    sortValue: (c) => c.coverage_mw,
    render: (c) => formatSignedMw(c.coverage_mw),
  },
  { key: 'trend', label: 'Trend', align: 'center', sortValue: (c) => c.delta_mw, render: (c) => trendSymbol[c.trend] },
]

export default function CountryTable({ countries }: { countries: Country[] }) {
  return (
    <Card title="Countries" subtitle="Click a column to sort. Click a country to open it.">
      <SortableTable columns={columns} rows={countries} rowKey={(c) => c.name} />
      {/* shortcut: the link sits under the table because Card has no header action slot; add one to Card when a second card needs a button. */}
      <div className="border-t border-zinc-100 px-4 py-3 text-right sm:px-5">
        <a href={countriesCsvApi} download className="text-xs font-medium text-brand-600 hover:text-brand-700">
          Download CSV
        </a>
      </div>
    </Card>
  )
}
