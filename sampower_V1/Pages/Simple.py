import streamlit as st
import pandas as pd
#import numpy as np
import samplics

from samplics.sampling import SampleSize
from samplics.utils.types import SizeMethod, PopParam
#from st_aggrid import AgGrid
import io



# Vérifier si l'utilisateur a accès à cette page
st.title("Sondage aléatoire simple")
if 'marge' not in st.session_state:
    st.session_state.marge = None
if 'taillePop' not in st.session_state:
    st.session_state.taillePop = None
if 'tauxReponse' not in st.session_state:
    st.session_state.tauxReponse = None
if 'tailleEffet' not in st.session_state:
    st.session_state.tailleEffet = None
if 'parametre' not in st.session_state:
    st.session_state.parametre = None
if 'methode' not in st.session_state:
    st.session_state.methode = None
if 'confiance' not in st.session_state:
    st.session_state.confiance = None
if 'sigma' not in st.session_state:
    st.session_state.sigma = None
if 'prop_est' not in st.session_state:
    st.session_state.prop_est = None
if 'calcul_moy' not in st.session_state:
    st.session_state.calcul = False
if 'calcul_prop' not in st.session_state:
    st.session_state.calcul= False
if 'base_echant_moy' not in st.session_state:
    st.session_state.base_echant = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'population' not in st.session_state:
    st.session_state.population = None
if 'tauxSondage' not in st.session_state:
    st.session_state.tauxSondage = None
#if 'base_telecharger' not in st.session_state:
#    st.session_state.base_telecharger = None


st.info("Les champs avec l'astérisque (*) rouge doivent être obligatoirement remplis")
st.markdown("##### Paramètre à estimer <span style='color:red;'>*</span>", unsafe_allow_html=True)
st.session_state.parametre = st.selectbox('Paramètre à estimer', ['None', 'Proportion', 'Moyenne'], label_visibility='collapsed')
if st.session_state.parametre == 'Proportion' or st.session_state.parametre == 'Moyenne':
    col1, col2,col3 = st.columns(3)

    with col1:
        if st.session_state.parametre == "Moyenne":
            st.markdown("##### Écart-type estimé <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Si vous avez accès à des données provenant d'études antérieures sur la même population ou des populations similaires, vous pouvez utiliser l'écart-type observé dans ces études comme estimation de 𝜎σ.")
            st.session_state.sigma = st.number_input("Marge d'erreur ", min_value = 0, label_visibility='collapsed')

        if st.session_state.parametre == "Proportion":
            st.markdown("##### Proportion estimée <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Si vous disposez d'études similaires précédentes vous pouvez utiliser ces résultats. Sinon la valeur prise par défaut est 0.5")
            st.session_state.prop_est = st.number_input("Proportion estimée", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')

        if st.session_state.parametre == "Proportion":
            st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
            st.session_state.marge = st.number_input("Marge d'erreur", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')
        
        if st.session_state.parametre == "Moyenne":
            st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
            st.session_state.marge = st.number_input("Marge d'erreur moy ", min_value= 0, label_visibility='collapsed')
    
    with col2:
        st.markdown("##### Niveau de confiance <span style='color:red;'>*</span>", unsafe_allow_html=True)
        with st.expander("En savoir plus ..."):
            st.info("Le niveau de confiance représente la probabilité que vous êtes prêt à accepter quant à la possibilité que votre estimation soit incorrecte.")
        st.session_state.confiance = st.number_input("Niveau de confiance",min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')
        
        st.markdown("##### Taille de la population")
        with st.expander("En savoir plus ..."):
            st.info('Taille de la population : Le nombre total d’individus dans la population étudiée. Ce paramètre est utilisé pour calculer la taille de l’échantillon.')
        st.session_state.population = st.number_input("Taille de la population", min_value = 1, value=st.session_state.taillePop, label_visibility='collapsed')

    
    with col3:
        st.markdown("##### Taux de réponse <span style='color:red;'>*</span>", unsafe_allow_html=True)
        with st.expander("En savoir plus ..."):
            st.info("Le taux de réponse est le pourcentage de personnes ayant répondu à un sondage par rapport au nombre total de personnes sollicitées. Assurez-vous d'atteindre ce taux de réponse au risque de ne pas avoir des estimations précises.")
        st.session_state.tauxReponse = st.number_input("Taux de réponse", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')

        st.markdown("##### Effet de plan <span style='color:red;'>*</span>", unsafe_allow_html=True)
        with st.expander("En savoir plus ..."):
            st.info("L'effet de plan est un facteur utilisé dans les enquêtes pour ajuster la taille d'échantillon nécessaire lorsque le plan d'échantillonnage diffère d'un simple échantillonnage aléatoire. Il mesure l'impact du plan d'échantillonnage sur la précision des estimations. Si vous utilisez un plan d'échantillonnage stratifié ou en grappes, par exemple, l'effet de plan prend en compte la corrélation au sein des groupes ou des strates, ce qui peut augmenter la variance des estimations. Un effet de plan supérieur à 1 signifie que la taille de l'échantillon doit être augmentée pour maintenir la même précision. Comme nous sommes dans le cas d'un sondage aléatoire simple, l'effet de plan est de 1")
        st.session_state.tailleEffet =  st.selectbox("Effet de plan",[1], label_visibility='collapsed')




    # Calcul de la taille dans le cas d'une proportion
    if st.session_state.parametre == "Proportion":
        st.session_state.methode = SampleSize(param=PopParam.prop, method=SizeMethod.wald, strat=False)
    if st.session_state.parametre == "Proportion":
        if st.session_state.methode is not None and st.session_state.tailleEffet != 0 and st.session_state.tauxReponse != 0 and st.session_state.taillePop != 0 and st.session_state.marge != 0:
            def calcul_taille():
                st.session_state.methode.calculate(
                    target = st.session_state.prop_est, 
                    half_ci=st.session_state.marge,
                    deff=st.session_state.tailleEffet, 
                    resp_rate=st.session_state.tauxReponse,
                    pop_size = st.session_state.population,
                    alpha = 1 - st.session_state.confiance)
                st.session_state.echantillon = st.session_state.methode.samp_size
            st.session_state.calcul = st.button("Calculer la taille",help="Cliquer pour lancer le calcul de la taille",on_click=calcul_taille)


    # Calcul de la taille dans le cas d'une moyenne
    if st.session_state.parametre == "Moyenne":
        st.session_state.methode = SampleSize(param=PopParam.mean, method=SizeMethod.wald, strat=False)
    if st.session_state.parametre == "Moyenne":
        if st.session_state.methode is not None and st.session_state.tailleEffet != 0 and st.session_state.tauxReponse != 0 and st.session_state.taillePop != 0 and st.session_state.marge != 0:
            def calcul_taille():
                st.session_state.methode.calculate(
                    sigma = st.session_state.sigma,
                    half_ci=st.session_state.marge,
                    deff=st.session_state.tailleEffet, 
                    resp_rate=st.session_state.tauxReponse,
                    pop_size = st.session_state.population,
                    alpha = 1 - st.session_state.confiance)
                st.session_state.echantillon = st.session_state.methode.samp_size
            st.session_state.calcul = st.button("Calculer la taille",help="Cliquer pour lancer le calcul de la taille",on_click=calcul_taille)

    if st.session_state.calcul:
        st.markdown('### Résultats')
        st.write(f"#### **Taille d'échantillon**:", st.session_state.echantillon)
        if st.session_state.population is not None:
            st.session_state.tauxSondage = round(st.session_state.echantillon / st.session_state.population,4)
            st.write("**Taux de sondage**: ",st.session_state.tauxSondage)
        if st.session_state.df is not None:
            with st.expander("Plus d'options"):
                st.write("*Echantillon tiré*",unsafe_allow_html=True)
                st.session_state.base_echant = st.session_state.df.sample(n = st.session_state.echantillon, random_state = 42)
                st.dataframe(st.session_state.base_echant)
            









