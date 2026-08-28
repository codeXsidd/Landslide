import { useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { ShieldAlert, Map, AlertTriangle, FileCheck, BrainCircuit, Activity, Network, ListChecks, History, PlayCircle } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

export default function Layout() {
  const { backendOnline, checkHealth } = useAppStore();

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <Map size={18} /> },
    { name: 'Risk Detail', path: '/risk', icon: <AlertTriangle size={18} /> },
    { name: 'Evidence', path: '/evidence', icon: <FileCheck size={18} /> },
    { name: 'Verification', path: '/verification', icon: <ShieldAlert size={18} /> },
    { name: 'Impact', path: '/impact', icon: <Network size={18} /> },
    { name: 'Simulation', path: '/simulation', icon: <Activity size={18} /> },
    { name: 'Decisions', path: '/decisions', icon: <ListChecks size={18} /> },
    { name: 'Audit', path: '/audit', icon: <History size={18} /> },
    { name: 'SIH Demo', path: '/demo', icon: <PlayCircle size={18} /> },
  ];

  return (
    <div className="flex h-screen bg-zinc-950 text-gray-100 overflow-hidden font-sans">

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-zinc-900 border-r border-white/5 flex flex-col z-50 shadow-xl">
        <div className="p-4 border-b border-white/5 bg-zinc-950/30">
          <div className="flex items-center gap-2 mb-1">
            <BrainCircuit className="text-cyan-400" size={24} />
            <h1 className="text-2xl font-bold font-outfit bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent tracking-tight">NER-LDI</h1>
          </div>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest leading-tight">Northeast Region<br/>Landslide Decision Intelligence</p>
        </div>

        <nav className="flex-1 py-4 overflow-y-auto">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                      isActive
                        ? 'bg-cyan-900/40 text-cyan-400 font-medium border border-cyan-500/20 shadow-[inset_0_0_12px_rgba(6,182,212,0.1)]'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-zinc-800'
                    }`
                  }
                >
                  {item.icon}
                  {item.name}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top Header */}
        <header className="h-14 bg-zinc-900/80 backdrop-blur border-b border-white/5 flex items-center justify-between px-6 z-40">
           <div className="flex gap-4">
              {backendOnline === true && (
                <div className="flex items-center gap-2 text-xs border border-emerald-500/20 bg-emerald-950/30 text-emerald-400 px-2 py-1 rounded">
                  <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
                  BACKEND: ONLINE
                </div>
              )}
              {backendOnline === false && (
                <div className="flex items-center gap-2 text-xs border border-rose-500/20 bg-rose-950/30 text-rose-400 px-2 py-1 rounded">
                  <div className="w-1.5 h-1.5 bg-rose-400 rounded-full"></div>
                  BACKEND: OFFLINE
                </div>
              )}
              {backendOnline === null && (
                <div className="flex items-center gap-2 text-xs border border-gray-500/20 bg-gray-950/30 text-gray-400 px-2 py-1 rounded">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                  CHECKING...
                </div>
              )}
              <div className="flex items-center gap-2 text-xs border border-cyan-500/20 bg-cyan-950/30 text-cyan-400 px-2 py-1 rounded">
                ML: HEURISTIC
              </div>
           </div>

           <div className="flex items-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                 <span className="uppercase text-xs tracking-wider">Role:</span>
                 <select className="bg-zinc-950 border border-white/10 rounded px-2 py-1 text-white text-xs outline-none focus:border-cyan-500 transition-colors">
                    <option>District Authority</option>
                    <option>Emergency Coordinator</option>
                    <option>Field Worker</option>
                    <option>Driver</option>
                    <option>Citizen</option>
                 </select>
              </div>
              <span className="text-xs">{new Date().toLocaleTimeString()}</span>
           </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
