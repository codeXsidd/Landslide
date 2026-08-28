"""NER-LDI Role-Specific Output Formatter.

Produces tailored risk communication for each stakeholder role.
AI output is explicitly framed as a recommendation, never as an official warning.
"""
from typing import Dict

ROLES = ("CITIZEN", "DRIVER", "FIELD_WORKER", "DISTRICT_AUTHORITY", "EMERGENCY_COORDINATOR")


def format_for_role(role: str, risk_state: Dict, impact: Dict = None, actions: Dict = None) -> Dict:
    """Format risk information for a specific stakeholder role."""
    if role not in ROLES:
        return {"error": f"Unknown role: {role}. Valid: {ROLES}"}

    risk_score = risk_state.get("risk_score", 0)
    risk_level = risk_state.get("risk_level", "UNKNOWN")
    confidence = risk_state.get("confidence", 0)
    location_name = risk_state.get("location", {}).get("name", "this area")

    base = {
        "role": role,
        "risk_level": risk_level,
        "confidence": confidence,
        "location": location_name,
        "disclaimer": "AI-generated recommendation only. Not an official emergency warning. Follow instructions from authorized disaster management authorities.",
        "is_simulated": risk_state.get("is_simulated", True),
    }

    if role == "CITIZEN":
        base["message"] = _citizen_message(risk_level, location_name)
        base["actions"] = ["Stay informed via official channels", "Prepare emergency supplies if HIGH/CRITICAL"]
        base["detail_level"] = "LOW"

    elif role == "DRIVER":
        blockage = (impact or {}).get("road_blockage_probability", 0)
        affected = (impact or {}).get("affected_roads", [])
        base["message"] = _driver_message(risk_level, blockage, affected)
        base["road_status"] = {"blockage_probability": blockage, "affected_count": len(affected)}
        base["actions"] = ["Check alternate routes", "Avoid affected corridors if blockage probability > 50%"]
        base["detail_level"] = "MEDIUM"

    elif role == "FIELD_WORKER":
        base["message"] = f"Risk assessment: {risk_level} ({risk_score:.2f}) with confidence {confidence:.2f}"
        base["terrain"] = risk_state.get("terrain_features", {})
        base["rainfall"] = risk_state.get("rainfall_features", {})
        base["actions"] = _field_worker_actions(risk_level, actions)
        base["detail_level"] = "HIGH"

    elif role == "DISTRICT_AUTHORITY":
        pop = (impact or {}).get("population_affected", 0)
        base["message"] = f"RECOMMENDATION: {risk_level} risk at {location_name}. Population potentially affected: {pop}."
        base["summary"] = {
            "risk_score": risk_score, "confidence": confidence,
            "population_exposed": pop,
            "road_blockage": (impact or {}).get("road_blockage_probability", 0),
            "village_isolation": (impact or {}).get("village_isolation_probability", 0),
        }
        base["recommended_actions"] = (actions or {}).get("selected_actions", [])
        base["approval_needed"] = (actions or {}).get("any_requires_approval", False)
        base["detail_level"] = "HIGH"

    elif role == "EMERGENCY_COORDINATOR":
        base["message"] = f"System recommendation: {risk_level} ({risk_score:.3f}, conf={confidence:.3f})"
        base["full_state"] = risk_state
        base["impact"] = impact or {}
        base["optimization"] = actions or {}
        base["detail_level"] = "FULL"

    return base


def _citizen_message(risk_level: str, location: str) -> str:
    if risk_level in ("CRITICAL", "HIGH"):
        return f"Elevated landslide risk reported near {location}. Follow guidance from local authorities. This is an AI recommendation, not an official warning."
    elif risk_level == "MODERATE":
        return f"Moderate landslide risk near {location}. Stay alert and monitor official channels."
    return f"Low landslide risk near {location}. No immediate action recommended."


def _driver_message(risk_level: str, blockage_prob: float, affected: list) -> str:
    if blockage_prob > 0.6:
        roads = ", ".join(r.get("name", r.get("road_id", "unknown"))[:20] for r in affected[:3])
        return f"High road blockage risk ({blockage_prob:.0%}). Potentially affected: {roads}. Consider alternate routes."
    elif blockage_prob > 0.3:
        return f"Moderate road disruption possible ({blockage_prob:.0%}). Drive with caution."
    return "Roads currently assessed as low risk. Normal travel conditions expected."


def _field_worker_actions(risk_level: str, actions: dict = None) -> list:
    base_actions = []
    if risk_level in ("CRITICAL", "HIGH"):
        base_actions = ["Conduct ground-truth inspection", "Document conditions with photos", "Report findings to control room"]
    elif risk_level == "MODERATE":
        base_actions = ["Visual inspection recommended", "Check drainage and slope stability indicators"]
    else:
        base_actions = ["Routine monitoring sufficient"]
    if actions and actions.get("selected_actions"):
        base_actions.extend(a["action"] for a in actions["selected_actions"][:3])
    return base_actions
