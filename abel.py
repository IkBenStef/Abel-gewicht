import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# 1. Paginaconfiguratie
st.set_page_config(
    page_title="Eet Overzicht Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS voor 100% transparante achtergrond
st.markdown("""
    <style>
        html, body, .stApp, 
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"], 
        [data-testid="stToolbar"], 
        [data-testid="stSidebar"],
        .main, .block-container {
            background-color: transparent !important;
            background: transparent !important;
        }

        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 0rem !important; 
            padding-left: 5rem !important; 
            padding-right: 5rem !important; 
        }

        div[data-testid="stMetric"] { 
            background-color: rgba(255, 255, 255, 0.05) !important; 
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 8px 12px; 
            border-radius: 8px; 
        }

        h2, h3 { 
            margin-bottom: 0px; 
            padding-bottom: 5px; 
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIES ---
def make_transparent(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff")
    )
    return fig

# 3. Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    df = conn.read()
    df = df.fillna("")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Kon geen gegevens ophalen uit Google Sheets. Controleer je secrets configuratie.")
    st.stop()

# 4. Bovenste Rij: Statistieken (top_col1 & top_col2)
st.markdown("### 📊 Overzicht")
top_col1, top_col2 = st.columns([1, 4])

with top_col1:
    st.metric("Totaal Maaltijden", len(df))

with top_col2:
    if not df.empty and "Wie" in df.columns:
        wie_counts = df["Wie"].value_counts().reset_index()
        wie_counts.columns = ["Wie", "Aantal"]
        
        fig_wie = px.bar(
            wie_counts, x="Aantal", y="Wie", color="Wie",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_wie.update_layout(height=100, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        fig_wie = make_transparent(fig_wie)
        st.plotly_chart(fig_wie, use_container_width=True)

st.divider()

# 5. Onderste Rij: Donut (bot_col1) + Tabel (bot_col2)
bot_col1, bot_col2 = st.columns(2)

with bot_col1:  # <-- Hier stond eerder "with a1:", wat de fout veroorzaakte
    st.markdown("### 🏷️ Categorieën Overzicht")
    if not df.empty and "Categorie" in df.columns:
        cat_counts = df["Categorie"].value_counts().reset_index()
        cat_counts.columns = ["Categorie", "Aantal"]
        
        fig_cat = px.pie(
            cat_counts, 
            names="Categorie", 
            values="Aantal", 
            hole=0.45, 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat.update_layout(
            height=420, 
            margin=dict(l=10, r=10, t=20, b=10), 
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        fig_cat = make_transparent(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

with bot_col2:
    st.markdown("### 📋 Recentste Maaltijden")
    if not df.empty:
        st.dataframe(df, hide_index=True, use_container_width=True, height=420)
