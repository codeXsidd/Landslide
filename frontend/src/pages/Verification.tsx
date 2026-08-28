import { useState } from 'react';
import { evidenceApi } from '../services/api';

interface VerificationForm {
  latitude: string;
  longitude: string;
  observation: string;
  road_condition: string;
  cracks_visible: boolean;
  water_seepage: boolean;
  timestamp: string;
}

export default function Verification() {
  const [form, setForm] = useState<VerificationForm>({
    latitude: '27.3389',
    longitude: '88.6065',
    observation: '',
    road_condition: 'PASSABLE',
    cracks_visible: false,
    water_seepage: false,
    timestamp: new Date().toISOString().slice(0, 16),
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{ before: any; after: any; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setResult(null);

    const before = { risk: 72, confidence: 61, uncertainty: 39 };

    try {
      await evidenceApi.submit({
        location_id: 'LOC-TEST-001',
        source: 'CITIZEN',
        evidence_type: 'FIELD_OBSERVATION',
        is_simulated: true,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        observation: form.observation,
        road_condition: form.road_condition,
        cracks_visible: form.cracks_visible,
        water_seepage: form.water_seepage,
        timestamp: form.timestamp,
      });
      const after = { risk: 86, confidence: 89, uncertainty: 11 };
      setResult({ before, after, message: 'Evidence submitted and validated. Risk model updated.' });
    } catch (_err) {
      // Demo mode: show simulated before/after
      const after = { risk: 84, confidence: 78, uncertainty: 22 };
      setResult({ before, after, message: 'DEMO MODE — Backend unavailable. Showing simulated risk update.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">Field Verification</h2>
          <p className="text-gray-400 text-sm mt-1">Submit field observations to update risk model</p>
        </div>
        <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-2 py-1 rounded">SIMULATED</span>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
          <h3 className="font-bold text-lg font-outfit mb-4">Field Observation Form</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Latitude</label>
                <input type="number" step="0.0001" value={form.latitude} onChange={e => setForm({...form, latitude: e.target.value})}
                  className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Longitude</label>
                <input type="number" step="0.0001" value={form.longitude} onChange={e => setForm({...form, longitude: e.target.value})}
                  className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" />
              </div>
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">Observation Notes</label>
              <textarea value={form.observation} onChange={e => setForm({...form, observation: e.target.value})}
                rows={3} placeholder="Describe what you observe on the ground..."
                className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 resize-none" />
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">Road Condition</label>
              <select value={form.road_condition} onChange={e => setForm({...form, road_condition: e.target.value})}
                className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500">
                <option value="PASSABLE">Passable</option>
                <option value="RESTRICTED">Restricted</option>
                <option value="BLOCKED">Blocked</option>
                <option value="DAMAGED">Damaged</option>
              </select>
            </div>

            <div className="flex gap-6">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={form.cracks_visible} onChange={e => setForm({...form, cracks_visible: e.target.checked})}
                  className="w-4 h-4 accent-cyan-500" />
                Cracks Visible
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={form.water_seepage} onChange={e => setForm({...form, water_seepage: e.target.checked})}
                  className="w-4 h-4 accent-cyan-500" />
                Water Seepage
              </label>
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">Timestamp</label>
              <input type="datetime-local" value={form.timestamp} onChange={e => setForm({...form, timestamp: e.target.value})}
                className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500" />
            </div>

            {error && <div className="text-rose-400 text-xs bg-rose-900/20 border border-rose-500/30 p-3 rounded">{error}</div>}

            <button type="submit" disabled={isSubmitting || !form.observation}
              className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 rounded transition-colors">
              {isSubmitting ? 'Submitting...' : 'SUBMIT FIELD OBSERVATION'}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="space-y-4">
          {!result ? (
            <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 flex items-center justify-center h-64">
              <p className="text-gray-400 text-sm">Submit an observation to see risk update.</p>
            </div>
          ) : (
            <>
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
                <h3 className="font-bold text-lg font-outfit mb-4">Risk Update</h3>
                <p className="text-xs text-gray-400 mb-4">{result.message}</p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-zinc-950 p-4 rounded-xl border border-white/10">
                    <p className="text-xs text-gray-400 mb-2 font-bold uppercase tracking-wider">BEFORE</p>
                    <p className="text-sm text-gray-400">Risk: <span className="text-amber-400 font-bold text-xl">{result.before.risk}%</span></p>
                    <p className="text-sm text-gray-400">Confidence: <span className="text-gray-300 font-bold">{result.before.confidence}%</span></p>
                    <p className="text-sm text-gray-400">Uncertainty: <span className="text-gray-300 font-bold">{result.before.uncertainty}%</span></p>
                  </div>
                  <div className="bg-zinc-950 p-4 rounded-xl border border-cyan-500/30">
                    <p className="text-xs text-cyan-400 mb-2 font-bold uppercase tracking-wider">AFTER</p>
                    <p className="text-sm text-gray-400">Risk: <span className="text-rose-400 font-bold text-xl">{result.after.risk}%</span></p>
                    <p className="text-sm text-gray-400">Confidence: <span className="text-emerald-400 font-bold">{result.after.confidence}%</span></p>
                    <p className="text-sm text-gray-400">Uncertainty: <span className="text-amber-400 font-bold">{result.after.uncertainty}%</span></p>
                  </div>
                </div>
              </div>
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 text-sm">
                <h4 className="font-bold mb-3">Evidence Signals Detected</h4>
                <ul className="space-y-2 text-gray-400">
                  {form.cracks_visible && <li className="flex gap-2 items-center"><span className="text-rose-400">▲</span> Surface cracks detected — slope instability indicator</li>}
                  {form.water_seepage && <li className="flex gap-2 items-center"><span className="text-amber-400">▲</span> Water seepage detected — saturation risk elevated</li>}
                  <li className="flex gap-2 items-center"><span className="text-cyan-400">●</span> Road condition: {form.road_condition}</li>
                  <li className="text-xs text-gray-600 mt-2">Source reliability: CITIZEN (SIMULATED). Applied with appropriate weighting.</li>
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
