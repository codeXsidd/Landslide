"""NER-LDI Map Data API Routes — serves geospatial layers."""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.geospatial.hydrography import get_waterways, load_metadata

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/waterways")
async def waterways(refresh: bool = Query(False, description="Force refresh from Overpass")):
    """Return NER waterways as GeoJSON FeatureCollection."""
    result = await get_waterways(force_refresh=refresh)
    return JSONResponse(
        content={
            "type": "FeatureCollection",
            "features": result["geojson"].get("features", []),
            "metadata": {
                "source": result.get("source", "unknown"),
                "retrieval_timestamp": result.get("retrieval_timestamp", "unknown"),
                "feature_count": result.get("feature_count", 0),
                "warning": result.get("warning"),
            },
        },
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/waterways/metadata")
async def waterways_metadata():
    """Return metadata about the cached waterways dataset."""
    meta = load_metadata()
    if meta:
        return meta
    return {"status": "no_data", "message": "No waterway data cached. Call GET /map/waterways?refresh=true to fetch."}
