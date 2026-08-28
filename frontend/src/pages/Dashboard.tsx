import MapComponent from '../components/map/MapComponent';
import { useAppStore } from '../store/appStore';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { activeRiskObject, isLoading, error } = useAppStore();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-full bg-zinc-950 p-4 gap-4 overflow-hidden text-sm">
      {error && (
         <div className="bg-rose-900/30 border border-rose-500/30 text-rose-400 p-3 rounded">
            Error loading risk data: {error}
         </div>
      )}
      
      {/* Top row: Map and main risk/evidence summary */}
      <div className="flex-1 grid grid-cols-12 gap-4 min-h-[400px]">
        {/* Left: MAP */}
        <div className="col-span-8 bg-zinc-900 rounded-xl border border-white/10 overflow-hidden relative shadow-lg">
          <div className="absolute top-4 left-4 z-[1000] bg-black/80 px-3 py-1 rounded border border-rose-500 text-rose-500 text-xs font-bold shadow-md tracking-wider">
             SIMULATED
          </div>
          <MapComponent />
        </div>

        {/* Right: Risk & Evidence Panels */}
        <div className="col-span-4 flex flex-col gap-4 overflow-y-auto pr-2">
          
          {/* Risk Card */}
          <div className="bg-zinc-900/80 rounded-xl border border-rose-500/30 p-5 shadow-lg relative overflow-hidden flex-shrink-0 cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/risk')}>
             <div className="absolute top-0 right-0 w-2 h-full bg-rose-500"></div>
             <h2 className="text-xl font-bold mb-4 font-outfit text-white">Risk Summary</h2>
             
             {isLoading ? (
                <div className="flex justify-center p-4"><div className="animate-spin w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full"></div></div>
             ) : activeRiskObject ? (
               <>
                 <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                       <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Overall Risk</p>
                       <p className="text-3xl font-bold text-rose-500">{Math.round(activeRiskObject.risk.score * 100)}%</p>
                    </div>
                    <div>
                       <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Risk Level</p>
                       <p className="text-xl font-bold text-rose-500 mt-2">{activeRiskObject.risk.level}</p>
                    </div>
                 </div>
                 <div className="grid grid-cols-2 gap-4">
                    <div className="bg-zinc-800 p-2 rounded border border-white/5">
                       <p className="text-gray-400 text-xs">Confidence</p>
                       <p className="text-lg font-bold text-emerald-400">{Math.round(activeRiskObject.risk.confidence * 100)}%</p>
                    </div>
                    <div className="bg-zinc-800 p-2 rounded border border-white/5">
                       <p className="text-gray-400 text-xs">Uncertainty</p>
                       <p className="text-lg font-bold text-amber-500">{Math.round((1 - activeRiskObject.risk.confidence) * 100)}%</p>
                    </div>
                 </div>
               </>
             ) : (
                <div className="text-gray-400">Select a location on the map to load risk prediction.</div>
             )}
          </div>

          {/* Evidence Panel */}
          <div className="bg-zinc-900/80 rounded-xl border border-white/10 p-5 shadow-lg flex-shrink-0 cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/evidence')}>
             <h2 className="text-xl font-bold mb-4 font-outfit text-white">System Knowledge Base</h2>
             
             <div className="space-y-3">
                <div className="border border-emerald-500/20 bg-emerald-900/10 p-3 rounded">
                   <div className="flex justify-between items-center mb-1">
                      <h4 className="font-bold text-emerald-400 text-xs uppercase">KNOWN</h4>
                   </div>
                   <ul className="text-gray-300 text-xs space-y-1">
                      <li>✓ Heavy rainfall detected</li>
                      <li>✓ Steep slope terrain</li>
                   </ul>
                </div>

                <div className="border border-amber-500/20 bg-amber-900/10 p-3 rounded">
                   <div className="flex justify-between items-center mb-1">
                      <h4 className="font-bold text-amber-500 text-xs uppercase">UNKNOWN / UNCERTAIN</h4>
                   </div>
                   <ul className="text-gray-300 text-xs space-y-1">
                      <li>? Current road condition on NH-10</li>
                   </ul>
                </div>
             </div>
          </div>
        </div>
      </div>

      {/* Bottom row: Next-best-evidence, Impact, Simulation, Decision */}
      <div className="grid grid-cols-4 gap-4 min-h-[250px] flex-shrink-0">
        
        {/* Next Best Evidence */}
        <div className="bg-zinc-900 rounded-xl border border-cyan-500/30 p-4 shadow-lg flex flex-col cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/verification')}>
           <h3 className="font-bold text-cyan-400 mb-2 uppercase text-xs tracking-wider">Next-Best-Evidence</h3>
           <div className="flex-1">
              <p className="text-white font-bold mb-1">ROAD STATUS VERIFICATION</p>
              <p className="text-gray-400 text-xs mb-3">Reason: Potential village isolation risk.</p>
              
              <div className="flex justify-between text-xs mb-1">
                 <span className="text-gray-400">Information Value:</span>
                 <span className="text-cyan-400 font-bold">VERY HIGH</span>
              </div>
           </div>
           <button className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2 rounded transition-colors text-xs">
              REQUEST VERIFICATION
           </button>
        </div>

        {/* Impact */}
        <div className="bg-zinc-900 rounded-xl border border-white/10 p-4 shadow-lg cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/impact')}>
           <h3 className="font-bold text-gray-400 mb-3 uppercase text-xs tracking-wider">Impact Assessment</h3>
           <div className="space-y-3">
              <div>
                 <div className="flex justify-between text-xs mb-1">
                    <span>Road Blockage Prob.</span>
                    <span className="text-rose-400 font-bold">{activeRiskObject?.impact?.road_blockage_probability ? Math.round(activeRiskObject.impact.road_blockage_probability * 100) : 78}%</span>
                 </div>
                 <div className="w-full bg-zinc-800 h-1.5 rounded-full"><div className="bg-rose-500 h-1.5 rounded-full w-[78%]"></div></div>
              </div>
           </div>
        </div>

        {/* Simulation */}
        <div className="bg-zinc-900 rounded-xl border border-white/10 p-4 shadow-lg flex flex-col cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/simulation')}>
           <h3 className="font-bold text-gray-400 mb-2 uppercase text-xs tracking-wider">What-If Simulation</h3>
           <div className="flex gap-2 mb-3">
              <button className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-xs py-1.5 rounded border border-white/5">+25% Rain</button>
              <button className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-xs py-1.5 rounded border border-white/5">Road Fail</button>
           </div>
           <button className="w-full mt-auto bg-zinc-800 hover:bg-zinc-700 text-white font-bold py-1.5 rounded transition-colors text-xs border border-white/10">
              RUN SIMULATION
           </button>
        </div>

        {/* Human Review */}
        <div className="bg-zinc-900 rounded-xl border border-amber-500/30 p-4 shadow-lg flex flex-col cursor-pointer hover:bg-zinc-800 transition-colors" onClick={() => navigate('/decisions')}>
           <h3 className="font-bold text-amber-500 mb-2 uppercase text-xs tracking-wider">Human Decision Required</h3>
           <p className="text-white text-xs mb-1 font-bold">AI Recommendation:</p>
           <p className="text-gray-300 text-xs mb-3">Pre-position emergency response team near Village A.</p>
           
           <div className="flex gap-2 mt-auto">
              <button className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded text-xs">ACCEPT</button>
              <button className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 rounded text-xs">REJECT</button>
           </div>
        </div>

      </div>
    </div>
  );
}
