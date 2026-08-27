import pandas as pd
import os
import argparse
import re
from datetime import datetime

REQUIRED_COLUMNS = [
    "sl_no", "slide_no", "state", "district", "slide_name", "nh_sh_location",
    "latitude", "longitude", "material_involved", "movement_type", "history", "pdf_page"
]

def parse_date(date_str):
    """Attempt to parse date from string."""
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    
    # Try multiple formats like "17 May 2016", "2019", "02 April 2010"
    formats = [
        "%d %B %Y", "%d %b %Y", "%B %Y", "%b %Y", "%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
            
    # Try regex for a 4-digit year as fallback
    match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if match:
        try:
            return datetime.strptime(match.group(0), "%Y")
        except ValueError:
            pass
            
    return None

def validate_and_clean(csv_path: str, clean_csv_path: str, report_path: str):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist.")
        return
        
    df = pd.read_csv(csv_path)
    report_lines = ["# GSI Landslide Inventory Validation Report\n"]
    
    # 1. Total number of rows
    total_rows = len(df)
    report_lines.append(f"- **1. Total rows:** {total_rows}")
    
    # 2. Total unique slide_no
    unique_slide_no = df['slide_no'].nunique() if 'slide_no' in df.columns else 0
    report_lines.append(f"- **2. Unique slide_no:** {unique_slide_no}")
    
    # 3. Required columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    report_lines.append(f"- **3. Required columns missing:** {', '.join(missing_cols) if missing_cols else 'None'}")
    
    # 4. Missing values per column
    report_lines.append("- **4. Missing values per column:**")
    for col in df.columns:
        missing_count = df[col].isna().sum()
        report_lines.append(f"  - {col}: {missing_count}")
        
    # Validation logic for coords
    def is_valid_lat(val):
        try:
            f = float(val)
            return pd.notna(f) and -90 <= f <= 90
        except (ValueError, TypeError):
            return False

    def is_valid_lon(val):
        try:
            f = float(val)
            return pd.notna(f) and -180 <= f <= 180
        except (ValueError, TypeError):
            return False

    if 'latitude' in df.columns and 'longitude' in df.columns:
        valid_lat_mask = df['latitude'].apply(is_valid_lat)
        valid_lon_mask = df['longitude'].apply(is_valid_lon)
        
        # 5, 6, 7, 8. Invalid coords & bounds
        invalid_lats = df[~valid_lat_mask]
        invalid_lons = df[~valid_lon_mask]
        
        report_lines.append(f"- **5. Invalid latitude values:** {len(invalid_lats)}")
        report_lines.append(f"- **6. Invalid longitude values:** {len(invalid_lons)}")
        report_lines.append("- **7 & 8. Out of range (Lat outside [-90,90] / Lon outside [-180,180]):** Counted in invalids above.")
    else:
        valid_lat_mask = pd.Series([False]*len(df))
        valid_lon_mask = pd.Series([False]*len(df))

    # 9. Duplicate slide_no
    if 'slide_no' in df.columns:
        dup_slide_no = df[df.duplicated(subset=['slide_no'], keep=False) & df['slide_no'].notna()]
        report_lines.append(f"- **9. Records with duplicate slide_no:** {len(dup_slide_no)}")
    else:
        report_lines.append("- **9. Records with duplicate slide_no:** 0")

    # 10. Duplicate lat/lon
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # only check valid ones for duplication to not flag all missing coords as dupes of each other
        valid_coords = df[valid_lat_mask & valid_lon_mask]
        dup_coords = valid_coords[valid_coords.duplicated(subset=['latitude', 'longitude'], keep=False)]
        report_lines.append(f"- **10. Records with duplicate valid lat/lon:** {len(dup_coords)}")
    else:
        report_lines.append("- **10. Records with duplicate valid lat/lon:** 0")

    # 11, 12, 14, 15: Counts by category
    for col, title, num in [('state', 'State', 11), ('district', 'District', 12), 
                            ('movement_type', 'Movement Type', 14), ('material_involved', 'Material Involved', 15)]:
        report_lines.append(f"- **{num}. Records by {title}:**")
        if col in df.columns:
            counts = df[col].value_counts(dropna=False)
            for k, v in counts.items():
                report_lines.append(f"  - {k}: {v}")
        else:
            report_lines.append("  - N/A")

    # 13. History = NA
    if 'history' in df.columns:
        missing_hist = df['history'].isna().sum()
        report_lines.append(f"- **13. Records with History = NA:** {missing_hist}")
        
        # 16. Earliest and latest history
        parsed_dates = df['history'].apply(parse_date).dropna()
        if not parsed_dates.empty:
            earliest = parsed_dates.min().strftime('%Y-%m-%d')
            latest = parsed_dates.max().strftime('%Y-%m-%d')
            report_lines.append(f"- **16. Earliest valid date:** {earliest}")
            report_lines.append(f"- **16. Latest valid date:** {latest}")
        else:
            report_lines.append("- **16. Earliest/Latest date:** None found")

    # 17, 18. PDF pages
    if 'pdf_page' in df.columns:
        page_counts = df['pdf_page'].value_counts().sort_index()
        report_lines.append("- **17. Rows per PDF page:** (Summary)")
        report_lines.append(f"  - Total Pages with data: {len(page_counts)}")
        report_lines.append(f"  - Max rows on a page: {page_counts.max()}")
        report_lines.append(f"  - Min rows on a page: {page_counts.min()}")
        
        low_records = page_counts[page_counts < 5]
        report_lines.append(f"- **18. Suspiciously low records (< 5):** {len(low_records)} pages")
        for p, count in low_records.items():
            report_lines.append(f"  - Page {p}: {count} rows")
    else:
        report_lines.append("- **17 & 18. PDF page analysis:** pdf_page column missing.")

    # --- CLEANING ---
    # We will remove rows with completely invalid coordinates.
    # The requirement says "If rows are removed, record exactly how many and why"
    # "Do not silently delete suspicious rows."
    
    clean_df = df.copy()
    
    report_lines.append("\n## Cleaning Log")
    
    # 1. Drop invalid coordinates
    invalid_mask = ~(valid_lat_mask & valid_lon_mask)
    num_invalid_dropped = invalid_mask.sum()
    clean_df = clean_df[~invalid_mask]
    report_lines.append(f"- Dropped {num_invalid_dropped} rows due to invalid or missing latitude/longitude.")

    # 2. Drop duplicates based on slide_no (keep first)
    if 'slide_no' in clean_df.columns:
        pre_dup_count = len(clean_df)
        # only consider non-null slide_nos for duplication
        dupes = clean_df.duplicated(subset=['slide_no'], keep='first') & clean_df['slide_no'].notna()
        clean_df = clean_df[~dupes]
        num_dupes_dropped = pre_dup_count - len(clean_df)
        report_lines.append(f"- Dropped {num_dupes_dropped} rows due to duplicate slide_no (kept first).")
    else:
        num_dupes_dropped = 0
        
    report_lines.append(f"- **Final Clean Rows:** {len(clean_df)}")
    
    # Write report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    # Write clean CSV
    os.makedirs(os.path.dirname(clean_csv_path), exist_ok=True)
    clean_df.to_csv(clean_csv_path, index=False)
    
    # Terminal Summary
    print("\n--- Validation Summary ---")
    print(f"Total Raw Rows: {total_rows}")
    print(f"Valid Coordinates: {len(clean_df)}")
    print(f"Invalid Coordinates (Dropped): {num_invalid_dropped}")
    print(f"Duplicates (Dropped): {num_dupes_dropped}")
    print(f"Number of States: {df['state'].nunique() if 'state' in df.columns else 0}")
    print(f"Extraction Warnings: {len(missing_cols)} missing cols, " +
          (f"{len(low_records)} low-record pages" if 'pdf_page' in df.columns else "N/A"))
    print("--------------------------\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/landslides/gsi_landslide_inventory.csv")
    parser.add_argument("--output", default="data/processed/landslides/gsi_landslide_inventory_clean.csv")
    parser.add_argument("--report", default="docs/data/gsi_validation_report.md")
    args = parser.parse_args()
    
    validate_and_clean(args.input, args.output, args.report)
