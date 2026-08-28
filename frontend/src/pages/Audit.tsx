const AUDIT_EVENTS = [
  { ts: '06:00 IST', type: 'PREDICTION', detail: 'Risk predicted: 72% | Confidence: 61% | Model: RF Baseline v1.0', color: 'border-cyan-500', dot: 'bg-cyan-500' },
  { ts: '06:05 IST', type: 'EVIDENCE', detail: 'Rainfall data ingested (7-day prototype) | Terrain: SRTM partial | Satellite: STALE (9 days)', color: 'border-amber-500', dot: 'bg-amber-500' },
  { ts: '06:10 IST', type: 'CONFLICT DETECTED', detail: 'Rainfall model vs stale satellite → Contradictions: 1 | Knowledge gaps: 2', color: 'border-rose-500', dot: 'bg-rose-500' },
  { ts: '06:12 IST', type: 'NEXT-BEST-EVIDENCE', detail: 'Road Status Verification selected | Information Value: VERY HIGH', color: 'border-purple-500', dot: 'bg-purple-500' },
  { ts: '06:20 IST', type: 'VERIFICATION', detail: 'Field observation submitted (SIMULATED) | Cracks observed | Road: RESTRICTED', color: 'border-blue-500', dot: 'bg-blue-500' },
  { ts: '06:22 IST', type: 'RISK UPDATE', detail: 'Risk: 72% → 86% | Confidence: 61% → 89% | Evidence applied', color: 'border-rose-500', dot: 'bg-rose-500' },
  { ts: '06:25 IST', type: 'HUMAN DECISION', detail: 'Recommendation: ACCEPTED | Officer: District Authority | Action: Pre-position response team', color: 'border-emerald-500', dot: 'bg-emerald-500' },
];

const TYPE_COLORS: Record<string, string> = {
  PREDICTION: 'text-cyan-400 bg-cyan-900/20 border-cyan-500/30',
  EVIDENCE: 'text-amber-400 bg-amber-900/20 border-amber-500/30',
  'CONFLICT DETECTED': 'text-rose-400 bg-rose-900/20 border-rose-500/30',
  'NEXT-BEST-EVIDENCE': 'text-purple-400 bg-purple-900/20 border-purple-500/30',
  VERIFICATION: 'text-blue-400 bg-blue-900/20 border-blue-500/30',
  'RISK UPDATE': 'text-rose-400 bg-rose-900/20 border-rose-500/30',
  'HUMAN DECISION': 'text-emerald-400 bg-emerald-900/20 border-emerald-500/30',
};

export default function Audit() {
  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">Audit History</h2>
          <p className="text-gray-400 text-sm mt-1">Full event timeline for NER-LDI decision cycle</p>
        </div>
        <span className="text-xs text-amber-400 border border-amber-500/30 bg-amber-900/20 px-2 py-1 rounded">DEMO RUN — 2026-08-28</span>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="col-span-2 space-y-0">
          {AUDIT_EVENTS.map((ev, i) => (
            <div key={i} className="flex gap-4">
              {/* Left: timestamp + connector */}
              <div className="flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full mt-5 flex-shrink-0 ${ev.dot}`}></div>
                {i < AUDIT_EVENTS.length - 1 && <div className="w-0.5 h-full bg-white/10 flex-shrink-0"></div>}
              </div>
              {/* Right: content */}
              <div className={`flex-1 mb-4 border-l-2 pl-4 ${ev.color}`}>
                <div className="flex items-center gap-3 mb-1">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded border ${TYPE_COLORS[ev.type] || 'text-gray-400 bg-zinc-800 border-white/10'}`}>{ev.type}</span>
                  <span className="text-xs text-gray-500">{ev.ts}</span>
                </div>
                <p className="text-sm text-gray-300">{ev.detail}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Summary sidebar */}
        <div className="space-y-4">
          <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
            <h3 className="font-bold font-outfit mb-4">Run Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Model Version</span><span>RF Baseline v1.0</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Start Time</span><span>06:00 IST</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Decision Made</span><span>06:25 IST</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Evidence Sources</span><span>6</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Conflicts</span><span className="text-rose-400 font-bold">1</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Unknowns Resolved</span><span className="text-emerald-400 font-bold">1/2</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Human Decision</span><span className="text-emerald-400 font-bold">ACCEPTED</span></div>
            </div>
          </div>

          <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 text-sm">
            <h3 className="font-bold font-outfit mb-3 text-gray-400 text-xs uppercase tracking-wider">Data Limitations</h3>
            <ul className="space-y-2 text-gray-400 text-xs">
              <li>⚠ Terrain: 24/57 SRTM cells</li>
              <li>⚠ Rainfall: 7-day prototype only</li>
              <li>⚠ Satellite: Simulated adapter</li>
              <li>⚠ Roads/Villages: Synthetic/demo data</li>
              <li>⚠ Dynamic model: PROTOTYPE (incomplete)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
