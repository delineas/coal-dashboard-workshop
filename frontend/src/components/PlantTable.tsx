import type { PlantSummary } from '../api/countries'
import { formatMw, formatSignedMw } from '../format'
import Card from './Card'
import SortableTable, { type Column } from './SortableTable'

const columns: Column<PlantSummary>[] = [
  {
    key: 'name',
    label: 'Plant',
    sortValue: (p) => p.name,
    render: (p) => (
      <>
        <span className="font-medium text-zinc-900">{p.name}</span>
        {p.subnational_unit && <span className="block text-xs text-zinc-500">{p.subnational_unit}</span>}
      </>
    ),
  },
  { key: 'mw17', label: 'MW 2017', align: 'right', sortValue: (p) => p.mw17, render: (p) => formatMw(p.mw17) },
  { key: 'mw23', label: 'MW 2023', align: 'right', sortValue: (p) => p.mw23, render: (p) => formatMw(p.mw23) },
  {
    key: 'delta',
    label: 'Δ MW',
    align: 'right',
    sortValue: (p) => p.cmp23 - p.cmp17,
    render: (p) => formatSignedMw(p.cmp23 - p.cmp17),
  },
]

export default function PlantTable({ plants }: { plants: PlantSummary[] }) {
  return (
    <Card title="Plants" subtitle={`${plants.length.toLocaleString('en-US')} plants. Click a column to sort.`}>
      <SortableTable columns={columns} rows={plants} rowKey={(p) => p.id} />
    </Card>
  )
}
