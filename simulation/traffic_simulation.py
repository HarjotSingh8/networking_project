#!/usr/bin/python -u
import random
import requests
import time
import timeit
import math
from utils import *
from osrm_utils import *

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
    attempted_routes = 0  # Renamed for clarity
    remaining_attempts = 100  # Renamed for clarity
    while len(simulated_trips) < num_trips and remaining_attempts > 0:
        remaining_attempts -= 1
        routes = generate_random_routes(num_routes=num_trips - len(simulated_trips), main_box=main_box)
        attempted_routes += len(routes)
        # Check if route crosses the bounding box
        for route in routes:
            try:
                # Simulate the car on the route
                simulation_data = simulate_car_on_route(route, time_window=time_window)
                # Check if the route is within the bounding box
                if simulation_data:
                    for position in simulation_data:
                        lon, lat = position["position"]
                        if (bounding_box["min_lat"] <= lat <= bounding_box["max_lat"] and
                                bounding_box["min_lon"] <= lon <= bounding_box["max_lon"]):
                            random_offset = int(random.uniform(*time_offset_range))  # Generate random integer time offset
                            simulated_trips.append({
                                "route": route,
                                "positions": simulation_data,
                                "offset": random_offset,
                            })
                            print(f"Simulated trip added with offset {random_offset:.2f} seconds")
                            break
            except Exception as e:
                print(f"Error simulating route: {e}")
    attempted_routes += len(routes)
    print(f"Number of routes attempted: {attempted_routes}")
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
