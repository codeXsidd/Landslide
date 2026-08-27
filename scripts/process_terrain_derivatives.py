"""
NASA SRTM GL1 DEM Terrain Derivatives Pipeline
Calculates Elevation, Slope, Aspect, and Terrain Ruggedness Index (TRI)
from data/processed/terrain/ner_dem.tif.
"""

import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import numpy as np
from PIL.TiffImagePlugin import ImageFileDirectory_v2

INPUT_DEM = "data/processed/terrain/ner_dem.tif"
OUT_DIR = "data/processed/terrain"
NODATA_VAL = -9999.0

def load_dem(filepath: str):
    im = Image.open(filepath)
    arr = np.array(im, dtype=np.float32)
    
    width, height = im.size
    nodata = None
    tiepoint = None
    scale = None
    geokey = None
    geodouble = None
    geoascii = None
    
    if hasattr(im, 'tag_v2'):
        nodata = im.tag_v2.get(42113, -32768)
        tiepoint = im.tag_v2.get(33922, (0.0, 0.0, 0.0, 92.0, 25.0, 0.0))
        scale = im.tag_v2.get(33550, (0.0002777777777778146, 0.0002777777777778146, 0.0))
        geokey = im.tag_v2.get(34735, None)
        geodouble = im.tag_v2.get(34736, None)
        geoascii = im.tag_v2.get(34737, None)
        
    left = tiepoint[3]
    top = tiepoint[4]
    res_x = scale[0]
    res_y = scale[1]
    right = left + width * res_x
    bottom = top - height * res_y
    
    meta = {
        'width': width,
        'height': height,
        'left': left,
        'top': top,
        'right': right,
        'bottom': bottom,
        'res_x': res_x,
        'res_y': res_y,
        'nodata': nodata,
        'tiepoint': tiepoint,
        'scale': scale,
        'geokey': geokey,
        'geodouble': geodouble,
        'geoascii': geoascii,
    }
    return arr, meta

def save_geotiff(filepath: str, data: np.ndarray, meta: dict, nodata_val: float):
    # Convert data to float32
    data_f32 = data.astype(np.float32)
    im = Image.fromarray(data_f32)
    
    tags = ImageFileDirectory_v2()
    # Standard GeoTIFF tags
    tags[256] = meta['width']
    tags[257] = meta['height']
    tags[258] = (32,) # 32-bit float
    tags[259] = 1    # Uncompressed
    tags[262] = 1    # BlackIsZero
    tags[33922] = meta['tiepoint']
    tags[33550] = meta['scale']
    tags[42113] = str(nodata_val)
    if meta.get('geokey'):
        tags[34735] = meta['geokey']
    if meta.get('geodouble'):
        tags[34736] = meta['geodouble']
    if meta.get('geoascii'):
        tags[34737] = meta['geoascii']
        
    im.save(filepath, tiffinfo=tags)
    print(f"Saved GeoTIFF: {filepath} ({os.path.getsize(filepath):,} bytes)")

def compute_derivatives():
    print(f"Loading base DEM from {INPUT_DEM}...")
    dem, meta = load_dem(INPUT_DEM)
    raw_nodata = meta['nodata']
    
    # Mask invalid values
    valid_mask = (dem != raw_nodata) & (~np.isnan(dem)) & (dem > -500)
    dem_clean = np.where(valid_mask, dem, np.nan)
    
    print(f"DEM Loaded: {meta['width']}x{meta['height']} pixels, Valid: {np.count_nonzero(valid_mask):,}")
    print(f"Min elevation: {np.nanmin(dem_clean):.2f}m, Max elevation: {np.nanmax(dem_clean):.2f}m")
    
    # 1. Elevation raster
    print("\n--- 1. Generating elevation.tif ---")
    elev_data = np.where(valid_mask, dem_clean, NODATA_VAL)
    elev_path = os.path.join(OUT_DIR, "elevation.tif")
    save_geotiff(elev_path, elev_data, meta, NODATA_VAL)
    
    # 2. Compute spatial gradients for Slope & Aspect using 3x3 Sobel/Horn kernels
    print("\n--- 2. Computing Slope & Aspect ---")
    # Latitude grid for longitude cell sizing
    lats = np.linspace(meta['top'], meta['bottom'], meta['height'], dtype=np.float32)
    lats_rad = np.radians(lats)
    
    # dy is constant (meters per degree lat ~ 111,120 m)
    dy = 111120.0 * meta['res_y'] # ~30.87 m
    # dx varies with latitude
    dx_per_lat = (111120.0 * np.cos(lats_rad) * meta['res_x']).reshape(-1, 1).astype(np.float32) # shape (height, 1)
    
    # Pad dem for 3x3 stencil
    padded = np.pad(dem_clean, pad_width=1, mode='edge')
    
    z1 = padded[0:-2, 0:-2] # top-left
    z2 = padded[0:-2, 1:-1] # top-mid
    z3 = padded[0:-2, 2:]   # top-right
    z4 = padded[1:-1, 0:-2] # mid-left
    z6 = padded[1:-1, 2:]   # mid-right
    z7 = padded[2:,   0:-2] # bot-left
    z8 = padded[2:,   1:-1] # bot-mid
    z9 = padded[2:,   2:]   # bot-right
    
    # Horn's 3x3 spatial derivatives
    dz_dx = ((z3 + 2*z6 + z9) - (z1 + 2*z4 + z7)) / (8.0 * dx_per_lat)
    dz_dy = ((z1 + 2*z2 + z3) - (z7 + 2*z8 + z9)) / (8.0 * dy)
    
    # Slope in degrees
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg = np.degrees(slope_rad)
    slope_out = np.where(valid_mask, slope_deg, NODATA_VAL)
    
    slope_path = os.path.join(OUT_DIR, "slope.tif")
    save_geotiff(slope_path, slope_out, meta, NODATA_VAL)
    
    # Aspect in degrees (0 - 360, 0=North, 90=East, 180=South, 270=West; -1=Flat)
    # aspect = mod(90 - atan2(dz_dy, -dz_dx) * 180 / pi, 360)
    aspect_rad = np.arctan2(dz_dy, -dz_dx)
    aspect_deg = np.degrees(aspect_rad)
    aspect_compass = np.mod(90.0 - aspect_deg, 360.0)
    # Set flat pixels (slope < 0.01 deg) to -1.0
    aspect_compass = np.where(slope_deg < 0.01, -1.0, aspect_compass)
    aspect_out = np.where(valid_mask, aspect_compass, NODATA_VAL)
    
    aspect_path = os.path.join(OUT_DIR, "aspect.tif")
    save_geotiff(aspect_path, aspect_out, meta, NODATA_VAL)
    
    # 3. Terrain Ruggedness Index (TRI) - Riley et al. (1999)
    # TRI = sqrt( sum( (z0 - zk)^2 for k in 1..8 ) / 8 )
    print("\n--- 3. Computing Terrain Ruggedness Index (TRI) ---")
    z0 = padded[1:-1, 1:-1]
    sum_sq_diff = ((z0 - z1)**2 + (z0 - z2)**2 + (z0 - z3)**2 +
                   (z0 - z4)**2 +               (z0 - z6)**2 +
                   (z0 - z7)**2 + (z0 - z8)**2 + (z0 - z9)**2)
    tri_val = np.sqrt(sum_sq_diff / 8.0)
    tri_out = np.where(valid_mask, tri_val, NODATA_VAL)
    
    tri_path = os.path.join(OUT_DIR, "terrain_ruggedness.tif")
    save_geotiff(tri_path, tri_out, meta, NODATA_VAL)
    
    print("\nAll 4 derivatives successfully created!")

if __name__ == "__main__":
    compute_derivatives()
