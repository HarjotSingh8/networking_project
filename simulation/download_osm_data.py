import requests

def geocode_query(query):
    """
    Geocodes a search query using the Nominatim API.

    Args:
        query (str): The search query to geocode.

    Returns:
        dict: A dictionary containing latitude and longitude if successful, None otherwise.
    """
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'OSMDataDownloader/1.0 (your_email@example.com)'  # Replace with your email
    }
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(nominatim_url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return location
        """
        location {'place_id': 341005746, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 'osm_type': 'relation', 'osm_id': 7025718, 'lat': '42.2858536', 'lon': '-82.9780695', 'class': 'boundary', 'type': 'administrative', 'place_rank': 12, 'importance': 0.5979273708630157, 'addresstype': 'city', 'name': 'Windsor', 'display_name': 'Windsor, Southwestern Ontario, Ontario, Canada', 'boundingbox': ['42.2341581', '42.3567913', '-83.1148496', '-82.8911364']}
        """
        # return {'lat': location['lat'], 'lon': location['lon']}
    else:
        print(f"Failed to geocode query '{query}'. HTTP status code: {response.status_code}")
        return None

def download_osm_data(query, output_file):
    """
    Downloads .osm data for a given search query using the Overpass API.

    Args:
        query (str): The search query for the OSM data.
        output_file (str): The file path to save the downloaded .osm data.
    """
    # Geocode the query to get coordinates
    location = geocode_query(query)
    if not location:
        print("Geocoding failed. Cannot proceed with downloading OSM data.")
        return
    print(location)
    
    # Extract osm_id for the area
    try:
        area_id = int(location['osm_id']) + 3600000000  # Convert to Overpass area ID
    except KeyError:
        print("The geocoded location does not contain 'osm_id'. Cannot proceed.")
        return

    # Define the Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    headers = {
        'User-Agent': 'OSMDataDownloader/1.0 (your_email@example.com)'  # Replace with your email
    }

    # Construct the Overpass QL query to include child relations
    overpass_query = f"""
    [out:xml];
    area({area_id})->.searchArea;
    (
      node(area.searchArea);
      way(area.searchArea);
      relation(area.searchArea);
      relation(r.searchArea);  // Include child relations recursively
    );
    out body;
    >;
    out skel qt;
    """
    print("Generated Overpass Query:")
    print(overpass_query)

    # Send the request to the Overpass API
    response = requests.post(overpass_url, data={'data': overpass_query}, headers=headers)

    # Check if the request was successful and response contains data
    if response.status_code == 200 and response.content.strip():
        # Save the response content to the output file
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"OSM data for '{query}' has been saved to '{output_file}'.")
    else:
        print(f"Failed to download OSM data. HTTP status code: {response.status_code}")
        if not response.content.strip():
            print("The response from the Overpass API is empty. Attempting fallback with bounding box.")
            # Fallback: Use bounding box if area query fails
            bounding_box = location.get('boundingbox', None)
            if bounding_box:
                bbox_query = f"""
                [out:xml];
                (
                  node({bounding_box[0]},{bounding_box[2]},{bounding_box[1]},{bounding_box[3]});
                  way({bounding_box[0]},{bounding_box[2]},{bounding_box[1]},{bounding_box[3]});
                  relation({bounding_box[0]},{bounding_box[2]},{bounding_box[1]},{bounding_box[3]});
                );
                out body;
                >;
                out skel qt;
                """
                print("Generated Bounding Box Query:")
                print(bbox_query)
                bbox_response = requests.post(overpass_url, data={'data': bbox_query}, headers=headers)
                if bbox_response.status_code == 200 and bbox_response.content.strip():
                    with open(output_file, 'wb') as file:
                        file.write(bbox_response.content)
                    print(f"OSM data for '{query}' has been saved to '{output_file}' using bounding box fallback.")
                else:
                    print("Fallback query also failed.")
                    print(f"Response: {bbox_response.text}")
            else:
                print("No bounding box available for fallback.")
        else:
            print(f"Response: {response.text}")

# Example usage
if __name__ == "__main__":
    # Replace 'search_query' and 'output.osm' with your desired query and output file path
    search_query = "Windsor, Ontario"
    output_file = "/data/alt.osm"
    download_osm_data(search_query, output_file)
