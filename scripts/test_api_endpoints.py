"""Test NER-LDI API endpoints without external database dependencies."""
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi import FastAPI

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

from api.routes.ldi import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_health():
    r = client.get("/ldi/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["is_simulated"] is True
    print("[PASS] GET /ldi/health")


def test_assess():
    payload = {
        "latitude": 25.5,
        "longitude": 93.0,
        "risk_score": 0.7,
        "name": "Test Location",
        "terrain_features": {"elevation": 850, "slope": 32, "aspect": 180, "terrain_ruggedness": 28},
        "rainfall_features": {"rainfall_1d": 45, "rainfall_3d": 120, "rainfall_7d": 280},
        "evidence": [
            {"evidence_type": "rainfall", "source_type": "rainfall_sensor", "source": "IMERG",
             "freshness": "FRESH", "reliability": 0.88, "value": {"intensity": "HIGH"}},
        ]
    }
    r = client.post("/ldi/assess", json=payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:300]}"
    data = r.json()
    unified = data["unified_risk"]

    # Verify all required fields from the spec
    assert unified["risk"]["score"] is not None
    assert unified["risk"]["level"] in ("VERY_LOW", "LOW", "MODERATE", "HIGH", "CRITICAL")
    assert 0 <= unified["risk"]["confidence"] <= 1
    assert unified["uncertainty"]["level"] in ("LOW", "MODERATE", "HIGH", "VERY_HIGH", "UNKNOWN")
    assert unified["evidence"]["fusion_status"] in ("KNOWN", "UNKNOWN", "UNCERTAIN", "CONFLICTING", "STALE")
    assert "road_blockage_probability" in unified["impact"]
    assert "village_isolation_probability" in unified["impact"]
    assert "population_exposed" in unified["impact"]
    assert "score" in unified["priority"]
    assert isinstance(unified["actions"]["recommended"], list)
    assert "requires_approval" in unified["actions"]
    assert unified["human_decision"]["status"] in ("PENDING", "APPROVED", "REJECTED", "MODIFIED", "NOT_REQUIRED")
    assert unified["metadata"]["is_simulated"] is True
    assert "disclaimer" in unified["metadata"]
    assert "timestamp" in unified
    assert unified["risk"]["model_version"] is not None

    # Next-best-evidence
    assert data["next_best_evidence"]["information_value"] > 0

    # Verify disclaimer present
    assert "disclaimer" in data

    print("[PASS] POST /ldi/assess - full unified risk object verified")
    print(f"       risk_score={unified['risk']['score']}, level={unified['risk']['level']}, confidence={unified['risk']['confidence']}")
    print(f"       uncertainty={unified['uncertainty']['level']}, evidence={unified['evidence']['fusion_status']}")
    print(f"       priority={unified['priority']['score']}, road_blockage={unified['impact']['road_blockage_probability']}")
    print(f"       actions={len(unified['actions']['recommended'])}, approval_needed={unified['actions']['requires_approval']}")


def test_simulate():
    payload = {
        "baseline_state": {"risk_score": 0.6, "rainfall_features": {"rainfall_1d": 50, "rainfall_3d": 120}},
        "scenario": {"type": "rainfall_increase", "rainfall_factor": 2.0}
    }
    r = client.post("/ldi/simulate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["is_simulated"] is True
    assert data["simulated_state"]["risk_score"] > 0.6
    assert data["delta"]["risk_change"] > 0
    print(f"[PASS] POST /ldi/simulate - risk {0.6:.4f} -> {data['simulated_state']['risk_score']:.4f} (delta={data['delta']['risk_change']:+.4f})")


def test_role_output():
    roles = ["CITIZEN", "DRIVER", "FIELD_WORKER", "DISTRICT_AUTHORITY", "EMERGENCY_COORDINATOR"]
    for role in roles:
        payload = {
            "role": role,
            "risk_state": {"risk_score": 0.75, "risk_level": "HIGH", "confidence": 0.6, "location": {"name": "Haflong"}},
            "impact": {"road_blockage_probability": 0.6, "affected_roads": [{"name": "NH44", "road_id": "r1"}], "population_affected": 2000},
            "actions": {"selected_actions": [{"action": "inspect_road", "requires_human_approval": False}], "any_requires_approval": False}
        }
        r = client.post("/ldi/role-output", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == role
        assert "disclaimer" in data
        assert data["is_simulated"] is True
    print(f"[PASS] POST /ldi/role-output - all 5 roles verified")


def test_assess_missing_coords():
    r = client.post("/ldi/assess", json={"risk_score": 0.5})
    assert r.status_code == 400
    print("[PASS] POST /ldi/assess - rejects missing coordinates")


def test_simulate_missing_fields():
    r = client.post("/ldi/simulate", json={"baseline_state": {}})
    assert r.status_code == 400
    print("[PASS] POST /ldi/simulate - rejects missing scenario")


def test_role_output_invalid_role():
    r = client.post("/ldi/role-output", json={"role": "INVALID", "risk_state": {"risk_score": 0.5}})
    assert r.status_code == 400
    print("[PASS] POST /ldi/role-output - rejects invalid role")


if __name__ == "__main__":
    print("=" * 60)
    print("NER-LDI API ENDPOINT VERIFICATION")
    print("=" * 60)
    print()

    tests = [test_health, test_assess, test_simulate, test_role_output,
             test_assess_missing_coords, test_simulate_missing_fields, test_role_output_invalid_role]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"API TESTS: {passed}/{passed+failed} PASS")
    if failed == 0:
        print("API STATUS: PASS")
    else:
        print(f"API STATUS: FAIL ({failed} failures)")
    print("=" * 60)
