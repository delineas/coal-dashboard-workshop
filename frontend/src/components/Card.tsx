import type { ReactNode } from 'react'

export default function Card({ title, subtitle, children }: { title?: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className="min-w-0 rounded-xl border border-zinc-200 bg-white shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
      {title && (
        <div className="border-b border-zinc-100 px-4 pt-4 pb-3 sm:px-5">
          <h2 className="text-sm font-semibold">{title}</h2>
          {subtitle && <p className="mt-0.5 text-xs text-zinc-500">{subtitle}</p>}
        </div>
      )}
      {children}
    </section>
  )
}
