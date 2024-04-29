from selenium import webdriver
import time
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt




st.write("""
# My first app
*Veuillez attendre 10 secondes*
""")

# Demander un texte à l'utilisateur
user_input = st.text_input("Entrez le lien de votre activité Strava", "")


# Spécifie le chemin vers ton pilote de navigateur
driver_path = '/Users/josephmestrallet/Downloads/Data for sport/Autres/chromedriver-mac-x64/chromedriver'

# URL de connexion
login_url = 'https://www.strava.com/login'
#data_url = 'https://www.strava.com/activities/11285831629/streams'
data_url = f"{user_input}/streams"

# Démarrer le navigateur
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

driver.get(login_url)


# Attendre que la page charge
time.sleep(2)  # Augmente si nécessaire

# Entrer l'adresse email
#email_input = driver.find_element_by_id('email')  # Assure-toi que l'id est correct

email_input = driver.find_element('id', 'email')  # Assure-toi que l'id est correct

email_input.send_keys('pierre06.mestrallet@gmail.com')

# Entrer le mot de passe
password_input = driver.find_element("id","password")  # Assure-toi que l'id est correct
password_input.send_keys('Antoine1')

# Soumettre le formulaire de connexion
login_button = driver.find_element("id",'login-button')  # Assure-toi que l'id est correct
login_button.click()

# Attendre que la connexion soit réussie et que la page suivante charge
time.sleep(5)  # Augmente si nécessaire

# Naviguer vers l'URL où se trouvent les données après connexion
driver.get(data_url)

# Attendre que les données chargent
time.sleep(5)  # Augmente si nécessaire

# Extraire les données
# Supposons que les données JSON sont directement dans le body ou dans un script
data_element = driver.find_element('tag name', 'body')  # Ou adapte selon où se trouve exactement le JSON
data = data_element.text  # Récupérer le texte, qui est le JSON brut

# Convertir le texte en JSON
try:
    json_data = json.loads(data)  # Charger le texte en tant qu'objet JSON

    # Sauvegarder les données dans un fichier JSON
    with open('data.json', 'w') as file:
        json.dump(json_data, file, indent=4)  # Enregistre avec une mise en forme

    print("Les données ont été récupérées et enregistrées.")
except json.JSONDecodeError:
    print("Erreur de décodage JSON : vérifiez que les données récupérées sont du JSON valide.")

# Fermer le navigateur
driver.quit()

nom_du_fichier = "data.json"


df = pd.read_json(nom_du_fichier)
df_selectionne = df[['distance', 'heartrate']]


# Création du graphique avec Altair
chart = alt.Chart(df_selectionne).mark_line().encode(
    x='distance',
    y=alt.Y('heartrate', scale=alt.Scale(domain=[120, 190]))  # Ici tu peux ajuster les limites de l'axe des ordonnées
).properties(
    width='container'  # Utilise la largeur du conteneur
)

# Affichage du graphique dans Streamlit
st.altair_chart(chart, use_container_width=True)