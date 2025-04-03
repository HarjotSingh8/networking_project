from network_simulation import NetworkSimulation
from geopy.distance import geodesic  # Import for distance calculation

class RandomTopology(NetworkSimulation):
    def __init__(self, cars, sim_co_ordinates, sim_params, sim_data_file=None):
        """
        Initialize the random topology simulation with a list of cars.

        Args:
            cars (list): A list of car objects. Each car object should have at least
                         'id', 'position' (latitude, longitude), and 'timestamp'.
        """
        super().__init__(cars, sim_co_ordinates, sim_params, sim_data_file)
        self.simulation_results = []
        self.time_tick = 0
        self.new_connections_made = 0
        self.old_connections_dropped = 0
        self.connection_durations = {}  # Track connection durations

    def check_network(self):
        """
        Check if cars are within the connection range of each other.

        Ensures each car maintains a minimum number of connections and updates
        the connections only if a connection needs to be dropped.
        """
        print("Checking network connections...")
        connection_distance = self.sim_params.get("connection_distance", 0.4)  # Default to 0.4 km
        num_min_connections = self.sim_params.get("num_min_connections", 3)  # Default to 3 connections
        connected_pairs = []
        new_connections = 0
        old_connections = 0
        
        active_cars = [car for car in self.cars if car.get("active", True)]  # Only consider active cars

        # Validate existing connections
        for car in active_cars:
            valid_connections = []
            for connected_car_id in car.get("connections", []):
                connected_car = next((c for c in active_cars if c["id"] == connected_car_id), None)
                if connected_car:
                    distance = geodesic(car["position"], connected_car["position"]).km
                    if distance <= connection_distance:
                        valid_connections.append(connected_car_id)
                        # Increment connection duration
                        pair_key = tuple(sorted((car["id"], connected_car_id)))
                        self.connection_durations[pair_key] = self.connection_durations.get(pair_key, 0) + 1
                    else:
                        old_connections += 1
                        # Remove connection duration tracking
                        pair_key = tuple(sorted((car["id"], connected_car_id)))
                        self.connection_durations.pop(pair_key, None)
                else:
                    old_connections += 1
            car["connections"] = valid_connections

        # Add new connections if needed
        for car in active_cars:
            if len(car["connections"]) >= num_min_connections:
                continue  # Skip cars that already satisfy the minimum connections

            potential_connections = []
            for other_car in active_cars:
                if other_car["id"] != car["id"] and other_car["id"] not in car["connections"]:
                    distance = geodesic(car["position"], other_car["position"]).km
                    if distance <= connection_distance:
                        potential_connections.append((other_car["id"], distance))
            
                # Check if potential connections + existing connections satisfy the minimum requirement
                if len(car["connections"]) + len(potential_connections) > num_min_connections:
                    break  # Skip if not enough potential connections to satisfy the requirement

            # potential_connections.sort(key=lambda x: x[1])  # Sort by distance

            for other_car_id, distance in potential_connections:
                if len(car["connections"]) >= num_min_connections:
                    break  # Stop adding connections if min_connections is satisfied
                car["connections"].append(other_car_id)
                other_car = next(c for c in active_cars if c["id"] == other_car_id)
                other_car["connections"].append(car["id"])
                connected_pairs.append((car["id"], other_car_id))
                new_connections += 1
                # Initialize connection duration
                pair_key = tuple(sorted((car["id"], other_car_id)))
                self.connection_durations[pair_key] = 1

        # Record connected pairs for this tick
        for car in active_cars:
            for connected_car_id in car["connections"]:
                if (car["id"], connected_car_id) not in connected_pairs and (connected_car_id, car["id"]) not in connected_pairs:
                    connected_pairs.append((car["id"], connected_car_id))

        # Calculate average connections per active car
        total_connections = sum(len(car["connections"]) for car in active_cars)
        avg_connections = total_connections / len(active_cars) if active_cars else 0
        print(f"Average connections per active car: {avg_connections:.2f}")

        # Calculate average connection duration
        if self.connection_durations:
            avg_connection_duration = sum(self.connection_durations.values()) / len(self.connection_durations)
        else:
            avg_connection_duration = 0
        self.avg_connection_duration = avg_connection_duration
        print(f"Average connection duration: {avg_connection_duration:.2f} ticks")

        # Calculate average connection health
        if connected_pairs:
            total_health = 0
            for car in active_cars:
                for connected_car_id in car["connections"]:
                    connected_car = next((c for c in active_cars if c["id"] == connected_car_id), None)
                    if connected_car:
                        distance = geodesic(car["position"], connected_car["position"]).km
                        connection_health = max(0, 1 - (distance / connection_distance))  # Normalize health to [0, 1]
                        total_health += connection_health
            avg_connection_health = total_health / len(connected_pairs)
        else:
            avg_connection_health = 0
        self.avg_connection_health = avg_connection_health
        print(f"Average connection health: {avg_connection_health:.2f}")

        # Record simulation results for this tick
        self.simulation_results.append({
            "time_tick": self.time_tick,
            "connected_pairs": connected_pairs,
            "avg_connection_duration": avg_connection_duration,  # Store average connection duration
            "avg_connection_health": avg_connection_health  # Store average connection health
        })

        # Update the counters for new and old connections
        self.new_connections_made = new_connections
        self.old_connections_dropped = old_connections
        self.num_connections = len(connected_pairs)

        # Update active connections
        self.active_connections = [
            (car["id"], connected_car_id)
            for car in active_cars
            for connected_car_id in car["connections"]
        ]

        print(f"created: {new_connections}, dropped: {old_connections}, connections: {len(connected_pairs)}, "
              f"avg_connection_duration: {avg_connection_duration:.2f} ticks, avg_connection_health: {avg_connection_health:.2f}")
