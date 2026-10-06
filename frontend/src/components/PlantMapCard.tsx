import type { MapPlant } from '../api/plants'
import { useApi } from '../useApi'
import Card from './Card'
import { LoadError, Loading } from './PageStatus'
import PlantMap from './PlantMap'

export default function PlantMapCard({
  api,
  title,
  subtitle,
  height,
  fitToPlants = false,
}: {
  api: string
  title: string
  subtitle: string
  height: string
  fitToPlants?: boolean
}) {
  const plants = useApi<MapPlant[]>(api)

  return (
    <Card title={title} subtitle={subtitle}>
      {plants.status === 'ok' ? (
        <PlantMap plants={plants.data} height={height} fitToPlants={fitToPlants} />
      ) : (
        <div className="p-5">{plants.status === 'error' ? <LoadError message={plants.message} /> : <Loading />}</div>
      )}
    </Card>
  )
}
