"""NER-LDI What-If Simulation Engine."""
import uuid, copy
from datetime import datetime, timezone
from typing import Dict


def run_simulation(baseline_state: Dict, scenario: Dict) -> Dict:
    """Run a what-if simulation without mutating the base state."""
    sim_id = str(uuid.uuid4())
    simulated = copy.deepcopy(baseline_state)

    scenario_type = scenario.get("type", "custom")
    rainfall_factor = scenario.get("rainfall_factor", 1.0)
    road_closure = scenario.get("road_closure", False)

    # Apply rainfall change
    if rainfall_factor != 1.0:
        base_risk = simulated.get("risk_score", 0.5)
        # Rainfall increase raises risk non-linearly
        risk_boost = (rainfall_factor - 1.0) * 0.3 * base_risk
        simulated["risk_score"] = min(1.0, base_risk + risk_boost)
        simulated["rainfall_features"] = {
            k: (v * rainfall_factor if v else None)
            for k, v in (simulated.get("rainfall_features") or {}).items()
        }

    # Apply road closure
    if road_closure:
        simulated["road_blockage_probability"] = max(simulated.get("road_blockage_probability", 0), 0.9)
        simulated["village_isolation_probability"] = max(simulated.get("village_isolation_probability", 0), 0.7)

    # Recalculate priority
    risk = simulated.get("risk_score", 0.5)
    pop = simulated.get("population_exposed", 0)
    simulated["priority_score"] = min(1.0, risk * 0.6 + (pop / 10000) * 0.4)

    # Update risk level
    r = simulated["risk_score"]
    simulated["risk_level"] = "CRITICAL" if r >= 0.8 else "HIGH" if r >= 0.6 else "MODERATE" if r >= 0.4 else "LOW" if r >= 0.2 else "VERY_LOW"

    delta = {
        "risk_change": simulated["risk_score"] - baseline_state.get("risk_score", 0.5),
        "priority_change": simulated.get("priority_score", 0) - baseline_state.get("priority_score", 0),
        "isolation_change": simulated.get("village_isolation_probability", 0) - baseline_state.get("village_isolation_probability", 0),
    }

    return {
        "simulation_id": sim_id,
        "scenario_type": scenario_type,
        "input_changes": scenario,
        "baseline_state": baseline_state,
        "simulated_state": simulated,
        "delta": delta,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_simulated": True,
    }
