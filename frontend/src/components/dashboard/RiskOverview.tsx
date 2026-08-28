import { useState } from 'react';
import { Activity, ShieldAlert, Users } from 'lucide-react';

export default function RiskOverview() {
  return (
    <div className="glass-panel flex flex-col gap-6 h-full">
      <h3 className="flex items-center gap-2 text-cyan-400 font-bold text-lg">
        <Activity size={20} />
        System Overview
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/5 p-4 rounded-xl border-l-4 border-rose-500 border border-rose-500/20">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
            <ShieldAlert size={14} className="text-rose-400" /> Critical Alerts
          </div>
          <div className="text-3xl font-bold">1</div>
          <div className="text-xs text-rose-400 mt-1">Road B Corridor</div>
        </div>
        <div className="bg-white/5 p-4 rounded-xl border-l-4 border-emerald-500 border border-emerald-500/20">
          <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
            <Users size={14} className="text-emerald-400" /> Pop. Protected
          </div>
          <div className="text-3xl font-bold">12.4k</div>
          <div className="text-xs text-gray-400 mt-1">Across 18 villages</div>
        </div>
      </div>
      <div className="mt-auto">
        <div className="text-sm text-gray-400 mb-2">Network Connectivity</div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full w-[92%] bg-gradient-to-r from-cyan-400 to-emerald-400 rounded-full"></div>
        </div>
      </div>
    </div>
  );
}
