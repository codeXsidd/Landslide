"""NER-LDI Satellite Evidence Adapter - standardized interface for satellite data."""
from datetime import datetime, timezone
from typing import Dict, Optional
import uuid


def create_satellite_observation(source: str = "sentinel_2", lat: float = 0, lon: float = 0,
                                 change_detected: bool = False, ndvi_change: float = 0.0,
                                 coherence: float = 1.0, is_simulated: bool = True) -> Dict:
    """Create a standardized satellite evidence object."""
    return {
        "evidence_id": str(uuid.uuid4()),
        "source": source,
        "source_type": "satellite",
        "evidence_type": "satellite",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": {"latitude": lat, "longitude": lon},
        "value": {
            "change_detected": change_detected,
            "ndvi_change": ndvi_change,
            "coherence": coherence,
            "deformation_mm": None,
        },
        "freshness": "FRESH",
        "reliability": 0.88 if not is_simulated else 0.30,
        "is_simulated": is_simulated,
        "provenance": {
            "satellite": source,
            "method": "simulated_observation" if is_simulated else "automated_processing",
            "note": "SIMULATED - no real satellite data available" if is_simulated else "Real observation"
        }
    }
