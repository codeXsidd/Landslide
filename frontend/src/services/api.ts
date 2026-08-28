import axios from 'axios';
import { UnifiedRiskObject } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export interface SimulationResult {
  simulation_id: string;
  scenario_type: string;
  input_changes: Record<string, unknown>;
  baseline_state: Record<string, unknown>;
  simulated_state: Record<string, unknown>;
  delta: {
    risk_change: number;
    priority_change: number;
    isolation_change: number;
  };
  timestamp: string;
  is_simulated: boolean;
}

export interface LdiAssessResult {
  unified_risk: UnifiedRiskObject;
  next_best_evidence: Record<string, unknown>;
  disclaimer: string;
}

export const riskApi = {
  predict: async (data: any): Promise<UnifiedRiskObject> => {
    const response = await apiClient.post('/risk/predict', data);
    return response.data;
  },
  getRisk: async (locationId: string): Promise<UnifiedRiskObject> => {
    const response = await apiClient.get(`/risk/${locationId}`);
    return response.data;
  },
};

export const evidenceApi = {
  submit: async (data: any): Promise<any> => {
    const response = await apiClient.post('/evidence', data);
    return response.data;
  },
  verify: async (data: any): Promise<any> => {
    const response = await apiClient.post('/evidence/verify', data);
    return response.data;
  },
};

export const simulationApi = {
  run: async (data: {
    location_id: string;
    scenario_type: string;
    rainfall_multiplier?: number;
    road_failure?: boolean;
  }): Promise<SimulationResult> => {
    const baselineState = {
      risk_score: 0.72,
      road_blockage_probability: 0.45,
      village_isolation_probability: 0.32,
      population_exposed: 850,
      rainfall_features: { cumulative_7d: 120, intensity_max: 35 },
    };

    const scenario: Record<string, unknown> = {
      type: data.scenario_type,
      rainfall_factor: data.rainfall_multiplier ?? 1.0,
      road_closure: data.road_failure ?? false,
    };

    const response = await apiClient.post('/ldi/simulate', {
      baseline_state: baselineState,
      scenario,
    });
    return response.data;
  },
};

export const impactApi = {
  get: async (locationId: string): Promise<any> => {
    const response = await apiClient.get(`/impact/${locationId}`);
    return response.data;
  },
};

export const decisionApi = {
  humanReview: async (data: any): Promise<any> => {
    const response = await apiClient.post('/decisions', {
      action_id: data.location_id,
      status: data.decision,
      decided_by: data.decided_by,
      reason: data.reason,
      timestamp: data.timestamp,
    });
    return response.data;
  },
};

export const mapApi = {
  getWaterways: async (): Promise<any> => {
    const response = await apiClient.get('/map/waterways');
    return response.data;
  },
};

export const ldiApi = {
  health: async (): Promise<{ status: string; system: string; version: string }> => {
    const response = await apiClient.get('/ldi/health');
    return response.data;
  },
  assess: async (data: any): Promise<LdiAssessResult> => {
    const response = await apiClient.post('/ldi/assess', data);
    return response.data;
  },
  simulate: async (baselineState: Record<string, unknown>, scenario: Record<string, unknown>): Promise<SimulationResult> => {
    const response = await apiClient.post('/ldi/simulate', {
      baseline_state: baselineState,
      scenario,
    });
    return response.data;
  },
};
