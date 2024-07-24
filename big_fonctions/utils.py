#This is the file calculating of the impact of external parameter on the performance 

#V1 will be super simple : 1 coefficient for each GPX
#Wind GPX 


import pandas as pd
import json
import numpy as np



marathon_name = 'Boston Marathon'
wind_angle = 89
wind_speed = 10





def calculate_global_wind_impact_V0_1(marathon_name, wind_angle, wind_speed, runner_mass = 70, runner_speed_kmh = 14, json_file_path='info_impact_majors.json'):
    """
    Calculate the global wind impact coefficient for a given marathon, wind angle, (and wind speed)
    """


    # Constants
    rho = 1.225  # Air density (kg/m^3)
    A = 0.5  # Frontal area of the runner (m^2)         ## personalizable data with user inputs
    Cd_no_pacers = 0.812  # Drag coefficient without pacers          ## from Bekele study, fine tunable
    runner_speed = runner_speed_kmh / 3.6  # Runner's speed in m/s

    # Load existing JSON data
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
    
    # Find the marathon data
    marathon_data = next((item for item in wind_data['marathons'] if item['marathon_name'] == marathon_name), None)
    
    if marathon_data is None:
        print(f"No data found for marathon: {marathon_name}")
        return None
    
    # Extract the coefficients
    wind_impact_coefficients = marathon_data['wind_impact_coefficients']
    
    # Normalize the wind angle to be within [0, 360)
    wind_angle = wind_angle % 360
    
    # Get the impact coefficient for the given wind angle
    impact_coefficient = wind_impact_coefficients[wind_angle]

    # Calculate the wind effect
    wind_effect = wind_speed/3.6 * impact_coefficient
    
    # Calculate the new effective speed considering the wind
    effective_speed = runner_speed + wind_effect
    
    # Calculate aerodynamic power with and without wind
    P_aero_no_wind = 0.5 * Cd_no_pacers * rho * A * (runner_speed ** 3)
    P_aero_with_wind = 0.5 * Cd_no_pacers * rho * A * (effective_speed ** 3)

    
    # Calculate the total mechanical power 
    P_total_no_wind = 9.42 + 4.73 * runner_speed + 0.266 * (runner_speed ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_no_wind
    P_total_with_wind = 9.42 + 4.73 * effective_speed + 0.266 * (effective_speed ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_with_wind

    
    
    # Calculate the impact coefficient
    wind_impact_coefficient = P_total_with_wind / P_total_no_wind

    
    return wind_impact_coefficient







def calculate_global_wind_impact_V1(marathon_name, wind_angle, wind_speed, runner_mass = 70, runner_speed_kmh = 14, json_file_path='info_impact_majors.json'):
    """
    Same thing but including the speed of the runner as scalar product of each km

    Calculate the global wind impact coefficient for a given marathon, wind angle, and wind speed.
    This coefficient can be used to adjust the runner's time for the wind conditions.
    """

    # Constants
    rho = 1.225  # Air density (kg/m^3)
    Cd_no_pacers = 0.812  # Drag coefficient without pacers (from Bekele study, fine-tunable)
    runner_speed = runner_speed_kmh / 3.6  # Convert runner's speed to m/s
    A =0.5
    
    # Load existing JSON data
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
    
    # Find the marathon data
    marathon_data = next((item for item in wind_data['marathons'] if item['marathon_name'] == marathon_name), None)
    
    if marathon_data is None:
        print(f"No data found for marathon: {marathon_name}")
        return None
    
    # Extract the coefficients and directions
    wind_impact_coefficients = marathon_data['wind_impact_coefficients']
    kilometer_directions = marathon_data['kilometer_directions']
    
    # Normalize the wind angle to be within [0, 360)
    wind_angle = wind_angle % 360
    
    # Convert wind angle to radians
    wind_angle_rad = np.radians(wind_angle)
    
    # Calculate wind vector
    wind_vector = np.array([np.cos(wind_angle_rad), np.sin(wind_angle_rad)]) * wind_speed/3.6
    
    total_no_wind = 0
    total_with_wind = 0
    
    for km_index, km_direction in enumerate(kilometer_directions):
        # Convert kilometer direction to radians
        km_direction_rad = np.radians(km_direction)
        
        # Calculate kilometer vector
        km_vector = np.array([np.cos(km_direction_rad), np.sin(km_direction_rad)]) * runner_speed
        
        # Calculate the impact of the wind on this segment
        dot_product = np.dot(wind_vector, km_vector)
        effective_speed = runner_speed + dot_product / np.linalg.norm(km_vector)
        
        # Calculate aerodynamic power with and without wind
        P_aero_no_wind = 0.5 * Cd_no_pacers * rho * A * (runner_speed ** 3)
        P_aero_with_wind = 0.5 * Cd_no_pacers * rho * A * (effective_speed ** 3)
        
        # Calculate the total mechanical power
        P_total_no_wind = 9.42 + 4.73 * runner_speed + 0.266 * (runner_speed ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_no_wind
        P_total_with_wind = 9.42 + 4.73 * effective_speed + 0.266 * (max(effective_speed,0) ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_with_wind
        
        total_no_wind += P_total_no_wind
        total_with_wind += P_total_with_wind

    # Calculate the impact coefficient
    wind_impact_coefficient = total_with_wind / total_no_wind
    
    return wind_impact_coefficient      #do not use yet





    












def calculate_global_altitude_impact_V1(marathon_name, json_file_path='info_impact_majors.json'):
    # Load existing JSON data
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
    
    # Find the marathon data
    marathon_data = next((item for item in wind_data['marathons'] if item['marathon_name'] == marathon_name), None)
    
    if marathon_data is None:
        print(f"No data found for marathon: {marathon_name}")
        return None
    
    # Extract the coefficients
    altitude  = marathon_data['average_altitude']
    global_impact = 1 + 0.041*altitude/1000
    return global_impact








def elevation_formula_general_public(gradient):
    return 1 + 0.0162*gradient + 0.000578*gradient*gradient



def calculate_global_elevation_impact_V1(marathon_name, json_file_path='info_impact_majors.json'):
    # Load existing JSON data
    global_impact = 0
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
    
    # Find the marathon data
    marathon_data = next((item for item in wind_data['marathons'] if item['marathon_name'] == marathon_name), None)
    
    if marathon_data is None:
        print(f"No data found for marathon: {marathon_name}")
        return None
    
    # Extract the coefficients
    gradients  = marathon_data['gradients_per_km']
    for i in range(len(gradients)):
        global_impact +=  elevation_formula_general_public(gradients[i])
    return global_impact/len(gradients)







def temperature_formula_general_public(temperature):
    return 1 + (1.2095136-0.22334*temperature+0.01031*temperature**2)/100   ##really for average runner not for elite nor commited amateur


def calculate_global_temperature_impact_V1(marathon_name, json_file_path='info_impact_majors.json'):
    # Load existing JSON data
    with open(json_file_path, 'r') as json_file:
        wind_data = json.load(json_file)
    
    # Find the marathon data
    marathon_data = next((item for item in wind_data['marathons'] if item['marathon_name'] == marathon_name), None)
    
    if marathon_data is None:
        print(f"No data found for marathon: {marathon_name}")
        return None
    
    # Extract the coefficients
    temperature  = marathon_data['temperature_start']
    
    global_impact = temperature_formula_general_public(temperature)
    return global_impact







print(calculate_global_altitude_impact_V1('Boston Marathon'))
print(calculate_global_elevation_impact_V1('Boston Marathon'))
print(calculate_global_temperature_impact_V1('Boston Marathon'))
print(calculate_global_wind_impact_V0_1('Boston Marathon',80,15))
print(calculate_global_wind_impact_V0_1('Boston Marathon',270,15))
print(calculate_global_wind_impact_V0_1('Boston Marathon',340,15))
print(calculate_global_wind_impact_V1('Boston Marathon',80,1))
print(calculate_global_wind_impact_V1('Boston Marathon',270,1))
print(calculate_global_wind_impact_V1('Boston Marathon',350,1))