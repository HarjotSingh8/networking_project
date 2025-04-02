import time
import math

class NetworkSimulation:
    def __init__(self, cars):
        """
        Initialize the network simulation with a list of cars.

        Args:
            cars (list): A list of car objects. Each car object should have at least
                         'id', 'position' (latitude, longitude), and 'timestamp'.
        """
        self.cars = cars

    def calculate_distance(self, pos1, pos2):
        """
        Calculate the distance between two positions using the Haversine formula.

        Args:
            pos1 (tuple): (latitude, longitude) of the first position.
            pos2 (tuple): (latitude, longitude) of the second position.

        Returns:
            float: Distance in meters.
        """
        R = 6371000  # Radius of Earth in meters
        lat1, lon1 = math.radians(pos1[0]), math.radians(pos1[1])
        lat2, lon2 = math.radians(pos2[0]), math.radians(pos2[1])
        dlat = lat2 - lat1
        dlon = dlon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def simulate_communication(self, range_meters=100):
        """
        Simulate communication between cars within a certain range.

        Args:
            range_meters (float): The communication range in meters.

        Returns:
            dict: A dictionary where keys are car IDs and values are lists of IDs
                  of cars within communication range.
        """
        communication_map = {}
        for car in self.cars:
            car_id = car['id']
            car_position = car['position']
            communication_map[car_id] = []

            for other_car in self.cars:
                if car_id == other_car['id']:
                    continue
                distance = self.calculate_distance(car_position, other_car['position'])
                if distance <= range_meters:
                    communication_map[car_id].append(other_car['id'])

        return communication_map

    def log_simulation(self, duration_seconds=10, interval_seconds=1):
        """
        Log the communication simulation over a period of time.

        Args:
            duration_seconds (int): Total duration of the simulation in seconds.
            interval_seconds (int): Interval between each simulation step in seconds.
        """
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            communication_map = self.simulate_communication()
            print(f"Communication Map at {time.time()}: {communication_map}")
            time.sleep(interval_seconds)

    def run_simulation_with_algorithm(self, algorithm, **kwargs):
        """
        Run the network simulation using a specified topology algorithm.

        Args:
            algorithm (callable): A function that implements the network topology algorithm.
                                  It should accept a list of cars and additional parameters.
            **kwargs: Additional parameters to pass to the algorithm.

        Returns:
            Any: The result of the algorithm execution.
        """
        if not callable(algorithm):
            raise ValueError("The provided algorithm must be callable.")
        
        print(f"Running simulation with algorithm: {algorithm.__name__}")
        return algorithm(self.cars, **kwargs)
