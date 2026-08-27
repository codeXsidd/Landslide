import React from 'react';
import dynamic from 'next/dynamic';
import RiskOverview from '@/components/dashboard/RiskOverview';
import SelfQuestioningPanel from '@/components/evidence/SelfQuestioningPanel';
import ApprovalTerminal from '@/components/decisions/ApprovalTerminal';

// Import Leaflet map dynamically to avoid SSR window errors
const GISMap = dynamic(() => import('@/components/map/GISMap'), { 
  ssr: false,
  loading: () => <div className="glass-panel" style={{ height: '100%', minHeight: '400px' }}>Loading Map...</div>
});

export default function DashboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 className="title-gradient" style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>NER-SAGE</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Self-Adaptive Geospatial Emergency Intelligence</p>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', background: 'rgba(6, 182, 212, 0.1)', padding: '0.5rem 1rem', borderRadius: '20px', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
          System Status: ACTIVE
        </div>
      </header>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '1.5rem', flex: 1, minHeight: 0 }}>
        
        {/* Left Column (Map & Overview) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ flex: '1 1 60%' }}>
            <GISMap />
          </div>
          <div style={{ flex: '1 1 40%' }}>
            <RiskOverview />
          </div>
        </div>

        {/* Right Column (Reasoning & Decisions) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ flex: '1 1 50%' }}>
            <SelfQuestioningPanel />
          </div>
          <div style={{ flex: '1 1 50%' }}>
            <ApprovalTerminal />
          </div>
        </div>

      </div>
    </div>
  );
}
