import streamlit as st
import pandas as pd
#import numpy as np
import io
import samplics


from samplics.sampling import SampleSize
from samplics.utils.types import SizeMethod, PopParam
#from st_aggrid import AgGrid
#from st_aggrid.grid_options_builder import GridOptionsBuilder



# Vérifier si l'utilisateur a accès à cette page
st.title("Sondage stratifié")
if 'marge_strat' not in st.session_state:
    st.session_state.marge_strat = None
if 'taillePop' not in st.session_state:
    st.session_state.taillePop = None
if 'tauxReponse_strat' not in st.session_state:
    st.session_state.tauxReponse_strat = None
if 'tailleEffet_strat' not in st.session_state:
    st.session_state.tailleEffet_strat = None
if 'parametre_strat' not in st.session_state:
    st.session_state.parametre_strat = None
if 'methode_strat' not in st.session_state:
    st.session_state.methode_strat = None
if 'confiance_strat' not in st.session_state:
    st.session_state.confiance_strat = None
if 'sigma_strat' not in st.session_state:
    st.session_state.sigma_strat = None
if 'prop_est_strat' not in st.session_state:
    st.session_state.prop_est_strat = None
if 'calcul_strat' not in st.session_state:
    st.session_state.calcul_strat = False
if 'echantillon_strat' not in st.session_state:
    st.session_state.echantillon_strat = None
if 'base_echant_strat' not in st.session_state:
    st.session_state.base_echant_strat = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'population_strat' not in st.session_state:
    st.session_state.population_strat = None
if 'variable_strat' not in st.session_state:
    st.session_state.variable_strat = None
if 'type_alloc' not in st.session_state:
    st.session_state.type_alloc = None
if 'modality_count' not in st.session_state:
    st.session_state.modality_count = None
if 'resultat' not in st.session_state:
    st.session_state.resultat = None
if 'tauxSondage_strat' not in st.session_state:
    st.session_state.tauxSondage_strat = None
if 'tot_taille' not in st.session_state:
    st.session_state.tot_taille = None
if 'nombre_tot' not in st.session_state:
    st.session_state.nombre_tot = None
if 'df_vide' not in st.session_state:
    st.session_state.df_vide = None
    


st.info("Les champs avec l'astérisque (*) rouge doivent être obligatoirement remplis")
st.markdown("##### Paramètre à estimer <span style='color:red;'>*</span>", unsafe_allow_html=True)
st.session_state.parametre_strat = st.selectbox('Paramètre à estimer', [None, 'Proportion', 'Moyenne'], label_visibility='collapsed')

cola, colb = st.columns(2)
with cola:
    st.markdown("##### Type de sondage stratifié <span style='color:red;'>*</span>", unsafe_allow_html=True)
    st.session_state.type_alloc = st.radio("Veuillez choisir le type de sondage stratifié souhaité", options = [None, 'Allocation proportionnelle', 'Calcul par strate'], label_visibility='collapsed')

if st.session_state.parametre_strat is not None and st.session_state.type_alloc is not None:
    
    with colb:
        if st.session_state.df is None:
            var = st.text_input("Quelle est la variable de stratification ?")
            n= int(st.number_input(f"Nombre de modalités (strates) dans {var} ?"))
            noms_colonnes = ["strate", "Taille"]
            # Créer un dataframe vide
            st.session_state.df_vide = pd.DataFrame([[None] * 2 for _ in range(n)], columns=noms_colonnes)

        if st.session_state.df is not None:
            # Filtrer les variables catégorielles (type 'object' ou avec moins de 6 valeurs uniques)
            variable_categ = [col for col in st.session_state.df.columns if st.session_state.df[col].dtype == 'object' or st.session_state.df[col].nunique() < 6]
            st.markdown("##### Variable de stratification (catégorielle) <span style='color:red;'>*</span>", unsafe_allow_html=True)
            # Vérifier s'il y a des variables catégorielles
            if len(variable_categ) > 0:
                st.session_state.variable_strat = st.selectbox('**Choisissez la variable de stratification (catégorielle)**', variable_categ, label_visibility='collapsed')
                if st.session_state.variable_strat is not None:
                    st.session_state.modality_count = pd.DataFrame(st.session_state.df[st.session_state.variable_strat].value_counts().reset_index())
                    st.session_state.modality_count.columns = [st.session_state.variable_strat, 'Taille']
                    # Afficher le tableau de données si il s'agit d'une allocation proportionnelle
                    #if st.session_state.type_alloc == 'Allocation proportionnelle':
                    #    st.dataframe(st.session_state.modality_count)

    if st.session_state.df is None:
        if st.session_state.type_alloc == "Allocation proportionnelle":
            st.write(f"Veuillez remplir les modalités de la variable {var} dans strates et donner la population dans chaque strate :")
            st.session_state.modality_count = st.data_editor(st.session_state.df_vide)
            st.session_state.modality_count['Taille'] = pd.to_numeric(st.session_state.modality_count['Taille'], errors='coerce')
            # Calculer la taille totale de la population pour l'allocation proportionnelle plus tard
            st.session_state.nombre_tot = st.session_state.modality_count['Taille'].sum()



    if st.session_state.type_alloc == 'Calcul par strate':
        if st.session_state.df is None:
            st.session_state.df_vide['Effet de plan'] = 0.0
            if st.session_state.parametre_strat == "Proportion":
                st.session_state.df_vide['Proportion estimée'] = 0.0
            if st.session_state.parametre_strat == "Moyenne":
                st.session_state.df_vide['Ecart-type estimé'] = 0.0
        elif st.session_state.df is not None:
            st.session_state.modality_count['Effet de plan'] = 0.0
            if st.session_state.parametre_strat == "Proportion":
                st.session_state.modality_count['Proportion estimée'] = 0.0
            if st.session_state.parametre_strat == "Moyenne":
                st.session_state.modality_count['Ecart-type estimé'] = 0.0


        st.write("**Remplissez les données manquantes du tableau**  <span style='color:red;'>*</span>", unsafe_allow_html=True)
        with st.expander("En savoir plus ..."):
            st.info("Si vous disposez d'études similaires précédentes vous pouvez utiliser ces résultats pour la proportion estimée. Sinon la valeur prise par défaut est 0.5.")
            st.info("\nL'effet de plan est un facteur utilisé dans les enquêtes pour ajuster la taille d'échantillon nécessaire lorsque le plan d'échantillonnage diffère d'un simple échantillonnage aléatoire. Il mesure l'impact du plan d'échantillonnage sur la précision des estimations. Si vous utilisez un plan d'échantillonnage stratifié ou en grappes, par exemple, l'effet de plan prend en compte la corrélation au sein des groupes ou des strates, ce qui peut augmenter la variance des estimations. Un effet de plan supérieur à 1 signifie que la taille de l'échantillon doit être augmentée pour maintenir la même précision. Comme nous sommes dans le cas d'un sondage aléatoire simple, l'effet de plan est de 1")
            st.info(" \n La valeur par défaut de la taille est le nombre d'individus par strate de la base. ")
        if st.session_state.df is None:
            st.session_state.modality_count = st.data_editor(st.session_state.df_vide)
            st.session_state.modality_count['Taille'] = pd.to_numeric(st.session_state.modality_count['Taille'], errors='coerce')
        elif st.session_state.df is not None:
            st.session_state.modality_count = st.data_editor(st.session_state.modality_count)
            
        # Calculer la taille totale de la population pour le calcul par strate
        st.session_state.nombre_tot = st.session_state.modality_count['Taille'].sum()
        
        # Récupération des valeurs du tableau pour les calculs
        if st.session_state.parametre_strat == "Moyenne":
            if st.session_state.df is not None:
                st.session_state.sigma_strat = st.session_state.modality_count[[st.session_state.variable_strat, 'Ecart-type estimé']].to_dict()
            elif st.session_state.df is None:
                st.session_state.sigma_strat = st.session_state.modality_count[['strate', 'Ecart-type estimé']].to_dict()
            st.session_state.sigma_strat_nombre = st.session_state.sigma_strat['Ecart-type estimé']

        #Extraction de la taille de la population pour chaque strate
        if st.session_state.df is not None:
            st.session_state.population_strat = st.session_state.modality_count[[st.session_state.variable_strat, 'Taille']].to_dict()
        elif st.session_state.df is  None:
            st.session_state.population_strat = st.session_state.modality_count[['strate', 'Taille']].to_dict()
        st.session_state.population_strat_nombre = st.session_state.population_strat['Taille']
        
        #Extraction de l'effet de plan pour chaque strate
        if st.session_state.df is not None:
            st.session_state.tailleEffet_strat = st.session_state.modality_count[[st.session_state.variable_strat, 'Effet de plan']].to_dict()
        elif st.session_state.df is None:
            st.session_state.tailleEffet_strat = st.session_state.modality_count[['strate', 'Effet de plan']].to_dict()
        st.session_state.tailleEffet_strat_nombre = st.session_state.tailleEffet_strat['Effet de plan']
        if st.session_state.df is not None:
            st.session_state.tailleEffet_strat_label = st.session_state.tailleEffet_strat[st.session_state.variable_strat]
        elif st.session_state.df is None:
            st.session_state.tailleEffet_strat_label = st.session_state.tailleEffet_strat['strate']

        if st.session_state.parametre_strat == "Proportion":
            if st.session_state.df is not None:
                st.session_state.prop_est_strat = st.session_state.modality_count[[st.session_state.variable_strat, 'Proportion estimée']].to_dict()
            elif st.session_state.df is None:
                st.session_state.prop_est_strat = st.session_state.modality_count[['strate', 'Proportion estimée']].to_dict()
            st.session_state.prop_est_strat_nombre = st.session_state.prop_est_strat['Proportion estimée']

        colc, cold, cole = st.columns(3)
        with colc:
            if st.session_state.parametre_strat == "Proportion":
                st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
                st.session_state.marge_strat = st.number_input("Marge d'erreur",min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')


            if st.session_state.parametre_strat == "Moyenne":
                st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
                st.session_state.marge_strat = st.number_input("Marge d'erreur moyenne ", min_value= 0, label_visibility='collapsed')

        with cold:
            st.markdown("##### Niveau de confiance <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Le niveau de confiance représente la probabilité que vous êtes prêt à accepter quant à la possibilité que votre estimation soit incorrecte.")
            st.session_state.confiance_strat = st.number_input("Niveau de confiance", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", label_visibility='collapsed')

        with cole:
            st.markdown("##### Taux de réponse <span style='color:red;'>*</span> ", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Le taux de réponse est le pourcentage de personnes ayant répondu à un sondage par rapport au nombre total de personnes sollicitées. Assurez-vous d'atteindre ce taux de réponse au risque de ne pas avoir des estimations précises.")
            st.session_state.tauxReponse_strat = st.number_input("Taux de réponse", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", value=0.90, label_visibility='collapsed')


        # Calcul de la taille dans le cas d'une proportion
        if st.session_state.parametre_strat == "Proportion":
            # Initialisation de la méthode
            st.session_state.methode_strat = SampleSize(param=PopParam.prop, method=SizeMethod.wald, strat=True)
            # Vérification des conditions avant le calcul
            if (
                st.session_state.methode_strat is not None and
                all(valeur is not None for valeur in st.session_state.tailleEffet_strat_nombre.values()) and
                all(valeur is not None for valeur in st.session_state.prop_est_strat_nombre.values()) and
                all(valeur is not None for valeur in st.session_state.population_strat_nombre.values()) and
                st.session_state.tauxReponse_strat != 0 and 
                st.session_state.marge_strat != 0
                ):
                # Fonction pour calculer la taille d'échantillon
                def calcul_taille():
                    st.session_state.methode_strat.calculate(
                        target=st.session_state.prop_est_strat_nombre, 
                        half_ci=st.session_state.marge_strat,
                        deff=st.session_state.tailleEffet_strat_nombre, 
                        resp_rate=st.session_state.tauxReponse_strat,
                        pop_size=st.session_state.population_strat_nombre,
                        alpha=1 - st.session_state.confiance_strat
                    )
                    st.session_state.echantillon_strat = st.session_state.methode_strat.samp_size
                # Bouton pour lancer le calcul
                st.session_state.calcul_strat = st.button(
                    "Calculer la taille", 
                    help="Cliquer pour lancer le calcul de la taille", 
                    on_click=calcul_taille
                )

        # Calcul de la taille dans le cas d'une Moyenne
        if st.session_state.parametre_strat == "Moyenne":
            # Initialisation de la méthode
            st.session_state.methode_strat = SampleSize(param=PopParam.mean, method=SizeMethod.wald, strat=True)
            
            # Vérification des conditions avant le calcul
            if (
                st.session_state.methode_strat is not None and
                all(valeur is not None for valeur in st.session_state.tailleEffet_strat_nombre.values()) and
                all(valeur is not None for valeur in st.session_state.sigma_strat_nombre.values()) and
                all(valeur is not None for valeur in st.session_state.population_strat_nombre.values()) and
                st.session_state.tauxReponse_strat != 0 and 
                st.session_state.marge_strat != 0
                ):
                # Fonction pour calculer la taille d'échantillon
                def calcul_taille():
                    st.session_state.methode_strat.calculate(
                        target=st.session_state.sigma_strat_nombre,
                        half_ci=st.session_state.marge_strat,
                        deff=st.session_state.tailleEffet_strat_nombre,
                        resp_rate=st.session_state.tauxReponse_strat,
                        pop_size=st.session_state.population_strat_nombre,
                        alpha=1 - st.session_state.confiance_strat
                    )
                    st.session_state.echantillon_strat = st.session_state.methode_strat.samp_size
                # Bouton pour lancer le calcul
                st.session_state.calcul_strat = st.button(
                    "Calculer la taille", 
                    help="Cliquer pour lancer le calcul de la taille", 
                    on_click=calcul_taille
                )

        
        if st.session_state.calcul_strat:
            st.markdown('### Présentation des résultats')
            # Fonction pour combiner les valeurs
            def combine_valeurs(key):
                return (st.session_state.tailleEffet_strat_label[key], st.session_state.echantillon_strat[key])

            # Obtenir toutes les clés
            cle = st.session_state.tailleEffet_strat_label.keys()
            # Utiliser map pour appliquer la fonction à chaque clé
            combined_values = map(combine_valeurs, cle)
            # Convertir le résultat de map en liste
            combined_list = list(combined_values)
            # Créer un DataFrame
            st.session_state.resultat = pd.DataFrame(combined_list, index=cle, columns=['Strates', "Taille de l'échantillon"])
            st.write(f"**Résultats**")
            st.session_state.resultat['Taux de sondage'] = round(st.session_state.resultat["Taille de l'échantillon"] / st.session_state.modality_count["Taille"], 5)
            
            tot_echant = st.session_state.resultat["Taille de l'échantillon"].sum()
            tot_sond = round(tot_echant/st.session_state.nombre_tot,4)
            st.session_state.resultat.loc['Total'] = ['Total',tot_echant,tot_sond]
            st.dataframe(st.session_state.resultat)

            if st.session_state.df is not None:
                with st.expander('Afficher plus'):
                    # Effectuer les tirages dans chaque strate
                    sampled_dataframes = []
                    for index, row in st.session_state.resultat.iterrows():
                        modality = row["Strates"]
                        sample_size = row["Taille de l'échantillon"]
                        
                        # Filtrer la base par strate/modality
                        if st.session_state.df is not None:
                            subset_strata = st.session_state.df[st.session_state.df[st.session_state.variable_strat] == modality]
                        elif st.session_state.df is None:
                            subset_strata = st.session_state.df[st.session_state.df['strate'] == modality]
                        # Tirer un échantillon dans chaque strate
                        if len(subset_strata) >= sample_size:  # Vérifier que la taille de la strate permet le tirage
                            sampled_strata = subset_strata.sample(n=sample_size, random_state=42)
                            sampled_dataframes.append(sampled_strata)
                        
                    # Combiner tous les échantillons tirés en un seul DataFrame
                    final_sample = pd.concat(sampled_dataframes)

                    # Stocker dans session_state pour utilisation ultérieure
                    st.session_state.base_echant_strat = final_sample

                    st.write("**Échantillon stratifié tiré** :")
                    st.dataframe(st.session_state.base_echant_strat)

            
    if st.session_state.type_alloc == 'Allocation proportionnelle':
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.session_state.parametre_strat == "Moyenne":
                st.markdown("##### Ecart-type estimé <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("Si vous avez accès à des données provenant d'études antérieures sur la même population ou des populations similaires, vous pouvez utiliser l'écart-type observé dans ces études comme estimation de 𝜎σ.")
                st.session_state.sigma_strat = st.number_input("Marge d'erreur ", min_value = 0, label_visibility='collapsed')

            if st.session_state.parametre_strat == "Proportion":
                st.markdown("##### Proportion estimée <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("Si vous disposez d'études similaires précédentes vous pouvez utiliser ces résultats. Sinon la valeur prise par défaut est 0.5")
                st.session_state.prop_est_strat = st.number_input("Proportion estimée", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", value=0.5, label_visibility='collapsed')

            if st.session_state.parametre_strat == "Proportion":
                st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
                st.session_state.marge_strat = st.number_input("Marge d'erreur", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", value=0.0005, label_visibility='collapsed')

            if st.session_state.parametre_strat == "Moyenne":
                st.markdown("##### Marge d'erreur <span style='color:red;'>*</span>", unsafe_allow_html=True)
                with st.expander("En savoir plus ..."):
                    st.info("La marge d'erreur permet de savoir correspond a la moitié de l'étendue de l'intervalle de confiance. C'est la valeur qui est ajoutée et retranchée de la proportion estimée pour obtenir l'intervalle de confiance")
                st.session_state.marge_strat = st.number_input("Marge d'erreur moy ", min_value= 0, label_visibility='collapsed')

        with col2:
            st.markdown("##### Niveau de confiance <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Le niveau de confiance représente la probabilité que vous êtes prêt à accepter quant à la possibilité que votre estimation soit incorrecte.")
            st.session_state.confiance_strat = st.number_input("Niveau de confiance",min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", value=0.95, label_visibility='collapsed')

            st.markdown("##### Taille de la population <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("La valeur par défaut de la taille est le nombre d'individus de la base s'il y en a")
            if st.session_state.df is not None:
                st.session_state.population_strat = st.number_input("Taille de la population", min_value = 1, value=st.session_state.taillePop, label_visibility='collapsed')
            if st.session_state.df is None and st.session_state.nombre_tot > 1:
                st.session_state.population_strat = st.number_input("Taille de la population", min_value = 1, value=st.session_state.nombre_tot, label_visibility='collapsed')
        
        with col3:
            st.markdown("##### Taux de réponse <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("Le taux de réponse est le pourcentage de personnes ayant répondu à un sondage par rapport au nombre total de personnes sollicitées. Assurez-vous d'atteindre ce taux de réponse au risque de ne pas avoir des estimations précises.")
            st.session_state.tauxReponse_strat = st.number_input("Taux de réponse", min_value=0.0, max_value= 1.0, step = 0.0001, format="%.4f", value=0.90, label_visibility='collapsed')

            st.markdown("##### Effet de plan <span style='color:red;'>*</span>", unsafe_allow_html=True)
            with st.expander("En savoir plus ..."):
                st.info("L'effet de plan est un facteur utilisé dans les enquêtes pour ajuster la taille d'échantillon nécessaire lorsque le plan d'échantillonnage diffère d'un simple échantillonnage aléatoire. Il mesure l'impact du plan d'échantillonnage sur la précision des estimations. Si vous utilisez un plan d'échantillonnage stratifié ou en grappes, par exemple, l'effet de plan prend en compte la corrélation au sein des groupes ou des strates, ce qui peut augmenter la variance des estimations. Un effet de plan supérieur à 1 signifie que la taille de l'échantillon doit être augmentée pour maintenir la même précision. Comme nous sommes dans le cas d'un sondage aléatoire simple, l'effet de plan est de 1")
            st.session_state.tailleEffet_strat =  st.selectbox("Effet de plan",[0.5,0.75,0.90,1],label_visibility='collapsed')



        # Calcul de la taille dans le cas d'une proportion
        if st.session_state.parametre_strat == "Proportion":
            st.session_state.methode_strat = SampleSize(param=PopParam.prop, method=SizeMethod.wald, strat=False)
            if st.session_state.methode_strat is not None and st.session_state.tailleEffet_strat != 0 and st.session_state.tauxReponse_strat != 0 and st.session_state.population_strat != 0 and st.session_state.marge_strat != 0:
                def calcul_taille():
                    st.session_state.methode_strat.calculate(
                        target = st.session_state.prop_est_strat, 
                        half_ci=st.session_state.marge_strat,
                        deff=st.session_state.tailleEffet_strat, 
                        resp_rate=st.session_state.tauxReponse_strat,
                        pop_size = st.session_state.population_strat,
                        alpha = 1 - st.session_state.confiance_strat)
                    st.session_state.echantillon_strat = st.session_state.methode_strat.samp_size
                st.session_state.calcul_strat = st.button("Calculer la taille",help="Cliquer pour lancer le calcul de la taille",on_click=calcul_taille)


        # Calcul de la taille dans le cas d'une moyenne
        if st.session_state.parametre_strat == "Moyenne":
            st.session_state.methode_strat = SampleSize(param=PopParam.mean, method=SizeMethod.wald, strat=False)
            if st.session_state.methode_strat is not None and st.session_state.tailleEffet_strat != 0 and st.session_state.tauxReponse_strat != 0 and st.session_state.taillePop_strat != 0 and st.session_state.marge_strat != 0:
                def calcul_taille():
                    st.session_state.methode_strat.calculate(
                        sigma = st.session_state.sigma_strat,
                        half_ci=st.session_state.marge_strat,
                        deff=st.session_state.tailleEffet_strat, 
                        resp_rate=st.session_state.tauxReponse_strat,
                        pop_size = st.session_state.population_strat,
                        alpha = 1 - st.session_state.confiance_strat)
                    st.session_state.echantillon_strat = st.session_state.methode_strat.samp_size
                st.session_state.calcul_strat = st.button("Calculer la taille",help="Cliquer pour lancer le calcul de la taille",on_click=calcul_taille)
        
        if st.session_state.calcul_strat:
            st.markdown('### Présentation des résultats')
            st.write("La taille d'échantillon nécessaire est: ",st.session_state.echantillon_strat)
            st.session_state.tauxSondage_strat = round(st.session_state.echantillon_strat / st.session_state.population_strat,4)
            st.write("Le taux de sondage est: ",st.session_state.tauxSondage_strat)
            st.session_state.modality_count["Taille de l'echantillon"] = round(st.session_state.modality_count['Taille'] * st.session_state.tauxSondage_strat).astype(int)
            st.session_state.modality_count['Taux de sondage'] = round(st.session_state.modality_count["Taille de l'echantillon"] / st.session_state.modality_count['Taille'],4)
            tot_nomb = st.session_state.modality_count['Taille'].sum()
            st.session_state.tot_taille = st.session_state.modality_count["Taille de l'echantillon"].sum()
            tot_tx = st.session_state.tot_taille / tot_nomb
            st.session_state.modality_count.loc['Total'] = ['Total',tot_nomb,st.session_state.tot_taille,tot_tx]
            st.dataframe(st.session_state.modality_count)

            if st.session_state.df is not None:
                with st.expander('Afficher plus'):
                # Effectuer les tirages dans chaque strate
                    sampled_dataframes = []
                    for index, row in st.session_state.modality_count.iterrows():
                        if st.session_state.df is not None:
                            modality = row[st.session_state.variable_strat]
                        elif st.session_state.df is None:
                            modality = row['strate']
                        sample_size = row["Taille de l'echantillon"]
                        
                        # Filtrer la base par strate/modalité
                        if st.session_state.df is not None:
                            subset_strata = st.session_state.df[st.session_state.df[st.session_state.variable_strat] == modality]
                        elif st.session_state.df is None:
                            subset_strata = st.session_state.df[st.session_state.df['strate'] == modality]
                    
                        # Tirer un échantillon dans chaque strate
                        if len(subset_strata) >= sample_size:  # Vérifier que la taille de la strate permet le tirage
                            sampled_strata = subset_strata.sample(n=sample_size, random_state=42)
                            sampled_dataframes.append(sampled_strata)

                    # Combiner tous les échantillons tirés en un seul DataFrame
                    final_sample = pd.concat(sampled_dataframes)

                    # Stocker dans session_state pour utilisation ultérieure
                    st.session_state.base_echant_strat = final_sample

                    st.write("Échantillon stratifié tiré :")
                    st.dataframe(st.session_state.base_echant_strat)








