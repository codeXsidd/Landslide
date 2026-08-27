"""
NER-SAGE — Risk API Routes

GET  /risk                    - List all current risk predictions
GET  /risk/{location_id}      - Get risk for a specific location
POST /risk/predict            - Trigger risk prediction for a location
"""


from fastapi import APIRouter, HTTPException, Query, status

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/risk", summary="List all current risk predictions")
async def list_risk_predictions(
    risk_level: str | None = Query(None, description="Filter by risk level (HIGH, MEDIUM, LOW)"),
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0),
):
    """
    Returns the most recent risk prediction for each monitored location.
    Results are sorted by risk_score descending (highest risk first).
    """
    collection = get_collection("risk_predictions")
    query = {}
    if risk_level:
        query["risk_level"] = risk_level.upper()

    cursor = collection.find(query).sort("risk_score", -1).skip(skip).limit(limit)
    predictions = await cursor.to_list(length=limit)
    for p in predictions:
        p["_id"] = str(p["_id"])
    return {"predictions": predictions, "total": len(predictions)}


@router.get("/risk/{location_id}", summary="Get risk prediction for a location")
async def get_risk_for_location(location_id: str):
    """
    Returns the most recent calibrated risk prediction for the specified location.
    Includes risk score, confidence, uncertainty level, and evidence status.
    """
    collection = get_collection("risk_predictions")
    doc = await collection.find_one(
        {"location_id": location_id},
        sort=[("created_at", -1)],
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk prediction found for location '{location_id}'",
        )
    doc["_id"] = str(doc["_id"])
    return doc


@router.post("/risk/predict", summary="Trigger risk prediction", status_code=201)
async def predict_risk(payload: dict):
    """
    Triggers the full ML risk prediction pipeline for a given location.
    Returns risk score, confidence, uncertainty profile, and evidence status.

    Pipeline:
      Input features → Feature Engineering → XGBoost / RF Inference
      → Calibration → Uncertainty Engine → Evidence Status → Store
    """
    from app.ml.inference.predictor import predict_landslide_risk
    location_id = payload.get("location_id")
    if not location_id:
        raise HTTPException(status_code=400, detail="location_id is required")

    result = await predict_landslide_risk(location_id, payload)
    return result
