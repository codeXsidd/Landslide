"""NER-LDI Evidence Update Loop - updates risk after new evidence arrives."""
import uuid
from datetime import datetime, timezone
from typing import Dict, List


def update_risk_with_evidence(current_state: Dict, new_evidence: Dict) -> Dict:
    """Update risk prediction after new evidence is incorporated."""
    audit_entry = {
        "update_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_added": new_evidence.get("evidence_type"),
        "previous_risk": current_state.get("risk_score"),
        "previous_confidence": current_state.get("confidence"),
    }

    # Bayesian-style update
    prior_risk = current_state.get("risk_score", 0.5)
    prior_confidence = current_state.get("confidence", 0.5)
    evidence_reliability = new_evidence.get("reliability", 0.5)
    evidence_supports_risk = new_evidence.get("supports_risk", None)

    if evidence_supports_risk is True:
        # Evidence confirms risk
        posterior_risk = prior_risk + (1 - prior_risk) * evidence_reliability * 0.2
    elif evidence_supports_risk is False:
        # Evidence contradicts risk
        posterior_risk = prior_risk - prior_risk * evidence_reliability * 0.2
    else:
        posterior_risk = prior_risk

    posterior_risk = max(0.0, min(1.0, posterior_risk))

    # Confidence increases with new reliable evidence
    confidence_boost = evidence_reliability * 0.1
    posterior_confidence = min(1.0, prior_confidence + confidence_boost)

    # Update risk level
    if posterior_risk >= 0.8:
        risk_level = "CRITICAL"
    elif posterior_risk >= 0.6:
        risk_level = "HIGH"
    elif posterior_risk >= 0.4:
        risk_level = "MODERATE"
    elif posterior_risk >= 0.2:
        risk_level = "LOW"
    else:
        risk_level = "VERY_LOW"

    audit_entry["new_risk"] = posterior_risk
    audit_entry["new_confidence"] = posterior_confidence
    audit_entry["update_method"] = "bayesian_evidence_update"

    updated_state = {**current_state}
    updated_state["risk_score"] = round(posterior_risk, 4)
    updated_state["risk_level"] = risk_level
    updated_state["confidence"] = round(posterior_confidence, 4)
    updated_state.setdefault("audit_trail", []).append(audit_entry)
    updated_state["last_updated"] = audit_entry["timestamp"]

    return updated_state
