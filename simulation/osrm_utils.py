import requests
from utils import generate_random_coordinates
OSRM_API_URL = "http://osrm-routed:5000"  # Update with your OSRM server URL

def get_route_from_osrm(start, end):
    """Fetch route from OSRM API."""
    url = f"{OSRM_API_URL}/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true"  # Request detailed steps in the response
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"OSRM API error: {response.status_code}, {response.text}")

def generate_random_routes(num_routes, main_box):
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