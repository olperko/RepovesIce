import geopandas as gpd
from shapely.geometry import LineString

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
path_gdf_metric = gpd.GeoDataFrame(
    index=[0],
    crs="EPSG:4326",
    geometry=[path_line]
).to_crs("EPSG:3067")

# Check the length of route
route_length = path_gdf_metric.length[0]
print(f"Total Ice Analysis Path: {route_length / 1000:.2f} km")