import streamlit as st
import pandas as pd
import requests
import joblib

# Configuration de la page
st.set_page_config(page_title="Edition Client", layout="wide", initial_sidebar_state="collapsed")

# Chargement du modèle
model_path = "./Model_NoAPI/model_20250214_173950.pkl"
model = joblib.load(model_path)
API_PREDICT = "https://customer-risk-profile-1586eef30b15.herokuapp.com/predict"

# Charger les données
def load_csv_from_dropbox(shared_link):
    """Charge un fichier CSV directement depuis un lien partagé Dropbox."""
    # Convertir le lien partagé en lien direct
    direct_link = shared_link.replace("dl=0", "dl=1")

    # Charger le fichier CSV dans un DataFrame pandas
    df = pd.read_csv(direct_link)
    return df

shared_link = "https://www.dropbox.com/scl/fi/ywb34b2q9dafx9ifkt10q/df_cleaned.csv?rlkey=s3f29j4267ef0h2qv77knula1&st=bfeef662&dl=0"

data = load_csv_from_dropbox(shared_link)


#data = pd.read_csv('./df_cleaned.csv')

# Vérification du client
def get_client_infos(client_id, data):
    client_data = data[data['sk_id_curr'] == client_id]
    if not client_data.empty:
        return client_data
    else:
        return None

# --- UI ---
st.title("✏️ Édition des Informations du Client")

# Saisie de l'ID client
client_id_input = st.text_input("ID du client à éditer")

if client_id_input:
    try:
        client_id_input = int(client_id_input)
        client_data = get_client_infos(client_id_input, data)

        if not client_data.empty:
            client_data_copy = client_data.copy().drop(columns=['target'])

            # Sélection dynamique des colonnes à modifier
            columns_to_edit = st.multiselect("Colonnes à modifier :", client_data_copy.columns)

            for col in columns_to_edit:
                current_val = client_data_copy[col].values[0]
                user_input = st.text_input(f"{col}", value=str(current_val))

                # Conversion automatique
                try:
                    converted = float(user_input)
                    if converted.is_integer():
                        converted = int(converted)
                    client_data_copy.at[client_data_copy.index[0], col] = converted
                except ValueError:
                    client_data_copy.at[client_data_copy.index[0], col] = user_input

            # # Affichage des types de données pour debug
            # with st.expander("🔍 Aperçu des données envoyées à l'API"):
            #     st.json(client_data_copy.to_dict(orient='records')[0])
            #     for k, v in client_data_copy.to_dict(orient='records')[0].items():
            #         st.write(f"{k} : {v} ({type(v).__name__})")

            # Bouton pour recalculer la prédiction
            if st.button("Recalculer la prédiction"):
                client_data_to_send = client_data_copy.to_dict(orient='records')
                
                try:
                    response = requests.post(API_PREDICT, json=client_data_to_send)

                    if response.status_code == 200:
                        prediction_data = response.json().get("predictions", [{}])[0]
                        probability = float(prediction_data.get("probability", 0))
                        prediction = prediction_data.get("prediction", -1)

                        # Affichage du résultat
                        if prediction == 1 and probability < 0.3:
                            st.warning(f"❗️ Client mal classé. Probabilité : {probability:.4f}.")
                        elif prediction == 1:
                            st.error(f"⚠️ Client à risque avec une probabilité de {probability:.4f}.")
                        elif prediction == 0 and probability > 0.3:
                            st.warning(f"❗️ Client à risque mal classé (probabilité : {probability:.4f}).")
                        else:
                            st.success(f"✅ Client non risqué. Probabilité : {probability:.4f}.")

                    else:
                        st.error(f"Erreur lors de la communication avec l'API. Code : {response.status_code}")
                        st.text(response.text)

                except Exception as e:
                    st.error("Une erreur est survenue lors de l'appel à l'API.")
                    st.exception(e)

        else:
            st.error("Client non trouvé. Veuillez vérifier l'ID.")
    except ValueError:
        st.error("Veuillez entrer un ID client valide (entier).")