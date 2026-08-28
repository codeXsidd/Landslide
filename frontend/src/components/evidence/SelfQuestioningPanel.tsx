import { useState } from 'react';
import { HelpCircle, FileSearch, CheckCircle2 } from 'lucide-react';

export default function SelfQuestioningPanel() {
  const [step, setStep] = useState(0);

  return (
    <div className="glass-panel h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h3 className="flex items-center gap-2 text-amber-400 font-bold text-lg">
          <HelpCircle size={20} /> Self-Questioning Engine
        </h3>
        <button
          onClick={() => setStep(s => Math.min(s + 1, 2))}
          disabled={step >= 2}
          className="bg-cyan-500 text-black px-3 py-1 rounded text-xs font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-cyan-400 transition-colors"
        >
          Next Step
        </button>
      </div>

      <div className="flex-1 flex flex-col gap-3 overflow-y-auto">
        <div className="bg-amber-900/20 border-l-4 border-amber-500 p-4 rounded-r-lg">
          <div className="text-sm text-amber-400 font-bold mb-1">1. Uncertainty Detected</div>
          <div className="text-sm">Risk is 82%, but confidence is 54%.</div>
          <div className="text-xs text-gray-400 mt-2 space-y-1">
            <div>• Satellite data is <span className="text-rose-400">STALE</span> (9 days old)</div>
            <div>• Ground evidence is <span className="text-rose-400">MISSING</span></div>
          </div>
        </div>

        {step >= 1 && (
          <div className="bg-cyan-900/20 border-l-4 border-cyan-500 p-4 rounded-r-lg">
            <div className="text-sm text-cyan-400 font-bold mb-1 flex items-center gap-2">
              <FileSearch size={14} /> 2. Next-Best-Evidence Strategy
            </div>
            <div className="text-sm">Requested citizen verification for Road B.</div>
            <div className="text-xs text-gray-400 mt-2 space-y-1">
              <div>Decision Value: 0.92 (Very High)</div>
              <div>Reason: High-consequence area (Village X isolated if fails).</div>
            </div>
          </div>
        )}

        {step >= 2 && (
          <div className="bg-emerald-900/20 border-l-4 border-emerald-500 p-4 rounded-r-lg">
            <div className="text-sm text-emerald-400 font-bold mb-1 flex items-center gap-2">
              <CheckCircle2 size={14} /> 3. Belief Update
            </div>
            <div className="text-sm">Human Evidence (Report #184) verified via CV.</div>
            <div className="flex gap-3 mt-3">
              <div className="bg-black/30 p-2 rounded flex-1">
                <div className="text-xs text-gray-400">New Risk</div>
                <div className="text-rose-400 font-bold">88% <span className="text-xs">↑6%</span></div>
              </div>
              <div className="bg-black/30 p-2 rounded flex-1">
                <div className="text-xs text-gray-400">New Confidence</div>
                <div className="text-emerald-400 font-bold">91% <span className="text-xs">↑37%</span></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
