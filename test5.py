import streamlit as st
import streamlit.components.v1 as components  # Importer le module components

# Fonction pour charger et afficher le fichier HTML de la carte
def load_html_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

# Définir la page Streamlit
st.title("Briefing Marathon")

# Collecter les données de l'utilisateur
name = st.text_input("Runner name", "")
weight = st.slider("Weight (in kg)", min_value=45, max_value=130, value=70)
age = st.slider("Age", min_value=18, max_value=100, value=30)
course = st.selectbox("Choose the race", ["Boston Marathon", "London Marathon","Ecotrail"])

# Affichage du bouton pour soumettre
if st.button("Show the course and informations"):
    if not name:
        st.error("Please enter the runner's name.")
    else:
        # Déterminer le fichier HTML à charger en fonction de la course
        if course == "London Marathon":
            html_file = 'map_London Marathon.html'
            length = "42,195 km"
            logo_path = "London Marathon.png"

        elif course == "Boston Marathon":
            html_file = 'map_Boston Marathon.html'
            length = "42,195 km"
            logo_path = "Boston Marathon.png"
        elif course == "Ecotrail":
            html_file = "map_Ecotrail.html"
            length = "78 km"
            logo_path = "Ecotrail.png"

        

        st.image(logo_path, width=100)  # Modifie "path_to_logo.png" par le chemin vers ton fichier image ou URL, et ajuste la largeur selon tes besoins.

    

        # Charger et afficher la carte
        html_content = load_html_map(html_file)
        components.html(html_content, height=600)  # Utiliser components.html pour intégrer la carte

        # Afficher un message d'encouragement
        st.success(f"Good luck {name}, the length will be {length}!")

