import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("Sales Dashboard")

# Chargement des données
@st.cache
def load_data():
    # Simuler des données pour l'exemple
    data = {
        "Order ID": ["CA-2014-145317", "CA-2016-118689"],
        "Order Date": ["2014-03-18", "2016-10-02"],
        "Segment": ["Home Office", "Corporate"],
        "Customer ID": ["SM-20320", "TC-20980"],
        "Customer Name": ["Sean Miller", "Tamara Chand"],
        "Country": ["United States", "United States"],
        "Region": ["South", "Central"],
        "State": ["Florida", "Indiana"],
        "City": ["Jacksonville", "Lafayette"],
        "Orders": [1, 1],
        "Quantity": [25, 18],
        "Sales": [23661, 18337]
    }
    df = pd.DataFrame(data)
    return df

df = load_data()

# Layout des métriques
st.write("## Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("REVENUE", "$2,297,201")
col2.metric("PROFIT", "$286,397")
col3.metric("ORDERS", "5009")
col4.metric("CUSTOMERS", "793")
col5.metric("QUANTITY", "37,873")

# Sales by Segment
st.write("## Sales by Segment")

segment_data = {
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "Consumer": [0.1, 0.15, 0.2, 0.1, 0.05, 0.1, 0.1, 0.15, 0.2, 0.1, 0.15, 0.2],
    "Corporate": [0.05, 0.1, 0.15, 0.05, 0.1, 0.15, 0.05, 0.1, 0.15, 0.05, 0.1, 0.15],
    "Home Office": [0.02, 0.03, 0.05, 0.02, 0.03, 0.05, 0.02, 0.03, 0.05, 0.02, 0.03, 0.05]
}

segment_df = pd.DataFrame(segment_data)
segment_df = segment_df.melt(id_vars='Month', value_vars=['Consumer', 'Corporate', 'Home Office'],
                             var_name='Segment', value_name='Sales')

fig_segment = px.bar(segment_df, x='Month', y='Sales', color='Segment', barmode='stack')
st.plotly_chart(fig_segment, use_container_width=True)

# Category Analysis
st.write("## Category Analysis")

category_data = {
    "Category": ["Furniture", "Office Supplies", "Technology"],
    "Orders": [0.25, 0.53, 0.22]
}

category_df = pd.DataFrame(category_data)

fig_category = go.Figure(data=[go.Pie(labels=category_df['Category'], values=category_df['Orders'], hole=.4)])
st.plotly_chart(fig_category, use_container_width=True)

# Order Log
st.write("## Order Log")

st.dataframe(df)

# Footer
st.write("""
    <style>
    footer {visibility: hidden;}
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
        <p>Developed by Your Name</p>
    </div>
    """, unsafe_allow_html=True)
