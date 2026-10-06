export type Change = 'new' | 'grew' | 'unchanged' | 'shrank' | 'retired' | 'coverage'

export const changes: Record<Change, { label: string; fill: string; stroke: string; badge: string }> = {
  new: { label: 'New', fill: '#c2410c', stroke: '#c2410c', badge: 'bg-orange-50 text-orange-700 ring-orange-200' },
  grew: { label: 'Grew', fill: '#fb923c', stroke: '#fb923c', badge: 'bg-orange-50 text-orange-600 ring-orange-100' },
  unchanged: { label: 'Unchanged', fill: '#a1a1aa', stroke: '#a1a1aa', badge: 'bg-zinc-100 text-zinc-600 ring-zinc-200' },
  shrank: { label: 'Shrank', fill: '#38bdf8', stroke: '#38bdf8', badge: 'bg-sky-50 text-sky-700 ring-sky-100' },
  retired: { label: 'Retired', fill: '#0369a1', stroke: '#0369a1', badge: 'bg-sky-50 text-sky-800 ring-sky-200' },
  coverage: {
    label: 'Tracker coverage change',
    fill: '#ffffff',
    stroke: '#71717a',
    badge: 'bg-white text-zinc-600 ring-zinc-300',
  },
}

export const changeOrder = Object.keys(changes) as Change[]
