import { useEffect, useState } from 'react'
import { fetchCountries, type Country } from './api/countries'
import AppShell from './components/AppShell'
import CountryTable from './components/CountryTable'
import KpiTiles from './components/KpiTiles'

export default function App() {
  const [countries, setCountries] = useState<Country[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCountries()
      .then(setCountries)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <AppShell>
      <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Operating coal capacity, 2017 vs 2023</h1>
      {error && <p className="mt-4 text-red-700">{error}</p>}
      {!countries && !error && <p className="mt-4 text-zinc-500">Loading…</p>}
      {countries && (
        <div className="mt-6 space-y-6">
          <KpiTiles countries={countries} />
          <CountryTable countries={countries} />
        </div>
      )}
    </AppShell>
  )
}
