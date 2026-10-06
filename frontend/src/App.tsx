import { useEffect, useState } from 'react'
import { fetchCountries, type Country } from './api/countries'
import { formatMw, formatPctChange, formatSignedMw, trendSymbol } from './format'

export default function App() {
  const [countries, setCountries] = useState<Country[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCountries()
      .then(setCountries)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main className="mx-auto max-w-4xl p-6 text-gray-900">
      <h1 className="text-2xl font-semibold">Operating coal capacity, 2017 vs 2023</h1>
      {error && <p className="mt-4 text-red-700">{error}</p>}
      {!countries && !error && <p className="mt-4 text-gray-500">Loading…</p>}
      {countries && (
        <table className="mt-6 w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500">
              <th className="py-2">Country</th>
              <th className="py-2 text-right">MW 2017</th>
              <th className="py-2 text-right">MW 2023</th>
              <th className="py-2 text-right">Δ MW</th>
              <th className="py-2 text-right">Δ %</th>
              <th className="py-2 text-right">Coverage</th>
              <th className="py-2 text-center">Trend</th>
            </tr>
          </thead>
          <tbody>
            {countries.map((c) => (
              <tr key={c.name} className="border-b border-gray-100">
                <td className="py-1.5">{c.name}</td>
                <td className="py-1.5 text-right tabular-nums">{formatMw(c.mw_2017)}</td>
                <td className="py-1.5 text-right tabular-nums">{formatMw(c.mw_2023)}</td>
                <td className="py-1.5 text-right tabular-nums">{formatSignedMw(c.delta_mw)}</td>
                <td className="py-1.5 text-right tabular-nums">{formatPctChange(c)}</td>
                <td className="py-1.5 text-right tabular-nums">{formatSignedMw(c.coverage_mw)}</td>
                <td className="py-1.5 text-center">{trendSymbol[c.trend]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}
