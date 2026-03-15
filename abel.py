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
    df['datum'] = pd.to_datetime(df['datum'])

    # 1. Definieer de lijngrafiek
    lijn = alt.Chart(df).mark_line(color='blue').encode(
        x='datum:T',
        y='gewicht:Q'
    )

    # 2. Definieer de scatter plot (de puntjes)
    punten = alt.Chart(df).mark_circle(size=60, color='red').encode(
        x='datum:T',
        y='gewicht:Q',
        tooltip=['datum', 'gewicht']
    )

    # 3. Combineer ze (layer)
    grafiek = alt.layer(lijn, punten).interactive()

    st.altair_chart(grafiek, use_container_width=True)

# 4. Tabel tonen
st.subheader("Historie")
st.dataframe(df.sort_values(by="datum", ascending=False), use_container_width=True)

# 5. Nieuwe invoer via een Formulier
st.divider()

