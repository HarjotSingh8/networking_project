# Networking Project

So far, the project sets up a routing and simulation environment using [OSRM (Open Source Routing Machine)](https://project-osrm.org/) and a custom traffic simulation. The project includes services for extracting, partitioning, customizing routing graphs, running a routing server, and a frontend for visualization.

Next additions will be a simulation class for network topology, and multiple simulation algorithms.

## Prerequisites

- Docker and Docker Compose installed on your system.

## Project Structure

- `data/`: Directory for storing map data and processed files.
- `simulation/`: Contains the traffic simulation scripts and Dockerfile.
- `docker-compose.yml`: Defines the services for the project.

## Services

1. **OSRM Backend Services**:
   - `osrm-extract`: Extracts routing data from an OSM file.
   - `osrm-partition`: Partitions the routing graph for faster queries.
   - `osrm-customize`: Customizes the routing graph for traffic data.
   - `osrm-routed`: Starts the routing server.

2. **OSRM Frontend**:
   - Provides a web-based interface for routing visualization.

3. **Simulation**:
   - Runs a custom traffic simulation script.

## Setup and Usage

1. **Prepare the Data**:
   - Place your `.osm` or `.osm.pbf` file in the `data/` directory.

2. **Build and Start Services**:
   - Run the following command to start all services:
     ```bash
     docker-compose up --build
     ```

3. **Access the Frontend**:
   - Open your browser and navigate to `http://localhost:9966`.

4. **Run Traffic Simulation**:
   - The simulation service runs automatically. You can modify the `command` in the `docker-compose.yml` file to run specific scripts.

## Notes

- The OSRM backend services depend on the `alt.osm.pbf` file in the `data/` directory. Ensure this file is present before starting the services.
- The frontend connects to the backend at `http://localhost:8000`.

## Troubleshooting

- If a service fails, check the logs using:
  ```bash
  docker-compose logs <service_name>
  ```
- Ensure the required files are in the correct directories.

## License

This project is licensed under the MIT License.
