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



def draw_wind_rose(direction,status):
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

    # Affichage avec Streamlit
    st.pyplot(fig)







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
    gradient_smooth = np.convolve(gradient, np.ones(30) / 30, mode='same')

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

