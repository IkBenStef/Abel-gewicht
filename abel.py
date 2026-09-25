import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# 1. Paginaconfiguratie (wide layout zodat alles naast elkaar past)
st.set_page_config(
    page_title="Eet Overzicht Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aangepaste CSS om de marges en padding extreem compact te maken (voorkomt scrollen)
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; }
        div[data-testid="stMetric"] { background-color: #f8f9fa; padding: 5px 10px; border-radius: 6px; }
        h3 { margin-bottom: 0px; padding-bottom: 0px; font-size: 1.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    df = conn.read()
    # Lege waarden opvullen met 'Onbekend' of lege tekst
    df = df.fillna("")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Kon geen gegevens ophalen uit Google Sheets. Controleer je secrets configuratie.")
    st.stop()

# Header
st.markdown("<h2 style='text-align: center; margin-bottom: 10px;'>🍽️ Eetdagboek & Analyse Dashboard</h2>", unsafe_allow_html=True)

# 3. Bovenste Rij: Invoerformulier + Key Metrics (naast elkaar)
col_form, col_metrics = st.columns([2, 1], gap="medium")

with col_form:
    st.markdown("### ➕ Nieuwe Maaltijd Toevoegen")
    with st.form("add_meal_form", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            dag = st.text_input("Dag (DD-MM-YYYY)", value=pd.Timestamp.now().strftime("%d-%m-%Y"))
            waar = st.text_input("Waar", value="Thuis")
        with f_col2:
            wie = st.text_input("Wie", value="Papa")
            wat = st.text_input("Wat")
        with f_col3:
            vlees = st.text_input("Vlees")
            groente = st.text_input("Groente")
        
        f_sub1, f_sub2 = st.columns([2, 1])
        with f_sub1:
            categorie = st.selectbox("Categorie", ["AVG", "AV", "Pasta", "Rijst", "Overig"])
        with f_sub2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Opslaan 💾", use_container_width=True)

        if submitted:
            new_data = pd.DataFrame([{
                "Dag": dag, "Waar": waar, "Wie": wie,
                "Wat": wat, "Vlees": vlees, "Groente": groente,
                "Categorie": categorie
            }])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Maaltijd opgeslagen!")
            st.cache_data.clear()
            st.rerun()

with col_metrics:
    st.markdown("### 📊 Statistieken")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Totaal Maaltijden", len(df))
        meeste_kok = df["Wie"].mode()[0] if not df.empty and "Wie" in df.columns and len(df["Wie"].mode()) > 0 else "-"
        st.metric("Meest Gekookt Door", meeste_kok)
    with m_col2:
        top_cat = df["Categorie"].mode()[0] if not df.empty and "Categorie" in df.columns and len(df["Categorie"].mode()) > 0 else "-"
        st.metric("Top Categorie", top_cat)
        thuis_pct = f"{round((df['Waar'] == 'Thuis').mean() * 100)}%" if not df.empty and "Waar" in df.columns else "-"
        st.metric("Thuis Gegeten", thuis_pct)

st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# 4. Onderste Rij: 2 Grafieken + Recentste Maaltijden Tabel (naast elkaar)
col_chart1, col_chart2, col_table = st.columns([1, 1, 1.2], gap="small")

with col_chart1:
    st.markdown("### Categorieën")
    if not df.empty and "Categorie" in df.columns:
        cat_counts = df["Categorie"].value_counts().reset_index()
        cat_counts.columns = ["Categorie", "Aantal"]
        fig_cat = px.pie(
            cat_counts, names="Categorie", values="Aantal", 
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat.update_layout(height=230, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
        st.plotly_chart(fig_cat, use_container_width=True)

with col_chart2:
    st.markdown("### Wie Kookt Er?")
    if not df.empty and "Wie" in df.columns:
        wie_counts = df["Wie"].value_counts().reset_index()
        wie_counts.columns = ["Wie", "Aantal"]
        fig_wie = px.bar(
            wie_counts, x="Wie", y="Aantal", color="Wie",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_wie.update_layout(height=230, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_wie, use_container_width=True)

with col_table:
    st.markdown("### 📋 Laatste Invoer")
    if not df.empty:
        # Toon de laatste 5 ingevoerde maaltijden (meest recente bovenaan)
        recent_df = df.tail(5).iloc[::-1][["Dag", "Wat", "Wie", "Categorie"]]
        st.dataframe(recent_df, hide_index=True, use_container_width=True, height=210)
