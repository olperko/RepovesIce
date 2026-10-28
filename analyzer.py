import numpy as np
import pystac_client
import planetary_computer
import odc.stac
import config
import processor


def run_full_analysis():
    """
    Run complete ice analysis on Sentinel-2 imagery.

    Returns:
        List of dictionaries containing analysis results for each date,
        including NDSI, NDWI, and composite ice index profiles.
    """
    # Set up the Planetary Computer STAC Catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    bbox = config.path_gdf.total_bounds

    # Search for Sentinel-2 Level-2A images
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=config.TIME_WINDOW,
        query={"eo:cloud_cover": {"lt": config.CLOUD_COVER_LIMIT}}
    )

    items = search.item_collection()
    print(f"Found {len(items)} clear images in time window {config.TIME_WINDOW}")

    if len(items) == 0:
        print("⚠️ No images found. Check time window and cloud cover settings.")
        return []

    results = []

    for item in items:
        date_str = item.datetime.strftime("%Y-%m-%d")
        print(f"Processing date: {date_str}")

        try:
            # Load bands: Green (B03), NIR (B08), SWIR (B11), and SCL
            ds = odc.stac.load(
                [item],
                bands=[config.BANDS['green'], config.BANDS['nir'],
                       config.BANDS['swir'], config.BANDS['scl']],
                bbox=bbox,
                crs="EPSG:3067",
                resolution=config.RESOLUTION_METERS
            )

            # Extract band data
            green = ds.B03.values[0].astype('float32')
            nir = ds.B08.values[0].astype('float32')
            swir = ds.B11.values[0].astype('float32')
            scl = ds.SCL.values[0]

            # Calculate spectral indices
            ndsi = processor.calculate_ndsi(green, swir)
            ndwi = processor.calculate_ndwi(green, nir)
            ice_index = processor.calculate_ice_index(ndsi, ndwi)

            # Apply cloud mask and restrict to water/snow-ice surfaces.
            # Without the surface restriction, land/vegetation pixels (high NIR
            # reflectance) get misclassified as ice by the NDWI threshold.
            cloud_mask = np.isin(scl, config.CLOUD_MASK_VALUES)
            surface_mask = np.isin(scl, config.SURFACE_SCL_VALUES)
            valid_mask = surface_mask & ~cloud_mask

            ndsi_masked = ndsi.copy()
            ndwi_masked = ndwi.copy()
            ice_index_masked = ice_index.copy()

            ndsi_masked[cloud_mask] = np.nan
            ndwi_masked[cloud_mask] = np.nan
            ice_index_masked[cloud_mask] = np.nan

            # Detect ice using both indices
            ice_mask = processor.detect_ice(ndsi, ndwi)
            ice_pct = processor.calculate_ice_coverage(ice_mask, valid_mask)

            # Extract profiles along the route
            distances, ndsi_profile = processor.get_path_profile(
                ndsi_masked,
                ds.B03.odc.geobox.transform,
                config.path_gdf_metric,
                step_meters=config.SAMPLING_STEP_METERS
            )

            _, ndwi_profile = processor.get_path_profile(
                ndwi_masked,
                ds.B03.odc.geobox.transform,
                config.path_gdf_metric,
                step_meters=config.SAMPLING_STEP_METERS
            )

            _, ice_index_profile = processor.get_path_profile(
                ice_index_masked,
                ds.B03.odc.geobox.transform,
                config.path_gdf_metric,
                step_meters=config.SAMPLING_STEP_METERS
            )

            results.append({
                "date": date_str,
                "ice_pct": ice_pct,
                "distances": distances,
                "ndsi_profile": ndsi_profile,
                "ndwi_profile": ndwi_profile,
                "ice_index_profile": ice_index_profile,
                # Keep legacy 'profile' key for backward compatibility
                "profile": ice_index_profile
            })

            print(f"  ✓ {date_str}: {ice_pct:.1f}% ice coverage")

        except Exception as e:
            print(f"  ✗ Error processing {date_str}: {e}")
            continue

    return results


# This part ensures that if you accidentally run analyzer.py directly, it still works
if __name__ == "__main__":
    data = run_full_analysis()
    if data:
        print(f"\n✓ Analysis complete. Processed {len(data)} images.")
