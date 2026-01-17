# Repovesi Ice Analyzer: Satellite-Based Route Monitoring

Goal of the program is to analyze a 12 kilometer water route from Point A to Point B and check if this route is clear from ice during the spring. My family does rock climbing and this water route is used to transport from cottage to location. 

This is a personal project to practice;
* **Data Analysis:** Interpreting multi-temporal satellite data
* **Remote Sensing:** Sentinel-2 imagery used for environmental monitoring.
* **Geoinformatics:** Coordinate transformations and spatial geometries.
* **Software Design:** Building a modular Python application for specific real-world tasks.

1. Spatial Configuration (`config.py`) 
* **Geometry:** A list of 22 high-precision waypoints are converted into a single `Shapely` LineString-object.
* **Coordinate Systems:** `GeoPandas` is used to initialize the route in EPSG:4326 (GPS coordinates) and transform it to EPSG:3067 (TM35-FIN).
* **Metric Accuracy:** Finnish metric system allows precise distance calculations (meters) instead of degrees, essential for navigating tight corridors in the lake.

2. Ice Detection Logic (`processor.py`)
* **Sentinel-2 Bands:** Green (B3) and Shortwave Infrared (SWIR - B11).
* **NDSI (Normalized Difference Snow Index):** NDSI = Green + SWIR / Green − SWIR
* **Spectral Response:** Ice and snow have high reflectance in the green spectrum but absorb SWIR radiation. Water aborbs both. NDSI is used to create a ratio to detect ice and liquid water in the pixels.
* **The Navigation Corridor:** 20 meter buffer is applied to both sides of the route. This creates a 40-meter wide polygon.

3. Data Streaming & Analysis (`analyzer.py`) 
To avoid downloading gigabytes of satellite data, the project uses a modern "Data-as-a-Service" approach.
* **STAC Interface:** Uses the `SpatioTemporal Asset Catalog API` to find imagery within a specific time window (March-May)
* **Microsoft Planetary Computer:** The data is streamed and only the specific pixels within the 40-meter corridor are processed.
* **Cloud Masking:** Integrates the `SCL (Scene Classification Layer)` to ignore pixels covered by clouds or shadows. This prevents skewed data.

# File Structure
* `main.py:` The entry point that runs the full seasonal analysis and generates the final report.
* `analyzer.py:` Handles the STAC search and data streaming logic.
* `processor.py:` Contains the mathematical NDSI functions and spatial profiling logic.
* `config.py:` Defines the waypoints and coordinate reference systems.

# Example Output

The program generates a Seasonal Melt Report and a visualization showing the ice profile of the route.

**Status Example:** `2025-05-10: 12.5% ice coverage - ⚠️ SLUSH`
