"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, AlertOctagon, Terminal } from 'lucide-react';

export default function ApprovalTerminal() {
  const [status, setStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  return (
    <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', background: 'rgba(9, 9, 11, 0.8)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
        <Terminal size={16} color="var(--text-secondary)" />
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>Decision Engine / Human-in-the-Loop</span>
      </div>

      <div style={{ flex: 1, fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--text-primary)' }}>
        <div style={{ color: 'var(--accent-rose)', marginBottom: '0.5rem' }}>CRITICAL ALERT: Road B Failure Imminent</div>
        <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Cascading impact: 850 residents in Village X will be isolated. Hospital Z access degraded.</div>
        
        <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '0.75rem', borderRadius: '4px', marginBottom: '1.5rem' }}>
          <div style={{ color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>RECOMMENDED INTERVENTIONS:</div>
          <div>1. Deploy immediate road inspection team</div>
          <div>2. Pre-position excavators at Junction Y</div>
          <div>3. Issue closure warning for Route B</div>
        </div>

        {status === 'PENDING' ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ color: 'var(--accent-amber)' }}>HUMAN OPERATOR AUTHORIZATION REQUIRED</div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button 
                onClick={() => setStatus('APPROVED')}
                style={{ flex: 1, padding: '0.5rem', background: 'var(--accent-emerald)', color: '#000', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: 'pointer' }}
              >
                APPROVE ACTIONS
              </button>
              <button 
                onClick={() => setStatus('REJECTED')}
                style={{ flex: 1, padding: '0.5rem', background: 'transparent', color: 'var(--accent-rose)', border: '1px solid var(--accent-rose)', borderRadius: '4px', fontWeight: 600, cursor: 'pointer' }}
              >
                REJECT
              </button>
            </div>
          </motion.div>
        ) : status === 'APPROVED' ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={16} /> ACTIONS DISPATCHED. AUDIT LOG UPDATED.
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertOctagon size={16} /> ACTIONS REJECTED BY OPERATOR.
          </motion.div>
        )}
      </div>
    </div>
  );
}
