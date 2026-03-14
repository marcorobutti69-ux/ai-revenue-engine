import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI Revenue Engine", layout="wide")

# LOGIN

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("AI Revenue Engine")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "hotel":
            st.session_state.login = True
        else:
            st.error("Credenziali non valide")

    st.stop()

# DASHBOARD

st.title("AI Revenue Dashboard")

hotel_name = st.text_input("Nome Hotel")

uploaded_file = st.file_uploader(
    "Carica dati hotel CSV",
    type="csv",
    key="hotel_csv"
)

if uploaded_file:

    data = pd.read_csv(uploaded_file)

    # KPI BASE

    data["occupancy"] = data["rooms_sold"] / data["rooms_available"]

    avg_occ = data["occupancy"].mean() * 100
    adr = data["ADR"].mean()
    revpar = adr * (avg_occ / 100)

    st.subheader("KPI Hotel")

    col1, col2, col3 = st.columns(3)

    col1.metric("Occupancy", f"{avg_occ:.1f}%")
    col2.metric("ADR", f"{adr:.0f}€")
    col3.metric("RevPAR", f"{revpar:.0f}€")

    # TREND PRENOTAZIONI

    st.subheader("Trend prenotazioni")

    st.line_chart(data["rooms_sold"])

    # FORECAST AI 365 GIORNI

    data["day"] = np.arange(len(data))

    X = data[["day"]]
    y = data["rooms_sold"]

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(len(data), len(data) + 365).reshape(-1, 1)

    forecast = model.predict(future_days)

    st.subheader("Forecast domanda 365 giorni")

    st.line_chart(forecast)

    predicted_demand = forecast.mean()

    # PRICING AI

    if predicted_demand > 90:
        suggested_price = adr * 1.2
    elif predicted_demand > 75:
        suggested_price = adr * 1.1
    else:
        suggested_price = adr * 0.9

    occupancy_forecast = predicted_demand / data["rooms_available"].iloc[0]

    revpar_forecast = suggested_price * occupancy_forecast

    st.subheader("Suggerimento AI")

    col4, col5, col6 = st.columns(3)

    col4.metric("Domanda prevista", f"{predicted_demand:.0f} camere")
    col5.metric("Prezzo suggerito", f"{suggested_price:.0f}€")
    col6.metric("RevPAR previsto", f"{revpar_forecast:.0f}€")

    # ANALISI COMPETITOR

    competitor_price = adr * 1.1

    st.subheader("Analisi Competitor")

    st.metric("Prezzo medio competitor", f"{competitor_price:.0f}€")

    if suggested_price < competitor_price:
        st.warning("Prezzo sotto la media competitor")
    else:
        st.success("Prezzo competitivo rispetto al mercato")

    # SIMULATORE PREZZO

    st.subheader("Simulatore prezzo")

    new_price = st.slider("Simula nuovo prezzo camera", 50, 400, int(suggested_price))

    simulated_revpar = new_price * occupancy_forecast

    rooms = data["rooms_available"].iloc[0]

    simulated_revenue = new_price * rooms * occupancy_forecast

    col7, col8 = st.columns(2)

    col7.metric("RevPAR simulato", f"{simulated_revpar:.0f}€")
    col8.metric("Revenue stimato", f"{simulated_revenue:.0f}€")



