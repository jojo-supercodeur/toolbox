import requests
import pandas as pd

# URL pointant vers le fichier JSON
url = "https://www.strava.com/activities/11285831629/streams"

from selenium import webdriver
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

# Spécifie le chemin du pilote de navigateur si nécessaire
path_to_driver = '/Users/josephmestrallet/Downloads/Data for sport/Autres/chromedriver-mac-x64/chromedriver'

# Initialiser le navigateur

service = Service(executable_path=path_to_driver)
driver = webdriver.Chrome(service=service)


# Ouvrir la page
driver.get(url)

time.sleep(2)


# Attendre que la page soit chargée ou attendre un élément spécifique
# Par exemple, driver.implicitly_wait(10) pour attendre 10 secondes
# Ou utiliser WebDriverWait pour attendre un élément spécifique

# Ici, tu peux ajouter des interactions si nécessaire
# Par exemple, cliquer sur un bouton, remplir un formulaire, etc.

# Obtenir les données de la page, tu peux adapter cela selon tes besoins
data = driver.find_element_by_tag_name('body').text

# Convertir les données en JSON (assure-toi que les données sont au format JSON valide)
json_data = json.loads(data)

# Sauvegarder les données dans un fichier JSON
with open('data.json', 'w') as json_file:
    json.dump(json_data, json_file)

# Fermer le navigateur
driver.quit()

print("Les données ont été récupérées et enregistrées.")
