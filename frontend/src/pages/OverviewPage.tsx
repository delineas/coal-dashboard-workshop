import { countriesApi, type Country } from '../api/countries'
import CountryTable from '../components/CountryTable'
import DeltaBarChart from '../components/DeltaBarChart'
import KpiTiles from '../components/KpiTiles'
import { LoadError, Loading } from '../components/PageStatus'
import { useApi } from '../useApi'

export default function OverviewPage() {
  const countries = useApi<Country[]>(countriesApi)

  return (
    <>
      <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Operating coal capacity, 2017 vs 2023</h1>
      <div className="mt-6 space-y-6">
        {countries.status === 'loading' && <Loading />}
        {countries.status === 'error' && <LoadError message={countries.message} />}
        {countries.status === 'ok' && (
          <>
            <KpiTiles countries={countries.data} />
            <div className="grid gap-4 sm:gap-6 xl:grid-cols-5">
              <div className="min-w-0 xl:col-span-3">
                <CountryTable countries={countries.data} />
              </div>
              <div className="min-w-0 xl:col-span-2">
                <DeltaBarChart countries={countries.data} />
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}
