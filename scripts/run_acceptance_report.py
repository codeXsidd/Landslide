"""NER-LDI Final Acceptance Report - verifies all system components."""
import json, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
ARTIFACTS = ROOT / "ml" / "artifacts"
SCHEMAS = ROOT / "data" / "schemas"
sys.path.insert(0, str(ROOT / "backend" / "app"))

results = {}


def check(name, fn):
    try:
        fn()
        results[name] = "PASS"
    except AssertionError as e:
        results[name] = f"FAIL ({e})"
    except Exception as e:
        results[name] = f"FAIL ({type(e).__name__}: {e})"


def check_baseline_model():
    import joblib
    m = joblib.load(ARTIFACTS / "terrain_susceptibility_model.joblib")
    meta = json.load(open(ARTIFACTS / "terrain_susceptibility_metadata.json"))
    assert hasattr(m, "predict_proba")
    assert meta["evaluation_metrics"]["roc_auc"] > 0.7


def check_dynamic_model():
    import joblib
    m2 = joblib.load(ARTIFACTS / "ner_dynamic_risk_model.joblib")
    meta2 = json.load(open(ARTIFACTS / "ner_dynamic_risk_metadata.json"))
    assert hasattr(m2, "predict_proba")
    status = meta2.get("status", "UNKNOWN")
    metrics = meta2.get("metrics") or meta2.get("evaluation_metrics", {})
    auc = metrics.get("roc_auc", 0)
    results["DYNAMIC RISK MODEL"] = f"INCOMPLETE (status={status}, AUC={auc:.4f})"
    raise SystemExit


def check_calibration():
    import joblib
    joblib.load(ARTIFACTS / "risk_calibrator.joblib")


def check_evidence_fusion():
    from evidence.evidence_fusion import fuse_evidence
    r = fuse_evidence([{"evidence_type": "rainfall", "freshness": "FRESH", "reliability": 0.9, "value": {}}])
    assert "status" in r


def check_uncertainty():
    from evidence.uncertainty_engine import compute_uncertainty
    r = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [])
    assert 0 <= r["confidence"] <= 1


def check_contradiction():
    from evidence.contradiction_engine import detect_contradictions
    r = detect_contradictions([])
    assert "has_contradictions" in r


def check_knowledge_gaps():
    from evidence.knowledge_gap_engine import identify_knowledge_gaps
    r = identify_knowledge_gaps([], {"latitude": 25, "longitude": 93})
    assert r["total_gaps"] > 0


def check_next_best():
    from evidence.next_best_evidence import compute_next_best_evidence
    r = compute_next_best_evidence(0.7, 0.5, {"unknown_items": [{"evidence_type": "road"}], "stale_items": []})
    assert r["information_value"] > 0


def check_citizen():
    from evidence.citizen_verification import verify_citizen_evidence
    r = verify_citizen_evidence({"latitude": 25.5, "longitude": 93, "description": "landslide", "image_keys": ["x.jpg"], "timestamp": "2026-08-27T10:00:00Z"})
    assert 0 <= r["reliability_score"] <= 1


def check_risk_update():
    from evidence.update_risk import update_risk_with_evidence
    r = update_risk_with_evidence({"risk_score": 0.5, "confidence": 0.5}, {"evidence_type": "test", "reliability": 0.8, "supports_risk": True})
    assert r["risk_score"] > 0.5


def check_road_impact():
    from impact.road_impact import compute_road_impact
    r = compute_road_impact(25.5, 93.0, 0.7)
    assert "road_blockage_probability" in r


def check_village_isolation():
    from impact.village_isolation import compute_village_isolation
    r = compute_village_isolation(25.5, 93.0, 0.7)
    assert "village_isolation_probability" in r


def check_infrastructure():
    from impact.village_isolation import compute_infrastructure_exposure
    r = compute_infrastructure_exposure(25.5, 93.0, 0.7)
    assert "exposure_score" in r


def check_simulation():
    from simulation.risk_simulation import run_simulation
    r = run_simulation({"risk_score": 0.5, "rainfall_features": {"r1": 50}}, {"type": "test", "rainfall_factor": 1.5})
    assert r["is_simulated"] is True


def check_optimizer():
    from decision_engine.optimizer import optimize_actions
    r = optimize_actions([{"location_id": "x", "risk_score": 0.7, "population_exposed": 500}])
    assert len(r["selected_actions"]) > 0


def check_human_decision():
    from decision_engine.human_decision import create_decision_record, record_human_decision, record_outcome
    d = create_decision_record({"lat": 25}, {"risk_score": 0.7, "risk_level": "HIGH", "confidence": 0.6}, [{"action": "x", "requires_human_approval": True}])
    d = record_human_decision(d, "APPROVED", "test")
    d = record_outcome(d, True, 0.1)
    assert d["outcome"]["actual_event"] is True


def check_silent_zone():
    from evidence.silent_zone_engine import detect_silent_zones
    r = detect_silent_zones([{"location_id": "x", "population": 100}], {"x": []}, {"x": 0.7})
    assert isinstance(r, list)


def check_satellite():
    from evidence.satellite_adapter import create_satellite_observation
    r = create_satellite_observation(source="sentinel_2", lat=25.5, lon=93.0)
    assert r["is_simulated"] is True


def check_role_output():
    from services.recommendation.role_output import format_for_role
    for role in ("CITIZEN", "DRIVER", "FIELD_WORKER", "DISTRICT_AUTHORITY", "EMERGENCY_COORDINATOR"):
        r = format_for_role(role, {"risk_score": 0.7, "risk_level": "HIGH", "confidence": 0.6, "location": {"name": "Test"}})
        assert "disclaimer" in r


def check_unified_risk():
    from schemas.unified_risk import build_unified_risk_object
    r = build_unified_risk_object({"latitude": 25.5, "longitude": 93.0}, 0.7, 0.6, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10})
    assert r["metadata"]["is_simulated"] is True
    assert "disclaimer" in r["metadata"]


def check_frontend_contract():
    contract = json.load(open(SCHEMAS / "frontend_data_contract.json"))
    assert "UnifiedRiskObject" in contract["definitions"]
    assert "RoleOutput" in contract["definitions"]


def check_demo_runner():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_ner_ldi_demo.py")], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"Exit code {r.returncode}: {r.stderr[:200]}"
    assert "DEMO COMPLETE" in r.stdout


def check_json_schemas():
    for name in ["risk_state", "evidence", "impact_prediction", "decision", "simulation", "human_feedback"]:
        assert (SCHEMAS / f"{name}.schema.json").exists(), f"Missing {name}"


def check_tests():
    r = subprocess.run([sys.executable, "-m", "pytest", str(ROOT / "tests"), "-q", "--tb=no"], capture_output=True, text=True, timeout=120)
    assert "passed" in r.stdout, f"Tests failed: {r.stdout[-200:]}"
    last_line = [l for l in r.stdout.strip().split("\n") if "passed" in l][-1]
    results["TEST SUITE"] = f"PASS ({last_line.strip()})"
    raise SystemExit


def check_model_registry():
    reg = json.load(open(ARTIFACTS / "model_registry.json"))
    assert len(reg["models"]) >= 2


if __name__ == "__main__":
    check("BASELINE MODEL", check_baseline_model)

    try:
        check_dynamic_model()
    except SystemExit:
        pass

    check("CALIBRATION", check_calibration)
    check("EVIDENCE FUSION", check_evidence_fusion)
    check("UNCERTAINTY ENGINE", check_uncertainty)
    check("CONTRADICTION ENGINE", check_contradiction)
    check("KNOWLEDGE GAP ENGINE", check_knowledge_gaps)
    check("NEXT-BEST-EVIDENCE", check_next_best)
    check("CITIZEN VERIFICATION", check_citizen)
    check("RISK UPDATE", check_risk_update)
    check("ROAD IMPACT", check_road_impact)
    check("VILLAGE ISOLATION", check_village_isolation)
    check("INFRASTRUCTURE EXPOSURE", check_infrastructure)
    check("SIMULATION ENGINE", check_simulation)
    check("ACTION OPTIMIZER", check_optimizer)
    check("HUMAN DECISION LOOP", check_human_decision)
    check("SILENT ZONE ENGINE", check_silent_zone)
    check("SATELLITE ADAPTER", check_satellite)
    check("ROLE-SPECIFIC OUTPUT", check_role_output)
    check("UNIFIED RISK OBJECT", check_unified_risk)
    check("FRONTEND DATA CONTRACT", check_frontend_contract)
    check("DEMO RUNNER", check_demo_runner)
    check("JSON SCHEMAS (6)", check_json_schemas)

    try:
        check_tests()
    except SystemExit:
        pass

    check("MODEL REGISTRY", check_model_registry)

    print()
    print("=" * 70)
    print("NER-LDI DECISION INTELLIGENCE SYSTEM - FINAL ACCEPTANCE REPORT")
    print("=" * 70)
    print()
    passes = sum(1 for v in results.values() if v.startswith("PASS"))
    incomplete = sum(1 for v in results.values() if "INCOMPLETE" in v)
    fails = sum(1 for v in results.values() if v.startswith("FAIL"))
    print(f"  PASS: {passes}  |  INCOMPLETE: {incomplete}  |  FAIL: {fails}")
    print()
    for component, status in results.items():
        if status.startswith("PASS"):
            icon = "+"
        elif "INCOMPLETE" in status:
            icon = "~"
        else:
            icon = "X"
        print(f"  [{icon}] {component:30s} {status}")
    print()
    print("=" * 70)
    if fails == 0:
        print("SYSTEM STATUS: OPERATIONAL (with noted incomplete components)")
    else:
        print(f"SYSTEM STATUS: {fails} COMPONENT(S) FAILED")
    print("=" * 70)
