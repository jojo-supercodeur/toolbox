import streamlit as st
from datetime import datetime, timedelta
import os
import streamlit.components.v1 as components  # Importer le module components
import json
import matplotlib.pyplot as plt
import numpy as np
import math
from functions_race import (
    draw_wind_rose,
    impact_vent_liste
    )



base_path = os.path.dirname(__file__)  # Obtenir le chemin du répertoire du script actuel









# Fonction pour générer les prévisions de vent
def get_wind_forecast():
    return 15, "Nord-Est"  # Exemple de valeurs arbitraires

def calculate_wind_assistance(course_direction, wind_direction, runner_speed, wind_speed):
    # Calcul de l'angle entre la direction de la course et celle du vent
    angle_difference = math.radians(wind_direction - course_direction)
    
    # Composante de la vitesse du vent dans la direction de la course
    wind_component = wind_speed * math.cos(angle_difference)
    
    # Calcul du ratio de l'aide du vent par rapport à la vitesse du coureur
    wind_assistance_ratio = wind_component / runner_speed
    
    return wind_assistance_ratio

# Fonction pour charger et afficher le fichier HTML de la carte
def load_html_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

def mean_angle_degrees(angles):
    x = sum(math.cos(math.radians(angle)) for angle in angles) / len(angles)
    y = sum(math.sin(math.radians(angle)) for angle in angles) / len(angles)
    mean_angle = math.degrees(math.atan2(y, x))
    return mean_angle if mean_angle >= 0 else mean_angle + 360









# Définition des courses disponibles
races = {
    "Your race": {"date": datetime(2024, 5, 4, 15, 0), "location": "Paris"},
    "Boston Marathon": {"date": datetime(2024, 12, 25, 9, 30), "location": "New York"},
    "London Marathon": {"date": datetime(2024, 7, 12, 14, 0), "location": "Tokyo"},
    "Ecotrail": {"date": datetime(2024, 8, 23, 17, 45), "location": "Berlin"}
}

# Interface utilisateur
selected_race = st.selectbox("Choose your race motherfucker", list(races.keys()))




taille = st.slider("Your height (m) - to calculate your air drag", 1.4, 2.1, 1.8)  # 15 comme valeur par défaut
runner_speed = st.slider("Your expected speed (km/h) - the speed increases drag effect", 6, 22, 17)  # 15 comme valeur par défaut


st.title(f"Wind Impact on {selected_race}")


if selected_race == "Your race":
    st.write("")
    st.write("")
    st.write("Enter your race and informations")

else : 


    logo_path = os.path.join(base_path, f"logo_race/{selected_race}.png")
    html_file_map = os.path.join(base_path,f"map_race/map_{selected_race}.html")
    html_file_weather = os.path.join(base_path,f"weather_race/wind_help_{selected_race}.html")
    directions_path = os.path.join(base_path,f"directions_race/{selected_race}_directions.json")



    with open(directions_path, 'r') as file:  # Remplacez 'file.json' par le chemin de votre fichier
        data = json.load(file)
        directions = [item['direction'] for item in data]
        mean_direction = sum(directions)/len(directions)




    st.image(logo_path, width=100)  # Modifie "path_to_logo.png" par le chemin vers ton fichier image ou URL, et ajuste la largeur selon tes besoins.





    #st.button("Generate wind prediction")
    race_info = races[selected_race]
    race_date = race_info["date"]
    st.write(f"The departure will be {race_date.strftime('%Y-%m-%d')} at {race_date.strftime('%H:%M')}")



    # Prévisions de vent
    if datetime.now() + timedelta(days=7) > race_date:
        wind_speed, wind_direction = get_wind_forecast()
        st.write(f"Our predictions are {wind_speed} km/h of wind strength and {wind_direction} direction, but feel free to play with it")
    else:
        st.write("The predictions are not available right now. We propose the average values over the last 10 years, but feel free to play with it")

    # Slider pour la force et la direction du vent
    wind_speed = st.slider("Wind Strength (km/h)", 0, 100, 15)  # 15 comme valeur par défaut
    #wind_direction_dir = st.select_slider("Wind Direction (dir)", options=["Nord", "Nord-Est", "Est", "Sud-Est", "Sud", "Sud-Ouest", "Ouest", "Nord-Ouest"], value="Sud-Est")
    wind_direction = st.slider("Wind Direction (°)", 0, 360, 115)




    if st.button("Generate the impact of the wind in my race"):
        # Charger et afficher la carte
        html_content_map = load_html_map(html_file_map)
        html_content_weather = load_html_map(html_file_weather)

        st.write("")
        st.write("")
        st.write("")

        course_direction = round(mean_angle_degrees(directions))

        st.write(f"The average direction of the race is : {course_direction}°")

        st.write(f"The average direction of the wind is : {wind_direction}°")



        # Création de trois colonnes pour les heures, les minutes, et les secondes
        col1, col2 = st.columns(2)


        with col1 : draw_wind_rose(wind_direction,"live")
        with col2 : components.html(html_content_map, height=360)  # Utiliser components.html pour intégrer la carte

        st.write("Here some informations about the live weather (next 48hours) => not accurate yet")
        ## col1, col2 = st.columns(2)


        ##with col1 : draw_wind_rose(wind_direction+180,"prevision")
        components.html(html_content_weather, height=600)  # Utiliser components.html pour intégrer la carte

        st.write("Here some informations about the live weather (next 48hours) => accurate")
        #impact_vent_liste(wind_direction, wind_speed,directions,selected_race)
        fig = impact_vent_liste(wind_direction, wind_speed, directions, selected_race)
        st.plotly_chart(fig, use_container_width=True) 







        impact = calculate_wind_assistance(course_direction, wind_direction, runner_speed, wind_speed)

        if impact >= 0:
            st.title(f"Estimated time gained due to wind: {impact:.2f} minutes")
        else :
            st.title(f"Estimated time lost due to wind: {-impact:.2f} minutes")
        

        



