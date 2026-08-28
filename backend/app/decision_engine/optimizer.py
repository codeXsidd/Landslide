"""NER-LDI Resource-Constrained Action Optimizer."""
from typing import Dict, List


INTERVENTIONS = [
    {"action": "inspect_road", "cost": 2, "time_hours": 3, "harm_reduction_factor": 0.1},
    {"action": "field_verification", "cost": 3, "time_hours": 4, "harm_reduction_factor": 0.15},
    {"action": "prepare_route", "cost": 5, "time_hours": 6, "harm_reduction_factor": 0.2},
    {"action": "pre_position_team", "cost": 8, "time_hours": 2, "harm_reduction_factor": 0.3},
    {"action": "increase_monitoring", "cost": 1, "time_hours": 1, "harm_reduction_factor": 0.05},
    {"action": "issue_warning_recommendation", "cost": 1, "time_hours": 0.5, "harm_reduction_factor": 0.25},
    {"action": "restrict_corridor_recommendation", "cost": 4, "time_hours": 1, "harm_reduction_factor": 0.35},
    {"action": "prepare_evacuation_support", "cost": 10, "time_hours": 4, "harm_reduction_factor": 0.4},
]


def optimize_actions(locations: List[Dict], budget: float = 20, teams: int = 3) -> Dict:
    """Greedy optimization: maximize expected harm reduction under resource constraints."""
    candidates = []

    for loc in locations:
        risk = loc.get("risk_score", 0.5)
        pop = loc.get("population_exposed", 100)
        expected_harm = risk * pop / 1000

        for intervention in INTERVENTIONS:
            if intervention["cost"] > budget:
                continue
            reduction = intervention["harm_reduction_factor"] * expected_harm
            efficiency = reduction / max(intervention["cost"], 0.1)
            candidates.append({
                "location_id": loc.get("location_id", "unknown"),
                "action": intervention["action"],
                "cost": intervention["cost"],
                "time_hours": intervention["time_hours"],
                "expected_harm_reduction": round(reduction, 4),
                "efficiency": round(efficiency, 4),
                "requires_human_approval": intervention["action"] in ("restrict_corridor_recommendation", "prepare_evacuation_support", "issue_warning_recommendation"),
            })

    # Greedy selection
    candidates.sort(key=lambda x: x["efficiency"], reverse=True)
    selected = []
    remaining_budget = budget
    remaining_teams = teams

    for c in candidates:
        if c["cost"] <= remaining_budget and remaining_teams > 0:
            selected.append(c)
            remaining_budget -= c["cost"]
            remaining_teams -= 1

    return {
        "selected_actions": selected,
        "total_cost": budget - remaining_budget,
        "total_harm_reduction": sum(a["expected_harm_reduction"] for a in selected),
        "remaining_budget": remaining_budget,
        "any_requires_approval": any(a["requires_human_approval"] for a in selected),
    }
