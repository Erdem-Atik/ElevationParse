import zipfile
import xml.etree.ElementTree as ET
import os
import numpy as np
from scipy.spatial import Delaunay
from elevation import get_elevation_data

# Extracts the KML file from the KMZ archive
def extract_kml_from_kmz(kmz_filepath):
    with zipfile.ZipFile(kmz_filepath, 'r') as kmz:  # Open the KMZ file as a zip archive
        for file in kmz.namelist():  # Loop through all files in the archive
            if file.endswith('.kml'):  # Check if the file is a KML file
                with kmz.open(file) as kml_file:  # Open the KML file
                    return kml_file.read()  # Return the contents of the KML file as a string
    return None  # Return None if no KML file is found

# Parses the KML data to extract coordinates
def parse_kml_for_coordinates(kml_data):
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}  # Define the namespace for KML elements
 
    root = ET.fromstring(kml_data)  # Parse the KML data into an XML tree
   

    for placemark in root.findall('.//kml:Placemark', namespace):  # Find all Placemark elements

        for polygon in placemark.findall('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespace):
            coord_text = polygon.text.strip()  # Get the coordinate text from the KML
            coord_list = [tuple(map(float, coord.split(',')[:2])) for coord in coord_text.split()]  # Parse the coordinates into (longitude, latitude) tuples
            
    print(f'coord_list: {coord_list}')
    return coord_list  # Return the list of coordinates of corners of area

# Determines the number of GCPs based on area size and terrain complexity
def determine_number_of_gcps(area_size, terrain_complexity):
    base_gcp_count = max(5, int(area_size / 10))  # Base count of GCPs, with a minimum of 5
    if terrain_complexity > 1:
        base_gcp_count += int(base_gcp_count * (terrain_complexity - 1))  # Increase GCP count for complex terrain
    return base_gcp_count  # Return the calculated number of GCPs

# Calculates the optimal GCP locations
def calculate_gcp_points(coordinates, elevation_data):
    all_points = np.array(coordinates[0])  # Convert the first set of coordinates to a NumPy array
    min_lon, min_lat = np.min(all_points, axis=0)  # Find the minimum longitude and latitude
    max_lon, max_lat = np.max(all_points, axis=0)  # Find the maximum longitude and latitude

    area_size = (max_lon - min_lon) * (max_lat - min_lat)  # Calculate the area size
    terrain_complexity = np.std(elevation_data)  # Calculate terrain complexity based on elevation standard deviation

    num_gcps = determine_number_of_gcps(area_size, terrain_complexity)  # Determine the number of GCPs needed

    # Use Delaunay triangulation to ensure GCPs are well-distributed
    tri = Delaunay(all_points)
    centroids = np.array([np.mean(tri.points[triangle], axis=0) for triangle in tri.simplices])  # Calculate the centroids of the triangles
    
    gcp_points = []
    spacing = max(1, len(centroids) // num_gcps)  # Determine the spacing between GCPs
    for i in range(0, len(centroids), spacing):
        lon, lat = centroids[i]  # Get the longitude and latitude of the centroid
        elevation_index = np.argmin(np.abs(all_points[:, 0] - lon) + np.abs(all_points[:, 1] - lat))  # Find the closest elevation data point
        elevation = elevation_data[elevation_index]  # Get the elevation at that point
        gcp_points.append((lon, lat, elevation))  # Append the GCP point (longitude, latitude, elevation) to the list
    
    return gcp_points  # Return the list of GCP points

# Main function to process the KMZ file and determine GCP locations
def process_kmz(filepath):
    kml_data = extract_kml_from_kmz(filepath)  # Extract the KML data from the KMZ file
    if kml_data is None:
        return {'status': 'error', 'message': 'No KML file found in KMZ'}  # Error if no KML found
    
    coordinates = parse_kml_for_coordinates(kml_data)  # Parse the coordinates from the KML data

    if not coordinates:
        return {'status': 'error', 'message': 'No coordinates found in KML file'}  # Error if no coordinates found
    
    # Simulate elevation data for the purpose of this example
    # In a real implementation, this would come from a DEM (Digital Elevation Model)
    elevation_data = np.random.rand(len(coordinates[0])) * 100  # Generate random elevation data
    #elevation_data = get_elevation_data(coordinates)
    gcp_points = calculate_gcp_points(coordinates, elevation_data)  # Calculate the GCP points

    return {
        'status': 'success',
        'message': f'Processed {os.path.basename(filepath)}',  # Success message with file name
        'gcp_points': gcp_points  # Include the calculated GCP points
    }

fl_path = "C:\\Users\\T460s\\Desktop\\GCP small_area.kmz"

process_kmz(fl_path)