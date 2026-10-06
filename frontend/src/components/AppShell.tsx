import { useState, type ReactNode } from 'react'
import { Link, NavLink } from 'react-router'

export default function AppShell({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-zinc-50 font-sans text-zinc-900 antialiased lg:flex">
      <aside className="sticky top-0 z-[1000] border-b border-zinc-200 bg-white lg:h-screen lg:w-64 lg:shrink-0 lg:border-r lg:border-b-0">
        <div className="flex h-14 items-center justify-between px-4 lg:h-16 lg:px-5">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
              <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor" aria-hidden="true">
                <path d="M3 15h2V9H3v6Zm4 0h2V5H7v10Zm4 0h2v-4h-2v4Zm4 0h2V7h-2v8Z" />
              </svg>
            </span>
            <span className="leading-tight">
              <span className="block text-sm font-semibold">Coal Capacity</span>
              <span className="block text-[11px] text-zinc-500">2017 → 2023</span>
            </span>
          </Link>
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-expanded={menuOpen}
            aria-controls="sidebar-body"
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-200 px-2.5 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50 lg:hidden"
          >
            Menu
          </button>
        </div>
        <div
          id="sidebar-body"
          className={`${menuOpen ? 'flex' : 'hidden'} flex-col px-4 pb-5 lg:flex lg:h-[calc(100vh-4rem)] lg:overflow-y-auto lg:px-5`}
        >
          <nav className="mt-1">
            <NavLink
              to="/"
              end
              onClick={() => setMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center rounded-md px-2.5 py-2 text-sm font-medium ${isActive ? 'bg-brand-50 text-brand-700' : 'text-zinc-600 hover:bg-zinc-50'}`
              }
            >
              Overview
            </NavLink>
          </nav>
          <p className="mt-6 border-t border-zinc-100 pt-4 text-[11px] text-zinc-400 lg:mt-auto">
            Data: GEM, Jan 2017 and July 2023
          </p>
        </div>
      </aside>
      <main className="max-w-[1400px] min-w-0 flex-1 px-4 py-6 sm:px-6 lg:px-10 lg:py-8">{children}</main>
    </div>
  )
}
