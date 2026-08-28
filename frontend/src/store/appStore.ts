import { create } from 'zustand';
import { UnifiedRiskObject } from '../types/api';
import { evidenceApi, simulationApi, decisionApi, ldiApi } from '../services/api';

interface LocationInfo {
  id: string;
  lat: number;
  lng: number;
  name?: string;
}

interface AppState {
  selectedLocationId: string | null;
  selectedLocation: LocationInfo | null;
  activeRiskObject: UnifiedRiskObject | null;
  simulationResult: Record<string, unknown> | null;
  isLoading: boolean;
  error: string | null;
  backendOnline: boolean | null;

  selectLocation: (loc: LocationInfo) => void;
  setSelectedLocationId: (id: string | null) => void;
  fetchRisk: (loc: LocationInfo) => Promise<void>;
  checkHealth: () => Promise<void>;
  submitVerification: (data: any) => Promise<void>;
  runSimulation: (params: any) => Promise<void>;
  submitHumanReview: (data: any) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  selectedLocationId: null,
  selectedLocation: null,
  activeRiskObject: null,
  simulationResult: null,
  isLoading: false,
  error: null,
  backendOnline: null,

  checkHealth: async () => {
    try {
      await ldiApi.health();
      set({ backendOnline: true });
    } catch {
      set({ backendOnline: false });
    }
  },

  setSelectedLocationId: (id) => {
    set({ selectedLocationId: id, error: null });
  },

  selectLocation: (loc) => {
    set({ selectedLocationId: loc.id, selectedLocation: loc, error: null });
    get().fetchRisk(loc);
  },

  fetchRisk: async (loc: LocationInfo) => {
    set({ isLoading: true, error: null });
    try {
      const result = await ldiApi.assess({
        location_id: loc.id,
        latitude: loc.lat,
        longitude: loc.lng,
        name: loc.name || 'Unknown',
        terrain_features: { elevation: 800, slope: 35, aspect: 220, terrain_ruggedness: 18 },
      });
      set({ activeRiskObject: result.unified_risk, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch risk', isLoading: false });
    }
  },

  submitVerification: async (data: any) => {
    set({ isLoading: true, error: null });
    try {
      await evidenceApi.submit(data);
      const loc = get().selectedLocation;
      if (loc) {
        await get().fetchRisk(loc);
      }
      set({ isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Verification failed', isLoading: false });
    }
  },

  runSimulation: async (params: any) => {
    set({ isLoading: true, error: null });
    try {
      const result = await simulationApi.run(params);
      set({ simulationResult: result as unknown as Record<string, unknown>, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Simulation failed', isLoading: false });
    }
  },

  submitHumanReview: async (data: any) => {
    set({ isLoading: true, error: null });
    try {
      await decisionApi.humanReview(data);
      set({ isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Review failed', isLoading: false });
    }
  },
}));
