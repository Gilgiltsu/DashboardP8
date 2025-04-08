import streamlit as st
import pandas as pd
import numpy as np
import requests

# Configuration pour cacher la sidebar
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.title("Analyse de Nouveaux Clients")
API_PREDICT = "https://customer-risk-profile-1586eef30b15.herokuapp.com/predict"

# === Fonction pour charger les colonnes importantes depuis le fichier .txt ===
def get_important_columns(file_path):
    with open(file_path, 'r') as f:
        important_columns = f.read().splitlines()  # Chaque ligne est une colonne
    # Assurer que les noms sont en minuscules et sans espaces
    important_columns = [col.strip().lower().replace(' ', '_') for col in important_columns]
    return important_columns

# === Interface Utilisateur ===
uploaded_file = st.file_uploader("Charger un fichier CSV pour de nouveaux clients", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)

    # Si le fichier contient plus de 10 lignes, proposer un choix à l'utilisateur
    if raw_df.shape[0] > 10:
        st.subheader("Choisissez comment limiter les données à 10 lignes :")
        
        # Boutons pour choix manuel ou aléatoire
        if st.button("Choisir les 10 premières lignes"):
            raw_df = raw_df.head(10)
        
        elif st.button("Choisir 10 lignes aléatoires"):
            raw_df = raw_df.sample(n=10, random_state=42)

    st.subheader("✅ Données brutes (limitées à 10 lignes)")
    st.dataframe(raw_df)

    # Si l'utilisateur souhaite envoyer les données à l'API
    if st.button("🚀 Envoyer les données à l'API"):
        try:
            # Conversion du DataFrame en JSON
            json_data = raw_df.to_dict(orient="records")
            # Envoi de la requête à l'API
            response = requests.post(API_PREDICT, json=json_data)
            if response.status_code == 200:
                    results = response.json().get("predictions", [])
                    results_df = pd.DataFrame(results)
                    st.success("✅ Prédictions reçues avec succès !")
                    st.dataframe(results_df)
            else:
                st.error(f"Erreur lors de la prédiction: {response.status_code}")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")