import { useState } from 'react';

const STEPS = [
  { step: 1, name: 'Observe', detail: 'Ingest rainfall (7-day), terrain (SRTM partial), historical data', status: 'complete' },
  { step: 2, name: 'Predict', detail: 'RF Baseline predicts: Risk 72%, Confidence 61%', status: 'complete' },
  { step: 3, name: 'Measure Confidence', detail: 'Epistemic uncertainty = 39%. Confidence LOW → Self-question triggered.', status: 'warning' },
  { step: 4, name: 'Detect Evidence Conflict', detail: 'Rainfall model HIGH risk. Satellite observation STALE (9 days). Contradiction flagged.', status: 'error' },
  { step: 5, name: 'Identify Unknowns', detail: 'Unknown: Road condition NH-10. Unknown: Village B access route.', status: 'warning' },
  { step: 6, name: 'Select Next-Best Evidence', detail: 'ROAD STATUS VERIFICATION selected. Info Value: 0.92 (VERY HIGH). Reason: Village isolation risk.', status: 'complete' },
  { step: 7, name: 'Human Verification', detail: 'Field worker reports cracks and water seepage. Road: RESTRICTED. Evidence submitted (SIMULATED).', status: 'complete' },
  { step: 8, name: 'Update Risk', detail: 'Bayesian update: Risk 72% → 86%. Confidence 61% → 89%. Evidence incorporated.', status: 'complete' },
  { step: 9, name: 'Road Impact', detail: 'Road Blockage Probability: 78%. NH-10 and Road B affected. Alt route: 2.5 hrs extra.', status: 'error' },
  { step: 10, name: 'Village Isolation', detail: 'Village A: Isolation 64%. 1,240 residents exposed. Hospital access: DEGRADED.', status: 'error' },
  { step: 11, name: 'What-If: Rainfall +25%', detail: 'Scenario: Risk 86% → 92%. Road Blockage 78% → 91%. Population exposed 1,240 → 1,580.', status: 'warning' },
  { step: 12, name: 'Priority Update', detail: 'Location re-ranked CRITICAL (1/4). Expected harm: 91%. Resource allocation updated.', status: 'error' },
  { step: 13, name: 'Action Optimization', detail: 'Recommended: (1) Inspect Road B (2) Prepare Route C (3) Pre-position response team.', status: 'complete' },
  { step: 14, name: 'Human Decision', detail: 'Officer: District Authority. ACCEPTED. Reason: "Isolation risk confirmed by field report."', status: 'complete' },
  { step: 15, name: 'Outcome', detail: 'Response team deployed. Road B inspection completed. Evacuation route prepared.', status: 'complete' },
  { step: 16, name: 'Feedback', detail: 'Outcome recorded. Model feedback loop updated. Audit log closed.', status: 'complete' },
];

const STATUS_STYLES: Record<string, string> = {
  complete: 'text-emerald-400 bg-emerald-900/20 border-emerald-500/30',
  warning: 'text-amber-400 bg-amber-900/20 border-amber-500/30',
  error: 'text-rose-400 bg-rose-900/20 border-rose-500/30',
  pending: 'text-gray-400 bg-zinc-900/50 border-white/10',
};

const DOT_STYLES: Record<string, string> = {
  complete: 'bg-emerald-500',
  warning: 'bg-amber-500',
  error: 'bg-rose-500',
  pending: 'bg-zinc-600',
};

export default function Demo() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playInterval, setPlayInterval] = useState<ReturnType<typeof setInterval> | null>(null);

  const totalSteps = STEPS.length;

  const goToStep = (step: number) => {
    if (step < 0 || step >= totalSteps) return;
    setCurrentStep(step);
  };

  const startPlay = () => {
    if (isPlaying) {
      if (playInterval) clearInterval(playInterval);
      setIsPlaying(false);
      setPlayInterval(null);
      return;
    }
    setIsPlaying(true);
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= totalSteps - 1) {
          clearInterval(interval);
          setIsPlaying(false);
          setPlayInterval(null);
          return prev;
        }
        return prev + 1;
      });
    }, 1800);
    setPlayInterval(interval);
  };

  const reset = () => {
    if (playInterval) clearInterval(playInterval);
    setIsPlaying(false);
    setPlayInterval(null);
    setCurrentStep(0);
  };

  const step = STEPS[currentStep];

  return (
    <div className="p-6 h-full overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">SIH Demo Replay</h2>
          <p className="text-gray-400 text-sm mt-1">Complete 16-step NER-LDI decision intelligence scenario</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-2 py-1 rounded">SIMULATED DEMO</span>
          <span className="text-xs text-gray-400">STEP {currentStep + 1} / {totalSteps}</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-zinc-800 rounded-full h-2 mb-6">
        <div className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-3 mb-6">
        <button onClick={() => goToStep(currentStep - 1)} disabled={currentStep === 0}
          className="px-5 py-2 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed rounded font-bold text-sm transition-colors">
          ← PREVIOUS
        </button>
        <button onClick={startPlay}
          className={`px-5 py-2 rounded font-bold text-sm transition-colors ${isPlaying ? 'bg-amber-600 hover:bg-amber-500' : 'bg-cyan-600 hover:bg-cyan-500'}`}>
          {isPlaying ? '⏸ PAUSE' : '▶ PLAY'}
        </button>
        <button onClick={() => goToStep(currentStep + 1)} disabled={currentStep === totalSteps - 1}
          className="px-5 py-2 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed rounded font-bold text-sm transition-colors">
          NEXT →
        </button>
        <button onClick={reset} className="px-5 py-2 bg-rose-900/50 hover:bg-rose-900 text-rose-400 rounded font-bold text-sm transition-colors">RESET</button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Step list */}
        <div className="col-span-4 bg-zinc-900 rounded-xl border border-white/10 overflow-hidden">
          <div className="p-3 border-b border-white/10 text-xs text-gray-400 uppercase tracking-wider font-bold">Steps</div>
          <div className="overflow-y-auto max-h-[500px]">
            {STEPS.map((s, i) => (
              <button key={s.step} onClick={() => goToStep(i)}
                className={`w-full text-left p-3 flex items-center gap-3 border-b border-white/5 transition-colors text-sm ${
                  i === currentStep ? 'bg-cyan-900/30 text-white' : i < currentStep ? 'text-gray-500' : 'text-gray-600'
                } hover:bg-white/5`}>
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${i <= currentStep ? DOT_STYLES[s.status] : 'bg-zinc-700'}`}></div>
                <span className="text-xs text-gray-500 w-6 flex-shrink-0">{s.step}</span>
                <span className="font-medium">{s.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Current step detail */}
        <div className="col-span-8 space-y-4">
          <div className={`bg-zinc-900 rounded-xl border p-6 ${STATUS_STYLES[step.status]}`}>
            <div className="flex items-center gap-3 mb-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${DOT_STYLES[step.status]} text-black`}>
                {step.step}
              </div>
              <div>
                <h3 className="text-xl font-bold font-outfit">{step.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded border ${STATUS_STYLES[step.status]}`}>
                  {step.status.toUpperCase()}
                </span>
              </div>
            </div>
            <p className="text-gray-200 text-base leading-relaxed">{step.detail}</p>
          </div>

          {/* Contextual cards for key steps */}
          {currentStep >= 7 && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-4 text-sm">
                <p className="text-gray-400 text-xs font-bold uppercase mb-2">Updated Risk</p>
                <p className="text-3xl font-bold text-rose-500">86%</p>
                <p className="text-xs text-gray-400 mt-1">Model: RF Baseline v1.0</p>
              </div>
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-4 text-sm">
                <p className="text-gray-400 text-xs font-bold uppercase mb-2">Updated Confidence</p>
                <p className="text-3xl font-bold text-emerald-400">89%</p>
                <p className="text-xs text-gray-400 mt-1">After field verification</p>
              </div>
            </div>
          )}

          {currentStep >= 13 && (
            <div className="bg-zinc-900 rounded-xl border border-emerald-500/30 p-4 text-sm">
              <p className="text-emerald-400 font-bold text-xs uppercase mb-2">Human Decision Logged</p>
              <p className="text-gray-300">Decision: <strong>ACCEPTED</strong> by District Authority</p>
              <p className="text-gray-400 text-xs mt-1">Reason: "Isolation risk confirmed by field report."</p>
              <p className="text-gray-500 text-xs mt-1">Timestamp: {new Date().toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
