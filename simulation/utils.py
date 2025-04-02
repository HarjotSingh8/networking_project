import random
import math

def generate_random_coordinates(main_box):
    """Generate random coordinates within the bounding box."""
    lat = random.uniform(main_box["min_lat"]*1000000, main_box["max_lat"]*1000000) / 1000000
    lon = random.uniform(main_box["min_lon"]*1000000, main_box["max_lon"]*1000000) / 1000000
    return lat, lon

def update_coordinate_range():
    """
    Updates the BOUNDING_BOX variable by extracting the bounding box
    from an OSM file using a simple XML parser.
    """
    global BOUNDING_BOX

    # Example OSM file path (update this to your actual OSM file path)
    osm_file_path = "/data/alt.osm"

    try:
        import xml.etree.ElementTree as ET

        # Parse the OSM XML file
        tree = ET.parse(osm_file_path)
        root = tree.getroot()

        # Initialize variables to calculate the average location
        total_lat, total_lon = 0, 0
        node_count = 0

        # Iterate through all "node" elements to calculate the average location
        for node in root.findall("node"):
            lat = float(node.attrib["lat"])
            lon = float(node.attrib["lon"])
            total_lat += lat
            total_lon += lon
            node_count += 1

        if node_count == 0:
            raise Exception("No nodes found in the OSM file.")

        # Calculate the average latitude and longitude
        avg_lat = total_lat / node_count
        avg_lon = total_lon / node_count

        # Define a 500 m square around the average location
        # Approximation: 1 degree of latitude ≈ 111 km, 1 degree of longitude ≈ 111 km * cos(latitude)
        lat_offset = 500 / 111000  # 500 meters in degrees latitude
        lon_offset = 500 / (111000 * abs(math.cos(math.radians(avg_lat))))  # 500 meters in degrees longitude

        # Update the BOUNDING_BOX variable
        BOUNDING_BOX["min_lat"] = avg_lat - lat_offset
        BOUNDING_BOX["max_lat"] = avg_lat + lat_offset
        BOUNDING_BOX["min_lon"] = avg_lon - lon_offset
        BOUNDING_BOX["max_lon"] = avg_lon + lon_offset

        print(f"Updated BOUNDING_BOX: {BOUNDING_BOX}")

    except Exception as e:
        print(f"Error updating coordinate range: {e}")

def manual_bounding_boxes(center, size):
    """
    Generate a square bounding box around a center point with a specified size.

    Args:
        center (tuple): Center point (latitude, longitude).
        size (float): Size of the bounding box in kms.

    Returns:
        dict: Bounding box with min and max latitude and longitude.
    """
    lat, lon = center
    # Convert size from kilometers to degrees
    lat_offset = size / 111  # 1 degree latitude ≈ 111 km
    lon_offset = size / (111 * abs(math.cos(math.radians(lat))))  # 1 degree longitude ≈ 111 km * cos(latitude)

    # Use the smaller offset to ensure the bounding box is square
    offset = min(lat_offset, lon_offset)

    return {
        "min_lat": lat - offset / 2,
        "max_lat": lat + offset / 2,
        "min_lon": lon - offset / 2,
        "max_lon": lon + offset / 2
    }