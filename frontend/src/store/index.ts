import { create } from 'zustand';
import { UnifiedRiskObject } from '../types/api';

interface AppState {
  selectedLocationId: string | null;
  activeRiskObject: UnifiedRiskObject | null;
  demoStep: number;
  setSelectedLocationId: (id: string | null) => void;
  setActiveRiskObject: (risk: UnifiedRiskObject | null) => void;
  setDemoStep: (step: number) => void;
  resetDemo: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedLocationId: null,
  activeRiskObject: null,
  demoStep: 0,
  setSelectedLocationId: (id) => set({ selectedLocationId: id }),
  setActiveRiskObject: (risk) => set({ activeRiskObject: risk }),
  setDemoStep: (step) => set({ demoStep: step }),
  resetDemo: () => set({ demoStep: 0, activeRiskObject: null, selectedLocationId: null }),
}));
