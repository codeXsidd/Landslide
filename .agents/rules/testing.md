# NER-SAGE Testing Standards

## Requirements

Every engine must have tests before it is considered complete.

### Unit Tests — Per Engine

| Engine | Required Tests |
|--------|---------------|
| Evidence Reliability | Score calculation for each evidence type |
| Freshness Checker | Each threshold boundary (HIGH/MEDIUM/LOW) |
| Contradiction Detector | Conflicting signals, consistent signals, partial conflicts |
| Uncertainty Estimator | High uncertainty, low uncertainty, missing inputs |
| Unknown Tracker | KNOWN/UNKNOWN/STALE/CONFLICTING classification |
| Next-Best Evidence | Decision value ranking, acquisition cost weighting |
| Road Graph | Connectivity queries, path finding |
| Isolation Calculator | Village isolated, village accessible, partial connectivity |
| Risk Model | Inference with full features, inference with missing features |
| Calibration | Calibrated output in [0,1], Brier score check |
| Decision Ranker | Action ranking with multiple candidates |
| Simulation Engine | Rainfall +25%, road failure, combination scenarios |

### Integration Tests

| Test | What to Verify |
|------|---------------|
| FastAPI → MongoDB | Write and read a risk prediction document |
| FastAPI → Neo4j | Create road node, query connectivity |
| FastAPI → Redis | Cache set, cache hit, cache miss |
| FastAPI → Qdrant | Insert chunk, semantic search returns relevant result |
| Evidence Pipeline | Input observation → reliability scored → stored → retrievable |
| Decision Pipeline | Risk input → uncertainty → next-best → human approval recorded |

### API Tests (httpx TestClient)

Every route must have:
- Happy path test (200/201 response)
- Missing required field test (422 response)
- Unauthorized request test (401 response)
- Invalid location (outside NER bbox) test (400 response)

### End-to-End Demo Scenario Test

Run the full Road B SIH demo scenario programmatically:
1. Seed demo data
2. GET `/risk/road_b` → verify risk=0.82, confidence=0.54
3. GET `/uncertainty/road_b` → verify satellite STALE, ground MISSING
4. GET `/next-evidence/road_b` → verify Road B verification is top recommendation
5. POST `/evidence/verify` with citizen report
6. GET `/risk/road_b` → verify risk=0.88, confidence=0.91
7. GET `/impact/road_b` → verify isolation probability > 0
8. POST `/simulation` with rainfall +25%
9. GET `/priorities` → verify road inspection is top action
10. POST `/decisions` with APPROVE
11. Verify audit log entry created

This scenario test must pass before any demo. Location: `tests/e2e/test_road_b_scenario.py`.

## Test File Organization

```
tests/
├── unit/
│   ├── evidence/       test_reliability.py, test_freshness.py, ...
│   ├── decision/       test_ranker.py, test_action_scoring.py
│   ├── ml/             test_inference.py, test_calibration.py
│   └── graph/          test_isolation.py, test_routing.py
├── integration/
│   ├── test_mongodb.py
│   ├── test_neo4j.py
│   ├── test_redis.py
│   └── test_qdrant.py
├── api/
│   ├── test_risk_routes.py
│   ├── test_evidence_routes.py
│   ├── test_simulation_routes.py
│   └── test_decision_routes.py
└── e2e/
    └── test_road_b_scenario.py
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific engine
pytest tests/unit/evidence/ -v

# E2E demo scenario
pytest tests/e2e/test_road_b_scenario.py -v
```

## Coverage Targets

| Component | Target |
|-----------|--------|
| Evidence Engine | ≥ 85% |
| Decision Engine | ≥ 85% |
| Graph Engine | ≥ 80% |
| API Routes | ≥ 75% |
| ML Inference | ≥ 70% |
| Overall | ≥ 75% |
