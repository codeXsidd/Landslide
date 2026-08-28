"use client";

import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet SSR issues
const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="width: 16px; height: 16px; background-color: ${color}; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px ${color}"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });
};

const pulseIcon = L.divIcon({
  className: 'marker-high-risk',
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

export default function GISMap() {

  return (
    <div className="glass-panel" style={{ padding: 0, overflow: 'hidden', height: '100%', position: 'relative' }}>
      <MapContainer 
        center={[25.5781, 92.7123]} 
        zoom={12} 
        style={{ height: '100%', width: '100%', minHeight: '400px' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* Road B (High Risk) */}
        <Marker position={[25.5781, 92.7123]} icon={pulseIcon}>
          <Popup>
            <strong style={{ color: 'black' }}>Road B Corridor</strong><br/>
            <span style={{ color: '#f43f5e' }}>Risk: 88% (HIGH)</span>
          </Popup>
        </Marker>

        {/* Village X */}
        <Marker position={[25.5900, 92.7000]} icon={createCustomIcon('#06b6d4')}>
          <Popup>
            <strong style={{ color: 'black' }}>Village X</strong><br/>
            Pop: 850<br/>
            Status: At Risk of Isolation
          </Popup>
        </Marker>

        {/* Risk Radius */}
        <Circle 
          center={[25.5781, 92.7123]} 
          radius={1500} 
          pathOptions={{ color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.1, dashArray: '5, 10' }} 
        />
      </MapContainer>
      
      {/* Map Overlay Stats */}
      <div style={{
        position: 'absolute', top: '1rem', right: '1rem', zIndex: 400,
        background: 'rgba(9, 9, 11, 0.8)', padding: '1rem', borderRadius: '8px',
        border: '1px solid var(--border-subtle)', backdropFilter: 'blur(4px)'
      }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Active Monitored Zone</div>
        <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>Dima Hasao, Assam</div>
      </div>
    </div>
  );
}
