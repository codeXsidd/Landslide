import pandas as pd
import os
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
import re

NER_STATES = [
    'Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 
    'Mizoram', 'Nagaland', 'Sikkim', 'Tripura'
]

def normalize_state_name(state_str):
    if pd.isna(state_str):
        return pd.NA
    
    # Remove leading dashes or whitespace, convert to title case
    s = str(state_str).strip('- \t\n')
    s = s.title()
    
    # Handle minor variations if necessary (e.g. "Arunachal pradesh" -> "Arunachal Pradesh")
    # title() usually handles this well enough.
    return s

def is_valid_ner_coord(lat, lon):
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        # Approximate bounding box for NER
        if pd.isna(lat_f) or pd.isna(lon_f):
            return False
        if (21.0 <= lat_f <= 30.0) and (87.0 <= lon_f <= 98.0):
            return True
        return False
    except (ValueError, TypeError):
        return False

def filter_and_validate_ner(input_csv, out_csv, report_path, map_path):
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} does not exist.")
        return
        
    df = pd.read_csv(input_csv)
    total_original = len(df)
    
    # 1. Normalize state names
    df['state_norm'] = df['state'].apply(normalize_state_name)
    
    # 2. Split into NER vs Non-NER based strictly on state name
    df_ner = df[df['state_norm'].isin(NER_STATES)].copy()
    df_outside = df[~df['state_norm'].isin(NER_STATES)].copy()
    
    rows_ner = len(df_ner)
    rows_outside = len(df_outside)
    
    # 3. Coordinate validation
    valid_mask = df_ner.apply(lambda row: is_valid_ner_coord(row.get('latitude'), row.get('longitude')), axis=1)
    df_ner_valid_coords = df_ner[valid_mask].copy()
    invalid_coord_count = rows_ner - len(df_ner_valid_coords)
    
    # 4. Duplicate handling
    # We remove duplicates based on slide_no, keeping the first
    # only consider non-null slide_nos for duplication
    dupes_mask = df_ner_valid_coords.duplicated(subset=['slide_no'], keep='first') & df_ner_valid_coords['slide_no'].notna()
    df_ner_final = df_ner_valid_coords[~dupes_mask].copy()
    duplicate_count = len(df_ner_valid_coords) - len(df_ner_final)
    
    final_count = len(df_ner_final)
    
    # Remove our temporary 'state_norm' column and put it back to 'state'
    df_ner_final['state'] = df_ner_final['state_norm']
    df_ner_final = df_ner_final.drop(columns=['state_norm'])
    
    # 5. Generate Report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# NER Landslide Inventory Validation Report\n\n")
        f.write("## Overall Extraction Summary\n")
        f.write(f"- **Total Rows in Original Extracted Dataset**: {total_original}\n")
        f.write(f"- **Rows Belonging to NER (Pre-Validation)**: {rows_ner}\n")
        f.write(f"- **Rows Outside NER**: {rows_outside}\n")
        
        f.write("\n## Cleaning Log\n")
        f.write(f"- **Rows with Invalid/Out-of-Bounds Coordinates Dropped**: {invalid_coord_count}\n")
        f.write(f"- **Duplicate slide_no Records Dropped**: {duplicate_count}\n")
        f.write(f"- **Final NER Row Count**: {final_count}\n")
        
        f.write("\n## Count by State\n")
        state_counts = df_ner_final['state'].value_counts()
        for state, count in state_counts.items():
            f.write(f"- {state}: {count}\n")
            
        f.write("\n## Top 20 Districts by Count\n")
        district_counts = df_ner_final['district'].value_counts().head(20)
        for district, count in district_counts.items():
            f.write(f"- {district}: {count}\n")
            
    # 6. Save clean CSV
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df_ner_final.to_csv(out_csv, index=False)
    
    # Save Parquet as a bonus
    parquet_path = out_csv.replace(".csv", ".parquet")
    df_ner_final.to_parquet(parquet_path, index=False)
    
    # 7. Generate Map
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    gdf = gpd.GeoDataFrame(
        df_ner_final, 
        geometry=gpd.points_from_xy(df_ner_final.longitude, df_ner_final.latitude),
        crs="EPSG:4326"
    )
    
    fig, ax = plt.subplots(figsize=(10, 8))
    gdf.plot(ax=ax, markersize=10, color='blue', alpha=0.6, edgecolor='white', linewidth=0.5)
    plt.title('NER Landslide Inventory Locations')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Plot strictly within the NER bounding box we validated against
    plt.xlim(87.0, 98.0)
    plt.ylim(21.0, 30.0)
    plt.tight_layout()
    plt.savefig(map_path, dpi=300)
    plt.close()
    
    # Terminal Output
    print("\n--- NER Filtering Summary ---")
    print(f"Total Original Records: {total_original}")
    print(f"NER Initial Records: {rows_ner}")
    print(f"Invalid Coordinates Dropped: {invalid_coord_count}")
    print(f"Duplicates Dropped: {duplicate_count}")
    print(f"Final NER Records: {final_count}")
    print("\nState-wise Counts:")
    print(state_counts.to_string())
    print("\nNER Dataset is ready for feature engineering.")
    print("-----------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/landslides/gsi_landslide_inventory.csv")
    parser.add_argument("--out-csv", default="data/processed/landslides/gsi_landslide_inventory_ner.csv")
    parser.add_argument("--report", default="docs/data/gsi_ner_validation_report.md")
    parser.add_argument("--map", default="docs/data/gsi_ner_inventory_map.png")
    args = parser.parse_args()
    
    filter_and_validate_ner(args.input, args.out_csv, args.report, args.map)
