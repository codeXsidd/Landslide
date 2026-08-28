import { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, LayersControl, LayerGroup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useAppStore } from '../../store/appStore';
import WaterwaysLayer from './WaterwaysLayer';

const RISK_LOCATIONS = [
  { id: 'LOC-TEST-001', lat: 27.3389, lng: 88.6065, name: 'Road B Corridor', risk: 'CRITICAL', color: '#f43f5e' },
  { id: 'LOC-TEST-002', lat: 27.5500, lng: 88.5000, name: 'Village A Access', risk: 'CRITICAL', color: '#f43f5e' },
  { id: 'LOC-TEST-003', lat: 27.1200, lng: 88.8000, name: 'School Road C', risk: 'HIGH', color: '#f59e0b' },
  { id: 'LOC-TEST-004', lat: 26.9000, lng: 88.4000, name: 'NH-10 Section', risk: 'HIGH', color: '#f59e0b' },
  { id: 'LOC-TEST-005', lat: 27.7000, lng: 89.0000, name: 'Bridge Point', risk: 'MODERATE', color: '#facc15' },
];

export default function MapComponent() {
  const { selectLocation, selectedLocationId } = useAppStore();
  const [hydStatus, setHydStatus] = useState<'loaded' | 'cached' | 'unavailable' | 'loading'>('loading');
  const center: [number, number] = [27.3, 88.6];

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={center}
        zoom={8}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="OpenStreetMap">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url='https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="Rivers / Waterways">
            <WaterwaysLayer onStatusChange={setHydStatus} />
          </LayersControl.Overlay>

          <LayersControl.Overlay checked name="Risk Locations">
            <LayerGroup>
              {RISK_LOCATIONS.map(loc => (
                <CircleMarker
                  key={loc.id}
                  center={[loc.lat, loc.lng]}
                  radius={selectedLocationId === loc.id ? 16 : 12}
                  pathOptions={{
                    color: loc.color,
                    fillColor: loc.color,
                    fillOpacity: 0.8,
                    weight: selectedLocationId === loc.id ? 3 : 1,
                  }}
                  eventHandlers={{
                    click: () => selectLocation({ id: loc.id, lat: loc.lat, lng: loc.lng, name: loc.name }),
                  }}
                >
                  <Popup>
                    <div className="font-sans text-gray-900 min-w-[140px]">
                      <div className="font-bold text-sm">{loc.name}</div>
                      <div className="text-xs mt-1">Risk: <strong style={{ color: loc.color }}>{loc.risk}</strong></div>
                      <div className="text-xs text-gray-500 mt-1">ID: {loc.id}</div>
                      <button
                        onClick={() => selectLocation({ id: loc.id, lat: loc.lat, lng: loc.lng, name: loc.name })}
                        className="mt-2 text-xs bg-cyan-600 text-white px-2 py-1 rounded w-full"
                      >
                        Load Risk Details
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
            </LayerGroup>
          </LayersControl.Overlay>
        </LayersControl>
      </MapContainer>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-black/85 backdrop-blur text-white text-[10px] p-3 rounded-lg border border-white/10 shadow-lg">
        <div className="font-bold text-[11px] mb-2 text-gray-300 uppercase tracking-wider">Risk</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-2.5 h-2.5 rounded-full bg-[#f43f5e]"></span> Critical</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></span> High</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-2.5 h-2.5 rounded-full bg-[#facc15]"></span> Moderate</div>
        <div className="flex items-center gap-2 mb-3"><span className="w-2.5 h-2.5 rounded-full bg-[#22c55e]"></span> Low</div>

        <div className="font-bold text-[11px] mb-2 text-gray-300 uppercase tracking-wider">Layers</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-4 h-[3px] bg-[#2563eb] rounded"></span> Rivers</div>
        <div className="flex items-center gap-2 mb-1"><span className="w-4 h-[1.5px] bg-[#60a5fa] rounded"></span> Streams</div>
        <div className="flex items-center gap-2"><span className="w-4 h-[2px] bg-[#7c3aed] rounded" style={{ borderBottom: '2px dashed #7c3aed' }}></span> Canals</div>
      </div>

      {/* Hydrography Status Badge */}
      <div className="absolute top-4 right-4 z-[1000]">
        {hydStatus === 'loaded' && (
          <span className="text-[10px] bg-blue-900/80 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded">OSM HYDROGRAPHY</span>
        )}
        {hydStatus === 'cached' && (
          <span className="text-[10px] bg-amber-900/80 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded">HYDROGRAPHY: CACHED</span>
        )}
        {hydStatus === 'unavailable' && (
          <span className="text-[10px] bg-gray-900/80 text-gray-400 border border-gray-500/30 px-2 py-0.5 rounded">HYDROGRAPHY: UNAVAILABLE</span>
        )}
        {hydStatus === 'loading' && (
          <span className="text-[10px] bg-gray-900/80 text-gray-400 border border-gray-500/30 px-2 py-0.5 rounded animate-pulse">LOADING WATERWAYS...</span>
        )}
      </div>
    </div>
  );
}
