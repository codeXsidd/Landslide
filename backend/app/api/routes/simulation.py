"""
NER-SAGE — Simulation API Routes

POST /simulation              - Run a what-if simulation scenario
GET  /simulation/{id}         - Get simulation results
"""

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_collection

router = APIRouter()


@router.post("/simulation", summary="Run a what-if simulation scenario", status_code=201)
async def run_simulation(payload: dict):
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

    from app.services.simulation.engine import run_scenario_simulation
    result = await run_scenario_simulation(payload)
    return result


@router.get("/simulation/{simulation_id}", summary="Get simulation results")
async def get_simulation(simulation_id: str):
    collection = get_collection("simulation_runs")
    doc = await collection.find_one({"_id": simulation_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Simulation not found")
    doc["_id"] = str(doc["_id"])
    return doc
