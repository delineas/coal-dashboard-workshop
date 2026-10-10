import { Link } from 'react-router'
import type { PlantSummary } from '../api/countries'
import { plantPath } from '../api/plants'
import { formatMw, formatSignedMw } from '../format'
import { changeOrder } from '../change'
import Card from './Card'
import ChangeBadge from './ChangeBadge'
import SortableTable, { type Column } from './SortableTable'

const columns: Column<PlantSummary>[] = [
  {
    key: 'name',
    label: 'Plant',
    sortValue: (p) => p.name,
    render: (p) => (
      <>
        <Link to={plantPath(p.id)} className="font-medium text-zinc-900 hover:text-brand-600">
          {p.name}
        </Link>
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
  {
    key: 'change',
    label: 'Change',
    sortValue: (p) => changeOrder.indexOf(p.change),
    render: (p) => <ChangeBadge change={p.change} />,
  },
]

export default function PlantTable({ plants }: { plants: PlantSummary[] }) {
  return (
    <Card title="Plants" subtitle={`${plants.length.toLocaleString('en-US')} plants. Click a column to sort. Click a plant to see its units.`}>
      <SortableTable columns={columns} rows={plants} rowKey={(p) => p.id} />
    </Card>
  )
}
