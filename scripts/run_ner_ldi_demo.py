"""
NER-LDI Demo Scenario Runner
Replays the complete decision intelligence loop with fixed seed.
All evidence is simulated (is_simulated=True).
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

from evidence.uncertainty_engine import compute_uncertainty
from evidence.evidence_fusion import fuse_evidence
from evidence.contradiction_engine import detect_contradictions
from evidence.knowledge_gap_engine import identify_knowledge_gaps
from evidence.next_best_evidence import compute_next_best_evidence
from evidence.update_risk import update_risk_with_evidence
from evidence.citizen_verification import verify_citizen_evidence
from evidence.satellite_adapter import create_satellite_observation  # noqa: F401
from impact.road_impact import compute_road_impact
from impact.village_isolation import compute_village_isolation, compute_infrastructure_exposure
from simulation.risk_simulation import run_simulation
from decision_engine.optimizer import optimize_actions
from decision_engine.human_decision import create_decision_record, record_human_decision, record_outcome


def run_demo():
    print("=" * 60)
    print("NER-LDI DECISION INTELLIGENCE DEMO")
    print("All evidence is SIMULATED (is_simulated=True)")
    print("=" * 60)

    location = {"latitude": 25.5, "longitude": 93.0, "location_id": "demo_loc_01", "name": "Haflong Road Corridor"}

    # Step 1: Terrain + rainfall triggers elevated risk
    print("\n[1] INITIAL RISK ASSESSMENT")
    risk_state = {
        "location": location,
        "risk_score": 0.65, "risk_level": "HIGH", "confidence": 0.55,
        "terrain_features": {"elevation": 850, "slope": 32, "aspect": 180, "terrain_ruggedness": 28},
        "rainfall_features": {"rainfall_1d": 45, "rainfall_3d": 120, "rainfall_7d": 280},
        "model_version": "2.0.0-dynamic-partial", "timestamp": "2024-06-05T06:00:00Z",
    }
    print(f"  Risk: {risk_state['risk_score']}, Confidence: {risk_state['confidence']}")

    # Step 2: Evidence collection
    print("\n[2] EVIDENCE COLLECTION")
    evidence_items = [
        {"evidence_id": "ev1", "source": "IMERG", "source_type": "rainfall_sensor", "evidence_type": "rainfall",
         "timestamp": "2024-06-05T05:00:00Z", "value": {"intensity": "HIGH", "rainfall_24h": 85},
         "reliability": 0.88, "freshness": "FRESH", "is_simulated": True},
        {"evidence_id": "ev2", "source": "terrain_model", "source_type": "model_output", "evidence_type": "terrain",
         "timestamp": "2024-06-05T06:00:00Z", "value": {"risk_level": "HIGH"},
         "reliability": 0.82, "freshness": "FRESH", "is_simulated": True},
        {"evidence_id": "ev3", "source": "sentinel_2", "source_type": "satellite", "evidence_type": "satellite",
         "timestamp": "2024-06-02T10:00:00Z", "value": {"change_detected": False},
         "reliability": 0.85, "freshness": "STALE", "is_simulated": True},
    ]
    print(f"  Sources: {len(evidence_items)} (rainfall=FRESH, satellite=STALE)")

    # Step 3: Uncertainty
    print("\n[3] UNCERTAINTY COMPUTATION")
    unc = compute_uncertainty(risk_state["risk_score"], risk_state["terrain_features"], evidence_items)
    risk_state["confidence"] = unc["confidence"]
    print(f"  Confidence: {unc['confidence']:.3f}, Level: {unc['uncertainty_level']}")
    print(f"  Reasons: {unc['uncertainty_reasons']}")

    # Step 4: Evidence fusion
    print("\n[4] EVIDENCE FUSION")
    fusion = fuse_evidence(evidence_items)
    print(f"  Status: {fusion['status']}, Coverage: {fusion['coverage']:.0%}")

    # Step 5: Contradiction detection
    print("\n[5] CONTRADICTION DETECTION")
    contradictions = detect_contradictions(evidence_items)
    print(f"  Contradictions: {contradictions['contradiction_count']}")
    if contradictions["contradictions"]:
        for c in contradictions["contradictions"]:
            print(f"    - {c['type']}: {c['explanation'][:60]}...")

    # Step 6: Knowledge gaps
    print("\n[6] KNOWLEDGE GAPS")
    gaps = identify_knowledge_gaps(evidence_items, location)
    print(f"  Total gaps: {gaps['total_gaps']}, Critical: {gaps['critical_gaps']}")
    for g in gaps["unknown_items"][:3]:
        print(f"    - Missing: {g['evidence_type']}")

    # Step 7: Next-best-evidence
    print("\n[7] NEXT-BEST-EVIDENCE RECOMMENDATION")
    nbe = compute_next_best_evidence(risk_state["risk_score"], unc["confidence"], gaps)
    print(f"  Recommended: {nbe['recommended_observation']}")
    print(f"  Information value: {nbe['information_value']:.3f}, Urgency: {nbe['urgency']}")

    # Step 8: Citizen evidence
    print("\n[8] CITIZEN EVIDENCE ARRIVES (SIMULATED)")
    citizen = {
        "latitude": 25.505, "longitude": 93.002,
        "timestamp": "2024-06-05T08:30:00Z",
        "description": "Large debris slide blocking road near km 42. Mud and rocks everywhere.",
        "image_keys": ["img_001.jpg"], "is_simulated": True,
    }
    verified = verify_citizen_evidence(citizen)
    print(f"  Reliability: {verified['reliability_score']:.3f}, Status: {verified['validation_status']}")

    # Step 9: Risk update
    print("\n[9] RISK UPDATE")
    risk_state = update_risk_with_evidence(risk_state, {"evidence_type": "citizen_report", "reliability": verified["reliability_score"], "supports_risk": True, "is_simulated": True})
    print(f"  Updated risk: {risk_state['risk_score']:.4f}, Confidence: {risk_state['confidence']:.4f}")

    # Step 10: Road impact
    print("\n[10] ROAD IMPACT ASSESSMENT")
    road = compute_road_impact(location["latitude"], location["longitude"], risk_state["risk_score"])
    risk_state["road_blockage_probability"] = road["road_blockage_probability"]
    print(f"  Blockage probability: {road['road_blockage_probability']:.3f}")
    print(f"  Affected roads: {len(road['affected_roads'])}")

    # Step 11: Village isolation
    print("\n[11] VILLAGE ISOLATION")
    isolation = compute_village_isolation(location["latitude"], location["longitude"], road["road_blockage_probability"])
    risk_state["village_isolation_probability"] = isolation["village_isolation_probability"]
    risk_state["population_exposed"] = isolation["population_affected"]
    print(f"  Isolation probability: {isolation['village_isolation_probability']:.3f}")
    print(f"  Population affected: {isolation['population_affected']}")

    # Step 12: Infrastructure exposure
    print("\n[12] INFRASTRUCTURE EXPOSURE")
    exposure = compute_infrastructure_exposure(location["latitude"], location["longitude"], risk_state["risk_score"])
    print(f"  Exposure score: {exposure['exposure_score']:.3f}")
    print(f"  Critical assets: {len(exposure['critical_assets'])}")

    # Step 13: What-if simulation
    print("\n[13] WHAT-IF SIMULATION (Rainfall +50%)")
    sim = run_simulation(risk_state, {"type": "rainfall_increase", "rainfall_factor": 1.5})
    print(f"  Simulated risk: {sim['simulated_state']['risk_score']:.4f} (delta: {sim['delta']['risk_change']:+.4f})")

    # Step 14: Priority
    print("\n[14] PRIORITY CALCULATION")
    risk_state["priority_score"] = min(1.0, risk_state["risk_score"] * 0.5 + (risk_state.get("population_exposed", 0) / 5000) * 0.3 + road["road_blockage_probability"] * 0.2)
    print(f"  Priority: {risk_state['priority_score']:.3f}")

    # Step 15: Action optimization
    print("\n[15] ACTION OPTIMIZATION")
    opt = optimize_actions([{**location, **risk_state}])
    print(f"  Selected actions: {len(opt['selected_actions'])}")
    for a in opt["selected_actions"][:3]:
        print(f"    - {a['action']} (harm reduction: {a['expected_harm_reduction']:.3f})")

    # Step 16: Human decision
    print("\n[16] HUMAN DECISION")
    decision = create_decision_record(location, risk_state, opt["selected_actions"])
    decision = record_human_decision(decision, "APPROVED", "district_dm_officer", "Field radio confirms. Approve.")
    decision = record_outcome(decision, actual_event=True, harm_realized=0.2, feedback_category="CORRECT")
    print(f"  Status: {decision['human_decision']['status']}")
    print(f"  Outcome: {decision['outcome']['feedback_category']}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE - All evidence was SIMULATED")
    print("=" * 60)
    print(f"\nFinal Risk: {risk_state['risk_score']:.4f}")
    print(f"Final Confidence: {risk_state['confidence']:.4f}")
    print(f"Population at risk: {risk_state.get('population_exposed', 0)}")
    return True


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
