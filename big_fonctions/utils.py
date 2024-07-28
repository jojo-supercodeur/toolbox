#This is the file calculating of the impact of external parameter on the performance 
#This file is property of Maurten AB
#It was coded by Joseph Mestrallet and its first version was delivered on 24 July.
#It's dedicated to be used in the fuel calculator project



import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats



marathon_name = 'Boston Marathon'
wind_angle = 89
wind_speed = 10








def calculate_frontal_area(runner_height):
    return 0.475*runner_height*0.45




def plot_gamma_distribution(marathon_name, file_path_json='info_impact_majors.json'):
    with open(file_path_json, 'r') as file:
        data = json.load(file)
    
    marathon = next((m for m in data['marathons'] if m['marathon_name'] == marathon_name), None)
    if marathon and marathon['total_runner'] != 0:
        shape = marathon['density_info']['shape']
        loc = marathon['density_info']['loc']
        scale = marathon['density_info']['scale']
        total_runner = marathon['total_runner']
        
        x = np.linspace(0, 500, 1000)  # Vous pouvez ajuster cette plage selon les données réelles
        y = stats.gamma.pdf(x, shape, loc, scale)*total_runner
        
        plt.plot(x, y, label=f'Gamma Distribution for {marathon_name}')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Number of runner')
        plt.title(f'Gamma Distribution for {marathon_name}')
        plt.legend()
        plt.show()
    else:
        print(f'No density info available for {marathon_name}')







def get_runners_at_minute(marathon_name, runner_time, file_path_json='info_impact_majors.json'):
    with open(file_path_json, 'r') as file:
        data = json.load(file)
    
    marathon = next((m for m in data['marathons'] if m['marathon_name'] == marathon_name), None)
    if marathon and 'density_info' in marathon:
        shape = marathon['density_info']['shape']
        loc = marathon['density_info']['loc']
        scale = marathon['density_info']['scale']
        total_runner = marathon['total_runner']
        
        # Calculer la densité de probabilité pour le temps donné
        runner_density = stats.gamma.pdf(runner_time, shape, loc, scale)
        # Convertir la densité en nombre de coureurs
        estimated_runners = runner_density * total_runner
        
        return estimated_runners
    else:
        print(f'No density info available for {marathon_name}')
        return None
    


def calculate_Cd(marathon_name, runner_time, json_file_path='info_impact_majors.json'):

    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    marathon = next((m for m in data['marathons'] if m['marathon_name'] == marathon_name), None)
    if marathon is None or marathon['total_runner'] == 0:
        cd = 0.348  #considering that if we have any info, the runner is in the pack
        #print("no results available")

    else : 

        runners = get_runners_at_minute(marathon_name, runner_time, json_file_path)
        # Coefficient de traînée
        cd_solo = 0.819
        cd_minimum = 0.348

        if runners is None : #or runners < 1:
            cd = cd_solo
        else: 
            # Fonction exponentielle pour la réduction du Cd
            cd = cd_solo - (cd_solo - cd_minimum) * (1 - np.exp(-runners / 6))
        
        # S'assurer que le Cd est dans les bornes [cd_minimum, cd_solo]
        cd = max(cd_minimum, min(cd, cd_solo))
    
    return cd




def plot_cd_vs_finish_time(marathon_name, json_file_path='info_impact_majors.json'):
    # Définir la plage de temps de 120 à 180 minutes
    time_range = np.arange(120, 181)
    cd_values = [calculate_Cd(marathon_name, time, json_file_path) for time in time_range]
    
    plt.plot(time_range, cd_values, label=f'Cd for {marathon_name}')
    plt.xlabel('Finish Time (minutes)')
    plt.ylabel('Cd')
    plt.title(f'Cd Evolution vs. Finish Time for {marathon_name}')
    plt.axhline(0.819, color='r', linestyle='--', label='Solo Cd (0.819)')
    plt.axhline(0.348, color='g', linestyle='--', label='Minimum Cd (0.348)')
    plt.legend()
    plt.show()









def calculate_global_wind_impact_V0_1(marathon_name, wind_angle, wind_speed, runner_time = 170, runner_height = 1.70, runner_mass = 70, runner_speed_kmh = 14, json_file_path='info_impact_majors.json'):
    """
    Calculate the global wind impact coefficient for a given marathon, wind angle, (and wind speed)
    """


    # Constants
    rho = 1.225  # Air density (kg/m^3)
    A = calculate_frontal_area(runner_height)  # Frontal area of the runner (m^2)         ## personalizable data with user inputs
    Cd = calculate_Cd(marathon_name, runner_time, json_file_path)
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
    P_aero_no_wind = 0.5 * Cd * rho * A * (runner_speed ** 3)
    P_aero_with_wind = 0.5 * Cd * rho * A * (effective_speed ** 3)

    
    # Calculate the total mechanical power 
    P_total_no_wind = 9.42 + 4.73 * runner_speed + 0.266 * (runner_speed ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_no_wind
    P_total_with_wind = 9.42 + 4.73 * effective_speed + 0.266 * (effective_speed ** 1.993) + (60 / (4.184 * runner_mass)) * P_aero_with_wind

    
    
    # Calculate the impact coefficient

    wind_impact_coefficient = P_total_with_wind / P_total_no_wind

    
    return wind_impact_coefficient







def calculate_global_wind_impact_V1(marathon_name, wind_angle, wind_speed, runner_time = 170, runner_height = 1.70, runner_mass = 70, runner_speed_kmh = 14, json_file_path='info_impact_majors.json'):
    """
    Same thing but including the speed of the runner as scalar product of each km

    Calculate the global wind impact coefficient for a given marathon, wind angle, and wind speed.
    This coefficient can be used to adjust the runner's time for the wind conditions.

    #PS I can factorize runner_speed and runner_time
    """

    # Constants
    rho = 1.225  # Air density (kg/m^3)
    A = calculate_frontal_area(runner_height)  # Frontal area of the runner (m^2)         ## personalizable data with user inputs
    Cd = calculate_Cd(marathon_name, runner_time, json_file_path)
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
        #print(effective_speed)
        
        # Calculate aerodynamic power with and without wind
        P_aero_no_wind = 0.5 * Cd * rho * A * (runner_speed ** 3)
        P_aero_with_wind = 0.5 * Cd * rho * A * (effective_speed ** 3)
        
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


def temperature_formula_general_public_wearing_black(temperature, runner_time): 
    return temperature_formula_general_public(temperature + rise_temperature(runner_time))


def rise_temperature(runner_time, irradiance=1000, surface_area=0.3, specific_heat_air=1005, mass_air=0.025):
    """
    We can include irradiance in the json info_impact_majors or in an api request
    Does the wind change something ?
    
    Arguments :
    - irradiance : Incident sun power (W/m²)
    - surface_area : we can use frontal_area (m²)
    - duration : esposure duration (secondes)
    - specific_heat_air : Thermic capacity (J/kg·K)
    - mass_air :  Moved air volume (kg)        #probably much more than that 
    
    """
    duration = runner_time*60


    # Absorptivité des vêtements noirs et blancs
    absorptivity_black = 0.9
    absorptivity_white = 0.2
    
    # Énergie absorbée par les vêtements noirs et blancs
    energy_black = absorptivity_black * irradiance * surface_area * duration
    energy_white = absorptivity_white * irradiance * surface_area * duration
    
    # Hausse de température
    temp_rise_black = energy_black / (specific_heat_air * mass_air)
    temp_rise_white = energy_white / (specific_heat_air * mass_air)
    
    # Différence de température
    temp_difference = temp_rise_black - temp_rise_white
    
    return temp_difference




def calculate_global_temperature_impact_V1(marathon_name, runner_time, wearing_black = False, json_file_path='info_impact_majors.json'):
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
    
    if wearing_black == True:
        global_impact = temperature_formula_general_public_wearing_black(temperature, runner_time)
    else : 
        global_impact = temperature_formula_general_public(temperature)
    return global_impact







print(calculate_global_altitude_impact_V1('Boston Marathon'))
print(calculate_global_elevation_impact_V1('Boston Marathon'))
print(calculate_global_temperature_impact_V1('Boston Marathon', 190))
print("avec le vent", calculate_global_wind_impact_V0_1('Boston Marathon',80,15))
print("avec le vent en sens inverse", calculate_global_wind_impact_V0_1('Boston Marathon',270,15))
print(calculate_global_wind_impact_V0_1('Boston Marathon',340,15))
print(calculate_global_wind_impact_V1('Boston Marathon',80,15))
print(calculate_global_wind_impact_V1('Boston Marathon',270,15))
print(calculate_global_wind_impact_V1('Boston Marathon',350,15))
plot_gamma_distribution('Boston Marathon')
plot_cd_vs_finish_time('Boston Marathon')    #just nice to see 