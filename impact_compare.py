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



# Courses prédéfinies avec des fichiers GPX fictifs
predefined_courses = {
    "Boston",
    "London",
    "Chicago",
    "Tokyo - not available yet",
    "Berlin - not available yet",
    "New-York - not available yet"
}











# Interface utilisateur
st.title("Compare the majors")
st.write("First draft, soon on Maurten website !")






# Charger les données JSON
def load_data():
    with open('race_infos.json', 'r') as file:
        data = json.load(file)
    return data

# Afficher les statistiques des courses
def display_race_stats(race1, race2, data):
    race1_stats = data[race1]
    race2_stats = data[race2]

    col1, col2 = st.columns(2)

    with col1:
        st.header(f"Course: {race1}")
        for stat, value in race1_stats.items():
            st.write(f"{stat}: {value}")

    with col2:
        st.header(f"Course: {race2}")
        for stat, value in race2_stats.items():
            st.write(f"{stat}: {value}")

# Charger les données
data = load_data()

# Interface utilisateur Streamlit
st.title("Comparaison des Statistiques de Courses")
race_options = list(data.keys())

# Sélection des courses
race1 = st.selectbox("Sélectionnez la première course", race_options)
race2 = st.selectbox("Sélectionnez la deuxième course", race_options)

# Afficher les statistiques des deux courses
display_race_stats(race1, race2, data)

# Espace pour les graphiques
st.header("Comparaison Graphique")
st.write("Graphique des temps des finishers des deux courses à venir...")

# Placeholder pour les fonctions de graphique
# Exemples de fonctions de graphique que vous pouvez ajouter
# def plot_finisher_times(race1_times, race2_times):
#     # code pour tracer les temps des finishers
#     pass

# if 'finisher_times' in data[race1] and 'finisher_times' in data[race2]:
#     plot_finisher_times(data[race1]['finisher_times'], data[race2]['finisher_times'])













st.write("Soon on Maurten Website - Contact me if you want other analyses")
  


