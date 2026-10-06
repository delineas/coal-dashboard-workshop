import { Link } from 'react-router'

export default function Breadcrumb({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-xs text-zinc-500">
      {items.map((item, i) => (
        <span key={item.label} className="flex items-center gap-1.5">
          {i > 0 && <span aria-hidden="true">›</span>}
          {item.to ? (
            <Link to={item.to} className="hover:text-zinc-900">
              {item.label}
            </Link>
          ) : (
            <span className="font-medium text-zinc-900">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
