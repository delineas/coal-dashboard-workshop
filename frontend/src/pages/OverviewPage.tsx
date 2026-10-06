import { countriesApi, type Country } from '../api/countries'
import { mapPlantsApi, type MapPlant } from '../api/plants'
import Card from '../components/Card'
import CountryTable from '../components/CountryTable'
import DeltaBarChart from '../components/DeltaBarChart'
import KpiTiles from '../components/KpiTiles'
import { LoadError, Loading } from '../components/PageStatus'
import PlantMap from '../components/PlantMap'
import { useApi } from '../useApi'

export default function OverviewPage() {
  const countries = useApi<Country[]>(countriesApi)
  const plants = useApi<MapPlant[]>(mapPlantsApi)

  return (
    <>
      <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Operating coal capacity, 2017 vs 2023</h1>
      <div className="mt-6 space-y-6">
        {countries.status === 'loading' && <Loading />}
        {countries.status === 'error' && <LoadError message={countries.message} />}
        {countries.status === 'ok' && (
          <>
            <KpiTiles countries={countries.data} />
            <Card title="Coal plants worldwide" subtitle="Click a circle to see the plant.">
              {plants.status === 'ok' ? (
                <PlantMap plants={plants.data} height="clamp(320px, 55vh, 480px)" />
              ) : (
                <div className="p-5">{plants.status === 'error' ? <LoadError message={plants.message} /> : <Loading />}</div>
              )}
            </Card>
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
