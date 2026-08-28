# NER-LDI Complete Model Architecture

## System Overview

The NER Landslide Decision Intelligence (NER-LDI) system is a multi-stage pipeline that transforms raw terrain and rainfall observations into actionable, human-reviewed risk recommendations for Northeast India.

**Critical disclaimer**: All outputs are AI-generated recommendations. The system is NOT an official emergency warning authority.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  OBSERVE → PREDICT → QUESTION → MEASURE UNCERTAINTY            │
│  → IDENTIFY GAPS → NEXT-BEST-EVIDENCE → HUMAN VERIFICATION    │
│  → UPDATE RISK → ASSESS CONSEQUENCES → SIMULATE               │
│  → PRIORITIZE → OPTIMIZE → HUMAN APPROVAL → FEEDBACK          │
│  → CALIBRATION                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 1: OBSERVE
- **Terrain**: SRTM GL1 30m DEM → elevation, slope, aspect, TRI
- **Rainfall**: NASA GPM IMERG (7 days available: 2024-06-01 to 2024-06-07)
- **Satellite**: Sentinel-2 adapter (SIMULATED - no real data connected)
- **Citizen Reports**: Field evidence with reliability scoring
- **Road/Infrastructure**: GeoJSON network (44 roads, 98 villages, 109 infrastructure)

### Layer 2: PREDICT
- **Baseline Model**: RandomForest (terrain-only), ROC-AUC = 0.8433
- **Dynamic Model**: XGBoost (terrain + rainfall), ROC-AUC = 0.7904 (INCOMPLETE - partial rainfall data)
- **Calibration**: Isotonic regression (Brier: 0.0902 → 0.0603)

### Layer 3: QUESTION (Uncertainty & Gaps)
- **Uncertainty Engine**: Separates risk score from confidence
- **Evidence Fusion**: KNOWN/UNKNOWN/UNCERTAIN/CONFLICTING/STALE classification
- **Contradiction Engine**: Detects rainfall-vs-satellite, citizen-vs-model conflicts
- **Knowledge Gap Engine**: Identifies what the system doesn't know
- **Silent Zone Engine**: Finds high-risk areas with no recent observations

### Layer 4: NEXT-BEST-EVIDENCE
- Information Value = (Uncertainty × Reliability × Decision Importance) / Cost
- Recommends most valuable next observation to acquire
- Candidate actions: field inspection, satellite refresh, road verification, etc.

### Layer 5: UPDATE
- Bayesian-style risk update when new evidence arrives
- Audit trail maintained for every update
- Evidence reliability weighted into posterior

### Layer 6: IMPACT ASSESSMENT
- **Road Impact**: Blockage probability using road network proximity
- **Village Isolation**: Population cut off from services
- **Infrastructure Exposure**: Critical assets (hospitals, schools) at risk

### Layer 7: SIMULATE
- What-if scenarios (rainfall +50%, road closure)
- Immutable baseline - simulations never mutate real state
- Delta computation for each scenario

### Layer 8: OPTIMIZE & DECIDE
- Greedy resource-constrained action selection
- Budget and team constraints
- Actions requiring human approval clearly flagged

### Layer 9: HUMAN-IN-THE-LOOP
- All high-impact actions require human approval
- Decision records: PENDING → APPROVED/REJECTED/MODIFIED
- Outcome recording for feedback loop
- Full audit trail

### Layer 10: ROLE-SPECIFIC OUTPUT
- CITIZEN: Simple messages, official channel guidance
- DRIVER: Road status, alternate routes
- FIELD_WORKER: Technical details, inspection checklists
- DISTRICT_AUTHORITY: Population impact, approval actions
- EMERGENCY_COORDINATOR: Full system state

## Data Coverage Status

| Component | Coverage | Status |
|-----------|----------|--------|
| Terrain (SRTM) | 24/57 required cells | PARTIAL (API rate limited) |
| Rainfall (IMERG) | 7 days only | PARTIAL |
| Satellite | 0 real observations | SIMULATED |
| Roads/Villages | Synthetic GeoJSON | SIMULATED |
| Citizen Reports | Demo only | SIMULATED |
| Historical Inventory | GSI 1460 landslides | REAL |

## Model Registry

| Model | Type | Status | Metric |
|-------|------|--------|--------|
| terrain_susceptibility_v1.0.0 | RandomForest | ACTIVE | AUC=0.8433 |
| ner_dynamic_risk_v2.0.0 | XGBoost | INCOMPLETE | AUC=0.7904 |
| risk_calibrator | Isotonic | ACTIVE | Brier=0.0603 |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /ldi/assess | Full decision intelligence assessment |
| POST | /ldi/simulate | What-if simulation |
| POST | /ldi/role-output | Role-specific formatted output |
| GET | /ldi/health | System health check |

## Safety Constraints

1. **Never claim official authority** - all outputs include disclaimer
2. **Never fabricate data** - simulated data explicitly marked `is_simulated: true`
3. **Never silently upgrade simulated→real** - provenance tracked
4. **Human approval required** for high-impact actions
5. **Audit trail** for every decision and state change
6. **Partial coverage acknowledged** - model metadata states INCOMPLETE where applicable
