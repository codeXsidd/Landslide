"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle, FileSearch, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function SelfQuestioningPanel() {
  const [step, setStep] = useState(0);

  const simulateProgress = () => {
    if (step < 2) setStep(s => s + 1);
  };

  return (
    <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 className="title-gradient" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <HelpCircle size={20} color="var(--accent-amber)" />
          Self-Questioning Engine
        </h3>
        <button 
          onClick={simulateProgress}
          disabled={step >= 2}
          style={{
            background: 'var(--accent-cyan)', color: '#000', border: 'none', 
            padding: '4px 12px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600,
            cursor: step >= 2 ? 'not-allowed' : 'pointer', opacity: step >= 2 ? 0.5 : 1
          }}
        >
          Next Step
        </button>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative' }}>
        
        {/* Step 0: Uncertainty Detection */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
          style={{ background: 'rgba(245, 158, 11, 0.1)', borderLeft: '3px solid var(--accent-amber)', padding: '1rem', borderRadius: '0 8px 8px 0' }}
        >
          <div style={{ fontSize: '0.85rem', color: 'var(--accent-amber)', marginBottom: '0.25rem', fontWeight: 600 }}>1. Uncertainty Detected</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>Risk is 82%, but confidence is 54%.</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            • Satellite data is <span style={{ color: 'var(--accent-rose)' }}>STALE</span> (9 days old)<br/>
            • Ground evidence is <span style={{ color: 'var(--accent-rose)' }}>MISSING</span>
          </div>
        </motion.div>

        {/* Step 1: Next-Best Action */}
        <AnimatePresence>
          {step >= 1 && (
            <motion.div 
              initial={{ opacity: 0, x: -20, height: 0 }} animate={{ opacity: 1, x: 0, height: 'auto' }}
              style={{ background: 'rgba(6, 182, 212, 0.1)', borderLeft: '3px solid var(--accent-cyan)', padding: '1rem', borderRadius: '0 8px 8px 0' }}
            >
              <div style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', marginBottom: '0.25rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileSearch size={14} /> 2. Next-Best-Evidence Strategy
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>Requested citizen verification for Road B.</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Decision Value: 0.92 (Very High)<br/>
                Reason: High-consequence area (Village X isolated if fails).
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step 2: Belief Update */}
        <AnimatePresence>
          {step >= 2 && (
            <motion.div 
              initial={{ opacity: 0, x: -20, height: 0 }} animate={{ opacity: 1, x: 0, height: 'auto' }}
              style={{ background: 'rgba(16, 185, 129, 0.1)', borderLeft: '3px solid var(--accent-emerald)', padding: '1rem', borderRadius: '0 8px 8px 0' }}
            >
              <div style={{ fontSize: '0.85rem', color: 'var(--accent-emerald)', marginBottom: '0.25rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={14} /> 3. Belief Update
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>Human Evidence (Report #184) verified via CV.</div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '4px', flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>New Risk</div>
                  <div style={{ color: 'var(--accent-rose)', fontWeight: 600 }}>88% <span style={{ fontSize: '0.7rem' }}>↑6%</span></div>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '4px', flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>New Confidence</div>
                  <div style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>91% <span style={{ fontSize: '0.7rem' }}>↑37%</span></div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
