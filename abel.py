import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Hond Gewicht Tracker", layout="centered")

st.title("🐾 Mijn Hond: Gewicht Tracker")

# 1. Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Zoek de URL expliciet op in de secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Geef de URL direct mee aan de connectie
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=sheet_url, ttl="0s")

# 3. Grafiek tonen
if not df.empty:
    st.subheader("Gewichtsverloop")
    # We zorgen dat 'dag' een datumtype is voor een mooie grafiek
    df['dag'] = pd.to_datetime(df['dag'])
    st.line_chart(data=df, x='dag', y='gewicht')

# 4. Tabel tonen
st.subheader("Historie")
st.dataframe(df.sort_values(by="dag", ascending=False), use_container_width=True)

# 5. Nieuwe invoer via een Formulier
st.divider()
st.subheader("Nieuwe meting toevoegen")

with st.form("entry_form"):
    dag = st.date_input("Datum van meting")
    gewicht = st.number_input("Gewicht (kg)", min_value=0.1, max_value=100.0, step=0.1)
    submit_button = st.form_submit_button(label="Opslaan in Google Sheets")

    if submit_button:
        # Nieuwe rij maken
        new_data = pd.DataFrame([{"dag": str(dag), "gewicht": gewicht}])
        
        # Bestaande data combineren met nieuwe data
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        # Terugschrijven naar Google Sheets
        conn.update(data=updated_df)
        
        st.success("Gegevens zijn opgeslagen!")
        st.balloons()
        # Pagina verversen om de nieuwe grafiek te zien
        st.rerun()
