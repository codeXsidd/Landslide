"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Activity, Users } from 'lucide-react';

export default function RiskOverview() {
  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      <h3 className="title-gradient" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Activity size={20} color="var(--accent-cyan)" />
        System Overview
      </h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <motion.div 
          whileHover={{ y: -2 }}
          style={{ 
            background: 'rgba(255, 255, 255, 0.03)', 
            padding: '1rem', 
            borderRadius: '12px',
            border: '1px solid rgba(244, 63, 94, 0.2)',
            borderLeft: '4px solid var(--accent-rose)'
          }}
        >
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={14} color="var(--accent-rose)" />
            Critical Alerts
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>1</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-rose)', marginTop: '0.25rem' }}>Road B Corridor</div>
        </motion.div>

        <motion.div 
          whileHover={{ y: -2 }}
          style={{ 
            background: 'rgba(255, 255, 255, 0.03)', 
            padding: '1rem', 
            borderRadius: '12px',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderLeft: '4px solid var(--accent-emerald)'
          }}
        >
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={14} color="var(--accent-emerald)" />
            Pop. Protected
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>12.4k</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Across 18 villages</div>
        </motion.div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Network Connectivity</div>
        <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', overflow: 'hidden' }}>
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: '92%' }}
            transition={{ duration: 1, ease: 'easeOut' }}
            style={{ height: '100%', background: 'linear-gradient(to right, var(--accent-cyan), var(--accent-emerald))' }}
          />
        </div>
      </div>
    </div>
  );
}
