import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Hond Gewicht Tracker", layout="centered")

st.title("🐾 Mijn Hond: Gewicht Tracker")

# 1. Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Zoek de URL expliciet op in de secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Haal de data op
df = conn.read(spreadsheet=sheet_url, ttl="0s")

# 3. Grafiek tonen
if not df.empty:
    st.subheader("Gewichtsverloop")
    # Let op: zorg dat de kolomnaam in je CSV/Sheet 'datum' is
    df['datum'] = pd.to_datetime(df['datum'])
    st.line_chart(data=df, x='datum', y='gewicht')

# 4. Tabel tonen
st.subheader("Historie")
st.dataframe(df.sort_values(by="datum", ascending=False), use_container_width=True)

# 5. Nieuwe invoer via een Formulier
st.divider()
st.subheader("Nieuwe meting toevoegen")

with st.form("entry_form"):
    dag = st.date_input("Datum van meting")
    gewicht = st.number_input("Gewicht (kg)", min_value=0.1, max_value=25.0, value=20.0, step=0.01)
    
    # --- NIEUW: Wachtwoord veld ---
    ingevuld_wachtwoord = st.text_input("Voer wachtwoord in om op te slaan", type="password")
    
    submit_button = st.form_submit_button(label="Opslaan")

    if submit_button:
        # Check of het wachtwoord overeenkomt met de Secrets
        if ingevuld_wachtwoord == st.secrets["wachtwoord"]:
            # Nieuwe rij maken
            new_data = pd.DataFrame([{"datum": str(dag), "gewicht": gewicht}])
            
            # Bestaande data combineren met nieuwe data
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # Terugschrijven naar Google Sheets
            conn.update(spreadsheet=sheet_url, data=updated_df)
            
            st.success("Gegevens zijn opgeslagen!")
            st.rerun()
        else:
            st.error("❌ Onjuist wachtwoord. De gegevens zijn niet opgeslagen.")
