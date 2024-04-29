import streamlit as st
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import altair as alt

# Configuration initiale
driver_path = '/Users/josephmestrallet/Downloads/Data for sport/Autres/chromedriver-mac-x64/chromedriver'
service = Service(executable_path=driver_path)

# Éviter le rechargement du navigateur
def setup_driver():
    driver = webdriver.Chrome(service=service)
    return driver

# Fonction de connexion et récupération des données
def get_data(url, email, password):
    driver = setup_driver()
    driver.get('https://www.strava.com/login')
    time.sleep(2)

    # Connexion
    driver.find_element('id', 'email').send_keys(email)
    driver.find_element('id', 'password').send_keys(password)
    driver.find_element('id', 'login-button').click()
    time.sleep(5)

    # Accéder aux données
    driver.get(f"{url}/streams")
    time.sleep(5)
    data = driver.find_element('tag name', 'body').text
    driver.quit()

    # Traiter les données JSON
    return json.loads(data)

# Entrée de l'utilisateur
st.write("# My first app\n*Veuillez attendre 10 secondes*")
url = st.text_input("Entrez le lien de votre activité Strava", "")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

# Bouton pour lancer le processus
if st.button("Récupérer les données"):
    if url and email and password:
        try:
            json_data = get_data(url, email, password)
            # Sauvegarder dans un fichier JSON
            with open('data.json', 'w') as f:
                json.dump(json_data, f, indent=4)

            # Chargement et affichage des données
            df = pd.read_json('data.json')
            df_selectionne = df[['distance', 'heartrate']]

            # Création et affichage du graphique
            chart = alt.Chart(df_selectionne).mark_line().encode(
                x='distance',
                y=alt.Y('heartrate', scale=alt.Scale(domain=[120, 190]))
            ).properties(width='container')
            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Erreur lors de la récupération des données: {e}")
    else:
        st.error("Veuillez remplir tous les champs requis.")
