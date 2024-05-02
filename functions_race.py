import streamlit as st
from datetime import datetime, timedelta
import os
import streamlit.components.v1 as components  # Importer le module components
import json
import matplotlib.pyplot as plt
import numpy as np
import math



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









def impact_vent_liste(gpx_filename, json_filename, index):
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
 

    # print(len(valeurs))
    # print(wind_speed)
    # plt.show()
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
                        paper_bgcolor=CUSTOM_COLORS["white"],
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
    fig.write_html(f"PUBLIC/output/{race_name}/wind_help_{race_name}.html")
    # fig.show()

    fig, ax = plt.subplots()
    ax.plot(direction_list_degrees)
    plt.title("Strength of the wind")
    plt.xlabel("Distance")  # erreur à réparer => pas par segments mais par kilomètres
    plt.ylabel("Sens race")
    plt.savefig(f"PUBLIC/output/{race_name}/sens_race_{race_name}.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(valeursdeg)
    plt.title("Strength of the wind")
    plt.xlabel("Distance")  # erreur à réparer => pas par segments mais par kilomètres
    plt.ylabel("Sens race ")
    plt.savefig(f"PUBLIC/output/{race_name}/sens_diff_{race_name}.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    return valeurs, wind_speed