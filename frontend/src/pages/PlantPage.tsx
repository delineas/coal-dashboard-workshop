import { useParams } from 'react-router'
import { countryPath } from '../api/countries'
import { plantApi, type PlantDetail } from '../api/plants'
import Breadcrumb from '../components/Breadcrumb'
import Card from '../components/Card'
import ChangeBadge from '../components/ChangeBadge'
import { LoadError, Loading, NotFound } from '../components/PageStatus'
import { PlantLocationMap } from '../components/PlantMap'
import UnitTable from '../components/UnitTable'
import { formatMw, formatSignedMw } from '../format'
import { useApi } from '../useApi'

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-zinc-500">{label}</dt>
      <dd className="mt-0.5 truncate text-sm font-medium" title={value}>
        {value || '—'}
      </dd>
    </div>
  )
}

function PlantHeader({ plant }: { plant: PlantDetail }) {
  return (
    <Card>
      <div className="grid gap-4 p-4 sm:p-5">
        <dl className="grid grid-cols-2 gap-4">
          <Field label="Country" value={plant.country} />
          <Field label="Subnational unit" value={plant.subnational_unit} />
          <Field label="Owner" value={plant.owner} />
          <Field label="Parent" value={plant.parent} />
        </dl>
        <dl className="grid grid-cols-3 gap-4">
          <Field label="MW 2017" value={formatMw(plant.mw17)} />
          <Field label="MW 2023" value={formatMw(plant.mw23)} />
          <Field label="Δ MW (comparable)" value={formatSignedMw(plant.cmp23 - plant.cmp17)} />
        </dl>
      </div>
    </Card>
  )
}

export default function PlantPage() {
  const id = useParams().id ?? ''
  const plant = useApi<PlantDetail>(plantApi(id))

  if (plant.status === 'not-found') return <NotFound />
  if (plant.status === 'loading') return <Loading />
  if (plant.status === 'error') return <LoadError message={plant.message} />

  const { data } = plant
  return (
    <>
      <Breadcrumb
        items={[{ label: 'Overview', to: '/' }, { label: data.country, to: countryPath(data.country) }, { label: data.name }]}
      />
      <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">{data.name}</h1>
          {data.change ? (
            <ChangeBadge change={data.change} />
          ) : (
            <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600">Not operating</span>
          )}
        </div>
        {data.wiki_url && (
          <a
            href={data.wiki_url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
          >
            Open in GEM wiki
          </a>
        )}
      </div>
      <div className="mt-6 space-y-6">
        <div className="grid gap-4 sm:gap-6 lg:grid-cols-3">
          <div className="min-w-0 lg:col-span-2">
            <PlantHeader plant={data} />
          </div>
          <Card title="Location">
            {data.lat !== null && data.lon !== null ? (
              <PlantLocationMap lat={data.lat} lon={data.lon} mw={Math.max(data.mw17, data.mw23)} change={data.change} />
            ) : (
              <p className="p-5 text-sm text-zinc-500">Location unavailable</p>
            )}
          </Card>
        </div>
        <UnitTable units={data.units} />
      </div>
    </>
  )
}
