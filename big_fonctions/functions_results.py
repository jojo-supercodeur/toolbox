import json
import plotly.graph_objects as go












def plot_time_distribution(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Extraire les temps d'arrivée et les convertir en minutes
    finish_times = []
    for key, value in data.items():
        time_str = value["Totals"]["Time Total (net)"]
        h, m, s = map(int, time_str.split(':'))
        total_minutes = int(h * 60 + m + s / 60)
        finish_times.append(total_minutes)
    
    # Créer un histogramme des temps d'arrivée
    fig = go.Figure(data=[go.Histogram(x=finish_times, xbins=dict(size=1))])

    # Définir les barrières mythiques en minutes
    barriers = [180, 210, 240]  # 3h, 3h30, 4h en minutes

    # Ajouter des lignes verticales pour les barrières
    shapes = [
        dict(
            type="line",
            x0=barrier,
            y0=0,
            x1=barrier,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color="red", width=2)
        ) for barrier in barriers
    ]
    fig.update_layout(shapes=shapes)

    # Définir les tickvals et ticktext pour l'axe x
    tickvals = list(range(0, int(max(finish_times)) + 1, 30))
    ticktext = [f"{int(t // 60):02d}:{int(t % 60):02d}" for t in tickvals]
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext
        ),
        title="Distribution of runners based on finish time",
        xaxis_title="Finish time (HH:MM)",
        yaxis_title="Number of runners",
        bargap=0.2,
    )
    
    # Afficher le graphique
    return fig















import json
import plotly.graph_objects as go

def convert_time_to_minutes(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 60 + m + s / 60

def plot_time_distribution_sex(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Extraire les temps d'arrivée et les convertir en minutes par sexe
    finish_times_men = []
    finish_times_women = []
    for key, value in data.items():
        time_str = value["Totals"]["Time Total (net)"]
        h, m, s = map(int, time_str.split(':'))
        total_minutes = int(h * 60 + m + s / 60)
        if value["Participant Details"]["Sex"] == "M":
            finish_times_men.append(total_minutes)
        elif value["Participant Details"]["Sex"] == "W":
            finish_times_women.append(total_minutes)
    
    # Créer les histogrammes des temps d'arrivée
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=finish_times_men, 
        xbins=dict(size=1),
        name='Men',
        opacity=0.75,
        marker_color="green",
        legendgroup='Men',
        visible=True
    ))



    
    fig.add_trace(go.Histogram(
        x=finish_times_women, 
        xbins=dict(size=1),
        name='Women',
        opacity=0.75,
        marker_color="pink",
        legendgroup='Women',
        visible=True
    ))

    # Définir les tickvals et ticktext pour l'axe x
    tickvals = list(range(0, int(max(finish_times_men + finish_times_women)) + 1, 30))
    ticktext = [f"{int(t // 60):02d}:{int(t % 60):02d}" for t in tickvals]
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext
        ),
        title="Distribution of runners based on finish time and sex",
        xaxis_title="Finish time (HH:MM)",
        yaxis_title="Number of runners",
        bargap=0.2,
        barmode='overlay',
        legend=dict(
            traceorder='normal'
        )
    )

    # Ajuster la visibilité des traces en utilisant les légendes
    fig.update_traces(selector=dict(name='Men'), visible=True)
    fig.update_traces(selector=dict(name='Women'), visible=True)
    
    # Ajuster l'opacité pour éviter de superposer complètement les barres
    fig.update_traces(opacity=0.75)

    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_time_distribution_sex('path_to_your_file.json')
# fig.show()














import json
import plotly.graph_objects as go
import numpy as np
import json
import plotly.graph_objects as go
import numpy as np

def plot_pourcentage_finish(file_path, additional_time=None):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Extraire les temps d'arrivée et les convertir en minutes
    finish_times = []
    for key, value in data.items():
        time_str = value["Totals"]["Time Total (net)"]
        h, m, s = map(int, time_str.split(':'))
        total_minutes = int(h * 60 + m + s / 60)
        finish_times.append(total_minutes)
    
    # Trier les temps de finish
    finish_times.sort()
    
    # Calculer le pourcentage cumulatif des finishers
    total_finishers = len(finish_times)
    cumulative_percentages = np.arange(1, total_finishers + 1) / total_finishers * 100
    
    # Créer la figure
    fig = go.Figure()
    
    # Ajouter la courbe du pourcentage cumulatif des finishers
    fig.add_trace(go.Scatter(x=finish_times, y=cumulative_percentages, mode='lines', name='Cumulative Percentage'))
    
    # Ajouter les lignes horizontales pour 25%, 50%, 75%
    for percent in [25, 50, 75]:
        fig.add_shape(
            type="line",
            x0=0,
            y0=percent,
            x1=max(finish_times),
            y1=percent,
            line=dict(color="red", width=2, dash="dash"),
        )
    
    # Trouver les temps correspondant à 25%, 50%, 75%
    percentiles = [25, 50, 75]
    percentile_times = [finish_times[int(p / 100 * total_finishers) - 1] for p in percentiles]
    
    # Ajouter les lignes verticales pour les temps correspondants
    for i, time in enumerate(percentile_times):
        fig.add_shape(
            type="line",
            x0=time,
            y0=0,
            x1=time,
            y1=percentiles[i],
            line=dict(color="red", width=2, dash="dash"),
        )
    
    # Ajouter les annotations pour les temps de barrières
    for i, time in enumerate(percentile_times):
        fig.add_annotation(
            x=time,
            y=percentiles[i],
            text=f"{percentiles[i]}%: {int(time // 60)}:{int(time % 60):02d}",
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-40
        )
    
    # Ajouter une ligne verticale pour le temps additionnel et une annotation
    if additional_time is not None:
        # Calculer le pourcentage de finishers pour le temps additionnel
        percentage_at_additional_time = np.sum(np.array(finish_times) <= additional_time) / total_finishers * 100
        
        fig.add_shape(
            type="line",
            x0=additional_time,
            y0=0,
            x1=additional_time,
            y1=percentage_at_additional_time,
            line=dict(color="green", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=additional_time,
            y=percentage_at_additional_time,
            text=f"{percentage_at_additional_time:.2f}%: {int(additional_time // 60)}:{int(additional_time % 60):02d}",
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-40,
            font=dict(color="green")
        )
    
    # Définir les tickvals et ticktext pour l'axe x
    tickvals = list(range(0, int(max(finish_times)) + 1, 30))
    ticktext = [f"{int(t // 60):02d}:{int(t % 60):02d}" for t in tickvals]
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext
        ),
        title="Cumulative percentage of finishers over time",
        xaxis_title="Finish time (HH:MM)",
        yaxis_title="Percentage of finishers",
        bargap=0.2,
    )
    
    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_pourcentage_finish('path_to_your_file.json', additional_time=200)
# fig.show()












def convert_time_to_minutes(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 60 + m + s / 60



def plot_top10_evolution(file_path, reference_time):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Convertir le temps de référence en minutes
    reference_minutes = convert_time_to_minutes(reference_time)
    
    # Extraire les temps de passage des coureurs du top 10
    top10_ids = sorted(data.keys(), key=lambda x: int(data[x]['Totals']['Place (Total)']))[:10]
    
    # Points de passage en kilomètres et miles
    splits_labels = ["5K", "10K", "15K", "20K", "HALF", "25K", "30K", "20 Miles", "21 Miles", "35K", "40K", "25.2 Miles", "Finish Net"]
    splits_distances = [5, 10, 15, 20, 21.1, 25, 30, 32.1869, 33.7962, 35, 40, 40.555, 42.195]  # en kilomètres et miles

    fig = go.Figure()

    # Tracer la courbe de référence
    reference_distances = [0] + splits_distances
    reference_diffs = [0] + [0 for _ in splits_distances]
    fig.add_trace(go.Scatter(x=reference_distances, y=reference_diffs, mode='lines', name=f'Reference: {int(reference_minutes // 60)}h{int(reference_minutes % 60):02d} smoothed', line=dict(dash='dash', color='red')))

    for runner_id in top10_ids:
        runner_data = data[runner_id]
        runner_name = runner_data["Participant Details"]["Name"]
        runner_splits = runner_data["Splits"]
        
        distances = [0]  # Ajouter le point 0 km pour chaque coureur
        time_diffs = [0]  # Ajouter le point 0 pour chaque coureur
        
        for split in runner_splits:
            if split["Split"] in splits_labels:
                split_time = convert_time_to_minutes(split["Time"])
                distance = splits_distances[splits_labels.index(split["Split"])]
                distances.append(distance)
                # Calculer l'écart par rapport au temps de référence lissé sur la distance parcourue
                expected_time = (distance / 42.195) * reference_minutes
                time_diff = split_time - expected_time
                time_diffs.append(-time_diff)  # Inverser l'axe des ordonnées
        
        fig.add_trace(go.Scatter(x=distances, y=time_diffs, mode='lines+markers', name=runner_name))
    
    # Configurer les axes et le titre
    fig.update_layout(
        title="Top 10 Men's Evolution of Times Compared to Reference Time",
        xaxis_title="Distance (km)",
        yaxis_title="Time Difference (seconds)",
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(0, 45, 5)],
            ticktext=[f"{i} km" for i in range(0, 45, 5)]
        )
    )
    
    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_top10_evolution('path_to_your_file.json', '02:02:00')
# fig.show()


















import json
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression

def convert_time_to_minutes(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 60 + m + s / 60
    except ValueError:
        return None

def calculate_split_coefficient(first_half, second_half):
    # Calculer la différence en minutes
    diff = second_half - first_half
    # Calculer le coefficient de positive split en pourcentage
    split_coefficient = (diff / first_half) * 100
    return split_coefficient, diff

def plot_split_coefficient(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    finish_times = []
    split_coefficients = []
    time_differences = []

    for runner_id, runner_data in data.items():
        splits = runner_data["Splits"]
        total_time_str = runner_data["Totals"]["Time Total (net)"]
        total_time = convert_time_to_minutes(total_time_str)
        
        if total_time is None:
            continue
        
        first_half_time = None
        second_half_time = None
        
        for split in splits:
            if split["Split"] == "HALF":
                first_half_time = convert_time_to_minutes(split["Time"])
            elif split["Split"] == "Finish Net" and first_half_time is not None:
                second_half_time = convert_time_to_minutes(split["Time"])
        
        if first_half_time is not None and second_half_time is not None:
            second_half_time = second_half_time - first_half_time
            split_coefficient, time_difference = calculate_split_coefficient(first_half_time, second_half_time)
            finish_times.append(total_time)
            split_coefficients.append(split_coefficient)
            time_differences.append(time_difference)
    
    # Convertir les données pour la régression linéaire
    X = np.array(finish_times).reshape(-1, 1)
    y = np.array(split_coefficients)
    
    # Ajuster la régression linéaire
    reg = LinearRegression().fit(X, y)
    trendline = reg.predict(X)
    
    # Créer le graphique
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=finish_times,
        y=split_coefficients,
        mode='markers',
        marker=dict(
            size=3,  # Taille plus petite des points
            color=time_differences,
            #colorbar=dict(title='Time Difference (min)'),
            colorscale='Viridis'
        ),
        #text=[f"Time Difference: {diff:.2f} min" for diff in time_differences],
        name='Split Coefficient'
    ))

    # Ajouter la courbe de tendance linéaire
    fig.add_trace(go.Scatter(
        x=finish_times,
        y=trendline,
        mode='lines',
        line=dict(color='red'),
        name='Trendline'
    ))
    
# Configurer les axes et le titre
    fig.update_layout(
        title="Split Coefficient vs Finishing Time",
        xaxis_title="Finishing Time (minutes)",
        yaxis_title="Positive Split Coefficient (%)",
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(0, int(max(finish_times)) + 1, 30)],
            ticktext=[f"{i//60}h{i%60:02d}" for i in range(0, int(max(finish_times)) + 1, 30)]
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(-50, 150 + 1, 10)],
            ticktext=[f"{i}%" for i in range(-50, 150 + 1, 10)]
        )
    )
    
    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_split_coefficient('path_to_your_file.json')
# fig.show()














import json
import plotly.graph_objects as go
from collections import Counter

def plot_nationality_distribution(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Extraire les nationalités à partir des noms
    nationalities = []
    for key, value in data.items():
        surname = value["Participant Details"]["Surname"]
        nationality = surname[surname.find("(")+1:surname.find(")")]
        nationalities.append(nationality)
    
    # Compter les occurrences de chaque nationalité
    nationality_counts = Counter(nationalities)
    total_runners = sum(nationality_counts.values())
    
    # Séparer les nationalités représentant moins de 5% des participants
    major_nationalities = {k: v for k, v in nationality_counts.items() if (v / total_runners) >= 0.05}
    other_nationalities_count = total_runners - sum(major_nationalities.values())
    
    # Ajouter la catégorie "Other nationalities"
    if other_nationalities_count > 0:
        major_nationalities["Other nationalities"] = other_nationalities_count
    
    # Préparer les données pour le graphique en camembert
    labels = list(major_nationalities.keys())
    values = list(major_nationalities.values())
    
    # Créer le graphique en camembert
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(
        title="Distribution of Nationalities in the Marathon",
    )
    
    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_nationality_distribution('path_to_your_file.json')
# fig.show()

















import json
import pandas as pd
import streamlit as st

def convert_time_to_minutes(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 60 + m + s / 60
    except ValueError:
        return None

def convert_minutes_to_hhmm(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h:02d}:{m:02d}"

def create_country_statistics_table(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Initialiser les dictionnaires pour stocker les statistiques
    country_counts = {}
    country_times = {}
    country_gender = {}
    
    total_runners = 0
    
    # Parcourir les données pour extraire les informations nécessaires
    for key, value in data.items():
        surname = value["Participant Details"]["Surname"]
        nationality = surname[surname.find("(")+1:surname.find(")")]
        
        if nationality not in country_counts:
            country_counts[nationality] = 0
            country_times[nationality] = []
            country_gender[nationality] = {'M': 0, 'W': 0}
        
        time_str = value["Totals"]["Time Total (net)"]
        total_minutes = convert_time_to_minutes(time_str)
        
        if total_minutes is not None:
            country_counts[nationality] += 1
            total_runners += 1
            country_times[nationality].append(total_minutes)
            
            sex = value["Participant Details"]["Sex"]
            if sex in country_gender[nationality]:
                country_gender[nationality][sex] += 1
    
    # Calculer les statistiques pour chaque pays
    country_statistics = []
    for country, count in country_counts.items():
        percentage = round((count / total_runners) * 100, 2)
        avg_time_minutes = sum(country_times[country]) / len(country_times[country])
        avg_time_hhmm = convert_minutes_to_hhmm(avg_time_minutes)
        male_count = country_gender[country]['M']
        female_count = country_gender[country]['W']
        #parity = f"{male_count}M / {female_count}F"
        if male_count+female_count != 0:
            parity = round(male_count/(male_count+female_count),2)
        else :
            parity = 1
        
        country_statistics.append({
            "Country": country,
            "Number of Runners": count,
            "Percentage of Runners (%)": f"{percentage}%",
            "Parity (M/W)": f"{parity}%",
            "Average Time (hh:mm)": avg_time_hhmm
        })
    
    # Convertir en DataFrame pour une présentation facile
    df_country_statistics = pd.DataFrame(country_statistics)
    
    # Classer par ordre décroissant du nombre de coureurs
    df_country_statistics = df_country_statistics.sort_values(by="Number of Runners", ascending=False)
    
    return df_country_statistics















import json
import plotly.express as px
import pandas as pd



def plot_name_speed_distribution(file_path):
    # Charger les données JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Extraire les prénoms et leurs temps de course
    name_times = {}
    for key, value in data.items():
        name = value["Participant Details"]["Surname"]
        time_str = value["Totals"]["Time Total (net)"]
        total_minutes = convert_time_to_minutes(time_str)
        
        if name not in name_times:
            name_times[name] = []
        name_times[name].append(total_minutes)
    
    # Calculer le nombre d'occurrences et le temps moyen pour chaque prénom
    name_statistics = []
    for name, times in name_times.items():
        count = len(times)
        if count >= 30:
            avg_time = sum(times) / count
            name_statistics.append({
                "Name": name,
                "Count": count,
                "Average Time (minutes)": avg_time
            })
    
    # Convertir en DataFrame pour une présentation facile
    df_name_statistics = pd.DataFrame(name_statistics)
    
    # Créer le graphique avec Plotly
    fig = px.scatter(df_name_statistics, x="Average Time (minutes)", y="Count", text="Name",
                     title="Speed Distribution of Names",
                     labels={"Average Time (minutes)": "Finishing Time (minutes)", "Count": "Number of Occurrences"},
                     hover_data=["Name"])
    
    fig.update_traces(marker=dict(size=10), textposition='top center')
    
    # Afficher le graphique
    return fig

# Utilisation de la fonction
# fig = plot_name_speed_distribution('path_to_your_file.json')
# fig.show()
