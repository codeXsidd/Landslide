"""
NER-SAGE — Locations API Routes
"""


from fastapi import APIRouter, HTTPException, Query

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/locations", summary="List all monitored locations")
async def list_locations(
    location_type: str | None = Query(None, description="road | village | hospital | junction"),
    limit: int = Query(100, le=500),
):
    collection = get_collection("locations")
    query = {}
    if location_type:
        query["location_type"] = location_type
    cursor = collection.find(query).limit(limit)
    locations = await cursor.to_list(length=limit)
    for loc in locations:
        loc["_id"] = str(loc["_id"])
    return {"locations": locations, "total": len(locations)}


@router.get("/locations/{location_id}", summary="Get a specific location")
async def get_location(location_id: str):
    collection = get_collection("locations")
    doc = await collection.find_one({"_id": location_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found")
    doc["_id"] = str(doc["_id"])
    return doc
