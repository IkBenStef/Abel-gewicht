import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Hond Gewicht Tracker", layout="centered")

st.title("🐾 Mijn Hond: Gewicht Tracker")

# 1. Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
df = conn.read(spreadsheet=sheet_url, ttl="0s")

# 3. Grafiek tonen
if not df.empty:
    st.subheader("Gewichtsverloop")
    df['datum'] = pd.to_datetime(df['datum'])


    fig = px.line(
        df, 
        x='datum', 
        y='gewicht', 
        markers=True,
        title='Gewicht over tijd'
    )
    fig.update_traces(line_color='blue', marker=dict(size=10, color='red'))
    st.plotly_chart(fig, use_container_width=True)


st.subheader("Historie")
st.dataframe(df.sort_values(by="datum", ascending=False), use_container_width=True)

st.divider()

