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

# 2. CSS voor 100% transparante achtergrond (geschikt voor iframe)
st.markdown("""
    <style>
        /* Maak alle Streamlit achtergrondlagen en containers 100% transparant */
        html, body, .stApp, 
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"], 
        [data-testid="stToolbar"], 
        [data-testid="stSidebar"],
        .main, .block-container {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Verwijder de standaard padding/marges voor strakke iframe-integratie */
        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 0rem !important; 
            padding-left: 5rem !important; 
            padding-right: 5rem !important; 
        }

        /* Transparante metric kaartjes met lichte subtiele rand */
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
        font=dict(color="#ffffff")  # Aanpassen naar #000000 als je site een lichte achtergrond heeft
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

# 4. Bovenste Rij: Statistieken (a1 & a2)
st.markdown("### 📊 Overzicht")
a1, a2 = st.columns([1, 4])
with a1:
    st.metric("Totaal Maaltijden", len(df))
with a2:
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

# 5. Onderste Rij: Categorieën (b1) + Dynamische Weergave (b2)
b1, b2 = st.columns(2)

with b1:
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
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=-0.1)
        )
        fig_cat = make_transparent(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True, height=500)

with b2:
    # Dropdown menu keuze
    weergave_optie = st.selectbox(
        "Kies weergave:",
        ["Heel DataFrame", "Detail grafieken"],
        label_visibility="collapsed"
    )

    if weergave_optie == "Heel DataFrame":
        if not df.empty:
            st.dataframe(df, hide_index=True, use_container_width=True, height=500)

    elif weergave_optie == "Detail grafieken":
        sub_left, sub_right = st.columns(2)

        with sub_left:
            # 1. Cirkeldiagram Vlees
            if not df.empty and "Vlees" in df.columns:
                vlees_df = df[df["Vlees"].astype(str).str.strip() != ""]
                if not vlees_df.empty:
                    vlees_counts = vlees_df["Vlees"].value_counts().reset_index()
                    vlees_counts.columns = ["Vlees", "Aantal"]
                    fig_vlees = px.pie(
                        vlees_counts, names="Vlees", values="Aantal", hole=0.3,
                        title="🥩 Vlees", color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_vlees.update_layout(height=250, margin=dict(l=5, r=5, t=30, b=5))
                    fig_vlees = make_transparent(fig_vlees)
                    st.plotly_chart(fig_vlees, use_container_width=True)

            # 2. Cirkeldiagram Groente
            if not df.empty and "Groente" in df.columns:
                groente_df = df[df["Groente"].astype(str).str.strip() != ""]
                if not groente_df.empty:
                    groente_counts = groente_df["Groente"].value_counts().reset_index()
                    groente_counts.columns = ["Groente", "Aantal"]
                    fig_groente = px.pie(
                        groente_counts, names="Groente", values="Aantal", hole=0.3,
                        title="🥦 Groente", color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig_groente.update_layout(height=250, margin=dict(l=5, r=5, t=30, b=5))
                    fig_groente = make_transparent(fig_groente)
                    st.plotly_chart(fig_groente, use_container_width=True)

        with sub_right:
            # Histogram voor 'Hoelaat' (Vroeger hoger op de Y-as)
            if not df.empty and "Hoelaat" in df.columns:
                hoelaat_df = df[df["Hoelaat"].astype(str).str.strip() != ""].copy()
                if not hoelaat_df.empty:
                    # 1. Omzetten naar datetime (we plakken er een dummy datum voor zodat Plotly het snapt)
                    hoelaat_df['Tijd_dt'] = pd.to_datetime("2026-01-01 " + hoelaat_df['Hoelaat'], format='%Y-%m-%d %H:%M', errors='coerce')
                    hoelaat_df = hoelaat_df.dropna(subset=['Tijd_dt'])
                    
                    # 2. Maak de histogram (we gebruiken nu de datetime kolom voor de Y-as)
                    fig_hoelaat = px.histogram(
                        hoelaat_df, 
                        y="Tijd_dt", 
                        nbins=20,
                        title="⏰ Tijdstippen",
                        color_discrete_sequence=["#FFA07A"]
                    )
                    
                    # 3. Layout aanpassen: as-titels leegmaken en bereik y-as vastzetten
                    fig_hoelaat.update_layout(
                        height=420, 
                        margin=dict(l=10, r=10, t=30, b=10),
                        yaxis_title="",   # Verwijdert de titel van de Y-as (optioneel)
                        xaxis_title="",   # VERWIJDERT DE TEKST 'Aantal' VAN DE X-AS
                        yaxis=dict(
                            type='date',  # Zorgt ervoor dat Plotly de as als tijdlijn ziet
                            tickformat='%H:%M', # Toont alleen de uren en minuten op de as
                            # Bereik instellen van 17:00 tot 19:00 (omgedraaid zodat vroeg bovenaan staat)
                            range=["2026-01-01 19:00", "2026-01-01 17:00"] 
                        )
                    )
                    fig_hoelaat = make_transparent(fig_hoelaat)
                    st.plotly_chart(fig_hoelaat, use_container_width=True, height=500)

