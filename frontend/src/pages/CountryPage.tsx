import { useParams } from 'react-router'
import { countryApi, type CountryDetail } from '../api/countries'
import { countryMapPlantsApi } from '../api/plants'
import Breadcrumb from '../components/Breadcrumb'
import KpiTiles from '../components/KpiTiles'
import { LoadError, Loading, NotFound } from '../components/PageStatus'
import PlantMapCard from '../components/PlantMapCard'
import PlantTable from '../components/PlantTable'
import { useApi } from '../useApi'

export default function CountryPage() {
  const name = useParams().name ?? ''
  const country = useApi<CountryDetail>(countryApi(name))

  if (country.status === 'not-found') return <NotFound />

  return (
    <>
      <Breadcrumb items={[{ label: 'Overview', to: '/' }, { label: name }]} />
      <h1 className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">{name}</h1>
      <div className="mt-6 space-y-6">
        {country.status === 'loading' && <Loading />}
        {country.status === 'error' && <LoadError message={country.message} />}
        {country.status === 'ok' && (
          <>
            <KpiTiles countries={[country.data]} />
            <PlantMapCard
              api={countryMapPlantsApi(name)}
              title={`Plants in ${name}`}
              subtitle="The map zooms to the plants of this country."
              height="clamp(300px, 50vh, 420px)"
              fitToPlants
            />
            <PlantTable plants={country.data.plants} />
          </>
        )}
      </div>
    </>
  )
}
