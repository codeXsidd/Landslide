import { useState } from 'react';
import { decisionApi } from '../services/api';

const LOCATIONS = [
  { id: '1', name: 'Road B Corridor', risk: 'CRITICAL', risk_score: 88, confidence: 84, uncertainty: 16, exposure: 850, isolation: 72, harm: 0.91, action: 'Inspect Road B' },
  { id: '2', name: 'Village A Access', risk: 'CRITICAL', risk_score: 82, confidence: 79, uncertainty: 21, exposure: 1240, isolation: 64, harm: 0.85, action: 'Prepare Evacuation Route' },
  { id: '3', name: 'School Road C', risk: 'HIGH', risk_score: 71, confidence: 88, uncertainty: 12, exposure: 320, isolation: 45, harm: 0.72, action: 'Increase Monitoring' },
  { id: '4', name: 'NH-10 Section', risk: 'HIGH', risk_score: 66, confidence: 77, uncertainty: 23, exposure: 580, isolation: 38, harm: 0.65, action: 'Pre-position Response Team' },
];

const RISK_COLORS: Record<string, string> = {
  CRITICAL: 'text-rose-400',
  HIGH: 'text-amber-400',
  MODERATE: 'text-yellow-400',
  LOW: 'text-emerald-400',
};

export default function Decisions() {
  const [selected, setSelected] = useState<typeof LOCATIONS[0] | null>(null);
  const [reason, setReason] = useState('');
  const [decisionResult, setDecisionResult] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDecision = async (action: 'APPROVED' | 'REJECTED' | 'MODIFIED') => {
    if (!selected || !reason.trim()) {
      alert('Please enter a decision reason.');
      return;
    }
    setIsSubmitting(true);
    try {
      await decisionApi.humanReview({
        location_id: selected.id,
        decision: action,
        reason,
        decided_by: 'District Authority',
        timestamp: new Date().toISOString(),
      });
      setDecisionResult(`[REAL BACKEND] Decision recorded: ${action}. Reason: "${reason}"`);
    } catch (_err) {
      setDecisionResult(`[DEMO] ${action} logged locally. Reason: "${reason}"`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">Decision Priority</h2>
          <p className="text-gray-400 text-sm mt-1">AI-ranked locations requiring human authorization</p>
        </div>
        <span className="text-xs text-amber-400 border border-amber-500/30 bg-amber-900/20 px-2 py-1 rounded">HUMAN APPROVAL REQUIRED</span>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Priority table */}
        <div className="col-span-7 bg-zinc-900 rounded-xl border border-white/10 overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <h3 className="font-bold font-outfit">Priority Ranking</h3>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-white/10">
                <th className="text-left p-3">#</th>
                <th className="text-left p-3">Location</th>
                <th className="text-left p-3">Risk</th>
                <th className="text-left p-3">Conf.</th>
                <th className="text-left p-3">Exposure</th>
                <th className="text-left p-3">Recommended</th>
              </tr>
            </thead>
            <tbody>
              {LOCATIONS.map((loc, i) => (
                <tr key={loc.id} onClick={() => { setSelected(loc); setDecisionResult(null); setReason(''); }}
                  className={`border-b border-white/5 cursor-pointer transition-colors ${selected?.id === loc.id ? 'bg-cyan-900/20' : 'hover:bg-white/5'}`}>
                  <td className="p-3 font-mono text-gray-400">{i + 1}</td>
                  <td className="p-3 font-medium">{loc.name}</td>
                  <td className={`p-3 font-bold ${RISK_COLORS[loc.risk]}`}>{loc.risk}</td>
                  <td className="p-3 text-gray-300">{loc.confidence}%</td>
                  <td className="p-3 text-gray-300">{loc.exposure.toLocaleString()}</td>
                  <td className="p-3 text-cyan-400 text-xs">{loc.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Human Decision Panel */}
        <div className="col-span-5 space-y-4">
          {!selected ? (
            <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 flex items-center justify-center h-48">
              <p className="text-gray-400 text-sm">Select a location to review and decide.</p>
            </div>
          ) : (
            <>
              <div className="bg-zinc-900 rounded-xl border border-amber-500/30 p-5">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                  <h3 className="font-bold text-amber-400 uppercase text-sm tracking-wider">Human Decision Required</h3>
                </div>
                <p className="text-lg font-bold mb-1">{selected.name}</p>
                <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                  <div className="bg-zinc-950 p-3 rounded">
                    <p className="text-gray-400 text-xs">Risk</p>
                    <p className={`font-bold text-xl ${RISK_COLORS[selected.risk]}`}>{selected.risk_score}%</p>
                  </div>
                  <div className="bg-zinc-950 p-3 rounded">
                    <p className="text-gray-400 text-xs">Confidence</p>
                    <p className="font-bold text-xl text-emerald-400">{selected.confidence}%</p>
                  </div>
                </div>

                <div className="bg-zinc-950 p-3 rounded mb-4 text-sm">
                  <p className="text-cyan-400 font-bold text-xs mb-1">AI RECOMMENDATION</p>
                  <p>{selected.action}</p>
                  <p className="text-xs text-gray-400 mt-1">Expected Harm Reduction: {Math.round(selected.harm * 100)}%</p>
                </div>

                {decisionResult ? (
                  <div className="bg-emerald-900/30 border border-emerald-500/30 text-emerald-400 p-3 rounded text-sm">{decisionResult}</div>
                ) : (
                  <>
                    <div className="mb-3">
                      <label className="block text-xs text-gray-400 mb-1">Decision Reason (required)</label>
                      <input value={reason} onChange={e => setReason(e.target.value)} placeholder="Enter justification..."
                        className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-amber-500" />
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <button onClick={() => handleDecision('APPROVED')} disabled={isSubmitting}
                        className="py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded text-xs transition-colors">ACCEPT</button>
                      <button onClick={() => handleDecision('MODIFIED')} disabled={isSubmitting}
                        className="py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-bold rounded text-xs transition-colors">MODIFY</button>
                      <button onClick={() => handleDecision('REJECTED')} disabled={isSubmitting}
                        className="py-2 bg-rose-700 hover:bg-rose-600 disabled:opacity-50 text-white font-bold rounded text-xs transition-colors">REJECT</button>
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
