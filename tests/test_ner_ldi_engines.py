"""Comprehensive tests for NER-LDI Decision Intelligence engines."""
import sys, json, copy
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

from evidence.uncertainty_engine import compute_uncertainty
from evidence.evidence_fusion import fuse_evidence
from evidence.contradiction_engine import detect_contradictions
from evidence.knowledge_gap_engine import identify_knowledge_gaps
from evidence.next_best_evidence import compute_next_best_evidence
from evidence.update_risk import update_risk_with_evidence
from evidence.citizen_verification import verify_citizen_evidence
from evidence.satellite_adapter import create_satellite_observation
from evidence.silent_zone_engine import detect_silent_zones
from impact.road_impact import compute_road_impact
from impact.village_isolation import compute_village_isolation, compute_infrastructure_exposure
from simulation.risk_simulation import run_simulation
from decision_engine.optimizer import optimize_actions
from decision_engine.human_decision import create_decision_record, record_human_decision, record_outcome


# ─── UNCERTAINTY ENGINE ────────────────────────────────────────────────────────

class TestUncertaintyEngine:
    def test_returns_all_fields(self):
        result = compute_uncertainty(0.6, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [])
        assert "risk_score" in result
        assert "confidence" in result
        assert "uncertainty_level" in result
        assert "uncertainty_reasons" in result
        assert "data_completeness" in result

    def test_confidence_bounded_0_1(self):
        result = compute_uncertainty(0.99, {"elevation": 5000, "slope": None, "aspect": None, "terrain_ruggedness": None},
                                     [{"reliability": 0.1, "freshness": "EXPIRED"}] * 10)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_partial_model_reduces_confidence(self):
        full = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [],
                                   model_version="2.0.0-dynamic")
        partial = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [],
                                      model_version="2.0.0-dynamic-partial")
        assert partial["confidence"] < full["confidence"]

    def test_missing_features_increase_uncertainty(self):
        full = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [])
        missing = compute_uncertainty(0.5, {"elevation": 500, "slope": None, "aspect": None, "terrain_ruggedness": 10}, [])
        assert missing["confidence"] < full["confidence"]

    def test_stale_evidence_penalizes(self):
        fresh = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10},
                                    [{"reliability": 0.8, "freshness": "FRESH"}])
        stale = compute_uncertainty(0.5, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10},
                                    [{"reliability": 0.8, "freshness": "STALE"}])
        assert stale["confidence"] <= fresh["confidence"]

    def test_high_elevation_ood(self):
        result = compute_uncertainty(0.5, {"elevation": 5000, "slope": 20, "aspect": 180, "terrain_ruggedness": 10}, [])
        assert any("training range" in r for r in result["uncertainty_reasons"])

    def test_uncertainty_levels(self):
        high_conf = compute_uncertainty(0.3, {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10},
                                        [{"reliability": 0.95, "freshness": "FRESH"}] * 3,
                                        model_version="2.0.0-dynamic")
        assert high_conf["uncertainty_level"] in ("LOW", "MODERATE", "HIGH", "VERY_HIGH")


# ─── EVIDENCE FUSION ──────────────────────────────────────────────────────────

class TestEvidenceFusion:
    def test_empty_returns_unknown(self):
        result = fuse_evidence([])
        assert result["status"] == "UNKNOWN"

    def test_known_status_with_good_evidence(self):
        items = [
            {"evidence_type": "rainfall", "source_type": "rainfall_sensor", "freshness": "FRESH", "reliability": 0.9, "value": {}},
            {"evidence_type": "terrain", "source_type": "model_output", "freshness": "FRESH", "reliability": 0.8, "value": {}},
            {"evidence_type": "satellite", "source_type": "satellite_sentinel", "freshness": "FRESH", "reliability": 0.92, "value": {}},
            {"evidence_type": "historical", "source_type": "historical", "freshness": "FRESH", "reliability": 0.7, "value": {}},
            {"evidence_type": "road_status", "source_type": "official_report", "freshness": "FRESH", "reliability": 0.9, "value": {}},
            {"evidence_type": "forecast", "source_type": "model_output", "freshness": "FRESH", "reliability": 0.8, "value": {}},
        ]
        result = fuse_evidence(items)
        assert result["status"] == "KNOWN"
        assert result["coverage"] == 1.0

    def test_stale_items_separated(self):
        items = [{"evidence_type": "rainfall", "freshness": "STALE", "reliability": 0.8, "value": {}}]
        result = fuse_evidence(items)
        assert len(result["stale"]) == 1

    def test_low_reliability_goes_to_uncertain(self):
        items = [{"evidence_type": "rainfall", "freshness": "FRESH", "reliability": 0.3, "value": {}}]
        result = fuse_evidence(items)
        assert len(result["uncertain"]) == 1

    def test_coverage_calculation(self):
        items = [
            {"evidence_type": "rainfall", "freshness": "FRESH", "reliability": 0.9, "value": {}},
            {"evidence_type": "terrain", "freshness": "FRESH", "reliability": 0.8, "value": {}},
        ]
        result = fuse_evidence(items)
        assert 0 < result["coverage"] < 1.0


# ─── CONTRADICTION ENGINE ─────────────────────────────────────────────────────

class TestContradictionEngine:
    def test_no_contradictions(self):
        items = [{"evidence_type": "rainfall", "source": "imerg", "value": {"intensity": "LOW"}}]
        result = detect_contradictions(items)
        assert result["has_contradictions"] is False
        assert result["contradiction_count"] == 0

    def test_rainfall_vs_satellite_contradiction(self):
        items = [
            {"evidence_type": "rainfall", "source": "imerg", "value": {"intensity": "HIGH"}},
            {"evidence_type": "satellite", "source": "sentinel", "value": {"change_detected": False}},
        ]
        result = detect_contradictions(items)
        assert result["has_contradictions"] is True
        assert any(c["type"] == "rainfall_vs_satellite" for c in result["contradictions"])

    def test_citizen_vs_model_contradiction(self):
        items = [
            {"evidence_type": "citizen_report", "source": "user_001", "value": "Large landslide blocking road"},
            {"evidence_type": "model_output", "source": "terrain_model", "value": {"risk_level": "LOW"}},
        ]
        result = detect_contradictions(items)
        assert result["has_contradictions"] is True
        assert any(c["type"] == "citizen_vs_model" for c in result["contradictions"])

    def test_road_status_conflict(self):
        items = [
            {"evidence_type": "road_status", "source": "official", "value": {"status": "OPEN"}},
            {"evidence_type": "road_status", "source": "citizen", "value": {"status": "BLOCKED"}},
        ]
        result = detect_contradictions(items)
        assert result["has_contradictions"] is True
        assert result["max_severity"] == "HIGH"


# ─── KNOWLEDGE GAP ENGINE ─────────────────────────────────────────────────────

class TestKnowledgeGapEngine:
    def test_all_missing_returns_many_gaps(self):
        result = identify_knowledge_gaps([], {"latitude": 25.0, "longitude": 93.0})
        assert result["total_gaps"] > 0
        assert result["critical_gaps"] > 0

    def test_full_evidence_low_gaps(self):
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        items = [
            {"evidence_type": "rainfall", "timestamp": now_iso, "reliability": 0.9},
            {"evidence_type": "terrain", "timestamp": now_iso, "reliability": 0.8},
            {"evidence_type": "satellite", "timestamp": now_iso, "reliability": 0.9},
            {"evidence_type": "historical", "timestamp": now_iso, "reliability": 0.7},
            {"evidence_type": "road_status", "timestamp": now_iso, "reliability": 0.9},
            {"evidence_type": "forecast", "timestamp": now_iso, "reliability": 0.8},
            {"evidence_type": "field_inspection", "timestamp": now_iso, "reliability": 0.95},
        ]
        result = identify_knowledge_gaps(items)
        assert result["total_gaps"] == 0

    def test_edge_location_flagged(self):
        items = [{"evidence_type": "rainfall", "timestamp": "2026-08-27T10:00:00Z", "reliability": 0.9}]
        result = identify_knowledge_gaps(items, {"latitude": 28.0, "longitude": 93.0})
        assert any(i.get("evidence_type") == "spatial" for i in result["uncertain_items"])

    def test_knowledge_completeness_between_0_1(self):
        result = identify_knowledge_gaps([])
        assert 0.0 <= result["knowledge_completeness"] <= 1.0


# ─── NEXT-BEST-EVIDENCE ENGINE ────────────────────────────────────────────────

class TestNextBestEvidence:
    def test_returns_recommendation(self):
        gaps = {"unknown_items": [{"evidence_type": "road_status"}], "stale_items": [], "total_gaps": 1, "critical_gaps": 1}
        result = compute_next_best_evidence(0.7, 0.5, gaps)
        assert "recommended_observation" in result
        assert result["information_value"] > 0

    def test_high_confidence_low_value(self):
        gaps = {"unknown_items": [], "stale_items": [], "total_gaps": 0, "critical_gaps": 0}
        result = compute_next_best_evidence(0.3, 0.9, gaps)
        # Low uncertainty means lower information value
        assert result["information_value"] < 5.0

    def test_urgency_critical_for_high_risk(self):
        gaps = {"unknown_items": [{"evidence_type": "field_inspection"}], "stale_items": [], "total_gaps": 1, "critical_gaps": 1}
        result = compute_next_best_evidence(0.85, 0.4, gaps)
        assert result["urgency"] == "CRITICAL"

    def test_candidates_sorted_by_value(self):
        gaps = {"unknown_items": [{"evidence_type": "road_status"}], "stale_items": [], "total_gaps": 1, "critical_gaps": 1}
        result = compute_next_best_evidence(0.6, 0.5, gaps)
        values = [c["information_value"] for c in result["all_candidates"]]
        assert values == sorted(values, reverse=True)


# ─── RISK UPDATE ENGINE ───────────────────────────────────────────────────────

class TestRiskUpdate:
    def test_supporting_evidence_increases_risk(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "citizen_report", "reliability": 0.8, "supports_risk": True})
        assert updated["risk_score"] > 0.5

    def test_contradicting_evidence_decreases_risk(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "satellite", "reliability": 0.8, "supports_risk": False})
        assert updated["risk_score"] < 0.5

    def test_neutral_evidence_preserves_risk(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "other", "reliability": 0.8, "supports_risk": None})
        assert updated["risk_score"] == 0.5

    def test_confidence_increases_with_new_evidence(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "field", "reliability": 0.9, "supports_risk": True})
        assert updated["confidence"] > 0.5

    def test_risk_bounded_0_1(self):
        state = {"risk_score": 0.99, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "x", "reliability": 1.0, "supports_risk": True})
        assert updated["risk_score"] <= 1.0
        state2 = {"risk_score": 0.01, "confidence": 0.5}
        updated2 = update_risk_with_evidence(state2, {"evidence_type": "x", "reliability": 1.0, "supports_risk": False})
        assert updated2["risk_score"] >= 0.0

    def test_audit_trail_maintained(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "test", "reliability": 0.5, "supports_risk": True})
        assert "audit_trail" in updated
        assert len(updated["audit_trail"]) == 1

    def test_risk_level_categories(self):
        state = {"risk_score": 0.9, "confidence": 0.5}
        updated = update_risk_with_evidence(state, {"evidence_type": "x", "reliability": 0.9, "supports_risk": True})
        assert updated["risk_level"] in ("CRITICAL", "HIGH", "MODERATE", "LOW", "VERY_LOW")

    def test_does_not_mutate_input(self):
        state = {"risk_score": 0.5, "confidence": 0.5}
        original = copy.deepcopy(state)
        update_risk_with_evidence(state, {"evidence_type": "test", "reliability": 0.5, "supports_risk": True})
        assert state == original


# ─── CITIZEN VERIFICATION ─────────────────────────────────────────────────────

class TestCitizenVerification:
    def test_good_report_likely_valid(self):
        report = {
            "latitude": 25.5, "longitude": 93.0,
            "timestamp": "2026-08-27T10:00:00Z",
            "description": "Large landslide blocking road with debris and mud everywhere",
            "image_keys": ["img1.jpg"],
        }
        result = verify_citizen_evidence(report)
        assert result["reliability_score"] >= 0.7
        assert result["validation_status"] == "LIKELY_VALID"

    def test_outside_ner_low_score(self):
        report = {"latitude": 10.0, "longitude": 50.0, "description": "slide"}
        result = verify_citizen_evidence(report)
        assert result["reliability_score"] < 0.7

    def test_empty_description_low_score(self):
        report = {"latitude": 25.5, "longitude": 93.0, "description": ""}
        result = verify_citizen_evidence(report)
        assert result["reliability_score"] < 0.8

    def test_simulated_flag_propagated(self):
        report = {"latitude": 25.5, "longitude": 93.0, "description": "test", "is_simulated": True}
        result = verify_citizen_evidence(report)
        assert result["is_simulated"] is True


# ─── ROAD IMPACT ENGINE ───────────────────────────────────────────────────────

class TestRoadImpact:
    def test_returns_structure(self):
        result = compute_road_impact(25.5, 93.0, 0.7)
        assert "road_blockage_probability" in result
        assert "affected_roads" in result
        assert "road_risk_level" in result

    def test_blockage_bounded(self):
        result = compute_road_impact(25.5, 93.0, 1.0)
        assert 0 <= result["road_blockage_probability"] <= 1.0

    def test_low_risk_low_blockage(self):
        result = compute_road_impact(25.5, 93.0, 0.1)
        assert result["road_blockage_probability"] < 0.5

    def test_outside_coverage_empty(self):
        result = compute_road_impact(10.0, 10.0, 0.9)
        assert result["road_blockage_probability"] == 0
        assert len(result["affected_roads"]) == 0


# ─── VILLAGE ISOLATION ENGINE ─────────────────────────────────────────────────

class TestVillageIsolation:
    def test_returns_structure(self):
        result = compute_village_isolation(25.5, 93.0, 0.7)
        assert "village_isolation_probability" in result
        assert "villages_at_risk" in result
        assert "population_affected" in result

    def test_isolation_bounded(self):
        result = compute_village_isolation(25.5, 93.0, 1.0)
        assert 0 <= result["village_isolation_probability"] <= 1.0

    def test_zero_blockage_no_isolation(self):
        result = compute_village_isolation(25.5, 93.0, 0.0)
        assert result["village_isolation_probability"] == 0


class TestInfrastructureExposure:
    def test_returns_structure(self):
        result = compute_infrastructure_exposure(25.5, 93.0, 0.7)
        assert "exposure_score" in result
        assert "critical_assets" in result
        assert "population_exposed" in result

    def test_exposure_bounded(self):
        result = compute_infrastructure_exposure(25.5, 93.0, 1.0)
        assert 0 <= result["exposure_score"] <= 1.0


# ─── SIMULATION ENGINE ────────────────────────────────────────────────────────

class TestSimulation:
    def test_does_not_mutate_baseline(self):
        baseline = {"risk_score": 0.5, "rainfall_features": {"rainfall_1d": 50}}
        original = copy.deepcopy(baseline)
        run_simulation(baseline, {"type": "rainfall_increase", "rainfall_factor": 2.0})
        assert baseline == original

    def test_rainfall_increase_raises_risk(self):
        baseline = {"risk_score": 0.5, "rainfall_features": {"rainfall_1d": 50}}
        result = run_simulation(baseline, {"type": "rainfall_increase", "rainfall_factor": 2.0})
        assert result["simulated_state"]["risk_score"] > baseline["risk_score"]
        assert result["delta"]["risk_change"] > 0

    def test_road_closure_scenario(self):
        baseline = {"risk_score": 0.5, "road_blockage_probability": 0.2, "village_isolation_probability": 0.1}
        result = run_simulation(baseline, {"type": "road_closure", "road_closure": True})
        assert result["simulated_state"]["road_blockage_probability"] >= 0.9
        assert result["simulated_state"]["village_isolation_probability"] >= 0.7

    def test_simulation_id_unique(self):
        baseline = {"risk_score": 0.5}
        r1 = run_simulation(baseline, {"type": "test"})
        r2 = run_simulation(baseline, {"type": "test"})
        assert r1["simulation_id"] != r2["simulation_id"]

    def test_is_simulated_flag(self):
        result = run_simulation({"risk_score": 0.5}, {"type": "test"})
        assert result["is_simulated"] is True


# ─── OPTIMIZER ENGINE ─────────────────────────────────────────────────────────

class TestOptimizer:
    def test_selects_actions_within_budget(self):
        locations = [{"location_id": "loc1", "risk_score": 0.7, "population_exposed": 500}]
        result = optimize_actions(locations, budget=20, teams=3)
        assert result["total_cost"] <= 20
        assert len(result["selected_actions"]) <= 3

    def test_empty_locations(self):
        result = optimize_actions([], budget=20, teams=3)
        assert len(result["selected_actions"]) == 0

    def test_zero_budget_no_actions(self):
        locations = [{"location_id": "loc1", "risk_score": 0.9, "population_exposed": 1000}]
        result = optimize_actions(locations, budget=0, teams=3)
        assert len(result["selected_actions"]) == 0

    def test_actions_sorted_by_efficiency(self):
        locations = [{"location_id": "loc1", "risk_score": 0.8, "population_exposed": 2000}]
        result = optimize_actions(locations, budget=50, teams=10)
        efficiencies = [a["efficiency"] for a in result["selected_actions"]]
        assert efficiencies == sorted(efficiencies, reverse=True)

    def test_approval_flag(self):
        locations = [{"location_id": "loc1", "risk_score": 0.9, "population_exposed": 5000}]
        result = optimize_actions(locations, budget=50, teams=10)
        if result["any_requires_approval"]:
            assert any(a["requires_human_approval"] for a in result["selected_actions"])


# ─── HUMAN DECISION ENGINE ────────────────────────────────────────────────────

class TestHumanDecision:
    def test_create_decision_record(self):
        loc = {"latitude": 25.5, "longitude": 93.0}
        risk = {"risk_score": 0.7, "risk_level": "HIGH", "confidence": 0.6}
        actions = [{"action": "inspect_road", "requires_human_approval": False}]
        record = create_decision_record(loc, risk, actions)
        assert record["human_decision"]["status"] == "PENDING"
        assert "decision_id" in record
        assert len(record["audit_trail"]) == 1

    def test_approve_decision(self):
        loc = {"latitude": 25.5, "longitude": 93.0}
        risk = {"risk_score": 0.7, "risk_level": "HIGH", "confidence": 0.6}
        actions = [{"action": "issue_warning_recommendation", "requires_human_approval": True}]
        record = create_decision_record(loc, risk, actions)
        record = record_human_decision(record, "APPROVED", "officer_1", "Confirmed by field team")
        assert record["human_decision"]["status"] == "APPROVED"
        assert record["human_decision"]["decided_by"] == "officer_1"
        assert len(record["audit_trail"]) == 2

    def test_reject_decision(self):
        loc = {"latitude": 25.5, "longitude": 93.0}
        risk = {"risk_score": 0.4, "risk_level": "MODERATE", "confidence": 0.7}
        actions = [{"action": "prepare_evacuation_support", "requires_human_approval": True}]
        record = create_decision_record(loc, risk, actions)
        record = record_human_decision(record, "REJECTED", "officer_2", "False alarm")
        assert record["human_decision"]["status"] == "REJECTED"

    def test_record_outcome(self):
        loc = {"latitude": 25.5, "longitude": 93.0}
        risk = {"risk_score": 0.7, "risk_level": "HIGH", "confidence": 0.6}
        actions = [{"action": "inspect_road", "requires_human_approval": False}]
        record = create_decision_record(loc, risk, actions)
        record = record_human_decision(record, "APPROVED", "officer_1")
        record = record_outcome(record, actual_event=True, harm_realized=0.3, feedback_category="CORRECT")
        assert record["outcome"]["actual_event"] is True
        assert record["outcome"]["feedback_category"] == "CORRECT"
        assert len(record["audit_trail"]) == 3

    def test_full_loop(self):
        loc = {"latitude": 25.5, "longitude": 93.0, "location_id": "test_loc"}
        risk = {"risk_score": 0.8, "risk_level": "HIGH", "confidence": 0.6}
        actions = [{"action": "restrict_corridor_recommendation", "requires_human_approval": True}]
        record = create_decision_record(loc, risk, actions)
        assert record["human_approval_required"] is True
        record = record_human_decision(record, "APPROVED", "dm_officer", "Field radio confirms")
        record = record_outcome(record, actual_event=True, harm_realized=0.1, feedback_category="CORRECT")
        assert record["human_decision"]["status"] == "APPROVED"
        assert record["outcome"]["harm_realized"] == 0.1


# ─── SATELLITE ADAPTER ────────────────────────────────────────────────────────

class TestSatelliteAdapter:
    def test_creates_observation(self):
        obs = create_satellite_observation(source="sentinel_2", lat=25.5, lon=93.0)
        assert obs["is_simulated"] is True
        assert "timestamp" in obs
        assert obs["source"] == "sentinel_2"


# ─── INTEGRATION: DEMO FLOW ──────────────────────────────────────────────────

class TestDemoIntegration:
    def test_full_pipeline_completes(self):
        """Run the complete decision loop end-to-end."""
        # Step 1: Initial state
        risk_state = {"risk_score": 0.65, "confidence": 0.55,
                      "terrain_features": {"elevation": 850, "slope": 32, "aspect": 180, "terrain_ruggedness": 28},
                      "rainfall_features": {"rainfall_1d": 45, "rainfall_3d": 120, "rainfall_7d": 280}}
        evidence_items = [
            {"evidence_id": "ev1", "source": "IMERG", "source_type": "rainfall_sensor",
             "evidence_type": "rainfall", "timestamp": "2026-08-27T05:00:00Z",
             "value": {"intensity": "HIGH", "rainfall_24h": 85}, "reliability": 0.88, "freshness": "FRESH"},
        ]

        # Step 2: Uncertainty
        unc = compute_uncertainty(risk_state["risk_score"], risk_state["terrain_features"], evidence_items)
        assert 0 <= unc["confidence"] <= 1

        # Step 3: Evidence fusion
        fusion = fuse_evidence(evidence_items)
        assert fusion["status"] in ("KNOWN", "UNKNOWN", "STALE", "UNCERTAIN", "CONFLICTING")

        # Step 4: Risk update
        updated = update_risk_with_evidence(risk_state, {"evidence_type": "citizen_report", "reliability": 0.75, "supports_risk": True})
        assert updated["risk_score"] > risk_state["risk_score"]

        # Step 5: Road impact
        road = compute_road_impact(25.5, 93.0, updated["risk_score"])
        assert "road_blockage_probability" in road

        # Step 6: Simulation
        sim = run_simulation(updated, {"type": "rainfall_increase", "rainfall_factor": 1.5})
        assert sim["is_simulated"] is True

        # Step 7: Optimization
        opt = optimize_actions([{"location_id": "test", "risk_score": updated["risk_score"], "population_exposed": 200}])
        assert "selected_actions" in opt

        # Step 8: Human decision
        decision = create_decision_record({"latitude": 25.5, "longitude": 93.0}, updated, opt["selected_actions"])
        decision = record_human_decision(decision, "APPROVED", "test_officer")
        decision = record_outcome(decision, actual_event=True, harm_realized=0.2)
        assert decision["outcome"]["actual_event"] is True
