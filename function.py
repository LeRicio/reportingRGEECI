import pandas as pd
import streamlit as st
from datetime import datetime

liste_equipe = {
"RGEECI_Ce0131" : "KOFFI BALEY YVES VINCENT",
"RGEECI_Ce0132" : "SOUMAHORO MONMIGNAN",
"RGEECI_Ce0133" : "GONGBE KOUADIO AUBAIN",
"RGEECI_Ce0134" : "YEO ZIE SAMUEL",
"RGEECI_Ce0135" : "DANGBE YOLÉ SYLVIE CARINE",
"RGEECI_Ce0136" : "BAGATE KARIM "

}

liste_sup = {
"RGEECI_Ce0131" : "KOFFI",
"RGEECI_Ce0132" : "KOFFI",
"RGEECI_Ce0133" : "KOFFI",
"RGEECI_Ce0134" : "KOUADIO",
"RGEECI_Ce0135" : "KOUADIO",
"RGEECI_Ce0136" : "KOUADIO"

}


def cooling_highlight(val):
    color = '#aaf6aa' if val else 'white'
    return f'background-color: {color}'

def convert_to_datetime(date_str):
    if date_str is None:
        return None
    if isinstance(date_str, float):
        return 
    else:
        return datetime.strptime(str(date_str), "%d/%m/%Y")

@st.cache_data
def get_data_from_forms(url):
    df = pd.read_csv(url,sep=';', dtype={"NumZD":"object"})
    df["Chef d'equipe"] = df["nom_CE"].map(liste_equipe)
    df["Superviseur"] = df["nom_CE"].map(liste_sup)
    df = df.rename(columns={"UEF_total":"UE formelle","UEI_total":"UE informelle","NbZD":"Nombre ZD","refus_total":"refus","partiel_total":"partiel" })
    return df

@st.cache_resource
def load_styles():
    with open('style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Appliquer la fonction à chaque ligne du DataFrame pour créer une nouvelle colonne
def style_dataframe(df):
    # Créer un DataFrame de style
    styled_df = df.style
    
    # Colorier les entêtes, les index et les lignes du corps en bleu nuit
    styled_df.set_table_styles([
        {'selector': 'td:hover','props': [('background-color', '#7dbef4')]},
        {'selector': '.index_name','props': 'font-style: italic; color: darkgrey; font-weight:normal;'},
        {'selector': 'th:not(.index_name)','props': 'background-color: #3a416c; color: white;'},
    ], overwrite=False)

    # Colorier les lignes du corps en alternance en gris et blanc
    def row_style(row):
        # Convertir row.name en entier si possible
        try:
            row_index = int(row.name)
        except ValueError:
            row_index = hash(row.name)
        
        if row_index % 2 == 0:
            return ['background-color: #ebecf0'] * len(row)
        else:
            return ['background-color: #f9fafd'] * len(row)

    styled_df.apply(row_style, axis=1)

    return styled_df
