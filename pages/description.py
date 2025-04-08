import pandas as pd 
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="index", layout="wide", initial_sidebar_state="collapsed")

# Titre principal centré
st.markdown(
    """
    <h1 style="text-align: center;">INDEX</h1>
    """,
    unsafe_allow_html=True
)


description = pd.read_csv('./HomeCredit_columns_description.csv')
description.rename(columns={'Row': 'Name'}, inplace=True)
description.drop(columns=['Table'], inplace=True)
description.reset_index(drop=True, inplace=True)

st.table(description)