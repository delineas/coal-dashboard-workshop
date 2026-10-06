import { useEffect, useState } from 'react'
import { fetchCountries, type Country } from './api/countries'
import AppShell from './components/AppShell'
import CountryTable from './components/CountryTable'
import DeltaBarChart from './components/DeltaBarChart'
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
          <div className="grid gap-4 sm:gap-6 xl:grid-cols-5">
            <div className="min-w-0 xl:col-span-3">
              <CountryTable countries={countries} />
            </div>
            <div className="min-w-0 xl:col-span-2">
              <DeltaBarChart countries={countries} />
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}
