import { useEffect } from 'react';
import { useAppStore } from '../store/appStore';

export default function RiskDetails() {
  const { selectedLocationId, activeRiskObject, isLoading, error } = useAppStore();

  return (
    <div className="p-6 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold mb-6 font-outfit">Risk Detail Analysis</h2>
      
      {!selectedLocationId ? (
        <div className="flex items-center justify-center h-64 text-gray-400 glass-panel">
           Please select a location from the dashboard map to view risk details.
        </div>
      ) : isLoading ? (
        <div className="flex justify-center p-10"><div className="animate-spin w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full"></div></div>
      ) : error ? (
        <div className="bg-rose-900/30 text-rose-400 p-4 rounded border border-rose-500/30">{error}</div>
      ) : activeRiskObject ? (
        <div className="glass-panel max-w-4xl">
          <div className="flex justify-between items-start border-b border-white/10 pb-4 mb-4">
             <div>
               <h3 className="text-xl font-bold">Location ID: {activeRiskObject.location.location_id}</h3>
               <p className="text-sm text-gray-400">{activeRiskObject.location.latitude}, {activeRiskObject.location.longitude}</p>
             </div>
             <div className="text-right">
                <p className="text-3xl font-bold text-rose-500">{Math.round(activeRiskObject.risk.score * 100)}% Risk</p>
                <p className="text-sm text-rose-400">{activeRiskObject.risk.level}</p>
             </div>
          </div>
          
          <div className="grid grid-cols-2 gap-6 mb-6">
             <div className="bg-zinc-900 p-4 rounded-xl border border-white/5">
                <p className="text-sm text-gray-400 mb-1">Model Confidence</p>
                <p className="text-2xl font-bold text-emerald-400">{Math.round(activeRiskObject.risk.confidence * 100)}%</p>
             </div>
             <div className="bg-zinc-900 p-4 rounded-xl border border-white/5">
                <p className="text-sm text-gray-400 mb-1">Uncertainty</p>
                <p className="text-2xl font-bold text-amber-500">{Math.round((1 - activeRiskObject.risk.confidence) * 100)}%</p>
             </div>
          </div>

          <div>
             <h4 className="font-bold text-gray-300 mb-2 uppercase text-xs tracking-widest">Model Information</h4>
             <p className="text-sm text-gray-400">Version: {activeRiskObject.risk.model_version || 'RF Baseline'}</p>
             <p className="text-sm text-gray-400 mb-4">Generated At: {new Date(activeRiskObject.timestamp).toLocaleString()}</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
