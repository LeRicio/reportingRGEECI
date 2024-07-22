# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import plotly.express as px
import function

# Configuration de la page Streamlit
st.set_page_config(
    page_title="RGEE-CI",
    layout="wide",
    initial_sidebar_state="auto",
    page_icon="logo_rgeeci.jpg"
)

# Cacher le menu principal, le pied de page et l'en-tête
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Titre de l'application
st.header("RGEE-CI: REPORTING COLLECTE")
function.load_styles()

# Récupération des données depuis l'URL spécifiée
url = "https://kf.kobotoolbox.org/api/v2/assets/aQTxCNZFyJ9avyyfDbXEz6/export-settings/esU2z5gz8LUBsmsbgJWjtug/data.csv"
df = function.get_data_from_forms(url)

# Barre latérale pour les filtres et actualisation
with st.sidebar:
    if st.button("ACTUALISER", type="primary"):
        function.get_data_from_forms.clear()

    st.title("Filtre")
    SUP = df["Superviseur"].sort_values().unique()
    SUP_SELECT = st.selectbox("SUPERVISEURS:", SUP, index=None)

    CE = df["Chef d'equipe"].sort_values().unique()
    CE_SELECT = st.selectbox("CHEFS D'EQUIPE:", CE, index=None)

    REG = df["NomReg"].sort_values().unique()
    REG_SELECT = st.selectbox("REGION:", REG, index=None)

    DEP = df["NomDep"].sort_values().unique()
    DEP_SELECT = st.selectbox("DEPARTEMENT:", DEP, index=None)

    SP = df["NomSp"].sort_values().unique()
    SP_SELECT = st.selectbox("SOUS-PREFECTURE:", SP, index=None)

# Filtrage des données selon les sélections
if len(df) != 0:
    try:
        if SUP_SELECT:
            df = df[df['Superviseur'] == SUP_SELECT]
        if CE_SELECT:
            df = df[df["Chef d'equipe"] == CE_SELECT]
        if REG_SELECT:
            df = df[df["NomReg"] == REG_SELECT]
        if DEP_SELECT:
            df = df[df["NomDep"] == DEP_SELECT]
        if SP_SELECT:
            df = df[df["NomSp"] == SP_SELECT]
    except:
        pass

# Fonction pour scinder et collecter les données de la colonne spécifiée
def split_and_collect(column):
    result = []
    for item in column:
        if isinstance(item, str):
            result.extend(item.split(','))
        elif pd.notna(item):
            result.append(str(item))
    return result

# Appliquer la fonction à la colonne 'NumZD'
liste_zd = split_and_collect(df['NumZD'])
liste_zd = list(set(liste_zd))
try:
    liste_zd.remove("0000")
except:
    pass

# Calcul des métriques
UET = df["UE_total"].sum()
REFUS = df["refus"].sum()
UEI = df["UE informelle"].sum()
UEF = df["UE formelle"].sum()
PARTIEL = df["partiel"].sum()
ZD_total = len(liste_zd)

# Affichage des métriques dans des colonnes
container = st.container()
with container:
    col1, col2, col3 , col4 = st.columns(4)
    col1.metric("UE", f"{UET:,}")
    col2.metric("UE formelle", f"{UEF:,}")
    col3.metric("UE informelle", f"{UEI:,}")
    col4.metric("Partiel", f"{PARTIEL:,}")
with container:
    col5, col6, col7 = st.columns([2, 3, 2])
    col5.metric("ZDs traités", f"{ZD_total:,}")
    col6.metric("Taux de réalisation ZD", f"{(ZD_total / 569) * 100:.2f}%")
    col7.metric("Refus", f"{REFUS:,}")

# Affichage des tableaux de suivi
st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR EQUIPE</h5>", unsafe_allow_html=True)
pivot_df = df.pivot_table(index="Chef d'equipe", columns='date_reporting', values='UE_total', aggfunc='sum', fill_value=0)
pivot_df["Ensemble"] = pivot_df.sum(axis=1)

# Tri du DataFrame par la colonne "Ensemble" dans l'ordre décroissant
pivot_df = pivot_df.sort_values(by="Ensemble", ascending=False)

sum_row = pivot_df.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
pivot_df = pd.concat([pivot_df, sum_row_df])

st.table(function.style_dataframe(pivot_df))

st.markdown("<h5 style='text-align: center;color: #3a416c;'>COURBE D'EVOLUTION DES EQUIPES</h5>", unsafe_allow_html=True)

# Regroupement des données par date
df_grouped = df.groupby(['date_reporting', 'Chef d\'equipe']).sum().reset_index()


# Création de la courbe d'évolution
fig = px.line(
    df_grouped, 
    x='date_reporting', 
    y='UE_total', 
    color="Chef d'equipe", 
    labels={"date_reporting": "Date de Reporting", "UE_total": "UE Total"},
    markers=True
)

# Ajout de mise en forme
fig.update_layout(
    xaxis_title='Date de Reporting',
    yaxis_title='UE Total',
    legend_title_text='Chef d\'équipe'
)

# Affichage de la courbe d'évolution
st.plotly_chart(fig)

st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR DEPARTEMENT</h5>", unsafe_allow_html=True)
df_depart = df.groupby("NomDep")[["UE formelle", "UE informelle", "UE_total", "refus", "Nombre ZD"]].sum().reset_index()

sum_row = df_depart.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
df_depart = pd.concat([df_depart, sum_row_df])
st.table(function.style_dataframe(df_depart))

st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR SUPERVISEUR</h5>", unsafe_allow_html=True)
df_sup = df.groupby("Superviseur")[["UE formelle", "UE informelle", "UE_total", "refus", "Nombre ZD"]].sum().reset_index()
st.table(function.style_dataframe(df_sup))

st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR CHEF D'EQUIPE</h5>", unsafe_allow_html=True)
df_chef = df.groupby("Chef d'equipe")[["UE formelle", "UE informelle", "UE_total", "refus", "Nombre ZD"]].sum().reset_index()
st.table(function.style_dataframe(df_chef))

# Ajout d'un diagramme en barres pour visualiser les refus par département
st.markdown("<h5 style='text-align: center;color: #3a416c;'>DIAGRAMME DES REFUS PAR DEPARTEMENT</h5>", unsafe_allow_html=True)
fig_refus_dep = px.bar(df_depart, x='NomDep', y='refus', title='Refus par Département')
st.plotly_chart(fig_refus_dep)

# Ajout d'un camembert pour visualiser la répartition des UE par type
st.markdown("<h5 style='text-align: center;color: #3a416c;'>REPARTITION DES UE PAR TYPE</h5>", unsafe_allow_html=True)
fig_pie = px.pie(values=[UEF, UEI], names=['UE formelle', 'UE informelle'], title='Répartition des UE par type')
st.plotly_chart(fig_pie)

# Ajout d'une heatmap pour visualiser les corrélations entre différentes colonnes
st.markdown("<h5 style='text-align: center;color: #3a416c;'>HEATMAP DES CORRELATIONS</h5>", unsafe_allow_html=True)
corr = df[["UE formelle", "UE informelle", "UE_total", "refus", "Nombre ZD"]].corr()
fig_heatmap = px.imshow(corr, text_auto=True, title='Heatmap des Corrélations')
st.plotly_chart(fig_heatmap)

# Footer avec lien vers LinkedIn
footer = """
    <style>
    a:link, a:visited {
        color: blue;
        background-color: transparent;
        text-decoration: underline;
    }
    a:hover, a:active {
        color: red;
        background-color: transparent;
        text-decoration: underline;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: black;
        text-align: center;
    }
    </style>
    <div class="footer">
        <p>Developed by <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/kouakou-kouadio-984517195/" target="_blank">Kouakou Kouadio Maurice</a></p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
