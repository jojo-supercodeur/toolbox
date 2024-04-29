import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# Chemin du fichier JSON
nom_du_fichier = "/Users/josephmestrallet/Downloads/Data for sport/GPX_analysis_insta/Traces_json/Bryan_10k_Malakof.json"

st.write("""
# My first app
Hello *world!*
""")

# Demander un texte à l'utilisateur
user_input = st.text_input("Entrez le lien de votre activité Strava", "")


# Chargement des données
df = pd.read_json(nom_du_fichier)
st.write("Bonjour, ", user_input, "!")

#df = pd.read_json(f"{user_input}/streams")

# Sélection des colonnes nécessaires
df_selectionne = df[['distance', 'heartrate']]



# # Création du graphique avec Matplotlib
# fig, ax = plt.subplots()
# ax.plot(df_selectionne['distance'], df_selectionne['heartrate'])
# ax.set_ylim([120, 190])  # Fixe les limites de l'axe des ordonnées
# ax.set_xlabel('Distance')
# ax.set_ylabel('Heart Rate')
# ax.set_title('Heart Rate vs Distance')

# # Affichage du graphique dans Streamlit
# st.pyplot(fig)



# Création du graphique
#st.line_chart(df_selectionne, y='heartrate', x='distance', use_container_width=True)


# Création du graphique avec Altair
chart = alt.Chart(df_selectionne).mark_line().encode(
    x='distance',
    y=alt.Y('heartrate', scale=alt.Scale(domain=[120, 190]))  # Ici tu peux ajuster les limites de l'axe des ordonnées
).properties(
    width='container'  # Utilise la largeur du conteneur
)

# Affichage du graphique dans Streamlit
st.altair_chart(chart, use_container_width=True)