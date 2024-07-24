import gpxpy
import numpy as np
import pandas as pd
import json
import os

def calculate_azimuth(lat1, lon1, lat2, lon2):
    """
    Calculate the azimuth between two geographical points.
    """
    d_lon = lon2 - lon1
    x = np.sin(d_lon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(d_lon))
    initial_bearing = np.arctan2(x, y)
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def read_gpx(file_path):
    """
    Read a GPX file and return a list of (latitude, longitude, altitude) tuples.
    """
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude, point.elevation))
                
    return points

def calculate_segment_azimuths(points):
    """
    Calculate the azimuths of all segments in the GPX file.
    """
    segment_azimuths = []
    
    for i in range(len(points) - 1):
        lat1, lon1, _ = points[i]
        lat2, lon2, _ = points[i + 1]
        azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
        segment_azimuths.append(azimuth)
    
    return segment_azimuths

def calculate_kilometer_directions(segment_azimuths, points):
    """
    Calculate the direction of each kilometer.
    """
    kilometer_directions = []
    total_distance = 0
    last_point = points[0]
    current_directions = []

    for i in range(1, len(points)):
        current_point = points[i]
        
        # Calculate distance between points
        d_lat = np.radians(current_point[0] - last_point[0])
        d_lon = np.radians(current_point[1] - last_point[1])
        a = (np.sin(d_lat / 2) ** 2 +
             np.cos(np.radians(last_point[0])) * np.cos(np.radians(current_point[0])) * np.sin(d_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = 6371000 * c  # Distance in meters
        
        total_distance += distance
        current_directions.append(segment_azimuths[i-1])
        
        if total_distance >= 1000:
            km_direction = np.mean(current_directions)
            kilometer_directions.append(km_direction)
            total_distance = 0
            current_directions = []
        
        last_point = current_point
    
    # Add the last segment if it's less than a kilometer
    if current_directions:
        km_direction = np.mean(current_directions)
        kilometer_directions.append(km_direction)
    
    return kilometer_directions

def calculate_gradients_per_km(points):
    """
    Calculate the gradient for each kilometer.
    """
    gradients = []
    total_distance = 0
    elevation_gain = 0
    elevation_loss = 0
    km_gradients = []
    last_point = points[0]
    
    for i in range(1, len(points)):
        current_point = points[i]
        
        # Calculate distance between points
        d_lat = np.radians(current_point[0] - last_point[0])
        d_lon = np.radians(current_point[1] - last_point[1])
        a = (np.sin(d_lat / 2) ** 2 +
             np.cos(np.radians(last_point[0])) * np.cos(np.radians(current_point[0])) * np.sin(d_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = 6371000 * c  # Distance in meters
        
        # Calculate elevation change
        elevation_change = current_point[2] - last_point[2]
        
        total_distance += distance
        if elevation_change > 0:
            elevation_gain += elevation_change
        else:
            elevation_loss += abs(elevation_change)
        
        if total_distance >= 1000:
            gradient = (elevation_gain - elevation_loss) / 10  # Gradient in percentage
            km_gradients.append(gradient)
            gradients.append({
                'distance': total_distance,
                'gradient': gradient,
                'elevation_gain': elevation_gain,
                'elevation_loss': elevation_loss
            })
            total_distance = 0
            elevation_gain = 0
            elevation_loss = 0
        
        last_point = current_point
    
    # Account for the last segment if less than a kilometer
    if total_distance > 0:
        gradient = (elevation_gain - elevation_loss) / 10
        km_gradients.append(gradient)
        gradients.append({
            'distance': total_distance,
            'gradient': gradient,
            'elevation_gain': elevation_gain,
            'elevation_loss': elevation_loss
        })

    return gradients, km_gradients

def calculate_wind_impact_coefficients(segment_azimuths, wind_speed=1.0):
    """
    Calculate wind impact coefficients for all wind angles (0-360 degrees) for each segment.
    """
    wind_impact_coefficients = []

    for wind_angle in range(360):
        total_impact = 0
        
        for segment_azimuth in segment_azimuths:
            angle_diff = np.abs(wind_angle - segment_azimuth)
            angle_diff = min(angle_diff, 360 - angle_diff)  # Ensure the angle difference is within [0, 180]
            impact = np.cos(np.radians(angle_diff)) * wind_speed
            total_impact += impact
            
        wind_impact_coefficients.append(total_impact / len(segment_azimuths))
    
    return wind_impact_coefficients


# Step 1: Calculate coefficients for each wind angle
marathon_name = 'Marathon de Valence'
gpx_file_path = f'PUBLIC/source/gpx_traces/{marathon_name}.gpx'

points = read_gpx(gpx_file_path)
segment_azimuths = calculate_segment_azimuths(points)
coefficients = calculate_wind_impact_coefficients(segment_azimuths)

# Calculate average altitude
average_altitude = np.mean([point[2] for point in points])
first_point_coordinates = (points[0][0], points[0][1])

# Calculate gradients per kilometer and total elevation gain/loss
gradients, km_gradients = calculate_gradients_per_km(points)
total_elevation_gain = sum(g['elevation_gain'] for g in gradients)
total_elevation_loss = sum(g['elevation_loss'] for g in gradients)

# Calculate directions of each kilometer
kilometer_directions = calculate_kilometer_directions(segment_azimuths, points)

# Load existing JSON data
json_file_path = 'info_impact_majors.json'
if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
else:
    wind_data = {}

# Ensure 'marathons' key exists in the dictionary
if 'marathons' not in wind_data:
    wind_data['marathons'] = []

# Update JSON data with new marathon coefficients
wind_data['marathons'].append({
    'marathon_name': marathon_name,
    'wind_impact_coefficients': coefficients,
    'average_altitude': average_altitude,
    'first_point_coordinates': first_point_coordinates,
    'gradients_per_km': km_gradients,
    'total_elevation_gain': total_elevation_gain,
    'total_elevation_loss': total_elevation_loss,
    'kilometer_directions': kilometer_directions
})

# Save the updated JSON data
with open(json_file_path, 'w') as json_file:
    json.dump(wind_data, json_file, indent=4)

# Display the coefficients DataFrame (optional, for verification)
coefficients_df = pd.DataFrame({'Wind Angle (Degrees)': range(360), 'Impact Coefficient': coefficients})
print(coefficients_df)

# Example usage of the global wind impact calculation
wind_angle = 45  # Example wind angle in degrees
wind_speed = 5  # Example wind speed in m/s
runner_speed_kmh = 17.75  # Example runner speed in km/h
runner_mass = 70  # Example runner mass in kg
A = 0.5  # Example frontal area of the runner in m^2


