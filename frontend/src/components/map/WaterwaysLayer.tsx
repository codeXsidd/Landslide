import { useEffect, useState } from 'react';
import { GeoJSON, LayerGroup } from 'react-leaflet';
import { mapApi } from '../../services/api';

interface WaterwayFeature {
  type: 'Feature';
  properties: {
    osm_id: number;
    name: string;
    waterway_type: string;
    source: string;
  };
  geometry: {
    type: 'LineString';
    coordinates: [number, number][];
  };
}

interface WaterwaysData {
  type: 'FeatureCollection';
  features: WaterwayFeature[];
  metadata?: {
    source: string;
    retrieval_timestamp: string;
    feature_count: number;
    warning?: string;
  };
}

const WATERWAY_STYLES: Record<string, { color: string; weight: number; opacity: number; dashArray?: string }> = {
  river: { color: '#2563eb', weight: 3, opacity: 0.8 },
  stream: { color: '#60a5fa', weight: 1.5, opacity: 0.6 },
  canal: { color: '#7c3aed', weight: 2, opacity: 0.7, dashArray: '5 3' },
};

function getStyle(feature: any) {
  const type = feature?.properties?.waterway_type || 'stream';
  return WATERWAY_STYLES[type] || WATERWAY_STYLES.stream;
}

interface Props {
  onStatusChange?: (status: 'loaded' | 'cached' | 'unavailable' | 'loading') => void;
}

export default function WaterwaysLayer({ onStatusChange }: Props) {
  const [data, setData] = useState<WaterwaysData | null>(null);

  useEffect(() => {
    let cancelled = false;
    onStatusChange?.('loading');

    mapApi.getWaterways()
      .then((res) => {
        if (cancelled) return;
        setData(res);
        const src = res?.metadata?.source;
        if (src === 'cached' || src === 'cached_fallback') {
          onStatusChange?.('cached');
        } else if (src === 'unavailable' || !res?.features?.length) {
          onStatusChange?.('unavailable');
        } else {
          onStatusChange?.('loaded');
        }
      })
      .catch(() => {
        if (!cancelled) onStatusChange?.('unavailable');
      });

    return () => { cancelled = true; };
  }, []);

  if (!data || !data.features?.length) return <LayerGroup />;

  const onEachFeature = (feature: any, layer: any) => {
    const props = feature.properties || {};
    const name = props.name || 'Unknown';
    const type = (props.waterway_type || 'waterway').charAt(0).toUpperCase() + (props.waterway_type || 'waterway').slice(1);
    const date = data.metadata?.retrieval_timestamp
      ? new Date(data.metadata.retrieval_timestamp).toLocaleDateString()
      : 'Unknown';

    layer.bindPopup(`
      <div style="font-family: system-ui; min-width: 160px;">
        <div style="font-weight: bold; font-size: 11px; color: #6b7280; text-transform: uppercase; margin-bottom: 4px;">River / Waterway</div>
        <div style="margin-bottom: 6px;">
          <div style="font-weight: 600; font-size: 14px; color: #1e293b;">${name}</div>
        </div>
        <div style="font-size: 12px; color: #475569; line-height: 1.6;">
          <div><strong>Type:</strong> ${type}</div>
          <div><strong>Source:</strong> OpenStreetMap</div>
          <div><strong>Data date:</strong> ${date}</div>
        </div>
      </div>
    `);
  };

  return (
    <GeoJSON
      data={data as any}
      style={getStyle}
      onEachFeature={onEachFeature}
    />
  );
}
