export default function Impact() {
  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">Impact Analysis</h2>
          <p className="text-gray-400 text-sm mt-1">Predicted consequences of landslide events</p>
        </div>
        <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-2 py-1 rounded">SIMULATED</span>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Road */}
        <div className="bg-zinc-900 rounded-xl border border-rose-500/20 p-5">
          <h3 className="font-bold text-lg font-outfit mb-4 text-rose-400">Road Impact</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1"><span className="text-gray-400">Blockage Probability</span><span className="font-bold text-rose-400">78%</span></div>
              <div className="w-full bg-zinc-800 h-2 rounded-full"><div className="bg-rose-500 h-2 rounded-full w-[78%]"></div></div>
            </div>
            <div className="bg-zinc-950 p-3 rounded text-sm space-y-2">
              <p className="text-gray-400">Critical Road: <span className="text-white font-medium">NH-10, Road B</span></p>
              <p className="text-gray-400">Alternative: <span className="text-amber-400 font-medium">Route C (2.5 hrs extra)</span></p>
              <p className="text-gray-400">Accessibility: <span className="text-rose-400 font-bold">DEGRADED</span></p>
            </div>
            <div className="text-xs text-gray-500 border border-white/5 bg-zinc-950 p-2 rounded">
              Roads/Villages data: <span className="text-amber-400">SYNTHETIC/DEMO</span>
            </div>
          </div>
        </div>

        {/* Village */}
        <div className="bg-zinc-900 rounded-xl border border-amber-500/20 p-5">
          <h3 className="font-bold text-lg font-outfit mb-4 text-amber-400">Village Impact</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1"><span className="text-gray-400">Isolation Probability</span><span className="font-bold text-amber-400">64%</span></div>
              <div className="w-full bg-zinc-800 h-2 rounded-full"><div className="bg-amber-500 h-2 rounded-full w-[64%]"></div></div>
            </div>
            <div className="bg-zinc-950 p-3 rounded text-sm space-y-2">
              <p className="text-gray-400">Affected Villages: <span className="text-white font-medium">Village A, B</span></p>
              <p className="text-gray-400">Population Exposed: <span className="text-rose-400 font-bold">1,240</span></p>
              <p className="text-gray-400">Emergency Access: <span className="text-rose-400 font-bold">AT RISK</span></p>
            </div>
          </div>
        </div>

        {/* Infrastructure */}
        <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
          <h3 className="font-bold text-lg font-outfit mb-4 text-gray-300">Infrastructure</h3>
          <div className="space-y-3 text-sm">
            {[
              { name: 'District Hospital', status: 'DEGRADED', icon: '🏥' },
              { name: 'Primary School', status: 'AT RISK', icon: '🏫' },
              { name: 'Bridge (NH-10)', status: 'AT RISK', icon: '🌉' },
              { name: 'Emergency Depot', status: 'ACCESSIBLE', icon: '🚒' },
            ].map(inf => (
              <div key={inf.name} className="flex justify-between items-center bg-zinc-950 px-3 py-2 rounded border border-white/5">
                <span>{inf.icon} {inf.name}</span>
                <span className={`text-xs font-bold ${
                  inf.status === 'ACCESSIBLE' ? 'text-emerald-400' :
                  inf.status === 'DEGRADED' ? 'text-rose-400' : 'text-amber-400'
                }`}>{inf.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
