import requests

def interpolate_points(start, end, distance):
    """
    Generate intermediate points between two coordinates at a specified distance using Cartesian geometry.
    """
    lat1, lon1 = start
    lat2, lon2 = end
    total_distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5
    print(f'total_distance: {total_distance}')
    points = []
    if total_distance == 0:
        return [start]
    
    num_points = int(total_distance // distance)
    print(f'num_points: {num_points}')

    for i in range(num_points):
        fraction = i / num_points
        lat = lat1 + fraction * (lat2 - lat1)
        lon = lon1 + fraction * (lon2 - lon1)
        points.append((lat, lon))
    
    points.append((lat2, lon2))  # Ensure the last point is included
    return points

def get_elevation_data(coordinates, interval=50):
    """
    Fetches elevation data for a set of coordinates at 50-meter intervals.
    
    Args:
        coordinates (list): A list of tuples containing latitude and longitude.
        interval (int): The interval distance (in meters) between points to fetch elevation.
        
    Returns:
        list: A list of dictionaries containing latitude, longitude, and elevation.
    """
    all_points = []

    for i in range(len(coordinates) - 1):
        start = coordinates[i]
        end = coordinates[i + 1]
        all_points.extend(interpolate_points(start, end, interval))   # Prepare the API query

   
coordinates = [(35.37595845788469, 38.9522538283185), (35.37859798212953, 38.95242226297977), (35.37879484832216, 38.9542421701009), (35.37591846319395, 38.95436793389439), (35.37595845788469, 38.9522538283185)]
    

get_elevation_data(coordinates)