# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import function
from datetime import datetime, timedelta

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
    except Exception as e:
        st.error(f"Erreur lors du filtrage des données: {e}")

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
except ValueError:
    pass

# Calcul des métriques
UET = df["UE_total"].sum()
REFUS = df["refus"].sum()
UEI = df["UE informelle"].sum()
UEF = df["UE formelle"].sum()
PARTIEL = df.loc[df["date_reporting"]==str(datetime.now().date()),"partiel"].sum()
ZD_total = len(liste_zd)

# Affichage des métriques dans des colonnes
container = st.container()
with container:
    col1, col2, col3, col4 = st.columns(4)
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
pivot_df = pivot_df.reset_index(drop=False)
pivot_df.index = pivot_df.index + 1
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

col1, col2 = st.columns(2)

#classement des AGENTS
with col1:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>CLASSEMENT AGENTS RECENSEURS</h5>", unsafe_allow_html=True)
    stat_agent = df[["nom_CE","UE_agent1","UE_agent2","UE_agent3"]]
    stat_agent =stat_agent.groupby("nom_CE").sum()
    stat_agent = stat_agent.reset_index()
    stat_agent = stat_agent.melt(id_vars=['nom_CE'], var_name='Agent', value_name='UE_Total')
    stat_agent['Nom_Agent'] = stat_agent['nom_CE'] + stat_agent['Agent'].str[-1]
    stat_agent = stat_agent[["Nom_Agent","UE_Total"]]
    stat_agent.sort_values(by="UE_Total",ascending=False,inplace=True)
    stat_agent = function.add_agent_name(stat_agent)
    stat_agent = stat_agent.reset_index(drop=True)
    stat_agent.index = stat_agent.index + 1
    st.table(function.style_dataframe(stat_agent))


# Créer le diagramme en barres
with col2:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>REPRESENTATION DES AGENTS PAR UE</h5>", unsafe_allow_html=True)
    fig_ag = px.bar(stat_agent, x='Nom_Agent', y='UE_Total', text='UE_Total', 
             labels={'Nom_Agent': 'Nom de l\'Agent', 'UE_Total': 'Total UE'})
    st.plotly_chart(fig_ag)



#--------------------------------------------------------------------------------------

# Regroupement des données des agents par date
st.markdown("<h5 style='text-align: center;color: #3a416c;'>COURBE D'EVOLUTION DES AGENTS</h5>", unsafe_allow_html=True)

stat_agent = df[["date_reporting", "nom_CE", "UE_agent1", "UE_agent2", "UE_agent3"]]
stat_agent = stat_agent.groupby(['date_reporting', 'nom_CE']).sum().reset_index()
stat_agent = stat_agent.melt(id_vars=['date_reporting', 'nom_CE'], var_name='Agent', value_name='UE_Total')
stat_agent['Nom_Agent'] = stat_agent['nom_CE'] + stat_agent['Agent'].str[-1]
stat_agent = stat_agent[["date_reporting", "Nom_Agent", "UE_Total"]]
stat_agent = function.add_agent_name(stat_agent)

# Création de la courbe d'évolution
fig_agt1 = px.line(
    stat_agent, 
    x='date_reporting', 
    y='UE_Total', 
    color="Nom_Agent", 
    labels={"date_reporting": "Date de Reporting", "UE_Total": "UE Total"},
    markers=True
)

# Ajout de mise en forme
fig_agt1.update_layout(
    xaxis_title='Date de Reporting',
    yaxis_title='UE Total',
    legend_title_text='Agent Enquêteur'
)

# Affichage de la courbe d'évolution
st.plotly_chart(fig_agt1)

#-------------------------------------------------------------------------------------

# Affichage des graphiques côte à côte
col1, col2 = st.columns(2)

# Diagrame empilé des type d'UE par équipe
segment_df = df.melt(id_vars="Chef d'equipe", value_vars=["UE informelle", "UE formelle", "refus"],
                             var_name='Segment', value_name='Value')
fig_segment = px.bar(segment_df, x="Chef d'equipe", y='Value', color='Segment', barmode='stack')
fig_segment=function.improve_layout(fig_segment)

with col1:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>TYPE D'UE PAR EQUIPE</h5>", unsafe_allow_html=True)
    st.plotly_chart(fig_segment, use_container_width=True)

# Diagramme en barres pour visualiser le nombre d'UE par équipe

with col2:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>DIAGRAMME DU NOMBRE D'UE PAR EQUIPE</h5>", unsafe_allow_html=True)
    fig_refus_dep = px.bar(df, x="Chef d'equipe", y='UE_total')
    fig_refus_dep=function.improve_layout(fig_refus_dep)
    st.plotly_chart(fig_refus_dep, use_container_width=True)


col1, col2 = st.columns(2)
# Camembert pour visualiser la répartition des UE par type

with col1:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>REPARTITION DES UE PAR TYPE</h5>", unsafe_allow_html=True)
    fig_pie = px.pie(values=[UEF, UEI], names=['UE formelle', 'UE informelle'])
    st.plotly_chart(function.improve_layout(fig_pie))


with col2:
    st.markdown("<h5 style='text-align: center;color: #3a416c;'>REPARTITION DES UE PAR TYPE</h5>", unsafe_allow_html=True)
    fig_category = go.Figure(data=[go.Pie(labels=['UE formelle', 'UE informelle'], values=[UEF, UEI], hole=.4)])
    fig_category=function.improve_layout(fig_category)
    st.plotly_chart(fig_category, use_container_width=True)

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
