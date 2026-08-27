import pandas as pd
import pytest
from scripts.extract_gsi_inventory import clean_and_standardize, validate_coordinates

def test_clean_and_standardize():
    data = [
        {"sl_no": "1", "state": "Assam", "latitude": "24.1", "longitude": "NA"},
        {"sl_no": "2", "state": "Assam", "latitude": "24.2", "longitude": "None"},
        {"sl_no": "3", "state": "Assam", "latitude": "24.3", "longitude": ""},
        {"sl_no": "1", "state": "Assam", "latitude": "24.1", "longitude": "NA"}, # Duplicate
    ]
    df = pd.DataFrame(data)
    
    cleaned = clean_and_standardize(df)
    
    # Check duplicate removed
    assert len(cleaned) == 3
    
    # Check NAs handled correctly (converted to pd.NA)
    assert pd.isna(cleaned.loc[0, "longitude"])
    assert pd.isna(cleaned.loc[1, "longitude"])
    assert pd.isna(cleaned.loc[2, "longitude"])
    assert not pd.isna(cleaned.loc[0, "latitude"])

def test_validate_coordinates():
    data = [
        {"sl_no": "1", "slide_no": "A", "latitude": "24.5", "longitude": "92.5"},     # Valid
        {"sl_no": "2", "slide_no": "B", "latitude": "100.5", "longitude": "92.5"},    # Invalid Lat
        {"sl_no": "3", "slide_no": "C", "latitude": "24.5", "longitude": "-200.5"},   # Invalid Lon
        {"sl_no": "4", "slide_no": "D", "latitude": "NA", "longitude": "92.5"},       # Missing Lat
        {"sl_no": "5", "slide_no": "E", "latitude": "invalid", "longitude": "92.5"},  # Non-numeric
    ]
    # Simulate the cleaning first
    df = clean_and_standardize(pd.DataFrame(data))
    
    invalid_rows = validate_coordinates(df)
    
    # Should catch 4 invalid rows (rows 2, 3, 4, 5)
    assert len(invalid_rows) == 4
    
    sl_nos = [row["sl_no"] for row in invalid_rows]
    assert "1" not in sl_nos
    assert "2" in sl_nos
    assert "3" in sl_nos
    assert "4" in sl_nos
    assert "5" in sl_nos
