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

