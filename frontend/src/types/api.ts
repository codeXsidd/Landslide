export interface Location {
  latitude: number;
  longitude: number;
  location_id?: string;
  name?: string;
}

export interface RiskSummary {
  score: number;
  level: 'VERY_LOW' | 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: number;
  model_version?: string;
}

export interface EvidenceStatus {
  fusion_status?: 'KNOWN' | 'UNKNOWN' | 'UNCERTAIN' | 'CONFLICTING' | 'STALE';
  coverage?: number;
  contradictions?: number;
  knowledge_gaps?: number;
  critical_gaps?: number;
}

export interface ImpactSummary {
  road_blockage_probability?: number;
  village_isolation_probability?: number;
  population_exposed?: number;
  infrastructure_exposure_score?: number;
  critical_assets_count?: number;
}

export interface Priority {
  score?: number;
  level?: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}

export interface ActionRecommendation {
  action: string;
  cost?: number;
  time_hours?: number;
  expected_harm_reduction?: number;
  requires_human_approval: boolean;
}

export interface HumanDecisionStatus {
  status?: 'PENDING' | 'APPROVED' | 'REJECTED' | 'MODIFIED' | 'NOT_REQUIRED';
  decided_by?: string | null;
}

export interface UnifiedRiskObject {
  object_id: string;
  version?: string;
  timestamp: string;
  location: Location;
  risk: RiskSummary;
  evidence?: EvidenceStatus;
  impact?: ImpactSummary;
  priority?: Priority;
  actions?: {
    recommended?: ActionRecommendation[];
    requires_approval?: boolean;
  };
  human_decision?: HumanDecisionStatus;
  metadata: {
    is_simulated: boolean;
    partial_coverage?: boolean;
    disclaimer: string;
  };
}

export interface RoleOutput {
  role: 'CITIZEN' | 'DRIVER' | 'FIELD_WORKER' | 'DISTRICT_AUTHORITY' | 'EMERGENCY_COORDINATOR';
  message: string;
  risk_level?: string;
  confidence?: number;
  actions?: string[];
  disclaimer: string;
  is_simulated: boolean;
}
