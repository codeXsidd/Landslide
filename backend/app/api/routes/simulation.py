"""
NER-SAGE — Simulation API Routes

POST /simulation              - Run a what-if simulation scenario
GET  /simulation/{id}         - Get simulation results
"""

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_collection

router = APIRouter()


@router.post("/simulation", summary="Run a what-if simulation scenario", status_code=201)
async def run_simulation_route(payload: dict):
    """
    Runs a what-if simulation scenario. Supported scenario types:
    - rainfall_increase: Simulate increased rainfall (e.g., +25%)
    - road_failure: Simulate Road X failing
    - evidence_update: Simulate new evidence arrival
    - intervention: Simulate a response action effect
    """
    required = ["location_id", "scenario_type"]
    for f in required:
        if f not in payload:
            raise HTTPException(status_code=422, detail=f"Missing required field: {f}")

    from app.simulation.risk_simulation import run_simulation

    baseline_state = {
        "risk_score": 0.72,
        "road_blockage_probability": 0.45,
        "village_isolation_probability": 0.32,
        "population_exposed": 850,
        "rainfall_features": {"cumulative_7d": 120, "intensity_max": 35},
    }
    scenario = {
        "type": payload.get("scenario_type"),
        "rainfall_factor": payload.get("rainfall_multiplier", 1.0),
        "road_closure": payload.get("road_failure", False),
    }
    result = run_simulation(baseline_state, scenario)
    return result


@router.get("/simulation/{simulation_id}", summary="Get simulation results")
async def get_simulation(simulation_id: str):
    collection = get_collection("simulation_runs")
    doc = await collection.find_one({"_id": simulation_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Simulation not found")
    doc["_id"] = str(doc["_id"])
    return doc
