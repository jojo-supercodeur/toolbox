import streamlit as st
from PIL import Image
import gpxpy
import os
import base64
from io import BytesIO
import json


def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str



from troisD_graphic import (
    create_3d_plot
)

from functions_race import (
    draw_wind_rose,
    impact_vent_liste,
    generate_elevation_and_gradient_plot,
    analyze_gpx,
    plot_weather_temp_wind,
    plot_weather_rain,
    create_wind_rose,
    create_gauge
    )


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


# Load the logo and provided image
logo_path = 'photos/logo_maurten_white.png'
logo = Image.open(logo_path)
provided_image_path = 'photos/logo_enduraw.png'
provided_image = Image.open(provided_image_path)
base_path = os.path.dirname(__file__)  # Obtenir le chemin du répertoire du script actuel

# Set up the page configuration
st.set_page_config(page_title="Marathon Briefing", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background-color: #000000;
        color: #FFFFFF;
    }
    .sidebar .sidebar-content {
        background-color: #000000;
    }
    h2 {
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the logo
st.image(logo, width=200)

# Title and subtitle
st.title("Personalized Marathon Briefing")

# Collect user information
with st.sidebar:
    st.subheader("Please enter your personal information")

    # Form for personal data
    with st.form(key='personal_data_form'):
        first_name = st.text_input("First Name")
        gender = st.selectbox("Gender", options=["Male", "Female"])
        weight = st.slider("Weight (kg)", min_value=30, max_value=150, step=1, value = 60)
        height = st.slider("Height (cm)", min_value=120, max_value=220, step=1, value = 165)
        age = st.slider("Age", min_value=16, max_value=80, step=1, value = 27)
        race_date_start = "2024-06-19" ## à changer pour mettre la date exacte ou 3 jours avant. Pour l'instant on a les prévisions toutes les 3 heures jusqu'à 5 jours
        race_hour_start = "09:00"  ## à changer, + gérer les fuseaux horaires 


        estimated_finish_time_minutes = st.slider(
            "Estimated Finish Time (minutes)",
            min_value=110,
            max_value=300,
            step=1,
            value = 220
        )
        estimated_finish_time = f"{estimated_finish_time_minutes // 60:02}:{estimated_finish_time_minutes % 60:02}"
        st.write(f"**Estimated Finish Time:** {estimated_finish_time}")

        race = st.selectbox("Choose the race", options=["Berlin Marathon", "Chicago Marathon", "New-York Marathon", "Chicago Marathon"])
        
        # Submit button for the form
        submit_button = st.form_submit_button(label='Submit')



if submit_button :
    with open("json_files/race_infos.json", "r") as file:
        marathon_data = json.load(file)
    race_data = marathon_data[race]
    provided_image = Image.open(f"logo_race/{race}.png")
    gpx_path = os.path.join(base_path, f"gpx_race/{race}.gpx")
    with open(gpx_path, "r") as gpx_file:
        provided_gpx = gpxpy.parse(gpx_file)
    threshold = 5
    data_gpx = analyze_gpx(provided_gpx)
    total_lenght = data_gpx[0]
    total_elevation_gain = data_gpx[1]
    total_elevation_loss = data_gpx[2]
    max_altitude = data_gpx[3]
    min_altitude = data_gpx[4]
    
    last_winner_man = race_data["last_winner"]["man_winner"]
    last_winner_woman = race_data["last_winner"]["woman_winner"]
    photo_winner_man = Image.open(f"photos/{last_winner_man}.png")     ## à changer pour la suite
    photo_winner_woman = Image.open(f"photos/{last_winner_woman}.png")     ## à changer pour la suite
    photo_winner_man_base64 = image_to_base64(photo_winner_man)
    photo_winner_woman_base64 = image_to_base64(photo_winner_woman)



    # Main content layout

























    st.header("Race Recap")

    st.markdown("<hr style='border:2px solid white'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])


    with col1:
        st.subheader("Race info")
        st.write(f"Race: {race}")
        st.write(f"Country: Germany")
        st.write(f"Distance: {round(total_lenght/1000,1)}km")
        st.write(f"Elevation: {round(total_elevation_gain)}m")
        st.write(f"Estimated Finish Time: {estimated_finish_time}")

    with col2:
        st.subheader("Runner Info")
        st.write(f"First name: {first_name}")
        st.write(f"Gender: {gender}")
        st.write(f"Age: {age}")
        st.write(f"Weight: {weight} kg")
        st.write(f"Height: {height} cm")

    with col4:
        st.image(provided_image, use_column_width=True)




















    st.header("Course")
    st.markdown("<hr style='border:2px solid white'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])


    with col1:
        fig = create_3d_plot(provided_gpx)
        st.plotly_chart(fig)

    with col2:
        fig = generate_elevation_and_gradient_plot(provided_gpx, threshold)
        st.plotly_chart(fig)

    st.markdown(
    """
    <a href="https://www.maurten.com/" target="_blank">
        <button style="background-color: black; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border: 2px solid white; border-radius: 5px;">Click here to send the GPX to your Garmin</button>
    </a>
    """,
    unsafe_allow_html=True
)


    st.write("")
    st.write(f"**Elevation Gain:** {round(total_elevation_gain)}m")
    st.write(f"**Elevation Loss:** {round(total_elevation_loss)}m")
    st.write(f"**Minimum Elevation:** {round(min_altitude)}m")
    st.write(f"**Maximum Elevation:** {round(max_altitude)}m")
    st.write("**Course Type:** Fast")
    st.write("**Performance Potential:** High")
    st.write("**Course Impact on Time:** WIP")





































    st.header("Weather")
    st.markdown("<hr style='border:2px solid white'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])



    with col1:
        fig = draw_wind_rose(gpx_path, race_date_start, race_hour_start, status = "live")
        st.pyplot(fig)
        #st.plotly_chart(fig)

    with col2:
        fig = plot_weather_temp_wind(gpx_path, race_date_start, race_hour_start, estimated_finish_time_minutes)
        st.plotly_chart(fig)



    col1, col2 = st.columns([1, 2])



    with col1:
        fig = create_wind_rose(gpx_path, race_date_start, race_hour_start)
        st.plotly_chart(fig)
        #st.plotly_chart(fig)

    with col2:
        fig = plot_weather_rain(gpx_path,race_date_start, race_hour_start, estimated_finish_time_minutes)
        st.plotly_chart(fig)



    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        #jauge de la vitesse du vent
        gauge_type = "Wind Speed"
        result = create_gauge(race_date_start, race_hour_start, gpx_path, gauge_type)
        fig = result[0]
        st.plotly_chart(fig)
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -100px;'>{result[1]}</h3>", unsafe_allow_html=True)   ## unité
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -80px;'>{result[2]}</h3>", unsafe_allow_html=True)   ## message 
    

    with col2:
        #jauge de la temperature
        gauge_type = "Temperature"
        result = create_gauge(race_date_start, race_hour_start, gpx_path, gauge_type)
        fig = result[0]
        time_lost = round(result[3]*estimated_finish_time_minutes,1)
        time_str = f"{int(time_lost):02d}:{int((time_lost - int(time_lost)) * 60):02d}"
        st.plotly_chart(fig)
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -100px;'>{result[1]}</h3>", unsafe_allow_html=True)   ## unité
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -80px;'>{result[2]}</h3>", unsafe_allow_html=True)   ## message 
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -40px;'>Temperature impact:</h3>", unsafe_allow_html=True)   ## time lost
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -30px;'>+{time_str}s</h3>", unsafe_allow_html=True)   ## time lost

    with col3:
        #jauge de l'humidité
        gauge_type = "Humidity"
        result = create_gauge(race_date_start, race_hour_start, gpx_path, gauge_type)
        fig = result[0]
        st.plotly_chart(fig)
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -100px;'>{result[1]}</h3>", unsafe_allow_html=True)   ## unité
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -80px;'>{result[2]}</h3>", unsafe_allow_html=True)   ## message 

    with col4:
        #jauge du risque de pluie
        gauge_type = "Risk of rain"
        result = create_gauge(race_date_start, race_hour_start, gpx_path, gauge_type)
        fig = result[0]
        st.plotly_chart(fig)
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -100px;'>{result[1]}</h3>", unsafe_allow_html=True)   ## unité
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: -80px;'>{result[2]}</h3>", unsafe_allow_html=True)   ## message 





































    st.header("Past results - 2023")
    st.markdown("<hr style='border:2px solid white'>", unsafe_allow_html=True)

    filepath = os.path.join(base_path, "results_race/sorted_Boston_2022.json")   # à changer
    col1, col2 = st.columns([1, 1])



    # Sélectionner les données pour le marathon de Berlin
    berlin_marathon = marathon_data["Berlin Marathon"]
    last_winner = berlin_marathon["last_winner"]

    # Créer deux colonnes pour afficher les informations des vainqueurs
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h3>{last_winner['man_winner']}</h3>
                <img src="data:image/png;base64,{photo_winner_man_base64}" width="200">
                <p>{last_winner['man_time']}</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h3>{last_winner['woman_winner']}</h3>
                <img src="data:image/png;base64,{photo_winner_woman_base64}" width="200">
                <p>{last_winner['woman_time']}</p>
            </div>
            """, unsafe_allow_html=True)
    


    st.write("Compared to last year edition")
    fig_2 = plot_pourcentage_finish(filepath, estimated_finish_time_minutes)
    st.plotly_chart(fig_2[0])
    st.write(f"With a time of {estimated_finish_time} you would have finished last year in the fastest {round(fig_2[1])}%.")



   
    fig_2 = plot_time_distribution(filepath, estimated_finish_time_minutes)
    st.plotly_chart(fig_2)
    st.write("In green your estimated time")




    

    













    st.header("Nutritional Advices")
    st.markdown("<hr style='border:2px solid white'>", unsafe_allow_html=True)







    st.write("")
    st.write("")
    st.write("")
    st.header("Powered by Maurten, Have a great race")

    





