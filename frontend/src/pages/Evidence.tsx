import { useState } from 'react';
import { evidenceApi } from '../services/api';

const EVIDENCE_SOURCES = [
  { source: 'Rainfall', status: 'KNOWN', freshness: '7-day prototype', reliability: 'HIGH', note: 'DATA LIMITED' },
  { source: 'Terrain', status: 'KNOWN', freshness: 'SRTM (partial)', reliability: 'HIGH', note: 'PARTIAL COVERAGE' },
  { source: 'Historical', status: 'KNOWN', freshness: 'Archive', reliability: 'HIGH', note: '' },
  { source: 'Satellite', status: 'STALE', freshness: '9 days old', reliability: 'LOW', note: 'SIMULATED' },
  { source: 'Citizen', status: 'MISSING', freshness: 'N/A', reliability: 'N/A', note: 'SIMULATED' },
  { source: 'Official', status: 'UNKNOWN', freshness: 'N/A', reliability: 'N/A', note: '' },
];

const STATUS_COLORS: Record<string, string> = {
  KNOWN: 'text-emerald-400 border-emerald-500/30 bg-emerald-900/20',
  STALE: 'text-amber-400 border-amber-500/30 bg-amber-900/20',
  MISSING: 'text-rose-400 border-rose-500/30 bg-rose-900/20',
  UNKNOWN: 'text-gray-400 border-gray-500/30 bg-gray-900/20',
  UNCERTAIN: 'text-yellow-400 border-yellow-500/30 bg-yellow-900/20',
  CONFLICTING: 'text-orange-400 border-orange-500/30 bg-orange-900/20',
};

export default function Evidence() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<string | null>(null);

  const handleRequestVerification = async () => {
    setIsSubmitting(true);
    setSubmitResult(null);
    try {
      await evidenceApi.submit({
        location_id: 'LOC-TEST-001',
        source: 'CITIZEN',
        source_type: 'citizen_report',
        evidence_type: 'ROAD_CONDITION',
        is_simulated: true,
        notes: 'Demo verification request from frontend',
      });
      setSubmitResult('[REAL BACKEND] Verification request submitted. Awaiting field response.');
    } catch (_err) {
      setSubmitResult('[DEMO] Backend unavailable — verification request logged locally.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">Evidence Intelligence</h2>
          <p className="text-gray-400 text-sm mt-1">What the system knows — and what it does not know</p>
        </div>
        <div className="flex gap-2 items-center">
          <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-2 py-1 rounded">SIMULATED SOURCES PRESENT</span>
          <span className="text-xs text-amber-400 border border-amber-500/30 bg-amber-900/20 px-2 py-1 rounded">DATA LIMITED</span>
        </div>
      </div>

      {/* "What the system does not know" — signature feature */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        {['KNOWN', 'UNKNOWN', 'UNCERTAIN', 'STALE', 'CONFLICTING'].map(cat => (
          <div key={cat} className={`p-3 rounded-xl border text-center ${STATUS_COLORS[cat] || 'text-gray-400 border-gray-500/30 bg-gray-900/20'}`}>
            <div className="text-xs font-bold tracking-wider">{cat}</div>
            <div className="text-2xl font-bold mt-1">
              {cat === 'KNOWN' ? 3 : cat === 'STALE' ? 1 : cat === 'UNKNOWN' ? 2 : cat === 'CONFLICTING' ? 1 : 0}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Evidence sources table */}
        <div className="bg-zinc-900 rounded-xl border border-white/10 overflow-hidden">
          <div className="p-4 border-b border-white/10">
            <h3 className="font-bold text-lg font-outfit">Evidence Sources</h3>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase text-gray-500 border-b border-white/10">
                <th className="text-left p-3">Source</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Freshness</th>
                <th className="text-left p-3">Flag</th>
              </tr>
            </thead>
            <tbody>
              {EVIDENCE_SOURCES.map(ev => (
                <tr key={ev.source} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="p-3 font-medium">{ev.source}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold border ${STATUS_COLORS[ev.status] || ''}`}>
                      {ev.status}
                    </span>
                  </td>
                  <td className="p-3 text-gray-400 text-xs">{ev.freshness}</td>
                  <td className="p-3">
                    {ev.note && <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-1.5 py-0.5 rounded">{ev.note}</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* What System Does Not Know */}
        <div className="space-y-4">
          <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
            <h3 className="font-bold text-lg font-outfit mb-4 text-amber-400">⚠ What the System Does Not Know</h3>
            <div className="space-y-3 text-sm">
              <div className="bg-emerald-900/20 border border-emerald-500/20 p-3 rounded-lg">
                <p className="text-emerald-400 font-bold text-xs mb-2">✓ KNOWN</p>
                <ul className="text-gray-300 space-y-1 text-xs">
                  <li>✓ Heavy rainfall (7-day API data)</li>
                  <li>✓ Steep slope terrain (SRTM, partial)</li>
                  <li>✓ Historical susceptibility index</li>
                </ul>
              </div>
              <div className="bg-amber-900/20 border border-amber-500/20 p-3 rounded-lg">
                <p className="text-amber-400 font-bold text-xs mb-2">? UNKNOWN / UNCERTAIN</p>
                <ul className="text-gray-300 space-y-1 text-xs">
                  <li>? Current road condition on NH-10</li>
                  <li>? Recent village road access status</li>
                </ul>
              </div>
              <div className="bg-rose-900/20 border border-rose-500/20 p-3 rounded-lg">
                <p className="text-rose-400 font-bold text-xs mb-2">⚠ STALE / CONFLICTING</p>
                <ul className="text-gray-300 space-y-1 text-xs">
                  <li>⚠ Satellite observation 9 days old</li>
                  <li>⚠ Rainfall model vs satellite conflict</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Next-Best-Evidence */}
          <div className="bg-zinc-900 rounded-xl border border-cyan-500/30 p-5">
            <h3 className="font-bold text-cyan-400 text-lg font-outfit mb-2">Next-Best-Evidence</h3>
            <p className="text-white font-bold mb-1">ROAD STATUS VERIFICATION</p>
            <div className="flex gap-4 text-xs mb-4 text-gray-400">
              <span>Info Value: <span className="text-cyan-400 font-bold">VERY HIGH</span></span>
              <span>Uncertainty Reduction: <span className="text-emerald-400 font-bold">HIGH</span></span>
            </div>
            {submitResult ? (
              <div className="bg-cyan-900/30 border border-cyan-500/30 text-cyan-400 p-3 rounded text-xs">{submitResult}</div>
            ) : (
              <button
                onClick={handleRequestVerification}
                disabled={isSubmitting}
                className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold py-2 rounded text-sm transition-colors"
              >
                {isSubmitting ? 'Submitting...' : 'REQUEST VERIFICATION'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
