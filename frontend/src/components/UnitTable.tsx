import { notComparableReason, type PlantUnit } from '../api/plants'
import { formatMw } from '../format'
import Card from './Card'
import SortableTable, { type Column } from './SortableTable'

function Status({ status }: { status: string | null }) {
  if (status === null) return <span className="text-zinc-400 italic">not tracked</span>
  const tone =
    status === 'operating' ? 'bg-emerald-50 text-emerald-700' : status === 'retired' ? 'bg-sky-50 text-sky-700' : 'bg-zinc-100 text-zinc-600'
  return <span className={`rounded-md px-1.5 py-0.5 text-xs font-medium ${tone}`}>{status}</span>
}

const columns: Column<PlantUnit>[] = [
  { key: 'name', label: 'Unit', sortValue: (u) => u.name, render: (u) => u.name },
  { key: 'mw', label: 'MW', align: 'right', sortValue: (u) => u.mw, render: (u) => formatMw(u.mw) },
  {
    key: 'status_2017',
    label: 'Status 2017',
    sortValue: (u) => u.status_2017,
    render: (u) => <Status status={u.status_2017} />,
  },
  {
    key: 'status_2023',
    label: 'Status 2023',
    sortValue: (u) => u.status_2023,
    render: (u) => <Status status={u.status_2023} />,
  },
  { key: 'start_year', label: 'Start year', sortValue: (u) => u.start_year, render: (u) => u.start_year || '—' },
  { key: 'retired_year', label: 'Retired year', sortValue: (u) => u.retired_year, render: (u) => u.retired_year || '—' },
  { key: 'technology', label: 'Technology', sortValue: (u) => u.technology, render: (u) => u.technology || '—' },
  {
    key: 'comparable',
    label: 'Comparable',
    sortValue: (u) => (u.comparable ? 'yes' : 'no'),
    render: (u) =>
      u.comparable ? (
        'yes'
      ) : (
        <span title={notComparableReason(u)} className="cursor-help underline decoration-dotted underline-offset-2">
          no
        </span>
      ),
  },
]

export default function UnitTable({ units }: { units: PlantUnit[] }) {
  return (
    <Card title="Units" subtitle="Hover “no” in the Comparable column to see the reason.">
      <SortableTable columns={columns} rows={units} rowKey={(u) => u.tracker_id} />
    </Card>
  )
}
