"""
NASA GPM IMERG Rainfall Preprocessing Pipeline
Reads raw .SUB.nc4 files, converts to long-format Parquet, and writes metadata JSON.
Does NOT modify raw files. Does NOT fabricate values.
"""

import os
import glob
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import xarray as xr


RAW_DIR = "data/raw/rainfall/imerg/final/"
OUT_DIR = "data/processed/rainfall/"
REPORT_PATH = "docs/data/imerg_validation_report.md"
PRECIP_VAR = "precipitation"  # Standard IMERG variable name


def find_nc_files(data_dir: str) -> list[str]:
    """Find all .nc4 or .nc files in the directory, sorted by name."""
    files = sorted(glob.glob(os.path.join(data_dir, "*.nc4")))
    if not files:
        files = sorted(glob.glob(os.path.join(data_dir, "*.nc")))
    return files


def inspect_file(filepath: str) -> dict:
    """
    Open one NetCDF file with xarray and extract metadata.
    Returns a metadata dict. Does NOT modify the file.
    """
    ds = xr.open_dataset(filepath, engine="netcdf4")
    info = {}

    # Variables and dimensions
    info["variables"] = list(ds.data_vars.keys())
    info["coords"] = list(ds.coords.keys())
    info["dims"] = dict(ds.sizes)

    # Lat / Lon
    lat_key = next((k for k in ["lat", "latitude", "Latitude", "LAT"] if k in ds.coords), None)
    lon_key = next((k for k in ["lon", "longitude", "Longitude", "LON"] if k in ds.coords), None)
    if lat_key is not None:
        lat = ds.coords[lat_key]
        info["lat_min"] = float(lat.min())
        info["lat_max"] = float(lat.max())
        info["lat_count"] = int(lat.size)
    if lon_key is not None:
        lon = ds.coords[lon_key]
        info["lon_min"] = float(lon.min())
        info["lon_max"] = float(lon.max())
        info["lon_count"] = int(lon.size)

    # Time
    if "time" in ds.coords:
        times = pd.DatetimeIndex(ds["time"].values)
        info["times"] = [str(t.date()) for t in times]
    else:
        info["times"] = []

    # Precipitation variable
    if PRECIP_VAR in ds.data_vars:
        pv = ds[PRECIP_VAR]
        info["precip_units"] = pv.attrs.get("units", "unknown")
        info["precip_long_name"] = pv.attrs.get("long_name", "")
        vals = pv.values.flatten()
        valid_mask = ~np.isnan(vals)
        info["precip_min"] = round(float(np.nanmin(vals)), 6) if valid_mask.any() else None
        info["precip_max"] = round(float(np.nanmax(vals)), 6) if valid_mask.any() else None
        info["missing_count"] = int(np.isnan(vals).sum())
        info["total_cells"] = int(vals.size)
    else:
        # Try to detect the precipitation variable
        for v in ds.data_vars:
            if "precip" in v.lower() or "rain" in v.lower():
                pv = ds[v]
                vals = pv.values.flatten()
                info["precip_units"] = pv.attrs.get("units", "unknown")
                info["precip_min"] = round(float(np.nanmin(vals)), 6)
                info["precip_max"] = round(float(np.nanmax(vals)), 6)
                info["missing_count"] = int(np.isnan(vals).sum())
                info["total_cells"] = int(vals.size)
                break

    ds.close()
    return info


def load_and_flatten(filepath: str) -> pd.DataFrame:
    """
    Load one NetCDF file and return a long-format DataFrame:
    Columns: date, latitude, longitude, precipitation_mm_day
    """
    ds = xr.open_dataset(filepath, engine="netcdf4")

    # Rename coords to standard names
    rename_map = {}
    if "lat" in ds.coords and "lat" not in ds.dims:
        rename_map["lat"] = "lat"
    if "lon" in ds.coords and "lon" not in ds.dims:
        rename_map["lon"] = "lon"

    if PRECIP_VAR not in ds.data_vars:
        ds.close()
        return pd.DataFrame()

    # Select the precipitation variable; squeeze out any size-1 time dimension
    da = ds[PRECIP_VAR].squeeze()

    # Convert to DataFrame (long format)
    df = da.to_dataframe(name="precipitation_mm_day").reset_index()

    # Rename coordinate columns to standard names
    col_rename = {}
    if "lat" in df.columns:
        col_rename["lat"] = "latitude"
    if "lon" in df.columns:
        col_rename["lon"] = "longitude"
    if "time" in df.columns:
        col_rename["time"] = "date"
    df = df.rename(columns=col_rename)

    # Normalize date to just date (not datetime)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    # Keep only essential columns
    keep = [c for c in ["date", "latitude", "longitude", "precipitation_mm_day"] if c in df.columns]
    df = df[keep]

    # Drop rows with NaN precipitation (do NOT invent values)
    df = df.dropna(subset=["precipitation_mm_day"])

    ds.close()
    return df


def check_missing_dates(file_dates: list[str]) -> dict:
    """Identify gaps in the date range of available files."""
    if not file_dates:
        return {}
    sorted_dates = sorted(pd.to_datetime(d) for d in file_dates)
    start = sorted_dates[0]
    end = sorted_dates[-1]
    all_dates = set(pd.date_range(start, end, freq="D"))
    available_dates = set(sorted_dates)
    missing = sorted(all_dates - available_dates)
    return {
        "start_date": str(start.date()),
        "end_date": str(end.date()),
        "total_days_in_range": len(all_dates),
        "available_days": len(available_dates),
        "missing_days": len(missing),
        "missing_dates": [str(d.date()) for d in missing],
    }


def write_report(report_path: str, files: list[str], file_infos: list[dict],
                 date_gaps: dict, preview_df: pd.DataFrame):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# NASA GPM IMERG Rainfall Validation Report\n\n")
        f.write(f"- **Files Found**: {len(files)}\n")
        f.write(f"- **Date Range**: {date_gaps.get('start_date')} to {date_gaps.get('end_date')}\n")
        f.write(f"- **Days in Range**: {date_gaps.get('total_days_in_range')}\n")
        f.write(f"- **Available Days**: {date_gaps.get('available_days')}\n")
        f.write(f"- **Missing Days**: {date_gaps.get('missing_days')}\n")
        if date_gaps.get("missing_dates"):
            f.write(f"  - Missing Dates: {', '.join(date_gaps['missing_dates'])}\n")
        else:
            f.write("  - No gaps in date range.\n")

        # Aggregate spatial extent from all files
        all_lat_min = min(i["lat_min"] for i in file_infos if "lat_min" in i)
        all_lat_max = max(i["lat_max"] for i in file_infos if "lat_max" in i)
        all_lon_min = min(i["lon_min"] for i in file_infos if "lon_min" in i)
        all_lon_max = max(i["lon_max"] for i in file_infos if "lon_max" in i)
        all_precip_min = min(i["precip_min"] for i in file_infos if i.get("precip_min") is not None)
        all_precip_max = max(i["precip_max"] for i in file_infos if i.get("precip_max") is not None)
        total_missing = sum(i.get("missing_count", 0) for i in file_infos)

        f.write(f"\n## Spatial Coverage\n")
        f.write(f"- **Latitude Range**: {all_lat_min}° to {all_lat_max}°\n")
        f.write(f"- **Longitude Range**: {all_lon_min}° to {all_lon_max}°\n")

        if file_infos:
            fi = file_infos[0]
            f.write(f"\n## Variables & Dimensions\n")
            f.write(f"- **Variables**: `{', '.join(fi.get('variables', []))}`\n")
            f.write(f"- **Coordinates**: `{', '.join(fi.get('coords', []))}`\n")
            f.write(f"- **Dimensions**: `{fi.get('dims', {})}`\n")
            f.write(f"- **Precipitation Units**: `{fi.get('precip_units', 'unknown')}`\n")
            f.write(f"- **Precipitation Long Name**: `{fi.get('precip_long_name', '')}`\n")

        f.write(f"\n## Precipitation Statistics\n")
        f.write(f"- **Min Precipitation (Global)**: {all_precip_min} mm/day\n")
        f.write(f"- **Max Precipitation (Global)**: {all_precip_max} mm/day\n")
        f.write(f"- **Total Missing Values (All Files)**: {total_missing}\n")

        f.write(f"\n## Per-File Summary\n\n")
        f.write("| File | Size (KB) | Date | Precip Min | Precip Max | Missing |\n")
        f.write("|---|---|---|---|---|---|\n")
        for fp, fi in zip(files, file_infos):
            fname = os.path.basename(fp)
            size_kb = round(os.path.getsize(fp) / 1024, 1)
            dates = ", ".join(fi.get("times", []))
            f.write(f"| `{fname}` | {size_kb} | {dates} | {fi.get('precip_min')} | {fi.get('precip_max')} | {fi.get('missing_count', 0)} |\n")

        f.write("\n## Preview: First 20 Rows (date, latitude, longitude, precipitation_mm_day)\n\n")
        if not preview_df.empty:
            f.write(preview_df.head(20).to_markdown(index=False))
        else:
            f.write("No data available for preview.\n")

        if date_gaps.get("missing_days", 0) > 0:
            f.write(f"\n\n> [!WARNING]\n")
            f.write(f"> **Missing Date Range**: {date_gaps['missing_days']} day(s) are absent from the dataset.\n")
            f.write(f"> Missing dates: `{', '.join(date_gaps['missing_dates'])}`.\n")
            f.write(f"> Download these files from NASA GES DISC before training any model.\n")
        else:
            f.write(f"\n\n> [!NOTE]\n> No date gaps detected in the available data range.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=RAW_DIR)
    parser.add_argument("--out-dir", default=OUT_DIR)
    parser.add_argument("--report", default=REPORT_PATH)
    args = parser.parse_args()

    files = find_nc_files(args.data_dir)
    if not files:
        print(f"No NetCDF files found in {args.data_dir}")
        return

    print(f"Found {len(files)} file(s). Inspecting...")

    # 1. Inspect all files
    file_infos = []
    all_file_dates = []
    for fp in files:
        info = inspect_file(fp)
        info["filename"] = os.path.basename(fp)
        info["size_bytes"] = os.path.getsize(fp)
        file_infos.append(info)
        all_file_dates.extend(info.get("times", []))
        print(f"  [{info['filename']}]  date={info.get('times')}  "
              f"precip_range=[{info.get('precip_min')}, {info.get('precip_max')}]  "
              f"missing={info.get('missing_count', 0)}")

    # 2. Check date gaps
    date_gaps = check_missing_dates(all_file_dates)

    # 3. Flatten all files into one long DataFrame
    print("\nConverting to long-format DataFrame...")
    dfs = []
    for fp in files:
        df = load_and_flatten(fp)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        print("ERROR: Could not extract any data from files.")
        return

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.sort_values(["date", "latitude", "longitude"]).reset_index(drop=True)
    combined_df["date"] = pd.to_datetime(combined_df["date"])

    print(f"Total rows in combined dataset: {len(combined_df):,}")
    print(f"Columns: {list(combined_df.columns)}")

    # 4. Save Parquet
    os.makedirs(args.out_dir, exist_ok=True)
    parquet_path = os.path.join(args.out_dir, "rainfall_daily.parquet")
    combined_df.to_parquet(parquet_path, index=False)
    print(f"Saved: {parquet_path}")

    # 5. Save metadata JSON
    fi0 = file_infos[0] if file_infos else {}
    metadata = {
        "source": "NASA GPM IMERG Final V07B",
        "product": "3B-DAY",
        "version": "V07B",
        "files_processed": len(files),
        "date_range_start": date_gaps.get("start_date"),
        "date_range_end": date_gaps.get("end_date"),
        "total_days_available": date_gaps.get("available_days"),
        "missing_days": date_gaps.get("missing_days"),
        "missing_dates": date_gaps.get("missing_dates", []),
        "latitude_range": [fi0.get("lat_min"), fi0.get("lat_max")],
        "longitude_range": [fi0.get("lon_min"), fi0.get("lon_max")],
        "latitude_count": fi0.get("lat_count"),
        "longitude_count": fi0.get("lon_count"),
        "variables": fi0.get("variables", []),
        "precip_units": fi0.get("precip_units"),
        "precip_long_name": fi0.get("precip_long_name"),
        "global_precip_min": min(i["precip_min"] for i in file_infos if i.get("precip_min") is not None),
        "global_precip_max": max(i["precip_max"] for i in file_infos if i.get("precip_max") is not None),
        "total_rows_processed": len(combined_df),
        "parquet_output": parquet_path,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = os.path.join(args.out_dir, "rainfall_metadata.json")
    with open(meta_path, "w") as mf:
        json.dump(metadata, mf, indent=2)
    print(f"Saved: {meta_path}")

    # 6. Validation report
    preview_df = combined_df[["date", "latitude", "longitude", "precipitation_mm_day"]].copy()
    preview_df["date"] = preview_df["date"].dt.date.astype(str)

    write_report(args.report, files, file_infos, date_gaps, preview_df)
    print(f"Saved: {args.report}")

    # 7. Terminal summary
    print("\n======= IMERG Processing Summary =======")
    print(f"Files processed: {len(files)}")
    print(f"Date range: {date_gaps.get('start_date')} to {date_gaps.get('end_date')}")
    print(f"Lat: {fi0.get('lat_min')} to {fi0.get('lat_max')}")
    print(f"Lon: {fi0.get('lon_min')} to {fi0.get('lon_max')}")
    print(f"Precip units: {fi0.get('precip_units')}")
    print(f"Global precip min: {metadata['global_precip_min']} mm/day")
    print(f"Global precip max: {metadata['global_precip_max']} mm/day")
    print(f"Total rows in Parquet: {len(combined_df):,}")
    if date_gaps.get("missing_days", 0) > 0:
        print(f"\nWARNING: {date_gaps['missing_days']} missing day(s): {date_gaps['missing_dates']}")
    else:
        print("No date gaps detected.")
    print("=========================================")

    # 8. Preview table
    print("\nPreview (first 10 rows):")
    print(preview_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
