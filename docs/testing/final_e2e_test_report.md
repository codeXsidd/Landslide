# NER-LDI Full System End-to-End Test Report

**Date:** 2026-08-28
**Environment:** Windows 11, Python 3.13, Node 20+, Vite 5.4.21

---

## OVERALL SYSTEM: PARTIAL

---

## Individual Component Results

| Component | Status | Notes |
|-----------|--------|-------|
| Data (landslides) | PASS | 10,982 GSI events, cleaned + NER-filtered |
| Data (terrain) | PARTIAL | 24/57 SRTM cells. elevation, slope, aspect, TRI exist |
| Data (rainfall) | PARTIAL | 7-day IMERG rainfall_daily.parquet exists |
| Data (roads) | PASS | ner_roads.geojson present |
| Data (villages) | PASS | ner_villages.geojson present |
| Data (infrastructure) | PASS | ner_infrastructure.geojson present |
| ML baseline (RandomForest) | PASS | ROC-AUC 0.843, trained on 23,895 samples |
| ML dynamic (XGBoost) | PARTIAL | ROC-AUC 0.790, marked INCOMPLETE (7-day rainfall only) |
| ML calibrator | PASS | Isotonic calibration model exists |
| ML inference | BLOCKED | scipy DLL blocked by Windows AppControl policy |
| FastAPI startup | PASS | Server starts with graceful DB degradation |
| FastAPI CORS | PASS | localhost:5173 allowed |
| API /ldi/health | PASS | Returns status ok |
| API /ldi/assess | PASS | Full pipeline returns unified risk object |
| API /ldi/simulate | PASS | Correct simulation with preserved baseline |
| API /risk/predict | PASS | Stub fallback works (real model blocked by DLL) |
| API /evidence | FAIL | Requires MongoDB (expected when DB offline) |
| API /decisions | FAIL | Requires MongoDB (expected when DB offline) |
| Evidence fusion | PASS | KNOWN/UNKNOWN/STALE/CONFLICTING states work |
| Contradiction detection | PASS | Detects conflicting evidence |
| Knowledge gaps | PASS | Identifies 7 gaps, 4 critical |
| Next-best-evidence | PASS | Ranks 5 candidates by information value |
| Evidence verification | PASS | Citizen report verification pipeline works |
| Risk update | PASS | Updates risk score + confidence after evidence |
| Road impact | PASS | Computes blockage probability, alternate routes |
| Village isolation | PASS | Population affected, hospital access computed |
| Infrastructure exposure | PASS | Critical assets identified |
| Simulation engine | PASS | Baseline preserved, delta computed correctly |
| Action optimization | PASS | 3 actions selected within budget constraints |
| Human decision | PASS | APPROVE/REJECT/MODIFY with audit trail |
| Feedback/outcome | PASS | Records actual outcome + feedback category |
| RAG | NOT AVAILABLE | No Groq API key configured |
| React frontend | PASS | Builds, type-checks, loads |
| Frontend build | PASS | tsc + vite build successful |
| Frontend lint | PASS | 0 errors, 8 warnings |
| Frontend-to-backend | PASS | CORS works, /ldi/simulate reachable |
| Simulation UI | PASS | Shows REAL BACKEND RESULT vs SIMULATED DEMO |
| Evidence UI | PASS | Shows [REAL BACKEND] vs [DEMO] labels |
| Decision UI | PASS | Shows [REAL BACKEND] vs [DEMO] labels |
| Map | PASS | Leaflet with OSM tiles, NER center |
| Demo script (16 steps) | PASS | All steps complete successfully |
| Security | PASS | No secrets in source, .env gitignored |
| Offline recovery | PASS | Frontend shows fallback, recovers on reconnect |
| Tests | PASS | 62/62 passed |
| Build | PASS | Frontend builds successfully |

---

## Critical Fixes Applied

1. **LDI router not registered** in `main.py` - added `app.include_router(ldi_router)`
2. **Frontend called wrong routes** - `/simulation/run` fixed to `/ldi/simulate`, `/evidence/submit` to `/evidence`, `/decision/human-review` to `/decisions`
3. **CORS missing localhost:5173** - added to allowed origins
4. **Backend lifespan hard-failed** without databases - made DB connections graceful with try/except
5. **structlog crash** - removed incompatible `add_logger_name` processor
6. **auth.py exported `auth` not `router`** - renamed to `router`
7. **Simulation route imported non-existent module** - fixed to use `app.simulation.risk_simulation`
8. **LDI route used fragile sys.path manipulation** - fixed to absolute `app.` imports
9. **Neo4j/Redis connection hangs** - added connection timeouts (3s)
10. **Qdrant function name mismatch** - `ensure_collections` → `init_qdrant_collections`
11. **TypeScript store type mismatch** - fixed SimulationResult assignment
12. **GISMap lint error** - removed unnecessary SSR guard
13. **Missing ESLint config** - created `.eslintrc.cjs`
14. **Missing frontend `.env`** - created with `VITE_API_BASE_URL`

---

## Known Limitations (Verified)

- Terrain coverage: 24/57 SRTM cells (PARTIAL)
- Rainfall: only 7 days of IMERG data
- Dynamic model: marked INCOMPLETE, not production-ready
- Satellite observations: SIMULATED
- Roads/villages/infrastructure: representative, not exhaustive
- MongoDB/Neo4j/Redis: required for evidence persistence and decisions (not for LDI pipeline)
- ML inference: blocked by Windows AppControl on scipy DLL (environment issue, not code issue)
- RAG: requires Groq API key (not configured)

---

## Files Changed

- `backend/app/main.py` - graceful startup, LDI router registration, qdrant function name
- `backend/app/config/settings.py` - CORS origins (added localhost:5173)
- `backend/app/config/logging.py` - removed incompatible processor
- `backend/app/api/routes/auth.py` - renamed `auth` to `router`
- `backend/app/api/routes/simulation.py` - fixed import, renamed function
- `backend/app/api/routes/ldi.py` - fixed imports to absolute paths
- `backend/app/database/neo4j.py` - added connection_timeout
- `backend/app/database/redis.py` - added socket timeouts
- `frontend/.env` - created
- `frontend/.eslintrc.cjs` - created
- `frontend/src/services/api.ts` - fixed all route paths, added proper types
- `frontend/src/pages/Simulation.tsx` - real backend vs demo distinction, loading state
- `frontend/src/pages/Evidence.tsx` - backend vs demo labels
- `frontend/src/pages/Decisions.tsx` - backend vs demo labels
- `frontend/src/store/appStore.ts` - fixed type errors
- `frontend/src/components/map/GISMap.tsx` - removed SSR guard (lint fix)
