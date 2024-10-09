# Importer les bases necessaires
import streamlit as st
#from Menu import menu
#from Menu import menu_with_redirect
import pandas as pd
#from streamlit_option_menu import option_menu as om
import os
#from st_aggrid import AgGrid

# Configuration de la page d'accueil
st.set_page_config(
    page_title="Acceuil",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state='collapsed'
)

# Création d'un menu des composantes de cette page
#with st.sidebar: 
#    selected = om(
#        menu_title=None,
#        options=['Description', 'Base de données', 'Choix du sondage'],
#        default_index = 0
#    )

if 'acces_sondage_simple' not in st.session_state:
    st.session_state.acces_sondage_simple = False 
if 'acces_sondage_stratifie' not in st.session_state:
    st.session_state.acces_sondage_stratifie = False 
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = None
if 'base' not in st.session_state:
    st.session_state.base = None
if 'taillePop' not in st.session_state:
    st.session_state.taillePop = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'type' not in st.session_state:
    st.session_state.type = None



# Chemin vers le fichier local (manuel d'utilisation)
file_path = "./files/Manuel.docx"

# Ouvrir et lire le fichier en mode binaire
with open(file_path, "rb") as file:
    file_data = file.read()

# Bouton de téléchargement pour le fichier local
st.download_button(
    label="Télécharger le manuel d'utilisation",
    data=file_data,
    file_name="Manuel d'utilisation de SamPower.docx",  # Le nom sous lequel le fichier sera téléchargé
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

choix = ['Simple', 'Stratifie']

def Validation():

    st.markdown("<h1 style='color:#2fd5cf; text-align: center;'>BIENVENUE SUR SamPower </h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2,gap="medium")
    
    with col1:
        base = st.radio("Disposez-vous d'une base de sondage ?", ["Non", "Oui"],horizontal = True, index = None)
        if base == "Oui":
            with st.expander("Cliquer ici pour choisir une base",icon=":material/database:"):
                st.markdown('### Sélectionner la base de sondage')
                st.info("Veuillez télécharger un fichier .dta ou .xlsx ou .csv.")
                st.session_state.uploaded = st.file_uploader('Choix de la base de sondage', type=["csv", "xlsx", "dta"], label_visibility='collapsed')

                if st.button("Charger la base par défaut"):
                    st.session_state.clear()
                    st.session_state.uploaded = "./files/base_ehcvm2.dta"
                    st.session_state.df = pd.read_stata(st.session_state.uploaded)
                    # Afficher un message de confirmation
                    st.success("Base de données chargée avec succès !")
                    # Afficher le DataFrame avec Streamlit
                    st.session_state.taillePop = len(st.session_state.df)

                else:
                    # Vérifier si un fichier a été téléchargé
                    if st.session_state.uploaded is not None:
                        # Lire la base de données Stata avec pandas
                        if st.session_state.uploaded.name.endswith('.csv'):
                            st.session_state.df = pd.read_csv(st.session_state.uploaded, sep = ';')
                        elif st.session_state.uploaded.name.endswith('.xlsx'):
                            st.session_state.df = pd.read_excel(st.session_state.uploaded)
                        elif st.session_state.uploaded.name.endswith('.dta'):
                            st.session_state.df = pd.read_stata(st.session_state.uploaded)
                            
                        # Afficher un message de confirmation
                        st.success("Base de données chargée avec succès !")
                    
                        # Afficher le DataFrame avec Streamlit
                        st.session_state.taillePop = len(st.session_state.df)

                    #else:
                    #    st.info("Veuillez télécharger un fichier .dta ou .xlsx ou .csv.")
    with col2:
        type = st.radio('Plan de sondage', choix,horizontal = True,index=None)
        if st.button("Valider"):
            st.session_state.type = type
            st.rerun()

def Revenir():
    st.session_state.type = None
    st.rerun()

type = st.session_state.type

#base_page = st.Page("Pages/Base.py",title="Base de sondage", icon=":material/database:")
deconnexion_page = st.Page(Revenir, title="Retour a l'accueil", icon=":material/logout:")
simple_page = st.Page("Pages/Simple.py",title="Paramètres",default=(type == 'Simple'),icon=":material/settings:")
resultat_page = st.Page("Pages/Resultat.py", title="Résultats",icon=":material/check_circle:")
stratifie_page = st.Page("Pages/Stratifie.py", title= 'Paramètres', default=(type == "Stratifie"))

compte = [deconnexion_page]
page_simple = [simple_page, resultat_page]
page_stratifie = [stratifie_page, resultat_page]

page_dict = {}

if st.session_state.type == "Simple":
    page_dict["Sondage aléatoire simple"] = page_simple
if st.session_state.type == "Stratifie":
    page_dict["Sondage stratife"] = page_stratifie

if len(page_dict) > 0:
    pg = st.navigation({"Accueil" : compte} | page_dict)
else:
    pg = st.navigation([st.Page(Validation)])

pg.run()

















#st.error('This is an error', icon="🚨")
















