import os
import re
import pandas as pd
import pdfplumber
import argparse
from pathlib import Path

# Expected final columns in snake_case
EXPECTED_COLUMNS = [
    "sl_no",
    "slide_no",
    "state",
    "district",
    "slide_name",
    "nh_sh_location",
    "latitude",
    "longitude",
    "material_involved",
    "movement_type",
    "history"
]

def clean_column_name(col: str) -> str:
    """Helper to clean a column name to match the expected format roughly."""
    if not isinstance(col, str):
        return ""
    # Remove newlines, dots, and trailing/leading spaces, replace internal spaces with underscore
    col = col.replace('\n', ' ').replace('.', '').strip().lower()
    col = re.sub(r'\s+', '_', col)
    return col

def extract_tables_from_pdf(pdf_path: str):
    """
    Reads the PDF and extracts all table rows.
    Skips headers/footers.
    Returns a list of dictionaries (rows) and a list of failed page numbers.
    """
    extracted_rows = []
    failed_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    for row in table:
                        # Clean the row (sometimes None appears)
                        clean_row = [str(cell).strip() if cell is not None else "NA" for cell in row]
                        
                        # Skip empty rows entirely
                        if all(val == "NA" or val == "" for val in clean_row):
                            continue
                            
                        # Skip the title row
                        if "LANDSLIDE INVENTORY" in str(clean_row[0]):
                            continue
                            
                        # Skip the header row
                        if "Sl.No." in clean_row[0] or "Sl" in clean_row[0]:
                            continue
                            
                        # If row length matches expected columns, map it
                        if len(clean_row) >= len(EXPECTED_COLUMNS):
                            # Take the first N columns
                            row_dict = {col: val for col, val in zip(EXPECTED_COLUMNS, clean_row[:len(EXPECTED_COLUMNS)])}
                            row_dict['pdf_page'] = i + 1
                            extracted_rows.append(row_dict)
                        elif len(clean_row) > 0:
                            # Try to pad if missing some trailing columns, though camelot/pdfplumber usually handles grid
                            padded = clean_row + ["NA"] * (len(EXPECTED_COLUMNS) - len(clean_row))
                            row_dict = {col: val for col, val in zip(EXPECTED_COLUMNS, padded)}
                            row_dict['pdf_page'] = i + 1
                            extracted_rows.append(row_dict)
            except Exception as e:
                print(f"Failed to extract table from page {i+1}: {e}")
                failed_pages.append(i + 1)
                
    return extracted_rows, failed_pages

def clean_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataframe:
    - Removes exact duplicates
    - Preserves "NA" values (we will keep the literal string "NA" or None/NaN based on pandas, 
      but the requirement is 'preserve NA values', 'never convert NA into a real value').
      We will replace empty strings with NaN, but keep "NA" as NaN to avoid inventing values.
      Actually, let's replace empty strings and "NA" strings with pandas pd.NA / np.nan to be true nulls.
    """
    if df.empty:
        return df

    # Replace literal "NA" or "None" or empty string with pandas NA (NaN)
    # The requirement says "never convert NA into a real value". NaN is not a real value.
    df = df.replace(["NA", "N/A", "None", "", "null"], pd.NA)
    
    # Remove exact duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    
    return df

def validate_coordinates(df: pd.DataFrame):
    """
    Validates latitude and longitude columns.
    Returns:
    - cleaned dataframe with invalid coords set to pd.NA (or just reported? The prompt says "Report rows with invalid or missing coordinates").
      We will keep them in the dataset but mark them as pd.NA if they are completely unparseable, 
      or we can just report their indices. Let's create a report dataframe.
    """
    invalid_rows = []
    
    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        
        is_valid = True
        if pd.isna(lat) or pd.isna(lon):
            is_valid = False
        else:
            try:
                lat_float = float(lat)
                lon_float = float(lon)
                
                # Check global valid bounds
                if not (-90 <= lat_float <= 90) or not (-180 <= lon_float <= 180):
                    is_valid = False
            except ValueError:
                is_valid = False
                
        if not is_valid:
            invalid_rows.append({
                'sl_no': row.get('sl_no', idx),
                'slide_no': row.get('slide_no', 'Unknown'),
                'latitude': lat,
                'longitude': lon
            })
            
    return invalid_rows

def generate_report(report_path: str, raw_count: int, final_count: int, failed_pages: list, invalid_rows: list):
    """
    Generates a Markdown validation report.
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# GSI Landslide Inventory Validation Report\n\n")
        f.write("## Extraction Summary\n")
        f.write(f"- **Total Raw Records Extracted**: {raw_count}\n")
        f.write(f"- **Final Clean Records (Duplicates Removed)**: {final_count}\n")
        f.write(f"- **Pages Failed Extraction**: {len(failed_pages)}\n")
        if failed_pages:
            f.write(f"  - Failed Page Numbers: {', '.join(map(str, failed_pages))}\n")
            
        f.write("\n## Coordinate Validation\n")
        f.write(f"- **Rows with Invalid or Missing Coordinates**: {len(invalid_rows)}\n\n")
        
        if invalid_rows:
            f.write("### Sample of Invalid Coordinates\n")
            f.write("| Sl No | Slide No | Latitude | Longitude |\n")
            f.write("|---|---|---|---|\n")
            # Show up to 100 invalid rows in report
            for row in invalid_rows[:100]:
                lat = str(row['latitude']).strip()
                lon = str(row['longitude']).strip()
                f.write(f"| {row['sl_no']} | {row['slide_no']} | {lat} | {lon} |\n")
            if len(invalid_rows) > 100:
                f.write(f"\n*(Truncated {len(invalid_rows) - 100} more rows)*\n")

def main():
    parser = argparse.ArgumentParser(description="Extract GSI landslide inventory from PDF")
    parser.add_argument("--pdf", type=str, default="data/raw/landslides/gsi/landslide_inventory_gsi.pdf", help="Path to raw PDF")
    parser.add_argument("--out-csv", type=str, default="data/processed/landslides/gsi_landslide_inventory.csv", help="Path to output CSV")
    parser.add_argument("--out-parquet", type=str, default="data/processed/landslides/gsi_landslide_inventory.parquet", help="Path to output Parquet")
    parser.add_argument("--report", type=str, default="docs/data/gsi_landslide_inventory_report.md", help="Path to validation report")
    args = parser.parse_args()
    
    print(f"Reading PDF from {args.pdf}")
    if not os.path.exists(args.pdf):
        print(f"Error: File {args.pdf} does not exist.")
        return
        
    extracted_rows, failed_pages = extract_tables_from_pdf(args.pdf)
    raw_count = len(extracted_rows)
    print(f"Extracted {raw_count} raw rows.")
    
    df = pd.DataFrame(extracted_rows)
    
    print("Cleaning and standardizing data...")
    df = clean_and_standardize(df)
    final_count = len(df)
    
    print("Validating coordinates...")
    invalid_rows = validate_coordinates(df)
    
    # Save Outputs
    print("Saving processed data...")
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    
    os.makedirs(os.path.dirname(args.out_parquet), exist_ok=True)
    df.to_parquet(args.out_parquet, index=False)
    
    print(f"Saving validation report to {args.report}...")
    generate_report(args.report, raw_count, final_count, failed_pages, invalid_rows)
    print("Extraction complete.")

if __name__ == "__main__":
    main()
