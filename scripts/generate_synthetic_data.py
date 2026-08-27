"""
NER-SAGE — Synthetic Data Generator for SIH Demo
Creates the deterministc "Road B" scenario data in MongoDB.
"""

import sys
from datetime import UTC, datetime, timedelta

from pymongo import MongoClient

# Base URI from .env.example
MONGO_URI = "mongodb://nersage:nersage_pass@localhost:27017/ner_sage?authSource=ner_sage"

def generate_demo_data():
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    db = client.ner_sage
    now = datetime.now(UTC)

    # 1. Locations
    locations = [
        {
            "_id": "road_b",
            "name": "Road B Corridor",
            "location_type": "road",
            "state": "Assam",
            "district": "Dima Hasao",
            "geometry": {"type": "Point", "coordinates": [92.7123, 25.5781]},
            "properties": {"length_km": 12.5, "is_critical": True},
            "is_simulated": True,
            "created_at": now
        },
        {
            "_id": "village_x",
            "name": "Village X",
            "location_type": "village",
            "state": "Assam",
            "district": "Dima Hasao",
            "geometry": {"type": "Point", "coordinates": [92.7000, 25.5900]},
            "properties": {"population": 850},
            "is_simulated": True,
            "created_at": now
        }
    ]
    db.locations.delete_many({"_id": {"$in": ["road_b", "village_x"]}})
    db.locations.insert_many(locations)
    print("Inserted locations.")

    # 2. Risk Prediction (Step 1 of Demo: Risk 82%, Confidence 54%)
    risk_predictions = [
        {
            "_id": "risk_road_b_01",
            "location_id": "road_b",
            "risk_score": 0.82,
            "risk_level": "HIGH",
            "confidence": 0.54,
            "confidence_level": "LOW",
            "uncertainty": "HIGH",
            "evidence_status": "CONFLICTING",
            "major_factors": ["steep slope", "historical susceptibility"],
            "model_version": "xgb_v1",
            "is_simulated": True,
            "created_at": now
        }
    ]
    db.risk_predictions.delete_many({"location_id": "road_b"})
    db.risk_predictions.insert_many(risk_predictions)
    print("Inserted risk prediction.")

    # 3. Evidence Items (Step 2 of Demo: Stale Satellite, Missing Ground)
    evidence_items = [
        {
            "_id": "ev_sat_01",
            "location_id": "road_b",
            "source": "sentinel_1",
            "source_type": "satellite",
            "evidence_type": "deformation",
            "reliability": 0.88,
            "freshness": "LOW",
            "information_state": "STALE",
            "acquired_at": now - timedelta(days=9),
            "is_simulated": True,
            "created_at": now - timedelta(days=9)
        },
        {
            "_id": "ev_rain_01",
            "location_id": "road_b",
            "source": "imd",
            "source_type": "rainfall",
            "evidence_type": "observation",
            "reliability": 0.85,
            "freshness": "HIGH",
            "information_state": "KNOWN",
            "raw_value": {"rainfall_mm": 110},
            "observed_at": now - timedelta(hours=1),
            "is_simulated": True,
            "created_at": now
        }
    ]
    db.evidence_items.delete_many({"location_id": "road_b"})
    db.evidence_items.insert_many(evidence_items)
    print("Inserted initial evidence items.")

    # 4. Impact Prediction
    impact = [
        {
            "_id": "imp_road_b_01",
            "location_id": "road_b",
            "road_blockage_probability": 0.76,
            "road_blockage_level": "HIGH",
            "isolation_probability": 0.64,
            "affected_population": 850,
            "hospital_access_degraded": True,
            "is_simulated": True,
            "created_at": now
        }
    ]
    db.impact_predictions.delete_many({"location_id": "road_b"})
    db.impact_predictions.insert_many(impact)
    print("Inserted impact predictions.")

    print("Demo data generation complete! Run `make demo` to see it in action.")

if __name__ == "__main__":
    generate_demo_data()
