import json
import matplotlib.pyplot as plt

'''
Data in the json files
[
{'timestamp': 1, 'cars_completed': 0, 'new_connections_made': 4, 'old_connections_dropped': 24, 'active_connections': 8, 'active_cars': 14, 'avg_connection_duration': 1.0}
]
'''

def load_simulation_data(filename):
    """
    Load simulation data from a JSON file.
    """
    try:
        with open(filename, "r") as file:
            data_loaded = json.load(file)
        print(f"Simulation data loaded from {filename}")
        return data_loaded
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}: {e}")
        try:
            with open(filename, "r") as file:
                print("Problematic content:")
                # print(file.read())
        except Exception as inner_e:
            print(f"Could not read file content due to: {inner_e}")
        return None
    except Exception as e:
        print(f"An error occurred while loading {filename}: {e}")
        return None

def plot_simulation_data(data, title):
    """
    Plot simulation data using matplotlib.
    """
    if data is None:
        print("No data to plot.")
        return

    timestamps = [entry['timestamp'] for entry in data]
    active_cars = [entry['active_cars'] for entry in data]
    new_connections = [entry['new_connections_made'] for entry in data]
    old_connections = [entry['old_connections_dropped'] for entry in data]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, active_cars, label='Active Cars', marker='o')
    plt.plot(timestamps, new_connections, label='New Connections', marker='o')
    plt.plot(timestamps, old_connections, label='Old Connections', marker='o')

    plt.title(title)
    plt.xlabel('Time Tick')
    plt.ylabel('Count')
    plt.legend()
    plt.grid()
    # plt.show()
    plt.savefig(f"/visualization/{title}.png")
    plt.close()

def plot_dual_simulation_data(data1, data2, title):
    """
    Plot simulation data using matplotlib.
    """
    if data1 is None or data2 is None:
        print("No data to plot.")
        return
    timestamps1 = [entry['timestamp'] for entry in data1]
    timestamps2 = [entry['timestamp'] for entry in data2]
    active_cars1 = [entry['active_cars'] for entry in data1]
    new_connections1 = [entry['new_connections_made'] for entry in data1]
    old_connections1 = [entry['old_connections_dropped'] for entry in data1]
    active_cars2 = [entry['active_cars'] for entry in data2]
    new_connections2 = [entry['new_connections_made'] for entry in data2]
    old_connections2 = [entry['old_connections_dropped'] for entry in data2]
    # Combine timestamps and data
    timestamps = sorted(set(timestamps1 + timestamps2))
    active_cars = [0] * len(timestamps)
    new_connections = [0] * len(timestamps)
    old_connections = [0] * len(timestamps)
    for i, timestamp in enumerate(timestamps):
        if timestamp in timestamps1:
            idx = timestamps1.index(timestamp)
            active_cars[i] += active_cars1[idx]
            new_connections[i] += new_connections1[idx]
            old_connections[i] += old_connections1[idx]
        if timestamp in timestamps2:
            idx = timestamps2.index(timestamp)
            active_cars[i] += active_cars2[idx]
            new_connections[i] += new_connections2[idx]
            old_connections[i] += old_connections2[idx]


    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, active_cars, label='Active Cars', marker='o')
    plt.plot(timestamps, new_connections, label='New Connections', marker='o')
    plt.plot(timestamps, old_connections, label='Old Connections', marker='o')

    plt.title(title)
    plt.xlabel('Time Tick')
    plt.ylabel('Count')
    plt.legend()
    plt.grid()
    # plt.show()
    plt.savefig(f"/visualization/{title}.png")
    plt.close()

def plot_comparison(data1, data2, key, title):
    """
    Plot comparison of two simulation data sets in black and white.
    """
    if data1 is None or data2 is None:
        print("No data to plot.")
        return

    timestamps1 = [entry['timestamp'] for entry in data1]
    timestamps2 = [entry['timestamp'] for entry in data2]
    values1 = [entry[key] for entry in data1]
    values2 = [entry[key] for entry in data2]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps1, values1, label='Algorithm 1', marker='o', color='black', linestyle='-')
    plt.plot(timestamps2, values2, label='Algorithm 2', marker='x', color='gray', linestyle='--')

    plt.title(title)
    plt.xlabel('Time Tick')
    plt.ylabel(key)
    plt.legend()
    plt.grid(color='gray', linestyle=':', linewidth=0.5)
    # plt.show()
    plt.savefig(f"/visualization/{title}.png")
    plt.close()

def main():
    random_algorithm = load_simulation_data("/simulation_data/random_topology.json")[100:300]
    smart_algorithm = load_simulation_data("/simulation_data/smart_topology.json")[100:300]
    # plot_comparison(random_algorithm, smart_algorithm, "avg_connection_duration", "Average Connection Duration Comparison")
    # plot_comparison(random_algorithm, smart_algorithm, "avg_connection_health", "Average Connection Health Comparison")
    # plot_comparison(random_algorithm, smart_algorithm, "active_connections", "Active Connections Comparison")
    # plot_comparison(random_algorithm, smart_algorithm, "new_connections_made", "New Connections Made Comparison")
    # plot_comparison(random_algorithm, smart_algorithm, "old_connections_dropped", "Old Connections Dropped Comparison")

    plot_simulation_data(random_algorithm, "Algorithm 1")
    plot_simulation_data(smart_algorithm, "Algorithm 2")
    # plot_dual_simulation_data(random_algorithm, smart_algorithm, "Comparison of Algorithms")


if __name__ == "__main__":
    main()