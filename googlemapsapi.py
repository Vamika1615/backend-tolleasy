import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

def get_traffic_details(location):
    """
    Gets traffic details around a specific location
    
    Args:
        location (str): Location to check traffic around
        
    Returns:
        dict: Traffic information around the location
    """
    # Get API key from environment variables
    api_key = GOOGLE_MAPS_API_KEY
    
    if not api_key:
        return {"error": "Google Maps API key not configured"}
    
    # Initialize the Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Get the geocoded location to extract coordinates
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": "Location not found"}
    
    # Extract coordinates of the location
    center_lat = geocode_result[0]['geometry']['location']['lat']
    center_lng = geocode_result[0]['geometry']['location']['lng']
    center_address = geocode_result[0]['formatted_address']
    
    # Define points in cardinal directions to check traffic
    # The offset of 0.02 is approximately 2-3 km depending on latitude
    directions = {
        "north": (center_lat + 0.02, center_lng),
        "northeast": (center_lat + 0.015, center_lng + 0.015),
        "east": (center_lat, center_lng + 0.02),
        "southeast": (center_lat - 0.015, center_lng + 0.015),
        "south": (center_lat - 0.02, center_lng),
        "southwest": (center_lat - 0.015, center_lng - 0.015),
        "west": (center_lat, center_lng - 0.02),
        "northwest": (center_lat + 0.015, center_lng - 0.015)
    }
    
    # Get the current time for real-time traffic
    now = datetime.now()
    
    # Check traffic in each direction
    traffic_data = {}
    center_coords = f"{center_lat},{center_lng}"
    
    for direction, coords in directions.items():
        dest_coords = f"{coords[0]},{coords[1]}"
        
        # Get distance matrix with traffic information
        result = gmaps.distance_matrix(
            origins=center_coords,
            destinations=dest_coords,
            mode="driving",
            departure_time=now,
            traffic_model="best_guess"
        )
        
        # Extract traffic information
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            
            normal_duration = element['duration']['value']  # in seconds
            traffic_duration = element.get('duration_in_traffic', {}).get('value', normal_duration)  # in seconds
            
            # Calculate traffic ratio and determine congestion level
            traffic_ratio = traffic_duration / normal_duration if normal_duration > 0 else 1
            delay_seconds = traffic_duration - normal_duration
            
            if traffic_ratio >= 2.0:
                congestion = "Severe congestion"
            elif traffic_ratio >= 1.5:
                congestion = "Heavy traffic"
            elif traffic_ratio >= 1.2:
                congestion = "Moderate traffic"
            else:
                congestion = "Clear"
                
            traffic_data[direction] = {
                'distance': element['distance']['text'],
                'normal_duration': element['duration']['text'],
                'duration_in_traffic': element.get('duration_in_traffic', {}).get('text', element['duration']['text']),
                'delay': f"{delay_seconds // 60} minutes {delay_seconds % 60} seconds" if delay_seconds > 0 else "No delay",
                'traffic_ratio': f"{traffic_ratio:.2f}x",
                'congestion_level': congestion
            }
    
    # Determine overall traffic condition
    congestion_levels = [data['congestion_level'] for _, data in traffic_data.items()]
    severe_count = congestion_levels.count("Severe congestion")
    heavy_count = congestion_levels.count("Heavy traffic")
    moderate_count = congestion_levels.count("Moderate traffic")
    
    if severe_count >= 3:
        overall_traffic = "Severe traffic congestion in the area"
        traffic_score = 10
    elif severe_count >= 1 or heavy_count >= 3:
        overall_traffic = "Heavy traffic in the area"
        traffic_score = 7
    elif heavy_count >= 1 or moderate_count >= 3:
        overall_traffic = "Moderate traffic in the area"
        traffic_score = 4
    else:
        overall_traffic = "Generally clear traffic in the area"
        traffic_score = 1
    
    return {
        "center_location": center_address,
        "coordinates": {"lat": center_lat, "lng": center_lng},
        "traffic_conditions": traffic_data,
        "overall_traffic": overall_traffic,
        "traffic_score": traffic_score  # 1-10 scale, 10 being worst traffic
    }

def get_route(origin, destination):
    """
    Gets route information between two locations
    
    Args:
        origin (str): Start location
        destination (str): End location
        
    Returns:
        dict: Route information including distance, duration, and directions
    """
    # Get API key from environment variables
    api_key = GOOGLE_MAPS_API_KEY
    
    if not api_key:
        return {"error": "Google Maps API key not configured"}
    
    # Initialize the Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Get directions
    directions_result = gmaps.directions(
        origin,
        destination,
        mode="driving",
        departure_time=datetime.now()
    )
    
    if not directions_result:
        return {"error": "Could not find directions between these locations"}
    
    route = directions_result[0]
    
    # Extract basic route information
    distance = route['legs'][0]['distance']['text']
    duration = route['legs'][0]['duration']['text']
    duration_in_traffic = route['legs'][0].get('duration_in_traffic', {}).get('text', duration)
    
    # Extract steps
    steps = []
    for step in route['legs'][0]['steps']:
        steps.append({
            'instruction': step['html_instructions'],
            'distance': step['distance']['text'],
            'duration': step['duration']['text']
        })
    
    # Extract polyline for map display
    overview_polyline = route['overview_polyline']['points']
    
    # Extract toll information
    has_tolls = False
    toll_details = []
    
    if 'warnings' in route and any('toll' in warning.lower() for warning in route['warnings']):
        has_tolls = True
    
    # Check for toll roads in each step
    for step in route['legs'][0]['steps']:
        if 'html_instructions' in step and 'toll' in step['html_instructions'].lower():
            has_tolls = True
            toll_details.append(step['html_instructions'])
    
    return {
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "duration": duration,
        "duration_in_traffic": duration_in_traffic,
        "has_tolls": has_tolls,
        "toll_details": toll_details,
        "steps": steps,
        "overview_polyline": overview_polyline
    }

def get_nearby_toll_plazas(location, radius=10000):
    """
    Finds toll plazas near a given location
    
    Args:
        location (str): Center location to search around
        radius (int): Search radius in meters (default 10km)
        
    Returns:
        list: Nearby toll plazas
    """
    # Get API key from environment variables
    api_key = GOOGLE_MAPS_API_KEY
    
    if not api_key:
        return {"error": "Google Maps API key not configured"}
    
    # Initialize the Google Maps client
    gmaps = googlemaps.Client(key=api_key)
    
    # Get the geocoded location to extract coordinates
    geocode_result = gmaps.geocode(location)
    
    if not geocode_result:
        return {"error": "Location not found"}
    
    # Extract coordinates of the location
    center_lat = geocode_result[0]['geometry']['location']['lat']
    center_lng = geocode_result[0]['geometry']['location']['lng']
    
    # Search for toll plazas using Places API (keyword search)
    places_result = gmaps.places_nearby(
        location=(center_lat, center_lng),
        radius=radius,
        keyword="toll plaza toll booth"
    )
    
    toll_plazas = []
    
    if 'results' in places_result:
        for place in places_result['results']:
            toll_plazas.append({
                "name": place['name'],
                "place_id": place['place_id'],
                "location": {
                    "lat": place['geometry']['location']['lat'],
                    "lng": place['geometry']['location']['lng']
                },
                "vicinity": place.get('vicinity', ''),
                "rating": place.get('rating', 'N/A')
            })
    
    return {
        "location": location,
        "search_radius_km": radius / 1000,
        "toll_plazas": toll_plazas
    }