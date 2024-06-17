import streamlit as st
from datetime import datetime, timedelta
import os
import streamlit.components.v1 as components  # Importer le module components
import json
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
#from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
#import folium
import gpxpy
import requests
import datetime
import matplotlib
from typing import Optional
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic
from scipy.ndimage import gaussian_filter1d
import gpxpy
import requests
import json
from datetime import datetime, timedelta
import folium
import streamlit as st
import folium
from streamlit.components.v1 import html



api_key = "7fe3a248dcf46e22801844e4ea5f138d"




def draw_wind_rose(gpx_file, race_start_date, race_hour_date,status):

    weather_data = analyze_gpx_and_weather(gpx_file, race_start_date)
    timestamps = [datetime.strptime(ts, "%Y-%m-%d-%H") for ts in weather_data['timestamp']]
    race_start_datetime = datetime.strptime(f"{race_start_date} {race_hour_date}", "%Y-%m-%d %H:%M")
    timestamps_seconds = [(ts - datetime(1970, 1, 1)).total_seconds() for ts in timestamps]
    race_start_seconds = (race_start_datetime - datetime(1970, 1, 1)).total_seconds()
    directions = weather_data['wind_directions']


    direction = round(np.interp(race_start_seconds, timestamps_seconds, directions))
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor('none')

    # Configurer l'axe radial
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rticks([])
    ax.set_yticklabels([])
    ax.set_xticks(np.arange(0, 2.0 * np.pi, np.pi / 4))
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    # Ajouter des cercles concentriques
    circle_colors = [
        "steelblue",
        "cornflowerblue",
        "steelblue",
        "cornflowerblue",
        "steelblue",
        "cornflowerblue",
    ]
    for i, color in enumerate(circle_colors):
        circle = plt.Circle(
            (0, 0),
            i / len(circle_colors),
            transform=ax.transData._b,
            color=color,
            alpha=0.4,
        )
        ax.add_artist(circle)

    # Tracer la direction du vent
    wind_direction_rad = np.deg2rad(direction)
    ax.plot([wind_direction_rad, wind_direction_rad], [0, 1], lw=3, color="red")
    if status == "prevision" :
        ax.plot([wind_direction_rad+10, wind_direction_rad], [0, 1], lw=3, color="blue")
        ax.plot([wind_direction_rad-10, wind_direction_rad], [0, 1], lw=3, color="blue")
    ax.quiver(
        wind_direction_rad,
        0,
        0,
        1,
        angles="xy",
        scale_units="xy",
        scale=1,
        color="red",
        alpha=1,
        width=0.015,
        label=f"Wind direction: {direction}°",
        zorder=5,
        lw=1,
    )

    # Ajouter une légende
    ax.legend(loc="upper right")
    plt.title("Wind direction at departure time")

    return fig
    # Affichage avec Streamlit
    #st.pyplot(fig)




def create_wind_rose(gpx_file, start_day, start_time):
    weather_data = analyze_gpx_and_weather(gpx_file, start_day)
    # Extraire les directions et les vitesses du vent
    directions = weather_data['wind_directions']
    speeds = weather_data['wind_speeds']
    timestamps = weather_data['timestamp']
    
    # Convertir les timestamps en objets datetime
    timestamps_dt = [datetime.strptime(ts, "%Y-%m-%d-%H") for ts in timestamps]
    
    # Convertir directions en radians
    directions_rad = np.deg2rad(directions)
    
    # Définir les bins pour les vitesses du vent
    speed_bins = [0, 2, 5, 8, 10, 15, 20, 25, 30, 35, 40]
    speed_colors = px.colors.sequential.Viridis[:len(speed_bins) - 1]

    # Convertir l'heure de départ
    start_datetime = datetime.strptime(f"{start_day} {start_time}", "%Y-%m-%d %H:%M")
    prev_day_datetime = start_datetime - timedelta(days=1)
    start_index = np.argmin(np.abs([dt - start_datetime for dt in timestamps_dt]))
    prev_day_index = np.argmin(np.abs([dt - prev_day_datetime for dt in timestamps_dt]))

    main_direction = directions[start_index]
    main_speed = speeds[start_index]
    prev_day_direction = directions[prev_day_index]
    prev_day_speed = speeds[prev_day_index]

    # Créer la figure
    fig = go.Figure()

    # Ajouter les barres pour les vitesses du vent
    for i in range(len(speed_bins) - 1):
        mask = (np.array(speeds) >= speed_bins[i]) & (np.array(speeds) < speed_bins[i + 1])
        fig.add_trace(go.Barpolar(
            r=np.array(speeds)[mask],
            theta=np.array(directions)[mask],
            name=f'{speed_bins[i]}-{speed_bins[i + 1]} m/s',
            marker_color=speed_colors[i],
            opacity=0.7
        ))

    # Ajouter les flèches pour le départ de la course et le jour précédent
    fig.add_trace(go.Scatterpolar(
        r=[0, main_speed],
        theta=[main_direction, main_direction],
        mode='lines+markers',
        line=dict(color='red', width=3),
        marker=dict(size=10, color='red'),
        name='Start Wind'
    ))

    fig.add_trace(go.Scatterpolar(
        r=[0, prev_day_speed],
        theta=[prev_day_direction, prev_day_direction],
        mode='lines+markers',
        line=dict(color='blue', width=3),
        marker=dict(size=10, color='blue'),
        name='Previous Day Wind'
    ))

    # Mettre à jour la mise en page
    fig.update_layout(
        title='Wind Rose',
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(speeds) + 5]),
            angularaxis=dict(direction="clockwise", rotation=90)
        ),
        showlegend=True
    )

    return fig
    #fig.show()











def generate_map_from_gpx(gpx_file, race_name, zoom_start_map=12):
    # Charger le fichier GPX
    with open(gpx_file, "r") as gpxfile:
        gpx = gpxpy.parse(gpxfile)


    # Extraire les coordonnées du fichier GPX
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))

    # Calculer les coordonnées centrales
    center_lat = sum(p[0] for p in points) / len(points)
    center_lon = sum(p[1] for p in points) / len(points)

    # Créer la carte avec Folium centrée sur la trace
    map = folium.Map(
        zoom_start=zoom_start_map, location=(center_lat, center_lon)
    )  # zoom start 9 est un peu trop large pour l'UTMB, 8 est pire

    # Ajouter la trace du GPX
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map)

    # retournet la carte en HTML
    map_html = map._repr_html_()
    map.save(f"html_race/{race_name}.html")
    return map_html



def impact_vent_liste(wind_degrees, wind_speed, direction_list_degrees,race_name):
    """
    Obtenir les données du vent et convertir les degrés en radians.
    """
    vent_rad = math.radians(wind_degrees)

    # Initialisation des listes de valeurs de retour
    valeurs = []
    valeursdeg = []

    # Calculer les valeurs pour chaque direction
    for direction_degrees in direction_list_degrees:
        direction_rad = math.radians(direction_degrees)
        diff_rad_deg = wind_degrees - direction_degrees
        diff_rad = math.radians(diff_rad_deg)

        # Calcul de la valeur de retour entre -1 et 1
        valeur = math.cos(diff_rad)
        valeurs.append(valeur)
        valeursdeg.append(diff_rad_deg)

    # Lisser les valeurs (si nécessaire)
    valeurs_smoothed = valeurs

    # Créer un DataFrame pour Plotly
    df = pd.DataFrame({"Wind help": valeurs_smoothed, "Distance": range(len(valeurs))})

    # Générer le graphique avec Plotly
    fig = px.line(
        df,
        x="Distance",
        y="Wind help",
        labels={"Wind help": "<b>Wind help</b> (normalized)", "Distance": "<b>Distance</b>"},
    )
    fig.update_layout(
        width=626,
        height=500, 
        font=dict(size=12, color='black'),  # Changez 'black' à une autre couleur si nécessaire
        #paper_bgcolor="white",
        plot_bgcolor="white",   # Fond blanc pour la zone du graphique
        dragmode="pan",
        margin=dict(l=30, r=30, t=30, b=30),  # Espacement autour du graphique
        



    )
    fig.update_traces(line_color="rgba(0, 0, 0, 0.6)")

    # Ajouter des formes et annotations
    height = 1.1
    fig.add_hline(y=0)
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=len(valeurs),
        y1=height,
        line=dict(width=0),
        fillcolor="green",
        opacity=0.1,
    )
    fig.add_annotation(
        x=len(valeurs) / 2,
        y=0.5,
        text="<i>Tailwind helps you</i>",
        showarrow=False,
        font=dict(size=20, color="darkgreen"),
    )
    fig.add_annotation(
        x=len(valeurs) / 2,
        y=-0.5,
        text="<i>Headwind slows you down</i>",
        showarrow=False,
        font=dict(size=20, color="darkred"),
    )
    fig.add_shape(
        type="rect",
        x0=0,
        y0=-height,
        x1=len(valeurs),
        y1=0,
        line=dict(width=0),
        fillcolor="red",
        opacity=0.1,
    )

    return fig







































import gpxpy
import numpy as np
import plotly.graph_objs as go
import streamlit as st

def generate_elevation_and_gradient_plot(gpx, threshold):
    # Charger le fichier GPX
    #gpx_content = gpx_file.read().decode("utf-8")
    #gpx_content = gpxpy.parse(gpx_file)

    # Extraire les points et les données d'altitude
    distances = [0]
    elevations = []

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                if i > 0:
                    prev_point = segment.points[i - 1]
                    distance_diff = point.distance_2d(prev_point)
                    distances.append(distances[-1] + distance_diff)
                elevations.append(point.elevation)

    # Calculer le gradient en pourcentage
    epsilon = 1e-7  # Petite constante pour éviter les divisions par zéro
    for i in range(len(elevations)):
        if elevations[i] is None:
            elevations[i] = elevations[i - 1]

    gradient = np.gradient(elevations) / (np.gradient(distances) + epsilon) * 100
    gradient = [g if g <= 100 else 0 for g in gradient]

    # Lisser le gradient avec un filtre
    gradient_smooth = np.convolve(gradient, np.ones(70) / 70, mode='same')

    # Tracer le profil d'altitude et le gradient en utilisant Plotly
    fig = go.Figure()

    # Tracé d'altitude
    fig.add_trace(go.Scatter(x=[d / 1000 for d in distances], y=elevations, name='Elevation (m)', line=dict(color='blue', width=2)))

    # Tracé du gradient
    fig.add_trace(go.Scatter(x=[d / 1000 for d in distances], y=gradient_smooth, name='Gradient (%)', line=dict(color='red', width=2), yaxis='y2'))

    # Ajouter des zones colorées au-dessus du seuil
    for i in range(len(gradient_smooth)):
        if gradient_smooth[i] > threshold:
            fig.add_shape(
                type="rect",
                x0=distances[i] / 1000,
                x1=(distances[i] / 1000) + 0.1,
                y0=0,
                y1=max(elevations),
                fillcolor="gray",
                opacity=0.3,
                layer="below",
                line_width=0
            )

    # Mise en forme du graphique avec double axe
    fig.update_layout(
        title="Elevation and Gradient Profile",
        xaxis_title="Distance (km)",
        yaxis=dict(title="Elevation (m)"),
        yaxis2=dict(title="Gradient (%)", overlaying='y', side='right', showgrid=False),
        template="plotly_white"
    )

    return fig

















def analyze_gpx(gpx):
    # Parse the GPX file
    #with open(file_path, 'r') as gpx_file:
    #   gpx = gpxpy.parse(gpx_file)

    total_distance = 0.0
    total_elevation_gain = 0.0
    total_elevation_loss = 0.0
    max_elevation = float('-inf')
    min_elevation = float('inf')

    previous_point = None
    previous_elevation = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if previous_point is not None:
                    # Calculate distance
                    coords_1 = (previous_point.latitude, previous_point.longitude)
                    coords_2 = (point.latitude, point.longitude)
                    total_distance += geodesic(coords_1, coords_2).meters

                    # Calculate elevation gain and loss
                    if previous_elevation is not None:
                        elevation_change = point.elevation - previous_elevation
                        if elevation_change > 0:
                            total_elevation_gain += elevation_change
                        else:
                            total_elevation_loss += abs(elevation_change)

                # Update max and min elevation
                if point.elevation is not None:
                    max_elevation = max(max_elevation, point.elevation)
                    min_elevation = min(min_elevation, point.elevation)

                # Update previous values
                previous_point = point
                previous_elevation = point.elevation

    return [
        total_distance,
        total_elevation_gain,
        total_elevation_loss,
        max_elevation,
        min_elevation
    ]
























def impact_vent_liste_2(gpx_filename, json_filename, index):
    """
    Obtenir les données du vent et convertir les degrés en radians
        Exemple d'utilisation
    index = 8  # Choisir l'index correspondant à l'heure souhaitée
    valeurs, wind_speed = impact_vent_liste(gpx_file, globaljsonfile , index)

    print(valeurs, wind_speed)
    """
    wind_speed, wind_degrees = get_wind_data(json_filename, index)
    vent_rad = math.radians(wind_degrees)

    # Initialisation de la liste de valeurs de retour
    valeurs = []
    valeursdeg = []
    direction_list_degrees = calculate_orientation(gpx_filename)

    with open(json_filename, "r") as f:
        json_data = json.load(f)
    race_name = json_data['race']['name']

    # Calcul de la valeur de retour pour chaque direction
    for direction_degrees in direction_list_degrees:
        direction_rad = math.radians(direction_degrees)
        # diff_rad = vent_rad - direction_rad
        diff_rad_deg = wind_degrees - direction_degrees +180    #on prend le vent dans la bonne direction 
        diff_rad = math.radians(diff_rad_deg)

        # # Normalisation de l'angle entre -pi et pi
        # if diff_rad > math.pi:
        #     diff_rad -= 2 * math.pi
        # elif diff_rad < -math.pi:
        #     diff_rad += 2 * math.pi

        # Calcul de la valeur de retour entre -1 et 1
        valeur = math.cos(diff_rad)
        valeurs.append(valeur)
        valeursdeg.append(diff_rad_deg)

        # Tracer le graphe
 

    valeurs_smoothed = gaussian_filter1d(valeurs, sigma=30)

    df = pd.DataFrame.from_dict(
        {"Wind help": valeurs_smoothed, "Distance": range(len(valeurs))}
    )
    fig = px.line(
        df,
        x="Distance",
        y="Wind help",
        labels={
            "Wind help": "<b>Wind help</b> (normalized)",
            "Distance": "<b>Distance</b>",
        },
    )
    fig.update_layout(width=626, 
                        height=500, 
                        paper_bgcolor="white",
                        dragmode="pan",  # Définir le mode de déplacement par défaut sur "pan"
                        )
    fig.update_traces(
        line_color="rgba(0, 0, 0, 0.6)",  # black with some transparency
    )
    fig.add_hline(y=0)
    height = 1.1
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=len(valeurs),
        y1=height,
        line=dict(width=0),
        fillcolor="green",
        opacity=0.1,
    )
    fig.add_annotation(
        x=len(valeurs) / 2,
        y=0.5,
        text="<i>Tailwind helps you</i>",
        showarrow=False,
        # yshift=10,
        font=dict(size=20, color="darkgreen"),
    )
    fig.add_annotation(
        x=len(valeurs) / 2,
        y=-0.5,
        text="<i>Headwind slows you down</i>",
        showarrow=False,
        # yshift=10,
        font=dict(size=20, color="darkred"),
    )
    fig.add_shape(
        type="rect",
        x0=0,
        y0=-height,
        x1=len(valeurs),
        y1=0,
        line=dict(width=0),
        fillcolor="red",
        opacity=0.1,
    )
    return fig













def get_weather_data(lat, lon, start_day):
    api_key = "7fe3a248dcf46e22801844e4ea5f138d"
    # Define the base URL for the OpenWeatherMap API
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"

    # Get the weather data from the API
    response = requests.get(url)
    weather_data = response.json()

    # Convert the start day to a datetime object
    start_datetime = datetime.strptime(start_day, "%Y-%m-%d")
    prev_day = start_datetime - timedelta(days=1)
    next_day = start_datetime + timedelta(days=1)

    # Initialize lists for the weather data
    time_of_info = []
    temperatures = []
    wind_speeds = []
    humidities = []
    rain_probabilities = []
    wind_directions = []



    # Loop through the weather data and collect the relevant information
    for item in weather_data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        #formatted_date_1 = datetime.fromtimestamp(dt)
        formatted_date = dt.strftime("%Y-%m-%d-%H")
        if prev_day <= dt <= next_day:
            time_of_info.append(formatted_date)
            temperatures.append(item['main']['temp'] - 273.15)  # Convert from Kelvin to Celsius
            wind_speeds.append(item['wind']['speed'])
            humidities.append(item['main']['humidity'])
            rain_probabilities.append(item.get('pop', 0)*100)
            wind_directions.append(item['wind']['deg'])

    return {
        'timestamp':time_of_info,
        'temperatures': temperatures,
        'wind_speeds': wind_speeds,
        'humidities': humidities,
        'rain_probabilities': rain_probabilities,
        'wind_directions': wind_directions
    }

def analyze_gpx_and_weather(gpx_file, start_day):
    # Parse the GPX file and get the start point coordinates
    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)
        start_point = gpx.tracks[0].segments[0].points[0]
        lat, lon = start_point.latitude, start_point.longitude

    # Get the weather data
    weather_data = get_weather_data(lat, lon, start_day)
    
    return weather_data


















import plotly.graph_objs as go
from datetime import datetime, timedelta

import plotly.graph_objs as go
from datetime import datetime, timedelta
import numpy as np

def plot_weather_temp_wind(gpx_file, start_day, start_time, race_duration_minutes):

    weather_data = analyze_gpx_and_weather(gpx_file, start_day)
    
    # Extraire les données de l'output de la fonction get_weather_data
    timestamps = weather_data['timestamp']
    temperatures = weather_data['temperatures']
    wind_speeds = weather_data['wind_speeds']

    timestamps_dt = [datetime.strptime(ts, "%Y-%m-%d-%H") for ts in timestamps]

    # Créer des traces pour chaque variable
    temp_trace = go.Scatter(
        x=timestamps_dt,
        y=temperatures,
        mode='lines+markers',
        name='Temperature (°C)'
    )

    wind_trace = go.Scatter(
        x=timestamps_dt,
        y=wind_speeds,
        mode='lines+markers',
        name='Wind Speed (m/s)'
    )

    # Convertir l'heure de départ et calculer l'heure de fin de la course
    start_datetime = datetime.strptime(f"{start_day} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + timedelta(minutes=race_duration_minutes)
    #(start_datetime)
    #print(end_datetime)

    # Interpoler les valeurs pour chaque minute entre le début et la fin de la course
    interpolated_times = [start_datetime + timedelta(minutes=i) for i in range((end_datetime - start_datetime).seconds // 60 + 1)]
    temperatures_interp = np.interp(
        [dt.timestamp() for dt in interpolated_times],
        [dt.timestamp() for dt in timestamps_dt],
        temperatures
    )
    wind_speeds_interp = np.interp(
        [dt.timestamp() for dt in interpolated_times],
        [dt.timestamp() for dt in timestamps_dt],
        wind_speeds
    )

    # Créer des traces interpolées
    temp_trace_interp = go.Scatter(
        x=interpolated_times,
        y=temperatures_interp,
        mode='lines',
        name='Interpolated Temperature (°C)',
        line=dict(dash='dot', color='red')
    )

    wind_trace_interp = go.Scatter(
        x=interpolated_times,
        y=wind_speeds_interp,
        mode='lines',
        name='Interpolated Wind Speed (m/s)',
        line=dict(dash='dot', color='blue')
    )

    # Créer la figure et ajouter les traces
    fig = go.Figure()
    fig.add_trace(temp_trace)
    fig.add_trace(wind_trace)
    fig.add_trace(temp_trace_interp)
    fig.add_trace(wind_trace_interp)

    # Ajouter une forme pour la durée de la course
    fig.add_shape(
        type="rect",
        x0=start_datetime,
        y0=min(min(temperatures), min(wind_speeds)),
        x1=end_datetime,
        y1=max(max(temperatures), max(wind_speeds)),
        fillcolor="gray",
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Ajouter des titres et ajuster la mise en page
    fig.update_layout(
        title='Weather Data',
        xaxis_title='Time',
        yaxis_title='Values',
        legend=dict(
            x=1,
            y=1,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        hovermode='x unified',
        xaxis=dict(
            type='date',
            tickformat='%d %B %H:%M'
        )
    )

    return fig







def plot_weather_rain(gpx_file, start_day, start_time, race_duration_minutes):

    weather_data = analyze_gpx_and_weather(gpx_file, start_day)
    #print(weather_data)
    
    # Extraire les données de l'output de la fonction get_weather_data
    timestamps = weather_data['timestamp']
    humidities = weather_data['humidities']
    rain_probabilities = weather_data['rain_probabilities']

    timestamps_dt = [datetime.strptime(ts, "%Y-%m-%d-%H") for ts in timestamps]

    # Créer des traces pour chaque variable
    humidity_trace = go.Scatter(
        x=timestamps_dt,
        y=humidities,
        mode='lines+markers',
        name='Humidity (%)'
    )
    
    rain_trace = go.Scatter(
        x=timestamps_dt,
        y=rain_probabilities,
        mode='lines+markers',
        name='Rain Probability (%)'
    )

    # Convertir l'heure de départ et calculer l'heure de fin de la course
    start_datetime = datetime.strptime(f"{start_day} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + timedelta(minutes=race_duration_minutes)
    #print(start_datetime)
    #print(end_datetime)

    # Interpoler les valeurs pour chaque minute entre le début et la fin de la course
    interpolated_times = [start_datetime + timedelta(minutes=i) for i in range((end_datetime - start_datetime).seconds // 60 + 1)]
    humidity_interp = np.interp(
        [dt.timestamp() for dt in interpolated_times],
        [dt.timestamp() for dt in timestamps_dt],
        humidities
    )
    rain_interp = np.interp(
        [dt.timestamp() for dt in interpolated_times],
        [dt.timestamp() for dt in timestamps_dt],
        rain_probabilities
    )

    # Créer des traces interpolées
    temp_trace_interp = go.Scatter(
        x=interpolated_times,
        y=humidity_interp,
        mode='lines',
        name='Interpolated Temperature (°C)',
        line=dict(dash='dot', color='red')
    )

    wind_trace_interp = go.Scatter(
        x=interpolated_times,
        y=rain_interp,
        mode='lines',
        name='Interpolated Wind Speed (m/s)',
        line=dict(dash='dot', color='blue')
    )

    # Créer la figure et ajouter les traces
    fig = go.Figure()
    fig.add_trace(humidity_trace)
    fig.add_trace(rain_trace)
    fig.add_trace(temp_trace_interp)
    fig.add_trace(wind_trace_interp)

    # Ajouter une forme pour la durée de la course
    fig.add_shape(
        type="rect",
        x0=start_datetime,
        y0=min(min(humidities), min(rain_probabilities)),
        x1=end_datetime,
        y1=max(max(humidities), max(rain_probabilities)),
        fillcolor="gray",
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Ajouter des titres et ajuster la mise en page
    fig.update_layout(
        title='Weather Data',
        xaxis_title='Time',
        yaxis_title='Values',
        legend=dict(
            x=1,
            y=1,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        hovermode='x unified',
        xaxis=dict(
            type='date',
            tickformat='%d %B %H:%M'
        )
    )

    return fig














def create_gauge(race_start_date, race_hour_date, gpx_file, jauge_type):

    weather_data = analyze_gpx_and_weather(gpx_file, race_start_date)
    timestamps = [datetime.strptime(ts, "%Y-%m-%d-%H") for ts in weather_data['timestamp']]
    race_start_datetime = datetime.strptime(f"{race_start_date} {race_hour_date}", "%Y-%m-%d %H:%M")
    timestamps_seconds = [(ts - datetime(1970, 1, 1)).total_seconds() for ts in timestamps]
    race_start_seconds = (race_start_datetime - datetime(1970, 1, 1)).total_seconds()

    






    if jauge_type == "Wind Speed":
        data_type = jauge_type
        bounds = [0,40]
        unit = "km/h"
        data_of_each_type = weather_data['wind_speeds']
        value = np.interp(race_start_seconds, timestamps_seconds, data_of_each_type)
        bin_value = np.digitize(value, bins=np.linspace(bounds[0], bounds[1], 5)) - 1
        message = ["Not windy", "Not so windy","A but windy", "Higly windly"][bin_value]
        coefficient = 1

    elif jauge_type == "Temperature":
        data_type = jauge_type
        bounds = [-5,35]
        unit = "°C"
        data_of_each_type = weather_data['temperatures']
        value = np.interp(race_start_seconds, timestamps_seconds, data_of_each_type)
        bin_value = np.digitize(value, bins=np.linspace(bounds[0], bounds[1], 5)) - 1
        message = ["Cold", "Cool","Warm", "Hot"][bin_value]
        coefficient = impact_temperature(value)

    elif jauge_type == "Humidity":
        data_type = jauge_type
        bounds = [0,100]
        unit = "%"
        data_of_each_type = weather_data['humidities']
        value = np.interp(race_start_seconds, timestamps_seconds, data_of_each_type)
        bin_value = np.digitize(value, bins=np.linspace(bounds[0], bounds[1], 5)) - 1
        message = ["Dry", "Kind of dry","Kind of moist", "Moist"][bin_value]
        coefficient = 1

    elif jauge_type == "Risk of rain":
        data_type = jauge_type
        bounds = [0,100]
        unit = "%"
        data_of_each_type = weather_data['rain_probabilities']
        value = np.interp(race_start_seconds, timestamps_seconds, data_of_each_type)
        bin_value = np.digitize(value-1, bins=np.linspace(bounds[0], bounds[1], 5)) - 1
        message = ["No risk", "Should be okay","Take care", "Take a jacket"][bin_value]
        coefficient = 1

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        #value = f"{value} {unit}",
        value = value,
        title = {'text': f"{data_type}"},
        delta = {'reference': bounds[1]},
        gauge = {
            'axis': {'range': bounds},
            'bar': {'color': "orange"},
            'steps' : [
                {'range': [bounds[0], bounds[1]*0.25], 'color': "lightgray"},
                {'range': [bounds[1]*0.25, bounds[1]*0.5], 'color': "gray"},
                {'range': [bounds[1]*0.5, bounds[1]*0.75], 'color': "lightgray"},
                {'range': [bounds[1]*0.75, bounds[1]], 'color': "gray"}],

            'threshold': {'line': {'color': "red", 'width': 4},'thickness': 0.75,'value': value}
            }
            )
            )

    fig.update_layout(
        font=dict(size=18),
        height=400,
        paper_bgcolor="black",
        font_color="white"
    )
    
    return fig, unit, message, coefficient








def impact_temperature(temperature):
    # Calculer le coefficient de temps perdu
    coefficient = (3.3744 - 0.22334 * temperature + 0.01031 * temperature * temperature - 2.1648864)/100
    # Calculer le temps perdu en minutes
    return coefficient