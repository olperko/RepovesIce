import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
import numpy as np


def calculate_ndsi(green_path, swir_path):
    """
    Loads Sentinel-2 Green (B3) and SWIR (B11) bands,
    resamples SWIR to 10m, and calculates NDSI.
    """
    with rasterio.open(green_path) as g_src:
        green = g_src.read(1).astype('float32')
        meta = g_src.meta

        # Resample SWIR (B11) to match Green (B3) dimensions
        with rasterio.open(swir_path) as s_src:
            swir = s_src.read(
                1,
                out_shape=(g_src.height, g_src.width),
                resampling=Resampling.bilinear
            ).astype('float32')

    # NDSI Formula: (Green - SWIR) / (Green + SWIR)
    # Adding a small epsilon (1e-10) to avoid division by zero
    ndsi = (green - swir) / (green + swir + 1e-10)

    return ndsi, meta


def clip_to_path(raster_data, meta, path_geometry, buffer_meters=20):
    """
    Buffers the Coast A -> Coast B line and clips the NDSI data to it.
    """
    # Note: Ensure path_geometry is in a projected CRS (like EPSG:3067 for Finland)
    path_polygon = path_geometry.buffer(buffer_meters)

    # Mask the raster using the buffered path
    # We use a temporary in-memory dataset for rasterio.mask to work
    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:
            dataset.write(raster_data, 1)
            out_image, out_transform = mask(dataset, [path_polygon], crop=True)

    return out_image[0]  # Returns the 2D array of the path corridor


def get_ice_coverage_stats(clipped_ndsi):
    # Ignore 'No Data' values (usually 0 or -9999 depending on mask)
    valid_pixels = clipped_ndsi[clipped_ndsi != 0]

    ice_pixels = np.sum(valid_pixels > 0.4)
    total_pixels = len(valid_pixels)

    coverage_pct = (ice_pixels / total_pixels) * 100
    return coverage_pct


def get_path_profile(raster_data, transform, path_gdf_metric, step_meters=100):
    line = path_gdf_metric.geometry.iloc[0]
    distances = np.arange(0, line.length, step_meters)

    profile_values = []
    inv_transform = ~transform

    for d in distances:
        point = line.interpolate(d)
        col, row = inv_transform * (point.x, point.y)

        try:
            # Check bounds to prevent crashing
            if 0 <= int(row) < raster_data.shape[0] and 0 <= int(col) < raster_data.shape[1]:
                val = raster_data[int(row), int(col)]
                profile_values.append(val)
            else:
                profile_values.append(np.nan)
        except IndexError:
            profile_values.append(np.nan)

    return distances, profile_values