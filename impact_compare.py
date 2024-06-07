import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
import os
import json
import gpxpy

from big_fonctions.functions_results import ( 
    plot_time_distribution,
    plot_time_distribution_sex,
    plot_pourcentage_finish,
    plot_top10_evolution,
    plot_split_coefficient,
    plot_nationality_distribution,
    create_country_statistics_table,
    plot_name_speed_distribution
)

# Définir une fonction pour convertir les minutes en HH:MM
def minutes_to_hhmm(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

base_path = os.path.dirname(__file__)  # Obtenir le chemin du répertoire du script actuel

# Charger les données JSON
def load_data():
    filepath = os.path.join(base_path, "json_files/race_infos.json")
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

# Charger les données
data = load_data()

# Interface utilisateur
st.title("Compare the Majors")
st.write("First draft, soon on Maurten website!")

race_options = list(data.keys())

col1, col2 = st.columns(2)

with col1:
    race1 = st.selectbox("Choose your race", ["Choose your race"] + race_options)

with col2:
    race2 = st.selectbox("Choose the race to compare", ["Choose the race to compare"] + race_options)

if race1 != "Choose your race" and race2 != "Choose the race to compare":
    race1_stats = data[race1]
    logo_path1 = os.path.join(base_path, f"logo_race/{race1}.png")
    race2_stats = data[race2]
    logo_path2 = os.path.join(base_path, f"logo_race/{race2}.png")

    # Affichage des titres des courses
    col1, col2 = st.columns(2)
    with col1:
        st.header(f"{race1}")
        st.markdown(f"<div style='text-align: center;'><img src='{logo_path1}' width='200'></div>", unsafe_allow_html=True)

    with col2:
        st.header(f"{race2}")
        st.markdown(f"<div style='text-align: center;'><img src='{logo_path2}' width='200'></div>", unsafe_allow_html=True)







    #chargement des statistiques 


    # Définir la taille de police
    font_size_large = 180  # Vous pouvez ajuster cette valeur selon vos préférences

    # Initialiser les variables locales pour chaque statistique
    race1_distance = race1_stats.get('Distance', 'N/A')
    race1_elevation = race1_stats.get('Elevation', 'N/A')
    race1_finishers = race1_stats.get('Finishers', 'N/A')
    race1_temperature = race1_stats.get('Temperature', 'N/A')
    race1_first_edition = race1_stats.get('first edition', 'N/A')

    race2_distance = race2_stats.get('Distance', 'N/A')
    race2_elevation = race2_stats.get('Elevation', 'N/A')
    race2_finishers = race2_stats.get('Finishers', 'N/A')
    race2_temperature = race2_stats.get('Temperature', 'N/A')
    race2_first_edition = race2_stats.get('first edition', 'N/A')




    #some work on the data 

    # Générer les messages d'élévation pour chaque course

    race_elevations = [race1_elevation, race2_elevation]
    messages_elevation = ["", ""]
    for i in range(2):
        if race_elevations[i] < 100:
            messages_elevation[i] = "This is quite flat"
        elif race_elevations[i] < 200:
            messages_elevation[i] = "There is some elevation"
        else:
            messages_elevation[i] = "Quite hilly marathon"

    # Assigner les messages aux variables
    message1_elevation, message2_elevation = messages_elevation





    # Initialiser les températures des courses et les variables pour les messages
    race_temperatures = [race1_temperature, race2_temperature]
    messages_temperature = ["", ""]

    # Générer les messages de température pour chaque course
    for i in range(2):
        if race_temperatures[i] < 10:
            messages_temperature[i] = "This is cold"
        elif race_temperatures[i] < 20:
            messages_temperature[i] = "This is mild"
        else:
            messages_temperature[i] = "This is hot"

    # Assigner les messages aux variables
    message1_temperature, message2_temperature = messages_temperature

         








    # Affichage des statistiques


    #First edition 
    st.write("The race was created in : ")
    with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race1_first_edition}</h1>", unsafe_allow_html=True)
    with col2:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race2_first_edition}</h1>", unsafe_allow_html=True)


    




    #Number of runner
    st.write("The number of runnner is :")
    with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race1_finishers}</h1>", unsafe_allow_html=True)
    with col2:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race2_finishers}</h1>", unsafe_allow_html=True)







    #Elevation of the race
    st.write("The positive elevation is :")
    with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race1_finishers}</h1>", unsafe_allow_html=True)
            st.write(message1_elevation)
    with col2:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race2_finishers}</h1>", unsafe_allow_html=True)
            st.write(message2_elevation)




    
    #Temperature
    st.write("The mean temperature the last 10 years was :")
    with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race1_temperature}</h1>", unsafe_allow_html=True)
            st.write(message1_temperature)
    with col2:
            st.markdown(f"<h1 style='text-align: center; font-size: {font_size_large}px;'>{race2_temperature}</h1>", unsafe_allow_html=True)
            st.write(message2_temperature)







st.write("Soon on Maurten Website - Contact me if you want other analyses")
