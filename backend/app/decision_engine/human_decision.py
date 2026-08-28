"""NER-LDI Human Decision Loop - AI recommends, human decides."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional


def create_decision_record(location: Dict, risk_state: Dict, recommended_actions: list) -> Dict:
    """Create a decision record requiring human review."""
    needs_approval = any(a.get("requires_human_approval") for a in recommended_actions)

    return {
        "decision_id": str(uuid.uuid4()),
        "location": location,
        "risk_state": {
            "risk_score": risk_state.get("risk_score"),
            "risk_level": risk_state.get("risk_level"),
            "confidence": risk_state.get("confidence"),
        },
        "recommended_actions": recommended_actions,
        "human_approval_required": needs_approval,
        "human_decision": {"status": "PENDING"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_trail": [{
            "event": "CREATED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "system",
        }],
    }


def record_human_decision(decision_record: Dict, status: str, decided_by: str,
                          reason: str = "", modified_actions: list = None) -> Dict:
    """Record human approval/rejection/modification."""
    decision_record["human_decision"] = {
        "status": status,
        "decided_by": decided_by,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modified_actions": modified_actions,
    }
    decision_record["audit_trail"].append({
        "event": f"HUMAN_{status}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": decided_by,
        "reason": reason,
    })
    return decision_record


def record_outcome(decision_record: Dict, actual_event: bool, harm_realized: float = 0,
                   feedback_category: str = "CORRECT") -> Dict:
    """Record the actual outcome for learning."""
    decision_record["outcome"] = {
        "actual_event": actual_event,
        "harm_realized": harm_realized,
        "feedback_category": feedback_category,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    decision_record["audit_trail"].append({
        "event": "OUTCOME_RECORDED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feedback": feedback_category,
    })
    return decision_record
