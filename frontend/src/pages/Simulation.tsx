import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { simulationApi, SimulationResult } from '../services/api';

const SCENARIOS = [
  { id: 'rainfall_increase_10', label: '+10% Rainfall', scenario_type: 'rainfall_increase', rainfall_multiplier: 1.1 },
  { id: 'rainfall_increase_25', label: '+25% Rainfall', scenario_type: 'rainfall_increase', rainfall_multiplier: 1.25 },
  { id: 'rainfall_increase_50', label: '+50% Rainfall', scenario_type: 'rainfall_increase', rainfall_multiplier: 1.5 },
  { id: 'road_failure', label: 'Road Failure', scenario_type: 'road_failure', road_failure: true },
];

interface SimDisplayResult {
  risk: number;
  confidence: number;
  uncertainty: number;
  road_blockage: number;
  village_isolation: number;
  population_exposed: number;
}

function parseBackendResult(res: SimulationResult): SimDisplayResult {
  const s = res.simulated_state as Record<string, number>;
  return {
    risk: Math.round((s.risk_score ?? 0) * 100),
    confidence: Math.round((1 - (res.delta?.risk_change ?? 0) * 0.5) * 84),
    uncertainty: Math.round((res.delta?.risk_change ?? 0) * 100 + 16),
    road_blockage: Math.round((s.road_blockage_probability ?? 0) * 100),
    village_isolation: Math.round((s.village_isolation_probability ?? 0) * 100),
    population_exposed: Math.round(s.population_exposed ?? 850),
  };
}

function computeDemoResult(scenarioId: string): SimDisplayResult {
  const baseline = { risk: 72, confidence: 84, uncertainty: 16, road_blockage: 45, village_isolation: 32, population_exposed: 850 };
  const multiplier = scenarioId === 'road_failure' ? 1.4 : parseFloat(scenarioId.replace('rainfall_increase_', '')) / 100 + 1;
  return {
    risk: Math.min(99, Math.round(baseline.risk * multiplier)),
    confidence: Math.min(99, Math.round(baseline.confidence * 0.95)),
    uncertainty: Math.min(99, Math.round(baseline.uncertainty * multiplier * 0.8)),
    road_blockage: Math.min(99, Math.round(baseline.road_blockage * multiplier)),
    village_isolation: Math.min(99, Math.round(baseline.village_isolation * multiplier)),
    population_exposed: Math.round(baseline.population_exposed * multiplier),
  };
}

export default function Simulation() {
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<SimDisplayResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<'backend' | 'demo' | null>(null);

  const baseline = { risk: 72, road_blockage: 45, village_isolation: 32, population_exposed: 850, uncertainty: 16 };

  const handleRun = async () => {
    if (!selected) return;
    setIsLoading(true);
    setError(null);
    setSource(null);
    const scenario = SCENARIOS.find(s => s.id === selected)!;

    try {
      const res = await simulationApi.run({
        location_id: 'LOC-TEST-001',
        scenario_type: scenario.scenario_type,
        rainfall_multiplier: scenario.rainfall_multiplier,
        road_failure: scenario.road_failure,
      });
      setResult(parseBackendResult(res));
      setSource('backend');
    } catch (_err) {
      setResult(computeDemoResult(selected));
      setSource('demo');
      setError('Backend unavailable — showing deterministic demo simulation.');
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = result ? [
    { name: 'Risk %', Current: baseline.risk, Scenario: result.risk },
    { name: 'Road Block %', Current: baseline.road_blockage, Scenario: result.road_blockage },
    { name: 'Village Iso. %', Current: baseline.village_isolation, Scenario: result.village_isolation },
    { name: 'Uncertainty %', Current: baseline.uncertainty, Scenario: result.uncertainty },
  ] : [];

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold font-outfit">What-If Simulation</h2>
          <p className="text-gray-400 text-sm mt-1">Explore scenarios and their predicted consequences</p>
        </div>
        {source === 'backend' && (
          <span className="text-xs text-emerald-400 border border-emerald-500/30 bg-emerald-900/20 px-2 py-1 rounded">REAL BACKEND RESULT</span>
        )}
        {source === 'demo' && (
          <span className="text-xs text-rose-400 border border-rose-500/30 bg-rose-900/20 px-2 py-1 rounded">SIMULATED DEMO RESULT</span>
        )}
        {!source && (
          <span className="text-xs text-gray-400 border border-gray-500/30 bg-gray-900/20 px-2 py-1 rounded">SIMULATED</span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Controls */}
        <div className="space-y-4">
          <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
            <h3 className="font-bold text-lg font-outfit mb-4">Select Scenario</h3>
            <div className="space-y-2">
              {SCENARIOS.map(s => (
                <button key={s.id} onClick={() => setSelected(s.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-all text-sm font-medium ${
                    selected === s.id
                      ? 'bg-cyan-900/40 border-cyan-500/50 text-cyan-400'
                      : 'bg-zinc-950 border-white/5 text-gray-300 hover:border-white/20'
                  }`}>
                  {s.label}
                </button>
              ))}
            </div>
            <button onClick={handleRun} disabled={!selected || isLoading}
              className="w-full mt-4 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 rounded transition-colors">
              {isLoading ? 'Running...' : 'RUN SIMULATION'}
            </button>
          </div>

          {/* Baseline */}
          <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
            <h4 className="font-bold mb-3 text-gray-400 uppercase text-xs tracking-wider">Current Baseline</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Risk</span><span className="font-bold text-amber-400">{baseline.risk}%</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Road Blockage</span><span className="font-bold">{baseline.road_blockage}%</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Village Isolation</span><span className="font-bold">{baseline.village_isolation}%</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Pop. Exposed</span><span className="font-bold">{baseline.population_exposed.toLocaleString()}</span></div>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="col-span-2 space-y-4">
          {error && <div className="text-amber-400 text-xs bg-amber-900/20 border border-amber-500/30 p-3 rounded">{error}</div>}

          {isLoading && (
            <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-3"></div>
                <p className="text-gray-400 text-sm">Running simulation...</p>
              </div>
            </div>
          )}

          {!result && !isLoading && (
            <div className="bg-zinc-900 rounded-xl border border-white/10 p-5 flex items-center justify-center h-64">
              <p className="text-gray-400 text-sm">Select a scenario and run simulation to see results.</p>
            </div>
          )}

          {result && !isLoading && (
            <>
              {/* Comparison table */}
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-lg font-outfit">Current vs Scenario</h3>
                  {source === 'backend' && <span className="text-xs text-emerald-400 font-mono">LIVE</span>}
                  {source === 'demo' && <span className="text-xs text-amber-400 font-mono">DEMO</span>}
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="font-bold text-gray-400 uppercase text-xs">Metric</div>
                  <div className="font-bold text-gray-400 uppercase text-xs text-center">Current</div>
                  <div className="font-bold text-cyan-400 uppercase text-xs text-center">Scenario</div>
                  {[
                    { label: 'Risk', cur: `${baseline.risk}%`, scen: `${result.risk}%`, up: result.risk > baseline.risk },
                    { label: 'Road Blockage', cur: `${baseline.road_blockage}%`, scen: `${result.road_blockage}%`, up: result.road_blockage > baseline.road_blockage },
                    { label: 'Village Isolation', cur: `${baseline.village_isolation}%`, scen: `${result.village_isolation}%`, up: result.village_isolation > baseline.village_isolation },
                    { label: 'Pop. Exposed', cur: baseline.population_exposed.toLocaleString(), scen: result.population_exposed.toLocaleString(), up: result.population_exposed > baseline.population_exposed },
                    { label: 'Uncertainty', cur: `${baseline.uncertainty}%`, scen: `${result.uncertainty}%`, up: result.uncertainty > baseline.uncertainty },
                  ].map(row => (
                    <div key={row.label} className="contents">
                      <div className="py-2 border-t border-white/5 text-gray-300">{row.label}</div>
                      <div className="py-2 border-t border-white/5 text-center font-mono">{row.cur}</div>
                      <div className={`py-2 border-t border-white/5 text-center font-mono font-bold ${row.up ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {row.scen} {row.up ? '↑' : '↓'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chart */}
              <div className="bg-zinc-900 rounded-xl border border-white/10 p-5">
                <h3 className="font-bold text-lg font-outfit mb-4">Visual Comparison</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData} barCategoryGap="25%">
                    <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
                    <Tooltip contentStyle={{ background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} labelStyle={{ color: '#fff' }} />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Bar dataKey="Current" fill="#3f3f46" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Scenario" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
