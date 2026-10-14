import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { countriesApi, countryPath, type Country } from '../api/countries'
import { matchesCountry } from '../search'
import { useApi } from '../useApi'

export default function CountrySearch({ onNavigate }: { onNavigate: () => void }) {
  const countries = useApi<Country[]>(countriesApi)
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const names = countries.status === 'ok' ? countries.data.map((c) => c.name).sort((a, b) => a.localeCompare(b)) : []
  const matches = names.filter((name) => matchesCountry(name, query))

  function open(name: string) {
    setQuery('')
    onNavigate()
    navigate(countryPath(name))
  }

  return (
    <div>
      <label htmlFor="country-search" className="text-[11px] font-semibold tracking-wider text-zinc-400 uppercase">
        Countries
      </label>
      <input
        id="country-search"
        type="search"
        value={query}
        placeholder="Search a country…"
        autoComplete="off"
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && matches.length > 0) open(matches[0])
        }}
        className="mt-2 w-full rounded-md border border-zinc-200 bg-zinc-50 px-2.5 py-2 text-sm placeholder:text-zinc-400 focus:border-brand-500 focus:bg-white focus:ring-2 focus:ring-brand-500/30 focus:outline-none"
      />
      <ul className="-mx-1 mt-2 max-h-64 overflow-y-auto text-sm">
        {matches.map((name) => (
          <li key={name}>
            <Link
              to={countryPath(name)}
              onClick={() => {
                setQuery('')
                onNavigate()
              }}
              className="block truncate rounded px-2 py-1 text-zinc-700 hover:bg-zinc-50 hover:text-zinc-900"
            >
              {name}
            </Link>
          </li>
        ))}
        {countries.status === 'ok' && matches.length === 0 && <li className="px-2 py-1 text-zinc-400">No match</li>}
      </ul>
    </div>
  )
}
