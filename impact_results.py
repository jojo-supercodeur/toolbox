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
    "Boston Marathon 2022",
    "Boston Marathon 2023",
    "Boston Marathon 2024",
    "Chicago 2023",
    "London 2024 - Mass results",
}











# Interface utilisateur
st.title("Boston Marathon results analysis")





# Utiliser un slider pour sélectionner le temps en minutes
total_minutes = st.slider(
    "Choose your finishing time (min) (it'll be used to compare yourself to the other runners)",
    min_value=0,
    max_value=600,  # Limite supérieure (10 heures)
    value=240  # Valeur par défaut (4 heures)
)


# Convertir les minutes en HH:MM
time_str = minutes_to_hhmm(total_minutes)

# Afficher le temps formaté et le nombre total de minutes
st.write(f"Your race time : {time_str}")



# threshold = st.slider("Set Gradient Threshold (%) for the visualisation", min_value=0, max_value=20, value=10)

# Sélectionner une course prédéfinie ou télécharger un fichier GPX
selected_course = st.selectbox("Select the edition of Boston Marathon", ["Choose your race to analyse !"] + list(predefined_courses))
#uploaded_file = st.file_uploader("Or upload a GPX file", type=["gpx"])


error_nationality = "RAS"
error_gender = "RAS"
error_elite = "RAS"


if selected_course != "Choose your race to analyse !" :

    if selected_course == "Boston Marathon 2022" :
        filepath = os.path.join(base_path, "results_race/sorted_Boston_2022.json")

    elif selected_course == "Boston Marathon 2023" :
        filepath = os.path.join(base_path, "results_race/sorted_Boston_2023.json")

    elif selected_course == "Boston Marathon 2024" :
        filepath = os.path.join(base_path, "results_race/sorted_Boston_2024.json")
        error_nationality ="Nationality not available this year"

    elif selected_course == "Chicago 2023" :
        filepath = os.path.join(base_path, "results_race/sorted_Chicago_2023.json")

    elif selected_course == "London 2024 - Mass results" :
        filepath = os.path.join(base_path, "results_race/sorted_London_2024.json")
        error_gender = "I struggled to scrap all the informations so the sex feature is not available rn"
        error_elite = "avalaible only for mass results"



    st.write("Runners distribution ")
    fig_1 = plot_time_distribution(filepath)
    st.plotly_chart(fig_1)
    
    if error_gender == "RAS":
        st.write("Runners distribution according to sex")
        fig_11 = plot_time_distribution_sex(filepath)
        st.plotly_chart(fig_11)

    st.write("Finish time percentage")
    fig_2 = plot_pourcentage_finish(filepath, total_minutes)
    st.plotly_chart(fig_2)

    if error_elite == "RAS":
        st.write("Top 10 pacing evolution")
        fig_3 = plot_top10_evolution(filepath, '02:04:00')
        st.plotly_chart(fig_3)
    else : 
        st.write("prouuuuuut")

    st.write("Negativ/Positiv split analysis according to level")
    fig_4 = plot_split_coefficient(filepath)
    st.plotly_chart(fig_4)

    if error_nationality =="RAS":
        st.write("Nationality of the runners")
        fig_5 = plot_nationality_distribution(filepath)
        st.plotly_chart(fig_5)

    if error_nationality =="RAS":
        st.write("Some statistics on each country")
        df_6 = create_country_statistics_table(filepath)
        st.dataframe(df_6)


    st.write("Speedness of each surname")
    fig_7 = plot_name_speed_distribution(filepath)
    st.plotly_chart(fig_7)


    st.write("Soon on Maurten Website - Contact me if you want other analyses")
  










