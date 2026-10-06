import L from 'leaflet'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import { useNavigate } from 'react-router'
import { plantPath, type MapPlant } from '../api/plants'
import { changeOrder, changes, yearModeColor, type Change } from '../change'
import { formatMw } from '../format'

interface PlantMarker {
  plant: MapPlant
  radius: number
  change: Change | null
  color: { color: string; fillColor: string; fillOpacity: number; weight: number }
}

type PlantCircleOptions = L.CircleMarkerOptions & { change: Change | null }

function clusterSize(total: number): number {
  return total < 10 ? 30 : total < 100 ? 38 : 46
}

function donut(counts: Map<Change | null, number>, total: number, size: number): string {
  const r = size / 2 - 4
  const circumference = 2 * Math.PI * r
  let offset = 0
  const keys: (Change | null)[] = [...changeOrder, null]
  const arcs = keys
    .filter((key) => counts.has(key))
    .map((key) => {
      const length = (counts.get(key)! / total) * circumference
      const color = key ? changes[key].stroke : yearModeColor
      const arc = `<circle r="${r}" cx="${size / 2}" cy="${size / 2}" fill="none" stroke="${color}" stroke-width="6"
        stroke-dasharray="${length} ${circumference - length}" stroke-dashoffset="${-offset}"
        transform="rotate(-90 ${size / 2} ${size / 2})" />`
      offset += length
      return arc
    })
    .join('')
  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true">
    <circle r="${r + 3}" cx="${size / 2}" cy="${size / 2}" fill="white" stroke="#d4d4d8" stroke-width="1" />
    ${arcs}
    <text x="50%" y="50%" dy="0.35em" text-anchor="middle" font-size="11" font-weight="600" fill="#18181b">${total}</text>
  </svg>`
}

function clusterIcon(cluster: L.MarkerCluster): L.DivIcon {
  const markers = cluster.getAllChildMarkers() as unknown as L.CircleMarker[]
  const counts = new Map<Change | null, number>()
  for (const marker of markers) {
    const change = (marker.options as PlantCircleOptions).change
    counts.set(change, (counts.get(change) ?? 0) + 1)
  }
  const size = clusterSize(markers.length)
  return L.divIcon({ html: donut(counts, markers.length, size), className: 'plant-cluster', iconSize: [size, size] })
}

function popupContent(plant: MapPlant, navigate: (path: string) => void): HTMLElement {
  const content = document.createElement('div')
  const name = document.createElement('p')
  name.className = 'font-semibold text-zinc-900'
  name.textContent = plant.name
  const mw = document.createElement('p')
  mw.className = 'tabular-nums text-zinc-600'
  mw.textContent = `${formatMw(plant.mw17)} MW → ${formatMw(plant.mw23)} MW`
  const link = document.createElement('a')
  link.href = plantPath(plant.id)
  link.className = 'font-medium'
  link.textContent = 'View plant →'
  link.addEventListener('click', (event) => {
    event.preventDefault()
    navigate(plantPath(plant.id))
  })
  content.append(name, mw, link)
  return content
}

export default function PlantClusterLayer({ markers }: { markers: PlantMarker[] }) {
  const map = useMap()
  const navigate = useNavigate()

  useEffect(() => {
    const group = L.markerClusterGroup({
      iconCreateFunction: clusterIcon,
      showCoverageOnHover: false,
      chunkedLoading: true,
      maxClusterRadius: 45,
      disableClusteringAtZoom: 9,
      animate: false,
    })
    group.addLayers(
      markers.map(({ plant, radius, change, color }) =>
        L.circleMarker([plant.lat, plant.lon], { ...color, radius, change } as PlantCircleOptions).bindPopup(() =>
          popupContent(plant, navigate),
        ),
      ),
    )
    map.addLayer(group)
    return () => {
      map.removeLayer(group)
    }
  }, [map, markers, navigate])

  return null
}
