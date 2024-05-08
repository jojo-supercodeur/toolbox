import streamlit as st
import datetime
import streamlit.components.v1 as components




def calculate_performance_loss(base_time, temperature):
    # Conversion du temps en minutes
    total_minutes = base_time.hour * 60 + base_time.minute + base_time.second / 60.0
    
    # Calcul de la perte de performance pour températures élevées
    if temperature > 13:
        loss_percentage = (temperature - 13) * 0.15
    # Ajout d'un calcul hypothétique pour les basses températures
    elif temperature < 12:
        loss_percentage = (12 - temperature) * 0.10  # Hypothèse: 0.10% par degré sous 12°C
    else:
        loss_percentage = 0
    
    time_loss_minutes = total_minutes * (loss_percentage / 100)
    # Convertir le temps perdu en minutes et secondes entières
    loss_minutes = int(time_loss_minutes)
    loss_seconds = int((time_loss_minutes - loss_minutes) * 60)
    
    return loss_minutes, loss_seconds, total_minutes + time_loss_minutes

def calculate_performance_loss_flouris(base_time, temperature):
    total_minutes = base_time.hour * 60 + base_time.minute + base_time.second / 60.0
    loss_percentage= 1,2095136-0.22334*temperature+0.01031*temperature*temperature
    time_loss_minutes = total_minutes * (loss_percentage / 100)


    loss_minutes = int(time_loss_minutes)
    loss_seconds = int((time_loss_minutes - loss_minutes) * 60)
    
    return loss_minutes, loss_seconds, total_minutes + time_loss_minutes
    


def get_weather_emoji(temperature):
    if temperature <= 0:
        return "❄️"
    elif temperature <= 13:
        return "🌤"
    elif temperature <= 25:
        return "☀️"
    else:
        return "🔥"
    











st.image("logo_enduraw.png", width=100)  # Modifie "path_to_logo.png" par le chemin vers ton fichier image ou URL, et ajuste la largeur selon tes besoins.





# Interface utilisateur
st.title("Heat impact on the performance")


st.write("")
st.markdown("The calculation are from this [scientific paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8677617/)")


st.write("")
st.write("")
st.write("Enter your expected race time and the temperature")






# Création de trois colonnes pour les heures, les minutes, et les secondes
col1, col2, col3 = st.columns(3)

# Utilisation de chaque colonne pour un champ spécifique
with col1:hours = st.number_input("Hours", min_value=0, max_value=23, value=0, step=1)

with col2:minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=1)

with col3: seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)



# Saisie de la température

temperature = st.slider("Temperature (°C)", min_value=-20, max_value=40, value=13)

# Conversion du temps de course en objet datetime.time
base_time = datetime.time(hour=hours, minute=minutes, second=seconds)

if st.button("Preview weather impact"):
    loss_minutes, loss_seconds, total_time = calculate_performance_loss_flouris(base_time, temperature)
    emoji = get_weather_emoji(temperature)
    # Formatage du temps total en heures, minutes et secondes
    total_hours = int(total_time // 60)
    total_minutes = int(total_time % 60)
    total_seconds = int((total_time * 60) % 60)
    if temperature > 13:
        st.write(f"Time lost due to heat: {loss_minutes}m{loss_seconds:02d}s")
    elif temperature < 12:
        st.write(f"Time lost due to cold: {loss_minutes}m{loss_seconds:02d}s")
    else : 
        st.write(f"Perfect temperature")


    
    st.write(f"Total race time : {total_hours}h{total_minutes}m{total_seconds}s")
    st.write(f"Weather conditions : {emoji}")






st.write("")
st.write("")

st.markdown("Do you want this tool directly integrated to Strava ? [Check our integration](https://www.joseph-mestrallet.com/strava-integration)")

