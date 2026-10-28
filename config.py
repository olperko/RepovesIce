import geopandas as gpd
from shapely.geometry import LineString

# ==================== ANALYSIS PARAMETERS ====================

# Time window for satellite imagery analysis
TIME_WINDOW = "2025-11-01/2026-05-31"

# Satellite data parameters
CLOUD_COVER_LIMIT = 20  # Maximum cloud cover percentage
RESOLUTION_METERS = 10  # Spatial resolution in meters
BUFFER_METERS = 20  # Buffer distance around route for analysis
SAMPLING_STEP_METERS = 100  # Distance between sampling points along route

# Ice detection thresholds
# Tuned against full-season 2025-11/2026-05 pixel distributions (see analysis notes):
# open water sits tightly around NDSI≈0 / NDWI≈0 with only a sparse high tail
# (NDSI 99th pct ≈0.13, NDWI 1st pct ≈-0.11 on confirmed open-water scenes),
# while confirmed full-ice scenes sit far past both thresholds (NDSI 10th pct ≈0.6,
# NDWI 10th pct ≈-0.29). NDSI=0.15 sits at the best cut point in the narrow overlap
# zone; NDWI tightened to -0.12 to shave off the open-water noise tail without
# losing sensitivity on real ice.
ICE_THRESHOLD_NDSI = 0.15  # NDSI threshold for ice detection (lowered for spring slush)
ICE_THRESHOLD_NDWI = -0.12  # NDWI threshold for ice detection (water > 0, ice < 0)

# Ice coverage status thresholds (percentages)
STATUS_FROZEN_THRESHOLD = 50  # Above this = FROZEN
STATUS_OPEN_THRESHOLD = 10  # Below this = OPEN, between = SLUSH

# Cloud masking SCL (Scene Classification Layer) values to exclude
# 3 = Cloud shadows, 8 = Cloud medium probability, 9 = Cloud high probability
CLOUD_MASK_VALUES = [3, 8, 9]

# SCL values that represent the actual surface being analyzed (water or snow/ice).
# Restricting to these excludes land/vegetation pixels, whose NIR reflectance can
# otherwise be misread as "black ice" by the NDWI threshold.
# 6 = Water, 11 = Snow/Ice
SURFACE_SCL_VALUES = [6, 11]

# Sentinel-2 bands for analysis
BANDS = {
    'green': 'B03',  # Green band (560 nm) - 10m resolution
    'nir': 'B08',    # Near-Infrared (842 nm) - 10m resolution
    'swir': 'B11',   # SWIR (1610 nm) - 20m resolution (resampled to 10m)
    'scl': 'SCL'     # Scene Classification Layer
}

# ==================== ROUTE GEOMETRY ====================

# Waypoints from Point A to point B (Longitude, Latitude)
waypoints = [
    # (Longitude, Latitude)
    (26.837916, 61.140081), # Point A
    (26.834718, 61.136952), # Central Tihvetjärvi
    (26.853450, 61.121139), # Peuranpäänsaarien ja Hulinsaarin ohi
    (26.879831, 61.136507), # Ottapajansaaret
    (26.879533, 61.141606), # Ottapajansaarien ohi
    (26.869198, 61.145964), # Tuuhansalmi
    (26.867548, 61.148150), # Tuuhansalmen läpi
    (26.871262, 61.149800), # Tervahaudanlahtea kohti
    (26.867346, 61.151458), # Sikoniemi
    (26.857437, 61.154447), # Kapiavesi
    (26.852460, 61.154359), # Poistuminen Kapiavedeltä
    (26.862778, 61.151489), # Sikoniemen ohi
    (26.845360, 61.157155), # Lossin lähestyminen
    (26.844445, 61.159846), # Lossi
    (26.836464, 61.163783), # Lapinsalmen silta
    (26.835713, 61.164934), # Sillan alitus
    (26.834422, 61.165217), # Saapuminen Lapinsalmeen
    (26.832811, 61.165324), # Lapinsalmi
    (26.830507, 61.166824), # Lapinsalmen läpi
    (26.831324, 61.170908), # Patasaaren ohi
    (26.833764, 61.175213), # Kaatiosaari
    (26.823674, 61.177995), # Ruskiasalmi
    (26.823583, 61.184256), # Point B: Karhulahden nuotiopaikka
]

path_line = LineString(waypoints)

# Initialize in WGS84 and project to Finnish Metric System (EPSG:3067)
path_gdf = gpd.GeoDataFrame(
    index=[0],
    crs="EPSG:4326",
    geometry=[path_line]
)
path_gdf_metric = path_gdf.to_crs("EPSG:3067")

# Check the length of route
route_length = path_gdf_metric.length[0]
print(f"Total Ice Analysis Path: {route_length / 1000:.2f} km")
