# NER-LDI Final Model Verification Report

**Date**: 2026-08-27  
**Status**: OPERATIONAL (with noted incomplete components)

---

## 1. BASELINE MODEL (RandomForest)

| Metric | Value |
|--------|-------|
| Model Type | RandomForest (200 trees) |
| Features | elevation, slope, aspect, terrain_ruggedness |
| Training Rows | 23,895 |
| Positive Samples | 7,965 (landslide locations from GSI inventory) |
| Negative Samples | 15,930 (random terrain with min 0.01° buffer) |
| Spatial Split | 0.5° block grid (no spatial leakage) |
| **ROC-AUC** | **0.8433** |
| PR-AUC | 0.4911 |
| F1 | 0.5917 |
| Brier Score | 0.1503 |
| Accuracy | 0.7642 |
| Precision | 0.4678 |
| Recall | 0.8046 |
| Status | **ACTIVE** |

### Real Inference Results (5 positive, 5 negative samples):
- Correctly identified **4/5 positives** as LANDSLIDE
- Correctly identified **3/5 negatives** as STABLE
- Probabilities range from 0.0137 to 0.8355

---

## 2. DYNAMIC RISK MODEL (XGBoost)

| Metric | Value |
|--------|-------|
| Model Type | XGBoost |
| Features | elevation, slope, aspect, terrain_ruggedness, rainfall_1d, rainfall_3d, rainfall_7d, antecedent_rainfall_index |
| Training Rows | 17,940 |
| Test Rows | 5,955 |
| Positive Samples | 6,026 |
| Negative Samples | 11,914 |
| **ROC-AUC** | **0.7904** |
| PR-AUC | 0.5860 |
| F1 | 0.4901 |
| Status | **INCOMPLETE** |

### Why INCOMPLETE:
- Only 7 days of IMERG rainfall data available (2024-06-01 to 2024-06-07)
- Insufficient historical rainfall coverage for production use
- Architecture is complete and functional
- Model trains and infers correctly on available data
- **NOT fabricated**: uses only real terrain + limited real rainfall

### Real Inference Results:
- Correctly identified **3/5 positives** as LANDSLIDE
- Correctly identified **3/5 negatives** as STABLE

---

## 3. CALIBRATION

| Metric | Value |
|--------|-------|
| Type | CalibratedClassifierCV (Isotonic) |
| Base Model | XGBoost (dynamic) |
| Input Features | 8 (terrain + rainfall) |
| Status | ACTIVE |

Note: Calibrator wraps the dynamic model (8 features). Cannot be applied to baseline (4 features) directly.

---

## 4. API ENDPOINTS — VERIFIED

| Endpoint | Status | Description |
|----------|--------|-------------|
| GET /ldi/health | PASS | System health |
| POST /ldi/assess | PASS | Full decision intelligence assessment |
| POST /ldi/simulate | PASS | What-if simulation |
| POST /ldi/role-output | PASS | Role-specific output (5 roles) |

All endpoints return `is_simulated: true` and include disclaimer.

### Unified Risk Response Fields (all verified PRESENT):
- risk_score, risk_level, confidence
- uncertainty (level + reasons)
- evidence_status (KNOWN/UNKNOWN/UNCERTAIN/CONFLICTING/STALE)
- knowledge_gaps, critical_gaps, contradictions
- road_blockage_probability, village_isolation_probability
- population_exposed
- priority_score
- recommended_next_evidence
- recommended_actions
- human_approval_required
- model_version, timestamp

---

## 5. TEST SUITE

| Suite | Tests | Status |
|-------|-------|--------|
| test_terrain.py | 29 | ALL PASS |
| test_ml_terrain.py | 16 | ALL PASS |
| test_ner_ldi_engines.py | 62 | ALL PASS |
| Other | 5 | ALL PASS |
| **Total** | **112** | **ALL PASS** |

---

## 6. ENGINES VERIFIED

| Engine | Status |
|--------|--------|
| Uncertainty Engine | PASS |
| Evidence Fusion | PASS |
| Contradiction Engine | PASS |
| Knowledge Gap Engine | PASS |
| Next-Best-Evidence | PASS |
| Citizen Verification | PASS |
| Risk Update (Bayesian) | PASS |
| Silent Zone Engine | PASS |
| Satellite Adapter (simulated) | PASS |
| Road Impact | PASS |
| Village Isolation | PASS |
| Infrastructure Exposure | PASS |
| Simulation Engine | PASS |
| Action Optimizer | PASS |
| Human Decision Loop | PASS |
| Role-Specific Output | PASS |
| Unified Risk Object | PASS |
| Frontend Data Contract | PASS |
| Model Registry | PASS |

---

## 7. KNOWN DATA LIMITATIONS

1. **Terrain coverage**: 24/57 required SRTM cells valid (33 blocked by OpenTopography 50-call/24hr rate limit)
2. **Rainfall**: Only 7 days IMERG (2024-06-01 to 2024-06-07). Insufficient for production dynamic model.
3. **Satellite**: No real Sentinel-2/SAR connected. Adapter interface exists, returns simulated data.
4. **Roads/Villages/Infrastructure**: Synthetic GeoJSON (44 roads, 98 villages, 109 infrastructure features). Real OSM/Census data not yet ingested.
5. **Citizen reports**: Demo only. No real-time collection system connected.
6. **Dynamic model degradation**: AUC dropped from 0.8433 (terrain-only) to 0.7904 (terrain+rainfall) because rainfall features are near-constant across only 7 days — this is expected and will improve with historical data.

---

## 8. SAFETY VERIFICATION

- [x] All outputs include `is_simulated: true`
- [x] All outputs include disclaimer: "AI-generated recommendation. Not an official emergency warning."
- [x] No fabricated data used for training
- [x] Partial coverage explicitly acknowledged in model metadata (`status: INCOMPLETE`)
- [x] Human approval required for high-impact actions
- [x] Audit trail maintained for every decision
- [x] No API keys exposed in code/logs/manifests
- [x] .env remains git-ignored
