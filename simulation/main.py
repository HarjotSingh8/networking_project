import traffic_simulation
from random_topology import RandomTopology
from smart_topology import SmartTopology
import json

simultation_params = {
    "time_window": 1,
    "sim_center": (42.3141061843, -83.0368789337),
    "connection_distance": 0.1,
    "num_min_connections": 3,
    "similarity_weight": 0.7,
    "distance_weight": 0.3,
}

def new_simulation():
    """
    Run a new simulation with the specified parameters.
    """
    # Example usage of manual bounding boxes
    center = (42.3141061843, -83.0368789337)
    buffer_size = 1.5  # Size in km
    size = 1  # Size in km
    traffic_sim_size = 10

    simulation_bounding_box_buffer = traffic_simulation.manual_bounding_boxes(center, buffer_size)
    simulation_bounding_box = traffic_simulation.manual_bounding_boxes(center, size)
    simulation_bounding_box_traffic = traffic_simulation.manual_bounding_boxes(center, traffic_sim_size)
    BOUNDING_BOX = simulation_bounding_box_traffic
    print(f"Manual BOUNDING_BOX: {BOUNDING_BOX}")
    print("("+str(BOUNDING_BOX["min_lat"])+", "+str(BOUNDING_BOX["min_lon"])+","+str(BOUNDING_BOX["max_lat"])+", "+str(BOUNDING_BOX["max_lon"])+")")
    # Simulate traffic within the bounding box
    simulated_routes = traffic_simulation.simulate_traffic_within_box(
        num_trips=1000,
        main_box=simulation_bounding_box,
        bounding_box=BOUNDING_BOX,
        time_window=1,
        time_offset_range=(0, 240),
    )
    return simulated_routes, simulation_bounding_box


def save_simulation(simulation_data, bounding_box, filename="/simulation_data/simulation_data.json"):
    """
    Save the simulation data and bounding box to a JSON file.
    """
    data_to_save = {
        "simulation_data": simulation_data,
        "bounding_box": bounding_box
    }
    with open(filename, "w") as file:
        json.dump(data_to_save, file)
    print(f"Simulation data and bounding box saved to {filename}")

def load_simulation(filename="/simulation_data/simulation_data.json"):
    """
    Load the simulation data and bounding box from a JSON file.
    """
    try:
        with open(filename, "r") as file:
            data_loaded = json.load(file)
        print(f"Simulation data and bounding box loaded from {filename}")
        return data_loaded.get("simulation_data"), data_loaded.get("bounding_box")
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None, None

if __name__ == "__main__":
    # simulated_routes, simulation_bounding_box = new_simulation()
    # Save the simulation data to a JSON file
    # save_simulation(simulated_routes, simulation_bounding_box)
    # Load the simulation data from the JSON file
    loaded_simulation_data, loaded_simulation_bounding_box = load_simulation()

    simulated_routes = loaded_simulation_data
    simulation_bounding_box = loaded_simulation_bounding_box


    # run network simulation on simulated routes
    # network_simulation = RandomTopology(simulated_routes, simulation_bounding_box, simultation_params)
    network_simulation = SmartTopology(simulated_routes, simulation_bounding_box, simultation_params, "/simulation_data/smart_topology.json")
    network_simulation.run_simulation(time_interval=1)
    network_simulation = RandomTopology(simulated_routes, simulation_bounding_box, simultation_params, "/simulation_data/random_topology.json")
    network_simulation.run_simulation(time_interval=1)