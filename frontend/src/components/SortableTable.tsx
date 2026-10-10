import { useState, type ReactNode } from 'react'

export interface Column<T> {
  key: string
  label: string
  align?: 'left' | 'right' | 'center'
  sortValue: (row: T) => number | string | null
  render: (row: T) => ReactNode
}

type Direction = 'asc' | 'desc'

const alignClass = { left: 'text-left', right: 'text-right', center: 'text-center' }

function compare(a: number | string | null, b: number | string | null, direction: Direction): number {
  if (a === null || b === null) return a === b ? 0 : a === null ? 1 : -1
  const order = typeof a === 'number' && typeof b === 'number' ? a - b : String(a).localeCompare(String(b))
  return direction === 'asc' ? order : -order
}

export default function SortableTable<T>({
  columns,
  rows,
  rowKey,
}: {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string
}) {
  const [sort, setSort] = useState<{ key: string; direction: Direction } | null>(null)

  const sortColumn = columns.find((c) => c.key === sort?.key)
  const sortedRows =
    sort && sortColumn
      ? [...rows].sort((a, b) => compare(sortColumn.sortValue(a), sortColumn.sortValue(b), sort.direction))
      : rows

  function toggle(column: Column<T>) {
    if (sort?.key === column.key) {
      setSort({ key: column.key, direction: sort.direction === 'asc' ? 'desc' : 'asc' })
    } else {
      const firstValue = rows.map(column.sortValue).find((v) => v !== null)
      setSort({ key: column.key, direction: typeof firstValue === 'number' ? 'desc' : 'asc' })
    }
  }

  return (
    <div className="max-h-[560px] overflow-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-zinc-500">
            {columns.map((column) => {
              const active = sort?.key === column.key
              return (
                <th
                  key={column.key}
                  aria-sort={active ? (sort.direction === 'asc' ? 'ascending' : 'descending') : 'none'}
                  className={`sticky top-0 border-b border-zinc-200 bg-zinc-50 px-3 py-2.5 text-xs font-medium whitespace-nowrap sm:px-4 ${alignClass[column.align ?? 'left']}`}
                >
                  <button type="button" onClick={() => toggle(column)} className="hover:text-zinc-900">
                    {column.label}
                    <span className="ml-1 inline-block w-2">{active ? (sort.direction === 'asc' ? '▲' : '▼') : ''}</span>
                  </button>
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row) => (
            <tr key={rowKey(row)} className="border-b border-zinc-100 hover:bg-zinc-50/60">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`px-3 py-2 whitespace-nowrap tabular-nums sm:px-4 ${alignClass[column.align ?? 'left']}`}
                >
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
