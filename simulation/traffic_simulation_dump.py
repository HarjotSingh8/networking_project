#!/usr/bin/python -u
import random
import requests
import time
import timeit
import math

# Define the bounding box for the map area (latitude and longitude)
BOUNDING_BOX = { # Example: Windsor Ontario
    "min_lat": 42.2500,
    "max_lat": 42.4000,
    "min_lon": -83.0500,
    "max_lon": -82.9000
}

OSRM_API_URL = "http://osrm-routed:5000"  # Update with your OSRM server URL

def generate_random_coordinates(main_box=BOUNDING_BOX):
    """Generate random coordinates within the bounding box."""
    lat = random.uniform(main_box["min_lat"]*1000000, main_box["max_lat"]*1000000) / 1000000
    lon = random.uniform(main_box["min_lon"]*1000000, main_box["max_lon"]*1000000) / 1000000
    return lat, lon

# def get_route_from_osrm(start, end):
#     """Fetch route from OSRM API."""
#     url = f"{OSRM_API_URL}/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
#     params = {
#         "overview": "full",
#         "geometries": "geojson",
#         "steps": "true"  # Request detailed steps in the response
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise Exception(f"OSRM API error: {response.status_code}, {response.text}")

def generate_random_routes(num_routes=10, main_box=BOUNDING_BOX):
    """Generate random routes using OSRM API."""
    routes = []
    for _ in range(num_routes):
        start = generate_random_coordinates(main_box)
        end = generate_random_coordinates(main_box)
        print(start,end)
        # Query OSRM API for the route
        try:
            route = get_route_from_osrm(start, end)
            routes.append(route)
        except Exception as e:
            print(f"Error fetching route: {e}")
    return routes

def simulate_car_on_route(route, time_window=1, start_time=None):
    """
    Simulate a car driving along a route using OSRM-provided speed data, evaluating position at each time window.

    Args:
        route (dict): The route data from OSRM API.
        time_window (float): Time window in seconds to evaluate the car's position.
        start_time (float): Start time of the simulation in seconds since the epoch.

    Returns:
        list: A list of dictionaries containing positions (latitude, longitude) and timestamps.
    """
    if "routes" not in route or not route["routes"]:
        print("Invalid route data.")
        return []

    # Extract the legs from the route
    legs = route["routes"][0]["legs"]
    positions = []  # List to store positions and timestamps at each time window

    if start_time is None:
        start_time = time.time()  # Default to current time if not provided

    total_distance = 0  # Initialize total distance
    total_duration = 0  # Initialize total duration

    print("Starting simulation...")
    for leg in legs:
        total_distance += leg["distance"]  # Accumulate total distance
        total_duration += leg["duration"]  # Accumulate total duration
        steps = leg.get("steps", [])
        if steps:
            # Simulate using steps if available
            for step in steps:
                start = step["geometry"]["coordinates"][0]
                end = step["geometry"]["coordinates"][-1]
                distance = step["distance"]  # Distance in meters
                duration = step["duration"]  # Duration in seconds
                road_name = step.get("name", "Unnamed Road")  # Road name (if available)

                # Calculate speed (m/s)
                speed = distance / duration if duration > 0 else 0

                print(f"Driving on {road_name} from {start} to {end} "
                      f"(distance: {distance:.2f} m, duration: {duration:.2f} s, speed: {speed:.2f} m/s)")

                # Simulate movement in time windows
                elapsed_time = 0
                while elapsed_time < duration:
                    # time.sleep(time_window)  # Commented out to avoid waiting
                    elapsed_time += time_window
                    progress = min(elapsed_time / duration, 1)  # Ensure progress does not exceed 1
                    current_position = [
                        start[0] + (end[0] - start[0]) * progress,
                        start[1] + (end[1] - start[1]) * progress
                    ]
                    current_timestamp = start_time + elapsed_time
                    positions.append({"position": current_position, "timestamp": current_timestamp})
                    # print(f"At time {elapsed_time:.2f}s: Current position: {current_position}, Timestamp: {current_timestamp}")
        else:
            # Fall back to geometry-based simulation if steps are not available
            print("No steps available in this leg. Falling back to geometry-based simulation.")
            coordinates = route["routes"][0]["geometry"]["coordinates"]
            total_distance = leg["distance"]  # Total distance in meters
            total_duration = leg["duration"]  # Total duration in seconds

            num_segments = len(coordinates) - 1
            if num_segments == 0:
                print("No segments to simulate.")
                continue

            segment_distance = total_distance / num_segments
            segment_duration = total_duration / num_segments

            for i in range(num_segments):
                start = coordinates[i]
                end = coordinates[i + 1]

                print(f"Moving from {start} to {end} "
                      f"(distance: {segment_distance:.2f} m, duration: {segment_duration:.2f} s)")

                # Simulate movement in time windows
                elapsed_time = 0
                while elapsed_time < segment_duration:
                    # time.sleep(time_window)  # Commented out to avoid waiting
                    elapsed_time += time_window
                    progress = min(elapsed_time / segment_duration, 1)  # Ensure progress does not exceed 1
                    current_position = [
                        start[0] + (end[0] - start[0]) * progress,
                        start[1] + (end[1] - start[1]) * progress
                    ]
                    current_timestamp = start_time + elapsed_time
                    positions.append({"position": current_position, "timestamp": current_timestamp})
                    # print(f"At time {elapsed_time:.2f}s: Current position: {current_position}, Timestamp: {current_timestamp}")

    print(f"Simulation complete. Total distance traveled: {total_distance:.2f} meters. ")
    print(f"Total time taken: {total_duration:.2f} seconds.")
    return positions

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

def simulate_traffic_within_box(num_trips, main_box, bounding_box, time_window=1, time_offset_range=(0, 60)):
    """
    Simulate traffic within a bounding box.

    Args:
        num_trips (int): Number of trips to simulate.
        time_window (int): Time window in seconds for each simulation step.
        bounding_box (dict): Bounding box with min and max latitude and longitude.
        time_offset_range (tuple): Range (min, max) of random time offsets in seconds.

    Returns:
        list: List of simulated trips with positions and timestamps.
    """
    simulated_trips = []
    tried_routes = 0
    tries = 100
    while len(simulated_trips) < num_trips and tries > 0:
        tries -= 1
        routes = generate_random_routes(num_routes=num_trips-len(simulated_trips), main_box=main_box)
        tried_routes += len(routes)
        # check if route crosses the bounding box
        for route in routes:
            try:
                # simulate the car on the route
                sim = simulate_car_on_route(route, time_window=time_window)
                # check if the route is within the bounding box
                if sim:
                    random_offset = random.uniform(*time_offset_range)  # Generate random time offset
                    for position in sim:
                        lon, lat = position["position"]
                        # position["timestamp"] += random_offset  # Apply the time offset
                        # print(f"Position: {position['position']}, Bounding Box: {bounding_box}")
                        if (bounding_box["min_lat"] <= lat <= bounding_box["max_lat"] and
                                bounding_box["min_lon"] <= lon <= bounding_box["max_lon"]):
                            simulated_trips.append(sim)
                            print(f"Simulated trip added with offset {random_offset:.2f} seconds")
                            break
                            
            except Exception as e:
                print(f"Error simulating route: {e}")
    tried_routes += len(routes)
    print(f"Number of routes tried: {tried_routes}")
    print(f"Number of trips simulated: {len(simulated_trips)}")
    return simulated_trips

if __name__ == "__main__":
    update_coordinate_range()  # Update the bounding box from OSRM
    # Example usage of manual bounding boxes
    center = (42.3141061843, -83.0368789337)
    buffer_size = 1.5  # Size in km
    size = 1  # Size in km
    traffic_sim_size = 10

    simulation_bounding_box_buffer = manual_bounding_boxes(center, buffer_size)
    simulation_bounding_box = manual_bounding_boxes(center, size)
    simulation_bounding_box_traffic = manual_bounding_boxes(center, traffic_sim_size)
    BOUNDING_BOX = simulation_bounding_box_traffic
    print(f"Manual BOUNDING_BOX: {BOUNDING_BOX}")
    print("("+str(BOUNDING_BOX["min_lat"])+", "+str(BOUNDING_BOX["min_lon"])+","+str(BOUNDING_BOX["max_lat"])+", "+str(BOUNDING_BOX["max_lon"])+")")
    simulate_traffic_within_box(1000, simulation_bounding_box, time_window=1)
    # def main_execution():
    #     # Generate a single random route
    #     routes = generate_random_routes(num_routes=1)
    #     if routes:
    #         print(routes[0])
    #         start_time = time.time()
    #         for route in routes:
    #             positions = simulate_car_on_route(route, time_window=1, start_time=start_time)  # Simulate using OSRM speed data    
    #         # positions = simulate_car_on_route(routes[0], time_window=1, start_time=start_time)  # Simulate using OSRM speed data
    #         # print("Positions at each time window:", positions)

    # # Time the execution of the main_execution function
    # execution_time = timeit.timeit(main_execution, number=1)
    # print(f"Execution time: {execution_time:.2f} seconds")

'''
{
    'code': 'Ok', 
    'routes': [
        {
            'geometry': {
                'coordinates': [[-82.912253, 42.297453], [-82.912353, 42.297568], [-82.912515, 42.298115], [-82.913544, 42.297928], [-82.913637, 42.298423], [-82.913746, 42.298768], [-82.913804, 42.298933], [-82.914023, 42.299312], [-82.914199, 42.299595], [-82.915409, 42.299276], [-82.916138, 42.299127], [-82.917423, 42.298811], [-82.917643, 42.298805], [-82.917773, 42.298824], [-82.917878, 42.298861], [-82.918032, 42.298962], [-82.91813, 42.299072], [-82.918303, 42.299489], [-82.91862, 42.300249], [-82.918932, 42.300965], [-82.918965, 42.30104], [-82.920955, 42.300363], [-82.921306, 42.300243], [-82.921516, 42.300174], [-82.922211, 42.299925], [-82.922322, 42.299886], [-82.92276, 42.299737], [-82.923458, 42.299481], [-82.923952, 42.299321], [-82.924403, 42.299125], [-82.924785, 42.298933], [-82.92507, 42.298719], [-82.925583, 42.298338], [-82.926064, 42.297962], [-82.926182, 42.297883], [-82.926338, 42.297778], [-82.926527, 42.297651], [-82.926871, 42.297492], [-82.927018, 42.297438], [-82.92734, 42.297319], [-82.92744, 42.297343], [-82.927852, 42.297213], [-82.927995, 42.297167], [-82.928151, 42.297115], [-82.928094, 42.297023], [-82.928064, 42.296973], [-82.927694, 42.296365], [-82.927254, 42.295647], [-82.926611, 42.294679], [-82.926256, 42.294147], [-82.925402, 42.292848], [-82.924953, 42.292104], [-82.924885, 42.292003], [-82.924681, 42.291724], [-82.924443, 42.29145], [-82.924089, 42.291044], [-82.923759, 42.290662], [-82.923511, 42.290353], [-82.923457, 42.290285], [-82.923067, 42.2898], [-82.922851, 42.289501], [-82.92281, 42.289432], [-82.922432, 42.288822], [-82.922018, 42.288199], [-82.921591, 42.28754], [-82.921419, 42.28726], [-82.921265, 42.287095], [-82.919988, 42.285016], [-82.918958, 42.283048], [-82.918091, 42.281726], [-82.914924, 42.276723], [-82.914583, 42.276185], [-82.914368, 42.275846], [-82.912879, 42.273498], [-82.912681, 42.273185], [-82.914303, 42.272891], [-82.919289, 42.271985], [-82.926839, 42.270615], [-82.928329, 42.270377], [-82.928344, 42.270155], [-82.928542, 42.267201], [-82.928841, 42.262741], [-82.926892, 42.262682]], 
                'type': 'LineString'
                }, 
            'legs': [
                {
                    'steps': [], 
                    'summary': '', 
                    'weight': 687.1, 
                    'duration': 687.1, 
                    'distance': 7114.2
                }
            ], 
            'weight_name': 'routability', 
            'weight': 687.1, 
            'duration': 687.1, 
            'distance': 7114.2
        }
    ], 
    'waypoints': [
        {
            'hint': 'CV4AgBteAIAWAAAAAAAAAAAAAADUAAAAbExzQQAAAAAAAAAALRkTQxYAAAAAAAAAAAAAANQAAACAAAAAA9wO-21ohQLa2w77umeFAgAAPwkWGwZe', 
            'distance': 20.168689195, 
            'name': 'Aspen Lane', 
            'location': [-82.912253, 42.297453]
        }, 
        {
            'hint': 'ywYAgAEHAIDGAgAA6AAAAPEDAAAAAAAANJ32Q5vpIEMUJi9EAAAAAMYCAADoAAAA8QMAAAAAAACAAAAA1KIO-5rghALzog77z-KEAgcADxEWGwZe', 
            'distance': 62.811503714, 
            'name': 'Baseline Road', 
            'location': [-82.926892, 42.262682]
        }
    ]
}
'''