import numpy as np
import pystac_client
import planetary_computer
import odc.stac
import config
import processor

def run_full_analysis():
    # Set up the Catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    bbox = config.path_gdf.total_bounds
    time_window = "2025-03-01/2025-05-31"

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=time_window,
        query={"eo:cloud_cover": {"lt": 20}}
    )

    items = search.item_collection()
    print(f"Found {len(items)} clear images.")

    results = []

    for item in items:
        date_str = item.datetime.strftime("%Y-%m-%d")
        print(f"Processing date: {date_str}")

        ds = odc.stac.load(
            [item],
            bands=["B03", "B11", "SCL"],
            bbox=bbox,
            crs="EPSG:3067",
            resolution=10
        )

        green = ds.B03.values[0].astype('float32')
        swir = ds.B11.values[0].astype('float32')
        scl = ds.SCL.values[0]

        ndsi = (green - swir) / (green + swir + 1e-10)
        ndsi[np.isin(scl, [3, 8, 9])] = np.nan

        distances, profile_values = processor.get_path_profile(
            ndsi,
            ds.B03.odc.geobox.transform,
            config.path_gdf_metric,
            step_meters=100
        )

        valid_ndsi = ndsi[~np.isnan(ndsi)]
        ice_pct = (np.sum(valid_ndsi > 0.4) / len(valid_ndsi)) * 100 if len(valid_ndsi) > 0 else 0

        results.append({
            "date": date_str,
            "ice_pct": ice_pct,
            "distances": distances,
            "profile": profile_values
        })

    return results

# This part ensures that if you accidentally run analyzer.py directly, it still works
if __name__ == "__main__":
    data = run_full_analysis()