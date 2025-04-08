import streamlit as st
import pandas as pd
import random
import requests
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import joblib 

shap.initjs()


API_PREDICT = "https://customer-risk-profile-1586eef30b15.herokuapp.com/predict"

# Liste des noms de fichiers
filenames = [f"df_cleaned_part{i+1}.csv" for i in range(6)]

# Lire et concaténer tous les fichiers
data = pd.concat([pd.read_csv(file) for file in filenames], ignore_index=True)

# Configuration de la page
st.set_page_config(page_title="Analyse Client", layout="wide", initial_sidebar_state="collapsed")

# Titre principal centré
st.markdown(
    """
    <h1 style="text-align: center;">Analyse Client</h1>
    """,
    unsafe_allow_html=True
)

def get_client_infos(current_client_id, data):
    for column in data.columns:
        if 'days' in column:
            data[column] = data[column].abs()
            data[column] = (data[column] / 365.25).astype(int)

    client_data = data[data['sk_id_curr'] == current_client_id]
    if not client_data.empty:
        age_client = client_data['days_birth'].values[0]
        income_client = round(client_data['amt_income_total'].values[0])
        tenure_client = client_data['days_employed'].values[0]
        goodprice_client = round(client_data['amt_goods_price'].values[0])
        rate_client = round(client_data['payment_rate'].values[0] * 100)

        # Déterminer le statut en fonction de la colonne 'target'
        target_value = client_data['target'].values[0]
        status = "🔴" if target_value == 1 else "🟢"

        client_info_table = pd.DataFrame({
            'Données': [age_client, income_client, tenure_client, goodprice_client, rate_client, status]
        }, index=['Âge (ans)', 'Revenus totaux', 'Ancienneté (ans)', 'Prix du bien', 'Taux de remboursement (%)', 'Statut'])

        return client_info_table

# Charger le modèle
model_path = "./Model_NoAPI/model_20250214_173950.pkl"
model = joblib.load(model_path)

# Initialisation de la session state
if 'client_id_input' not in st.session_state:
    st.session_state.client_id_input = ""
if "client_info" not in st.session_state:
    st.session_state.client_info = ""

# Client ID input
st.subheader("Entrez l'ID du client")
col1, col2 = st.columns([3, 1])
with col1:
    client_id_input = st.text_input("", label_visibility="collapsed", key="client_id_input_field")

with col2:
    if st.button("Entrer", key="enter_button_unique", use_container_width=True):
        try:
            client_id = int(client_id_input)
            if client_id in data['sk_id_curr'].values:
                st.session_state.client_id_input = client_id
                st.session_state.client_info = get_client_infos(client_id, data)
                st.session_state.response_message = f"Analyse terminée pour le client avec l'ID {client_id}."
                client_data = data[data['sk_id_curr'] == client_id]
                client_data = client_data.drop(columns=['target'])
                client_data = client_data.to_dict(orient='records')
                st.session_state.client_data = client_data
                response = requests.post(API_PREDICT, json=client_data)
                prediction_data = response.json().get("predictions", [{}])[0]
                # Afficher la réponse de l'API
                probability = float(prediction_data.get("probability", 0))
                prediction = prediction_data.get("prediction", -1)
                if prediction == 1 and probability < 0.3:
                    st.session_state.response_test_message = (
                    f"<span style='color: orange;'>Le client avec l'ID {client_id} a été mal classé. Il ne s'agit pas d'un client à risque (probabilité : {probability:.4f})</span>"
                    )
                elif prediction == 1:
                    st.session_state.response_test_message = (
                    f"<span style='color: red;'>Le client avec l'ID {client_id} est un client à risque avec une probabilité de {probability:.4f}</span>"
                    )
                elif prediction == 0 and probability > 0.3:
                    st.session_state.response_test_message = (
                    f"<span style='color: red;'>Le client avec l'ID {client_id} a été mal classé. Il s'agit d'un client à risque (probabilité : {probability:.4f})</span>"
                    )
                else:
                    st.session_state.response_test_message = (
                    f"<span style='color: green;'>Le client avec l'ID {client_id} n'est pas un client à risque avec une probabilité de {probability:.4f}</span>"
                )
            else:
                st.session_state.response_message = "ID client invalide. Veuillez entrer un ID valide."
        except ValueError:
            st.session_state.response_message = "Veuillez entrer un nombre entier valide pour l'ID du client."

# Boutons pour sélectionner aléatoirement un client
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.write("")  # Espace vide pour centrer

with col2:
    left, right = st.columns(2)

    if left.button("Sélectionner un client aléatoire", key="random_client_button_unique", use_container_width=True):
        client_ids = data['sk_id_curr'].dropna().tolist()
        if client_ids:  # On vérifie qu'il y a bien des valeurs
            random_client_id = random.choice(client_ids)
            st.session_state.response_id = f"ID client : {random_client_id}"
        else:
            st.warning("Aucun client disponible pour la sélection aléatoire.")

    if right.button("Sélectionner un client refusé aléatoire", key="random_refused_client_button_unique", use_container_width=True):
        refused_clients = data[data['target'] == 1]['sk_id_curr'].dropna().tolist()
        if refused_clients:
            random_refused_client_id = random.choice(refused_clients)
            st.session_state.response_id = f"ID client : {random_refused_client_id}"
        else:
            st.warning("Aucun client refusé trouvé.")

with col3:
    if  'response_id' not in st.session_state:
        st.write("")
    else:
        st.write(f"<div style='text-align:center;'> {st.session_state.response_id} </div>", unsafe_allow_html=True)

# Display response message
if 'response_message' in st.session_state:
    st.write(f"<div style='text-align:center;'> {st.session_state.response_message} </div>", unsafe_allow_html=True)
    st.header(f"Informations du Client {st.session_state.client_id_input}")
    st.table(st.session_state.client_info)
    # Bouton pour éditer le client
    if st.button("Éditer le client", key="edit_client_button_unique"):
        # Redirection vers la page d'édition du client
        st.write(f'<a href="/edit_client?client_id={st.session_state.client_id_input}" target="_blank">Cliquez ici pour modifier le client {st.session_state.client_id_input}</a>', unsafe_allow_html=True)


if "response_test_message" in st.session_state:
    st.write(f"<div style='text-align:center;'> {st.session_state.response_test_message} </div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        left, right = st.columns(2) 
        # Affiche le bouton uniquement si le message est présent
        if left.button("Comparer avec les clients acceptés"):
            # Séparer les données du client et des clients acceptés
            client_data = data[data['sk_id_curr'] == st.session_state.client_id_input]
            client_data = client_data.fillna(0).drop(columns='target')
            data = data[data['target'] == 0]
            data = data.groupby('target', as_index=False).apply(lambda s: s.sample(
                    10000, random_state=0)).fillna(0).drop(columns='target')

            # Calcul des valeurs SHAP
            explainer = shap.Explainer(model)

            # SHAP sur client_data (1 seul individu)
            shap_values_client = explainer(client_data)
            shap_vals_client = shap_values_client.values[0]

            # SHAP sur tout data
            shap_values_data = explainer(data)
            shap_vals_data = shap_values_data.values.mean(axis=0)

            # Get feature names
            feature_names = shap_values_client.feature_names

            # DataFrame pour comparer
            df = pd.DataFrame({
                'Feature': feature_names,
                'Client': shap_vals_client,
                'Accepted Mean': shap_vals_data
            })

            # Garder les 10 features les plus importantes
            df['Accepted_Mean_abs'] = np.abs(df['Accepted Mean'])
            top_features = df.nlargest(10, 'Accepted_Mean_abs')

            # Plot
            x = np.arange(len(top_features))  # positions
            width = 0.35

            fig, ax = plt.subplots(figsize=(10, 6))
            bars1 = ax.bar(x - width/2, top_features['Client'], width, color="red", label='Client')
            bars2 = ax.bar(x + width/2, top_features['Accepted Mean'], width, color='green', label='Accepted Mean')

            ax.set_xticks(x)
            ax.set_xticklabels(top_features['Feature'], rotation=45, ha='right')
            ax.set_ylabel("SHAP Value")
            ax.set_title("Comparaison des SHAP values (Client vs Moyenne Acceptés)")
            ax.legend()

            plt.tight_layout()
            st.pyplot(fig)
            st.page_link("pages/description.py", label="info et description", icon="ℹ️")

        if right.button("Quelles informations impacte le résultat ? "):
            # Séparer les données du client
            client_data = data[data['sk_id_curr'] == st.session_state.client_id_input]
            client_data = client_data.fillna(0).drop(columns='target')

            # Calcul des valeurs SHAP
            explainer = shap.Explainer(model)
            shap_values_client = explainer(client_data)[0]

            # Récupérer les SHAP values et noms de features
            shap_values_array = shap_values_client.values
            feature_names = shap_values_client.feature_names
            feature_values = client_data.values[0]

            # Créer un DataFrame pour faciliter le tri
            df_shap = pd.DataFrame({
                'Feature': feature_names,
                'SHAP Value': shap_values_array,
                'Feature Value': feature_values
            })

            # Garder les 10 features les plus importantes en valeur absolue
            top_df = df_shap.reindex(df_shap['SHAP Value'].abs().sort_values(ascending=False).index).head(10)

            # Couleur selon le signe de la valeur SHAP
            colors = top_df['SHAP Value'].apply(lambda x: 'red' if x > 0 else 'green')

            # Tracer le barplot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(top_df['Feature'], top_df['SHAP Value'], color=colors)
            ax.set_xlabel("SHAP Value")
            ax.set_title("Top 10 features influençant la décision")
            ax.axvline(0, color='black', linewidth=0.8)  # ligne verticale au milieu
            plt.tight_layout()
            st.pyplot(fig)
            st.page_link("pages/description.py", label="Info et description", icon="ℹ️")

        


# Footer
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    text-align: center;
    padding: 10px;
}
</style>
<div class="footer">
    Pour toute question ou suggestion concernant l'utilisation de ce dashboard, veuillez contacter le support.
</div>
""", unsafe_allow_html=True)
