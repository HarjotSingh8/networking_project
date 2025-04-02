from network_simulation import NetworkSimulation
from geopy.distance import geodesic

class SmartTopology(NetworkSimulation):
    def __init__(self, cars, sim_co_ordinates, sim_params, sim_data_file=None):
        """
        Initialize the smart topology simulation with a list of cars.

        Args:
            cars (list): A list of car objects. Each car object should have at least
                         'id', 'position' (latitude, longitude), and 'timestamp'.
        """
        super().__init__(cars, sim_co_ordinates, sim_params, sim_data_file)
        self.simulation_results = []
        self.time_tick = 0
        self.new_connections_made = 0
        self.old_connections_dropped = 0
        self.active_connections = 0  # Initialize active connections as a number
        self.avg_connection_health = 0
        self.connection_durations = {}  # Track connection durations
        self.avg_connection_duration = 0

    def calculate_vector_similarity(self, vector1, vector2):
        """
        Calculate the similarity between two motion vectors using cosine similarity.

        Args:
            vector1 (tuple): Motion vector of the first car (x, y).
            vector2 (tuple): Motion vector of the second car (x, y).

        Returns:
            float: Cosine similarity between the two vectors.
        """
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = (vector1[0]**2 + vector1[1]**2)**0.5
        magnitude2 = (vector2[0]**2 + vector2[1]**2)**0.5
        if magnitude1 == 0 or magnitude2 == 0:
            return 0  # Avoid division by zero
        return dot_product / (magnitude1 * magnitude2)

    def check_network(self):
        """
        Check if cars are within the connection range of each other and prioritize
        connections between cars moving in the same direction.
        """
        print("Checking network connections with motion vector prioritization...")
        connection_distance = self.sim_params.get("connection_distance", 0.4)  # Default to 0.4 km
        num_min_connections = self.sim_params.get("num_min_connections", 3)  # Default to 3 connections
        similarity_threshold = self.sim_params.get("similarity_threshold", 0.8)  # Default to 0.8 cosine similarity
        similarity_weight = self.sim_params.get("similarity_weight", 0.7)  # Default weight for similarity
        distance_weight = self.sim_params.get("distance_weight", 0.3)  # Default weight for distance
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
                        similarity = self.calculate_vector_similarity(
                            car.get("motion_vector", (0, 0)),
                            other_car.get("motion_vector", (0, 0))
                        )
                        # Normalize distance to a score between 0 and 1
                        distance_score = max(0, 1 - (distance / connection_distance))
                        # Calculate final score using weights
                        final_score = (similarity_weight * similarity) + (distance_weight * distance_score)
                        potential_connections.append((other_car["id"], final_score))

            # Sort potential connections by final score (descending)
            potential_connections.sort(key=lambda x: -x[1])

            for other_car_id, final_score in potential_connections:
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
        connected_pairs = []  # Reset connected pairs
        for car in active_cars:
            for connected_car_id in car["connections"]:
                if (car["id"], connected_car_id) not in connected_pairs and (connected_car_id, car["id"]) not in connected_pairs:
                    connected_pairs.append((car["id"], connected_car_id))

        self.simulation_results.append({
            "time_tick": self.time_tick,
            "connected_pairs": connected_pairs
        })

        # Update the number of active connections
        self.active_connections = len(connected_pairs)

        # Calculate average connections per active car
        total_connections = sum(len(car["connections"]) for car in active_cars)
        avg_connections = total_connections / len(active_cars) if active_cars else 0
        print(f"Average connections per active car: {avg_connections:.2f}")

        # Calculate average connection duration
        if not hasattr(self, "connection_durations"):
            self.connection_durations = {}  # Initialize connection durations if not present
        for car in active_cars:
            for connected_car_id in car["connections"]:
                pair_key = tuple(sorted((car["id"], connected_car_id)))
                self.connection_durations[pair_key] = self.connection_durations.get(pair_key, 0) + 1
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
        print(f"New connections made: {new_connections}, Old connections dropped: {old_connections}")
