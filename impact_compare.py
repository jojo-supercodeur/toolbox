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
        st.image(logo_path1, width=100)

    with col2:
        st.header(f"{race2}")
        st.image(logo_path2, width=100)

    # Affichage des statistiques
    for stat1, value1 in race1_stats.items():
        st.write(f"Let's compare {stat1}")
        col1, col2 = st.columns(2)
        with col1:
            if isinstance(value1, int):
                st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{value1}</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='text-align: center;'>{value1}</h2>", unsafe_allow_html=True)
                
        with col2:
            value2 = race2_stats[stat1]
            if isinstance(value2, int):
                st.markdown(f"<h1 style='text-align: center;'>{value2}</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='text-align: center;'>{value2}</h2>", unsafe_allow_html=True)

st.write("Soon on Maurten Website - Contact me if you want other analyses")
