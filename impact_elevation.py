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

        gpx_path = uploaded_file
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
    st.write(gpx_path)
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

    st.write(gpx_path)

    fig = generate_elevation_and_gradient_plot(gpx_path, threshold)
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












