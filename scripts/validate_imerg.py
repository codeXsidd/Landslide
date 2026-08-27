"""
NASA GPM IMERG Rainfall Data Validation Script
Inspects all NetCDF4 files in data/raw/rainfall/imerg/final/
Does NOT modify any raw files.
"""
import os
import glob
import argparse
import numpy as np
from pathlib import Path

# Try netCDF4 first, fall back to scipy
try:
    import netCDF4 as nc
    BACKEND = "netCDF4"
except ImportError:
    nc = None
    BACKEND = None

try:
    from scipy.io import netcdf
    if BACKEND is None:
        BACKEND = "scipy"
except ImportError:
    netcdf = None


def inspect_file_netcdf4(filepath: str) -> dict:
    """Inspect a NetCDF4 file using the netCDF4 library."""
    result = {
        "file": os.path.basename(filepath),
        "size_bytes": os.path.getsize(filepath),
        "size_kb": round(os.path.getsize(filepath) / 1024, 2),
        "variables": [],
        "dimensions": {},
        "latitude_range": (None, None),
        "longitude_range": (None, None),
        "time_range": [],
        "precip_units": None,
        "precip_min": None,
        "precip_max": None,
        "precip_missing_count": None,
        "global_attrs": {},
        "errors": []
    }

    try:
        ds = nc.Dataset(filepath, 'r')

        # Variables
        result["variables"] = list(ds.variables.keys())
        
        # Dimensions
        result["dimensions"] = {k: len(v) for k, v in ds.dimensions.items()}
        
        # Global attributes
        for attr in ds.ncattrs():
            try:
                result["global_attrs"][attr] = str(getattr(ds, attr))
            except Exception:
                pass

        # Latitude
        for lat_name in ['lat', 'latitude', 'Latitude', 'LAT']:
            if lat_name in ds.variables:
                lat_data = ds.variables[lat_name][:]
                result["latitude_range"] = (float(lat_data.min()), float(lat_data.max()))
                break

        # Longitude
        for lon_name in ['lon', 'longitude', 'Longitude', 'LON']:
            if lon_name in ds.variables:
                lon_data = ds.variables[lon_name][:]
                result["longitude_range"] = (float(lon_data.min()), float(lon_data.max()))
                break

        # Time
        for time_name in ['time', 'Time', 'TIME']:
            if time_name in ds.variables:
                time_var = ds.variables[time_name]
                try:
                    import netCDF4 as nc4
                    times = nc4.num2date(time_var[:], units=time_var.units, 
                                         calendar=getattr(time_var, 'calendar', 'standard'))
                    result["time_range"] = [str(t) for t in times]
                except Exception as e:
                    # Just store raw time values
                    result["time_range"] = [str(v) for v in time_var[:].tolist()]
                break

        # Precipitation variable — IMERG uses 'precipitation' or 'precipitationCal'
        for precip_name in ['precipitation', 'precipitationCal', 'precipitationUncal',
                            'Precipitation', 'PRECIPITATION', 'pr', 'precip', 'HQprecipitation']:
            if precip_name in ds.variables:
                pv = ds.variables[precip_name]
                
                # Units
                try:
                    result["precip_units"] = pv.units
                except AttributeError:
                    result["precip_units"] = "Unknown"
                    
                # Get raw data, applying mask
                pdata = pv[:]
                if hasattr(pdata, 'filled'):
                    # MaskedArray — get fill value
                    fill_val = getattr(pv, '_FillValue', None) or getattr(pv, 'missing_value', None)
                    missing = int(pdata.mask.sum()) if hasattr(pdata, 'mask') and pdata.mask.any() else 0
                    pdata_clean = pdata.compressed()  # Only valid (non-masked) values
                else:
                    fill_val = getattr(pv, '_FillValue', -9999.9)
                    missing = int(np.sum(pdata == fill_val)) if fill_val is not None else 0
                    pdata_clean = pdata[pdata != fill_val] if fill_val is not None else pdata.flatten()
                    
                result["precip_missing_count"] = missing
                
                if pdata_clean.size > 0:
                    result["precip_min"] = round(float(pdata_clean.min()), 6)
                    result["precip_max"] = round(float(pdata_clean.max()), 6)
                break

        ds.close()

    except Exception as e:
        result["errors"].append(str(e))

    return result


def validate_imerg_directory(data_dir: str, report_path: str):
    pattern = os.path.join(data_dir, "*.nc4")
    files = sorted(glob.glob(pattern))
    
    if not files:
        # Try .nc extension too
        pattern = os.path.join(data_dir, "*.nc")
        files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"No NetCDF4 files found in {data_dir}")
        return

    print(f"Found {len(files)} NetCDF4 files in {data_dir}")
    print(f"Backend: {BACKEND}\n")

    results = []
    for fp in files:
        print(f"  Inspecting: {os.path.basename(fp)}")
        result = inspect_file_netcdf4(fp)
        results.append(result)

    # Write Markdown report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# NASA GPM IMERG Rainfall Data Validation Report\n\n")
        f.write(f"**Data Directory**: `{data_dir}`  \n")
        f.write(f"**Inspection Backend**: `{BACKEND}`  \n")
        f.write(f"**Files Found**: {len(files)}\n\n---\n\n")

        for r in results:
            f.write(f"## {r['file']}\n\n")
            f.write(f"**1. File Name**: `{r['file']}`  \n")
            f.write(f"**2. File Size**: {r['size_bytes']} bytes ({r['size_kb']} KB)  \n")
            f.write(f"**3. NetCDF Variables**: `{', '.join(r['variables'])}`  \n")
            f.write(f"   - Dimensions: {r['dimensions']}  \n")
            f.write(f"**4. Latitude Range**: {r['latitude_range'][0]} to {r['latitude_range'][1]}  \n")
            f.write(f"**5. Longitude Range**: {r['longitude_range'][0]} to {r['longitude_range'][1]}  \n")
            f.write(f"**6. Time Values**: {', '.join(r['time_range']) if r['time_range'] else 'N/A'}  \n")
            f.write(f"**7. Precipitation Units**: `{r['precip_units']}`  \n")
            f.write(f"**8. Minimum Precipitation**: {r['precip_min']}  \n")
            f.write(f"**9. Maximum Precipitation**: {r['precip_max']}  \n")
            f.write(f"**10. Missing Values**: {r['precip_missing_count']}  \n")
            
            if r['errors']:
                f.write(f"\n> [!WARNING]\n> Errors: {'; '.join(r['errors'])}\n")
            f.write("\n---\n\n")

        # Cross-file summary
        f.write("## Summary Across All Files\n\n")
        all_mins = [r['precip_min'] for r in results if r['precip_min'] is not None]
        all_maxs = [r['precip_max'] for r in results if r['precip_max'] is not None]
        all_missing = [r['precip_missing_count'] for r in results if r['precip_missing_count'] is not None]
        lat_mins = [r['latitude_range'][0] for r in results if r['latitude_range'][0] is not None]
        lat_maxs = [r['latitude_range'][1] for r in results if r['latitude_range'][1] is not None]
        lon_mins = [r['longitude_range'][0] for r in results if r['longitude_range'][0] is not None]
        lon_maxs = [r['longitude_range'][1] for r in results if r['longitude_range'][1] is not None]
        
        f.write(f"- **Total Files**: {len(files)}\n")
        if all_mins:
            f.write(f"- **Global Precipitation Min**: {min(all_mins)}\n")
        if all_maxs:
            f.write(f"- **Global Precipitation Max**: {max(all_maxs)}\n")
        if all_missing:
            f.write(f"- **Total Missing Values Across All Files**: {sum(all_missing)}\n")
        if lat_mins and lat_maxs:
            f.write(f"- **Overall Latitude Coverage**: {min(lat_mins)} to {max(lat_maxs)}\n")
        if lon_mins and lon_maxs:
            f.write(f"- **Overall Longitude Coverage**: {min(lon_mins)} to {max(lon_maxs)}\n")
        
        # Errors check
        files_with_errors = [r['file'] for r in results if r['errors']]
        if files_with_errors:
            f.write(f"- **Files with Errors**: {', '.join(files_with_errors)}\n")
        else:
            f.write("- **Files with Errors**: None\n")

    # Print concise terminal output
    print("\n========== IMERG Validation Summary ==========")
    for r in results:
        print(f"\n  [{r['file']}]")
        print(f"    Size: {r['size_kb']} KB")
        print(f"    Variables: {r['variables']}")
        print(f"    Lat Range: {r['latitude_range']}")
        print(f"    Lon Range: {r['longitude_range']}")
        print(f"    Time: {r['time_range']}")
        print(f"    Precip Units: {r['precip_units']}")
        print(f"    Precip Min: {r['precip_min']}")
        print(f"    Precip Max: {r['precip_max']}")
        print(f"    Missing: {r['precip_missing_count']}")
        if r['errors']:
            print(f"    ERRORS: {r['errors']}")
    print("\n==============================================")
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate NASA GPM IMERG NetCDF4 files")
    parser.add_argument("--data-dir", default="data/raw/rainfall/imerg/final/",
                        help="Directory containing IMERG NetCDF4 files")
    parser.add_argument("--report", default="docs/data/imerg_validation_report.md",
                        help="Path to write the Markdown validation report")
    args = parser.parse_args()
    
    validate_imerg_directory(args.data_dir, args.report)
