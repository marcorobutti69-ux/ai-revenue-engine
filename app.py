import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI Revenue Engine", layout="wide")

# LOGIN SEMPLICE
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

uploaded_file = st.file_uploader("Carica dati hotel CSV", type="csv")

if uploaded_file:

    data = pd.read_csv(uploaded_file)

    data["occupancy"] = data["rooms_sold"] / data["rooms_available"]

    col1, col2, col3 = st.columns(3)

    avg_occ = data["occupancy"].mean()*100
    adr = data["ADR"].mean()
    revpar = adr * (avg_occ/100)

    col1.metric("Occupazione media", f"{avg_occ:.1f}%")
    col2.metric("ADR medio", f"{adr:.0f}€")
    col3.metric("RevPAR medio", f"{revpar:.0f}€")

    st.subheader("Trend prenotazioni")

    st.line_chart(data["rooms_sold"])

    # AI forecast

    data["day"] = np.arange(len(data))

    X = data[["day"]]
    y = data["rooms_sold"]

    model = LinearRegression()
    model.fit(X,y)

    future_days = np.arange(len(data), len(data)+30).reshape(-1,1)

    forecast = model.predict(future_days)

    st.subheader("Forecast occupazione 30 giorni")

    st.line_chart(forecast)

    predicted_demand = forecast.mean()

    if predicted_demand > 90:
        suggested_price = adr * 1.2
    elif predicted_demand > 75:
        suggested_price = adr * 1.1
    else:
        suggested_price = adr * 0.9

    occupancy_forecast = predicted_demand / data["rooms_available"].iloc[0]

    revpar_forecast = suggested_price * occupancy_forecast

    col4, col5, col6 = st.columns(3)

    col4.metric("Domanda prevista", f"{predicted_demand:.0f} camere")
    col5.metric("Prezzo suggerito", f"{suggested_price:.0f}€")
    col6.metric("RevPAR previsto", f"{revpar_forecast:.0f}€")

    st.subheader("Simulatore prezzo")

    new_price = st.slider("Simula nuovo prezzo camera", 50, 400, int(suggested_price))

    simulated_revpar = new_price * occupancy_forecast

    st.metric("RevPAR simulato", f"{simulated_revpar:.0f}€")
