import 'leaflet/dist/leaflet.css'
import { latLngBounds } from 'leaflet'
import { useEffect, type ReactNode } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import { Link } from 'react-router'
import { plantPath, type MapPlant } from '../api/plants'
import { changes, type Change } from '../change'
import { formatMw } from '../format'
import ChangeLegend from './ChangeLegend'

const TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
const TILE_ATTRIBUTION = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'

function radius(mw: number): number {
  return 2 + Math.sqrt(mw) / 6
}

function FitToPlants({ plants }: { plants: MapPlant[] }) {
  const map = useMap()
  useEffect(() => {
    if (plants.length > 0) map.fitBounds(latLngBounds(plants.map((p) => [p.lat, p.lon])), { padding: [24, 24], maxZoom: 9 })
  }, [map, plants])
  return null
}

function pathOptions(change: Change | null) {
  const colors = change ? changes[change] : { fill: '#4f46e5', stroke: '#4f46e5' }
  return { color: colors.stroke, fillColor: colors.fill, fillOpacity: 0.85, weight: 1 }
}

function BaseMap({ center, zoom, children }: { center: [number, number]; zoom: number; children: ReactNode }) {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      minZoom={2}
      preferCanvas
      scrollWheelZoom={false}
      className="h-full w-full rounded-b-xl bg-zinc-100"
    >
      <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} maxZoom={16} />
      {children}
    </MapContainer>
  )
}

export function PlantLocationMap({ lat, lon, mw, change }: { lat: number; lon: number; mw: number; change: Change | null }) {
  return (
    <div style={{ height: 260 }}>
      <BaseMap center={[lat, lon]} zoom={8}>
        <CircleMarker center={[lat, lon]} radius={Math.max(6, radius(mw))} pathOptions={pathOptions(change)} />
      </BaseMap>
    </div>
  )
}

export default function PlantMap({
  plants,
  height,
  fitToPlants = false,
}: {
  plants: MapPlant[]
  height: string
  fitToPlants?: boolean
}) {
  return (
    <div className="relative" style={{ height }}>
      <BaseMap center={[25, 60]} zoom={2}>
        {fitToPlants && <FitToPlants plants={plants} />}
        {plants.map((p) => (
          <CircleMarker
            key={p.id}
            center={[p.lat, p.lon]}
            radius={radius(Math.max(p.mw17, p.mw23))}
            pathOptions={pathOptions(p.change)}
          >
            <Popup>
              <p className="font-semibold text-zinc-900">{p.name}</p>
              <p className="tabular-nums text-zinc-600">
                {formatMw(p.mw17)} MW → {formatMw(p.mw23)} MW
              </p>
              <Link to={plantPath(p.id)} className="font-medium">
                View plant →
              </Link>
            </Popup>
          </CircleMarker>
        ))}
      </BaseMap>
      <div className="pointer-events-none absolute bottom-6 left-2 z-[400] rounded-md bg-white/90 px-3 py-2 shadow-sm">
        <ChangeLegend />
      </div>
    </div>
  )
}
