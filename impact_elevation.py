import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
import os
import json
import gpxpy

from functions_race import (
    draw_wind_rose,
    impact_vent_liste,
    generate_elevation_and_gradient_plot
    )





# Définition des courses disponibles
races = {
    "Your race": {"date": datetime(2024, 5, 4, 15, 0), "location": "Paris"},
    "Boston Marathon": {"date": datetime(2024, 12, 25, 9, 30), "location": "New York"},
    "London Marathon": {"date": datetime(2024, 7, 12, 14, 0), "location": "Tokyo"},
    "Ecotrail": {"date": datetime(2024, 8, 23, 17, 45), "location": "Berlin"}
}

base_path = os.path.dirname(__file__)  # Obtenir le chemin du répertoire du script actuel































# Courses prédéfinies avec des fichiers GPX fictifs
predefined_courses = {
    "Boston Marathon",
    "London Marathon",
    "Ecotrail",
    "Upload your own GPX"
    
}

# Interface utilisateur
st.title("Course Altitude and Gradient Profile")

threshold = st.slider("Set Gradient Threshold (%) for the visualisation", min_value=0, max_value=20, value=10)

# Sélectionner une course prédéfinie ou télécharger un fichier GPX
selected_course = st.selectbox("Select a predefined course or upload your GPX", ["Choose your race"] + list(predefined_courses))
#uploaded_file = st.file_uploader("Or upload a GPX file", type=["gpx"])

# Variable pour stocker les points GPS
points = []

# Si un fichier GPX est demandé

if selected_course == "Upload your own GPX":
    uploaded_file = st.file_uploader("Or upload a GPX file", type=["gpx"])  

    if uploaded_file is not None:

        gpx = gpxpy.parse(uploaded_file)

        track = gpx.tracks[0] if gpx.tracks else None
        segment = track.segments[0] if track and track.segments else None

        if segment:
            points = [(point.latitude, point.longitude, point.elevation) for point in segment.points]
            st.write(f"Number of points in the uploaded GPX file: {len(points)}")
        else:
            st.write("The uploaded GPX file doesn't contain a valid track.")

# Sinon, (si une course prédéfinie est sélectionnée)
elif selected_course in predefined_courses :
    gpx_path = os.path.join(base_path, f"gpx_race/{selected_course}.gpx")
    with open(gpx_path, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    track = gpx.tracks[0] if gpx.tracks else None
    segment = track.segments[0] if track and track.segments else None

    if segment:
        points = [(point.latitude, point.longitude, point.elevation) for point in segment.points]
        st.write(f"Number of points in {selected_course}: {len(points)}")


    

# Si l'une des deux conditions est remplie, on passe à l'étape suivante
if points:
    # Exemple d'étape suivante : afficher les premiers points
    st.write(f"First 5 points: {points[:5]}")

fig = generate_elevation_and_gradient_plot(uploaded_file, threshold)
st.plotly_chart(fig)



















st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")







# Interface utilisateur

st.title("Course Altitude and Gradient Profile")
selected_race = st.selectbox("Choose your race", list(races.keys()))




#uphill_level = st.slider("Your uphill level - from flat runner to uphill runner", 0, 1, 0.5)  # 0,5 comme valeur par défaut
uphill_level = st.select_slider("Wind Direction (dir)", options=["Flat runner", "Prefer flat section","Average", "Good when hilly", "Uphill runner", "Vertical Kilometer runner"], value="Average")

runner_speed = st.slider("Your expected speed (km/h) - the speed impacts the grade adjusted speed", 6, 22, 17)  # 15 comme valeur par défaut


#st.title(f"Wind Impact on {selected_race}")


if selected_race == "Your race":
    st.write("")
    st.write("")
    st.write("Enter your race and informations")

else : 


    logo_path = os.path.join(base_path, f"logo_race/{selected_race}.png")
    html_file_map = os.path.join(base_path,f"map_race/map_{selected_race}.html")
    html_file_weather = os.path.join(base_path,f"weather_race/wind_help_{selected_race}.html")
    directions_path = os.path.join(base_path,f"directions_race/{selected_race}_directions.json")
    elev_path = os.path.join(base_path, f"elev_race/elevation_profile2_{selected_race}.png")
    grad_path = os.path.join(base_path, f"grad_race/elevation_profile3_{selected_race}.png")




    with open(directions_path, 'r') as file:  # Remplacez 'file.json' par le chemin de votre fichier
        data = json.load(file)
        directions = [item['direction'] for item in data]
        mean_direction = sum(directions)/len(directions)




    st.image(logo_path, width=300)  # Modifie "path_to_logo.png" par le chemin vers ton fichier image ou URL, et ajuste la largeur selon tes besoins.

    st.image(elev_path)
    st.image(grad_path)




# Display the charts in Streamlit
st.plotly_chart(fig_altitude)
st.plotly_chart(fig_gradient)




