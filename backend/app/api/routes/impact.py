"""
NER-SAGE — Impact & Connectivity Routes

GET /impact/{location_id}       - Get impact prediction (blockage, isolation, hospital)
GET /connectivity/{location_id} - Get Neo4j connectivity analysis
"""

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/impact/{location_id}", summary="Get impact prediction for a location")
async def get_impact(location_id: str):
    """
    Returns predicted impact of a landslide at this location:
    - Road blockage probability
    - Village isolation probability + affected population
    - Hospital/facility accessibility degradation
    - Available alternate routes
    - Cascading consequence chain
    """
    collection = get_collection("impact_predictions")
    doc = await collection.find_one(
        {"location_id": location_id}, sort=[("created_at", -1)]
    )
    if not doc:
        raise HTTPException(status_code=404, detail=f"No impact data for '{location_id}'")
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/connectivity/{location_id}", summary="Get road connectivity analysis")
async def get_connectivity(location_id: str):
    """
    Queries the Neo4j road graph for connectivity analysis:
    - Is the village currently reachable?
    - What is the shortest path to the nearest hospital?
    - Are there alternate routes if the primary road fails?
    - Which roads are critical (single-point-of-failure)?
    """
    from app.graph_engine.route_analysis import analyze_connectivity
    result = await analyze_connectivity(location_id)
    return result
