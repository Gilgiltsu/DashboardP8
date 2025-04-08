import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Scoring Crédit",
    layout="wide",
    initial_sidebar_state="collapsed"  # Cela masque le menu latéral
)

# Image de présentation centrée et réduite
col1, col2, col3 = st.columns([1, 2, 1])


with col1:
    st.write("")  # Espace vide pour centrer

with col2:
    st.image("./Images//Pret_a_depenser.png", use_container_width = False)
    
with col3:
    st.write("")  # Espace vide pour centrer



# Titre principal centré
st.markdown(
    """
    <h1 style="text-align: center;">Dashboard Scoring Crédit</h1>
    """,
    unsafe_allow_html=True
)

# Description
st.markdown("""
Le Dashboard Scoring Crédit est un outil conçu pour évaluer la probabilité de remboursement d'un crédit par un client.
Il permet de classifier les demandes de crédit en accordé ou refusé, en se basant sur un score de crédit calculé.

Cet outil a été développé pour répondre à une demande croissante de transparence de la part des clients concernant les décisions d'octroi de crédit.
Il permet aux chargés de relation client de Prêt à Dépenser d'expliquer de manière claire et transparente les décisions prises,
lors des rendez-vous avec les clients. Cette transparence est en ligne avec les valeurs fondamentales de l'entreprise.
""")

# Espace entre la description et les boutons
st.write("\n\n")

# Boutons d'action centrés
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.write("")  # Espace vide pour centrer

with col2:
    if st.button("Analyser les clients existants", use_container_width=True):
        st.switch_page("pages/analyse.py")
    if st.button("Lancer une nouvelle analyse client", use_container_width=True):
        st.switch_page("pages/new_customer.py")

with col3:
    st.write("")  # Espace vide pour centrer

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
