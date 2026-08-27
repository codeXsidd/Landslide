import pandas as pd
import pytest
import os
from scripts.filter_ner_gsi import normalize_state_name, is_valid_ner_coord

def test_normalize_state_name():
    assert normalize_state_name(" -Arunachal Pradesh ") == "Arunachal Pradesh"
    assert normalize_state_name("ASSAM") == "Assam"
    assert normalize_state_name("nagaland ") == "Nagaland"
    assert pd.isna(normalize_state_name(pd.NA))
    
def test_is_valid_ner_coord():
    # Valid NER coords (e.g. Assam approx)
    assert is_valid_ner_coord(26.2, 92.5) == True
    
    # Outside NER bounds (South India)
    assert is_valid_ner_coord(10.0, 77.0) == False
    
    # Outside NER bounds (Negative Lat)
    assert is_valid_ner_coord(-23.7, 90.0) == False
    
    # Invalid strings/missing
    assert is_valid_ner_coord("invalid", 92.5) == False
    assert is_valid_ner_coord(pd.NA, 92.5) == False
    
def test_filter_ner_logic(tmp_path):
    # Instead of fully calling the script, we can mock the data flow or just 
    # test the core conditions since the script is slightly procedural.
    
    # Let's create a minimal test dataset and run the script logic
    test_csv = tmp_path / "test_gsi.csv"
    out_csv = tmp_path / "test_gsi_ner.csv"
    report_path = tmp_path / "report.md"
    map_path = tmp_path / "map.png"
    
    df = pd.DataFrame([
        {"sl_no": 1, "slide_no": "A1", "state": " -Arunachal Pradesh", "latitude": 27.5, "longitude": 94.0, "district": "D1"},  # Valid NER
        {"sl_no": 2, "slide_no": "A2", "state": "ASSAM", "latitude": 26.2, "longitude": 92.5, "district": "D2"},  # Valid NER
        {"sl_no": 3, "slide_no": "A3", "state": "Kerala", "latitude": 10.0, "longitude": 77.0, "district": "D3"},  # Non-NER
        {"sl_no": 4, "slide_no": "A4", "state": "Manipur", "latitude": -23.0, "longitude": 93.0, "district": "D4"}, # Invalid NER coord
        {"sl_no": 5, "slide_no": "A1", "state": "Arunachal Pradesh", "latitude": 27.5, "longitude": 94.0, "district": "D1"} # Duplicate slide_no
    ])
    df.to_csv(test_csv, index=False)
    
    from scripts.filter_ner_gsi import filter_and_validate_ner
    filter_and_validate_ner(str(test_csv), str(out_csv), str(report_path), str(map_path))
    
    # Verify outputs
    assert os.path.exists(out_csv)
    assert os.path.exists(report_path)
    
    out_df = pd.read_csv(out_csv)
    
    # Total rows should be 2 (A1 and A2). 
    # A3 is dropped (non-NER).
    # A4 is dropped (invalid coord).
    # Row 5 (A1) is dropped (duplicate slide_no).
    assert len(out_df) == 2
    
    # Check states are normalized
    assert "Arunachal Pradesh" in out_df['state'].values
    assert "Assam" in out_df['state'].values
    assert " -Arunachal Pradesh" not in out_df['state'].values
    
    # Check required columns (assuming these 6 are strictly tested here)
    assert all(col in out_df.columns for col in ["sl_no", "slide_no", "state", "latitude", "longitude", "district"])
