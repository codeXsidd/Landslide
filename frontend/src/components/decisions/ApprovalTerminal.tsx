import { useState } from 'react';
import { Terminal, ShieldCheck, AlertOctagon } from 'lucide-react';

export default function ApprovalTerminal() {
  const [status, setStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  return (
    <div className="glass-panel h-full flex flex-col bg-zinc-950/80">
      <div className="flex items-center gap-2 border-b border-white/10 pb-3 mb-4">
        <Terminal size={16} className="text-gray-400" />
        <span className="text-sm text-gray-400 font-mono">Decision Engine / Human-in-the-Loop</span>
      </div>
      <div className="flex-1 font-mono text-sm text-gray-100">
        <div className="text-rose-400 mb-2 font-bold">CRITICAL ALERT: Road B Failure Imminent</div>
        <div className="mb-4 text-gray-400 text-xs leading-relaxed">Cascading impact: 850 residents in Village X will be isolated. Hospital Z access degraded.</div>
        <div className="bg-white/5 p-3 rounded mb-4 text-xs">
          <div className="text-cyan-400 mb-1 font-bold">RECOMMENDED INTERVENTIONS:</div>
          <div>1. Deploy immediate road inspection team</div>
          <div>2. Pre-position excavators at Junction Y</div>
          <div>3. Issue closure warning for Route B</div>
        </div>
        {status === 'PENDING' && (
          <div className="flex flex-col gap-3">
            <div className="text-amber-500 text-xs">HUMAN OPERATOR AUTHORIZATION REQUIRED</div>
            <div className="flex gap-2">
              <button onClick={() => setStatus('APPROVED')} className="flex-1 py-2 bg-emerald-500 text-black font-bold rounded text-xs hover:bg-emerald-400 transition-colors">APPROVE ACTIONS</button>
              <button onClick={() => setStatus('REJECTED')} className="flex-1 py-2 bg-transparent text-rose-400 border border-rose-500 font-bold rounded text-xs hover:bg-rose-900/20 transition-colors">REJECT</button>
            </div>
          </div>
        )}
        {status === 'APPROVED' && (
          <div className="text-emerald-400 flex items-center gap-2 text-xs">
            <ShieldCheck size={16} /> ACTIONS DISPATCHED. AUDIT LOG UPDATED.
          </div>
        )}
        {status === 'REJECTED' && (
          <div className="text-rose-400 flex items-center gap-2 text-xs">
            <AlertOctagon size={16} /> ACTIONS REJECTED BY OPERATOR.
          </div>
        )}
      </div>
    </div>
  );
}
