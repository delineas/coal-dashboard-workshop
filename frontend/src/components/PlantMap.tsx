import 'leaflet/dist/leaflet.css'
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
import { Link } from 'react-router'
import { plantPath, type MapPlant } from '../api/plants'
import { changes } from '../change'
import { formatMw } from '../format'
import ChangeLegend from './ChangeLegend'

const TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
const TILE_ATTRIBUTION = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'

function radius(mw: number): number {
  return 2 + Math.sqrt(mw) / 6
}

export default function PlantMap({ plants, height }: { plants: MapPlant[]; height: string }) {
  return (
    <div className="relative" style={{ height }}>
      <MapContainer
        center={[25, 60]}
        zoom={2}
        minZoom={2}
        preferCanvas
        scrollWheelZoom={false}
        className="h-full w-full rounded-b-xl bg-zinc-100"
      >
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} maxZoom={16} />
        {plants.map((p) => (
          <CircleMarker
            key={p.id}
            center={[p.lat, p.lon]}
            radius={radius(Math.max(p.mw17, p.mw23))}
            pathOptions={{
              color: changes[p.change].stroke,
              fillColor: changes[p.change].fill,
              fillOpacity: 0.85,
              weight: 1,
            }}
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
      </MapContainer>
      <div className="pointer-events-none absolute bottom-6 left-2 z-[400] rounded-md bg-white/90 px-3 py-2 shadow-sm">
        <ChangeLegend />
      </div>
    </div>
  )
}
