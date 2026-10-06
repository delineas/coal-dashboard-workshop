import { useParams } from 'react-router'
import { countryApi, type Country } from '../api/countries'
import Breadcrumb from '../components/Breadcrumb'
import KpiTiles from '../components/KpiTiles'
import { LoadError, Loading, NotFound } from '../components/PageStatus'
import { useApi } from '../useApi'

export default function CountryPage() {
  const name = useParams().name ?? ''
  const country = useApi<Country>(countryApi(name))

  if (country.status === 'not-found') return <NotFound />

  return (
    <>
      <Breadcrumb items={[{ label: 'Overview', to: '/' }, { label: name }]} />
      <h1 className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">{name}</h1>
      <div className="mt-6 space-y-6">
        {country.status === 'loading' && <Loading />}
        {country.status === 'error' && <LoadError message={country.message} />}
        {country.status === 'ok' && <KpiTiles countries={[country.data]} />}
      </div>
    </>
  )
}
