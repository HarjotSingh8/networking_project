import time
import math
import random

class NetworkSimulation:
    def __init__(self, cars, sim_co_ordinates, sim_params, sim_data_file=None):
        """
        Initialize the network simulation with a list of cars.

        Args:
            cars (list): A list of car objects. Each car object should have at least
                         'id', 'position' (latitude, longitude), and 'timestamp'.
                         The car object received contains 'offset' time and 'positions' data, and positions
        """
        self.cars = cars
        self.sim_co_ordinates = sim_co_ordinates
        self.sim_params = sim_params
        self.sim_data_file = sim_data_file
        self.init_cars()
        self.timestamp = 0
        self.cars_completed = 0
        self.new_connections_made = 0
        self.old_connections_dropped = 0
        self.active_connections = 0
        self.analytics = []

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
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def init_cars(self):
        """
        Initialize the cars with their positions and active status.
        """
        for id, car in enumerate(self.cars):
            car['active'] = False
            car['completed'] = False  # Add 'completed' flag
            car['id'] = id
            car['position'] = (car['positions'][0]['position'][0], car['positions'][0]['position'][1])  # Fixed reference
            car['network_connections'] = []

    def simulate_car_vectors(self, car, time_interval):
        """
        Returns motion and location vector of the car.
        """
        # Filter position data up to the current simulation timestamp
        relevant_positions = [pos for pos in car['positions'] if pos['timestamp'] <= self.timestamp]
        last_positions = relevant_positions[-5:]  # Take the last 5 positions

        if len(last_positions) < 2:
            return (0, 0, 0)  # Return zero vector and speed if insufficient data

        # Calculate the average vector
        avg_vector = (0, 0)
        for i in range(1, len(last_positions)):
            avg_vector = (
                avg_vector[0] + (last_positions[i]['position'][0] - last_positions[i-1]['position'][0]),
                avg_vector[1] + (last_positions[i]['position'][1] - last_positions[i-1]['position'][1])
            )
        avg_vector = (avg_vector[0] / (len(last_positions) - 1), avg_vector[1] / (len(last_positions) - 1))

        # Add random noise to the vector
        noise = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
        avg_vector = (avg_vector[0] + noise[0], avg_vector[1] + noise[1])

        # Calculate the distance and speed
        distance = self.calculate_distance(car['position'], last_positions[-1]['position'])
        speed = distance / time_interval

        return (avg_vector[0], avg_vector[1], speed)

    def simulate_car_positions(self, time_interval):
        """
        Simulate positions of cars by picking positions from their position data.
        """
        for car in self.cars:
            # Check if the car should be active at the current simulation timestamp
            if car['completed']:
                continue  # Skip cars that have completed their routes

            if self.timestamp >= car['offset'] and self.timestamp < (car['offset'] + len(car['positions'])):
                # Get the current position from the position data
                current_position = car['positions'][int(self.timestamp - car['offset'])]  # Ensure index is an integer
                car['position'] = (current_position['position'][0], current_position['position'][1])  # Fixed reference
                car['active'] = True
            else:
                car['active'] = False
                if self.timestamp >= (car['offset'] + len(car['positions'])):
                    car['completed'] = True  # Mark car as completed
                    self.cars_completed += 1
                    print(f"{self.cars_completed} cars have completed their routes.")

    def check_network(self):
        """
        Check the network connectivity of the cars.
        This function should be implemented in subclasses.
        """
        raise NotImplementedError("This method should be overridden in subclasses.")
    def analytics_update(self):
        """
        Update the analytics for the simulation.
        This function should be implemented in subclasses.
        """
        self.analytics.append({
            'timestamp': self.timestamp,
            'cars_completed': self.cars_completed,
            'new_connections_made': self.new_connections_made,
            'old_connections_dropped': self.old_connections_dropped,
            'active_connections': self.active_connections,
            'active_cars': len([car for car in self.cars if car['active']]),
        })
    
    def save_analytics(self, filename):
        """
        Save the simulation analytics to a file.

        Args:
            filename (str): The name of the file to save the analytics.
        """
        with open(filename, 'w') as f:
            for entry in self.analytics:
                f.write(f"{entry}\n")
        print(f"Analytics saved to {filename}")
    def run_simulation(self, time_interval=1):
        """
        Run the simulation for each car in the network.

        Args:
            time_interval (int): Time interval in seconds for each simulation step.
        """
        # Update car positions based on the current timestamp
        self.simulate_car_positions(time_interval)

        # Run simulation till all cars have completed their positions
        while any(not car['completed'] for car in self.cars):
            self.check_network()
            self.timestamp += time_interval
            # time.sleep(time_interval)
            self.simulate_car_positions(time_interval)
            for car in self.cars:
                if car['active']:
                    # Update the car's position directly from the position data
                    current_position = car['positions'][int(self.timestamp - car['offset'])]  # Ensure index is an integer
                    car['position'] = (current_position['position'][0], current_position['position'][1])  # Fixed reference
                    
                    # Calculate the motion vector and speed for network topology
                    car['motion_vector'] = self.simulate_car_vectors(car, time_interval)
            
            # Update the analytics
            self.analytics_update()
        
        # save the analytics to a file
        self.save_analytics(self.sim_data_file)