import { changes, type Change } from '../change'

export default function ChangeBadge({ change }: { change: Change }) {
  const { label, fill, stroke, badge } = changes[change]
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${badge}`}>
      <span className="h-1.5 w-1.5 rounded-full border" style={{ background: fill, borderColor: stroke }} />
      {label}
    </span>
  )
}
