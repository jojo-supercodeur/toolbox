import json
import os
import gpxpy
import numpy as np
import pandas as pd
import scipy.stats as stats

def calculate_azimuth(lat1, lon1, lat2, lon2):
    d_lon = lon2 - lon1
    x = np.sin(d_lon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(d_lon))
    initial_bearing = np.arctan2(x, y)
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def read_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    points = [(point.latitude, point.longitude, point.elevation) 
              for track in gpx.tracks 
              for segment in track.segments 
              for point in segment.points]
    return points

def calculate_segment_azimuths(points):
    segment_azimuths = [calculate_azimuth(points[i][0], points[i][1], points[i+1][0], points[i+1][1]) 
                        for i in range(len(points) - 1)]
    return segment_azimuths

def calculate_kilometer_directions(segment_azimuths, points):
    kilometer_directions = []
    total_distance = 0
    last_point = points[0]
    current_directions = []

    for i in range(1, len(points)):
        current_point = points[i]
        d_lat = np.radians(current_point[0] - last_point[0])
        d_lon = np.radians(current_point[1] - last_point[1])
        a = (np.sin(d_lat / 2) ** 2 +
             np.cos(np.radians(last_point[0])) * np.cos(np.radians(current_point[0])) * np.sin(d_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = 6371000 * c
        
        total_distance += distance
        current_directions.append(segment_azimuths[i-1])
        
        if total_distance >= 1000:
            km_direction = np.mean(current_directions)
            kilometer_directions.append(km_direction)
            total_distance = 0
            current_directions = []
        
        last_point = current_point
    
    if current_directions:
        km_direction = np.mean(current_directions)
        kilometer_directions.append(km_direction)
    
    return kilometer_directions

def calculate_gradients_per_km(points):
    gradients = []
    total_distance = 0
    elevation_gain = 0
    elevation_loss = 0
    km_gradients = []
    last_point = points[0]
    
    for i in range(1, len(points)):
        current_point = points[i]
        d_lat = np.radians(current_point[0] - last_point[0])
        d_lon = np.radians(current_point[1] - last_point[1])
        a = (np.sin(d_lat / 2) ** 2 +
             np.cos(np.radians(last_point[0])) * np.cos(np.radians(current_point[0])) * np.sin(d_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = 6371000 * c
        
        elevation_change = current_point[2] - last_point[2]
        
        total_distance += distance
        if elevation_change > 0:
            elevation_gain += elevation_change
        else:
            elevation_loss += abs(elevation_change)
        
        if total_distance >= 1000:
            gradient = (elevation_gain - elevation_loss) / 10
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
    wind_impact_coefficients = []
    for wind_angle in range(360):
        total_impact = sum(np.cos(np.radians(min(abs(wind_angle - azimuth), 360 - abs(wind_angle - azimuth)))) * wind_speed 
                           for azimuth in segment_azimuths)
        wind_impact_coefficients.append(total_impact / len(segment_azimuths))
    return wind_impact_coefficients

def load_finish_times(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    finish_times = [int(h) * 60 + int(m) + int(s) / 60 for key, value in data.items() 
                    for h, m, s in [value["Totals"]["Time Total (net)"].split(':')]]
    return np.array(finish_times)

def fit_distribution(finish_times):
    shape, loc, scale = stats.gamma.fit(finish_times)
    total_runner = len(finish_times)
    return shape, loc, scale, total_runner

def update_json_with_density_info(file_path, marathon_name, shape, loc, scale, total_runner, wind_impact_coefficients, average_altitude, first_point_coordinates, km_gradients, total_elevation_gain, total_elevation_loss, kilometer_directions):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {'marathons': []}

    marathon = next((m for m in data['marathons'] if m['marathon_name'] == marathon_name), None)
    if marathon:
        marathon.update({
            'density_info': {"shape": shape, "loc": loc, "scale": scale},
            'total_runner': total_runner,
            'wind_impact_coefficients': wind_impact_coefficients,
            'average_altitude': average_altitude,
            'first_point_coordinates': first_point_coordinates,
            'gradients_per_km': km_gradients,
            'total_elevation_gain': total_elevation_gain,
            'total_elevation_loss': total_elevation_loss,
            'kilometer_directions': kilometer_directions
        })
    else:
        data['marathons'].append({
            'marathon_name': marathon_name,
            'density_info': {"shape": shape, "loc": loc, "scale": scale},
            'total_runner': total_runner,
            'wind_impact_coefficients': wind_impact_coefficients,
            'average_altitude': average_altitude,
            'first_point_coordinates': first_point_coordinates,
            'gradients_per_km': km_gradients,
            'total_elevation_gain': total_elevation_gain,
            'total_elevation_loss': total_elevation_loss,
            'kilometer_directions': kilometer_directions
        })

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def process_marathon(gpx_file_path, file_path_json, file_path_times, marathon_name):
    points = read_gpx(gpx_file_path)
    segment_azimuths = calculate_segment_azimuths(points)
    wind_impact_coefficients = calculate_wind_impact_coefficients(segment_azimuths)
    average_altitude = np.mean([point[2] for point in points])
    first_point_coordinates = (points[0][0], points[0][1])
    gradients, km_gradients = calculate_gradients_per_km(points)
    total_elevation_gain = sum(g['elevation_gain'] for g in gradients)
    total_elevation_loss = sum(g['elevation_loss'] for g in gradients)
    kilometer_directions = calculate_kilometer_directions(segment_azimuths, points)
    
    
    if os.path.exists(file_path_times):
        finish_times = load_finish_times(file_path_times)
        shape, loc, scale, total_runner = fit_distribution(finish_times)
        
    else : 
        shape, loc, scale, total_runner = 0, 0, 0, 0
        print("The results are not available")
    
    update_json_with_density_info(file_path_json, marathon_name, shape, loc, scale, total_runner, wind_impact_coefficients, average_altitude, first_point_coordinates, km_gradients, total_elevation_gain, total_elevation_loss, kilometer_directions)

# Utilisation
file_path_json = 'info_impact_majors.json'
marathon_name = 'Chicago Marathon'
gpx_file_path = f'../gpx_race/{marathon_name}.gpx'
file_path_times = f'../results_race/results_{marathon_name}.json'


process_marathon(gpx_file_path, file_path_json, file_path_times, marathon_name)

