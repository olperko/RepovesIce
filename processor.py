import numpy as np
import config


def calculate_ndsi(green, swir):
    """
    Calculate NDSI (Normalized Difference Snow Index).

    NDSI = (Green - SWIR) / (Green + SWIR)

    Ice and snow have high reflectance in green and low in SWIR.
    Higher values indicate ice/snow presence.

    Args:
        green: Green band (B03) array
        swir: SWIR band (B11) array

    Returns:
        NDSI array with values between -1 and 1
    """
    return (green - swir) / (green + swir + 1e-10)


def calculate_ndwi(green, nir):
    """
    Calculate NDWI (Normalized Difference Water Index).

    NDWI = (Green - NIR) / (Green + NIR)

    Water has high reflectance in green and low in NIR (positive NDWI).
    Ice reflects more NIR than water (negative NDWI values).
    Useful for detecting black ice in spring conditions.

    Args:
        green: Green band (B03) array
        nir: NIR band (B08) array

    Returns:
        NDWI array with values between -1 and 1
    """
    return (green - nir) / (green + nir + 1e-10)


def calculate_ice_index(ndsi, ndwi):
    """
    Calculate composite ice index combining NDSI and NDWI.

    This combines:
    - NDSI: Detects bright ice/snow
    - NDWI: Detects ice vs water (negative values = ice, positive = water)

    The composite index helps detect both bright ice and darker "black ice".

    Args:
        ndsi: NDSI array
        ndwi: NDWI array

    Returns:
        Composite ice index (higher = more ice-like)
    """
    # Normalize NDWI to ice-positive scale (invert so ice = positive)
    ice_ndwi = -ndwi

    # Average of both indices
    return (ndsi + ice_ndwi) / 2.0


def detect_ice(ndsi, ndwi):
    """
    Detect ice pixels using both NDSI and NDWI thresholds.

    A pixel is classified as ice if:
    - NDSI > threshold (bright ice/snow) OR
    - NDWI < threshold (ice reflects more NIR than water)

    Args:
        ndsi: NDSI array
        ndwi: NDWI array

    Returns:
        Boolean array where True = ice detected
    """
    ice_by_ndsi = ndsi > config.ICE_THRESHOLD_NDSI
    ice_by_ndwi = ndwi < config.ICE_THRESHOLD_NDWI

    # Ice if either condition is met
    return ice_by_ndsi | ice_by_ndwi


def calculate_ice_coverage(ice_mask, valid_mask):
    """
    Calculate percentage of ice coverage in valid (non-cloud) pixels.

    Args:
        ice_mask: Boolean array of ice detection
        valid_mask: Boolean array of valid (non-cloud) pixels

    Returns:
        Ice coverage percentage (0-100)
    """
    valid_pixels = valid_mask.sum()
    if valid_pixels == 0:
        return 0.0

    ice_pixels = (ice_mask & valid_mask).sum()
    return (ice_pixels / valid_pixels) * 100


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
