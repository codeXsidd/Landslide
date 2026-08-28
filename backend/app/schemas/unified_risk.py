"""NER-LDI Unified Risk Object - single source of truth for a location's risk state."""
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid


def build_unified_risk_object(
    location: Dict,
    risk_score: float,
    confidence: float,
    terrain_features: Dict,
    rainfall_features: Dict = None,
    evidence_fusion: Dict = None,
    uncertainty: Dict = None,
    contradictions: Dict = None,
    knowledge_gaps: Dict = None,
    road_impact: Dict = None,
    village_isolation: Dict = None,
    infrastructure_exposure: Dict = None,
    simulation: Dict = None,
    optimization: Dict = None,
    human_decision: Dict = None,
    model_version: str = "2.0.0-dynamic-partial",
) -> Dict:
    """Assemble the complete unified risk object for a single location."""
    risk_level = _risk_level(risk_score)
    pop_exposed = (village_isolation or {}).get("population_affected", 0)
    priority = min(1.0, risk_score * 0.5 + (pop_exposed / 5000) * 0.3 +
                   (road_impact or {}).get("road_blockage_probability", 0) * 0.2)

    return {
        "object_id": str(uuid.uuid4()),
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "risk": {
            "score": round(risk_score, 4),
            "level": risk_level,
            "confidence": round(confidence, 4),
            "model_version": model_version,
        },
        "features": {
            "terrain": terrain_features,
            "rainfall": rainfall_features or {},
        },
        "evidence": {
            "fusion_status": (evidence_fusion or {}).get("status", "UNKNOWN"),
            "coverage": (evidence_fusion or {}).get("coverage", 0),
            "contradictions": (contradictions or {}).get("contradiction_count", 0),
            "knowledge_gaps": (knowledge_gaps or {}).get("total_gaps", 0),
            "critical_gaps": (knowledge_gaps or {}).get("critical_gaps", 0),
        },
        "uncertainty": {
            "level": (uncertainty or {}).get("uncertainty_level", "UNKNOWN"),
            "reasons": (uncertainty or {}).get("uncertainty_reasons", []),
            "data_completeness": (uncertainty or {}).get("data_completeness", 0),
        },
        "impact": {
            "road_blockage_probability": (road_impact or {}).get("road_blockage_probability", 0),
            "village_isolation_probability": (village_isolation or {}).get("village_isolation_probability", 0),
            "population_exposed": pop_exposed,
            "infrastructure_exposure_score": (infrastructure_exposure or {}).get("exposure_score", 0),
            "critical_assets_count": len((infrastructure_exposure or {}).get("critical_assets", [])),
        },
        "priority": {
            "score": round(priority, 4),
            "level": "CRITICAL" if priority > 0.8 else "HIGH" if priority > 0.6 else "MODERATE" if priority > 0.4 else "LOW",
        },
        "simulation": {
            "available": simulation is not None,
            "scenario_type": (simulation or {}).get("scenario_type"),
            "risk_delta": (simulation or {}).get("delta", {}).get("risk_change", 0),
        },
        "actions": {
            "recommended": (optimization or {}).get("selected_actions", []),
            "total_cost": (optimization or {}).get("total_cost", 0),
            "requires_approval": (optimization or {}).get("any_requires_approval", False),
        },
        "human_decision": {
            "status": (human_decision or {}).get("human_decision", {}).get("status", "NOT_REQUIRED"),
            "decided_by": (human_decision or {}).get("human_decision", {}).get("decided_by"),
        },
        "metadata": {
            "is_simulated": True,
            "partial_coverage": "partial" in model_version,
            "disclaimer": "AI-generated risk assessment. Not an official warning.",
        },
    }


def _risk_level(score: float) -> str:
    if score >= 0.8:
        return "CRITICAL"
    elif score >= 0.6:
        return "HIGH"
    elif score >= 0.4:
        return "MODERATE"
    elif score >= 0.2:
        return "LOW"
    return "VERY_LOW"
