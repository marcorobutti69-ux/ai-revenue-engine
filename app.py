import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI Revenue Engine SaaS", layout="wide")

# -------------------------
# LOGIN MULTI HOTEL
# -------------------------

users = {
    "hotel1": "password1",
    "hotel2": "password2",
    "admin": "hotel"
}

if "login" not in st.session_state:
    st.session_state.login = False

if "hotel" not in st.session_state:
    st.session_state.hotel = None

if not st.session_state.login:

    st.title("AI Revenue Engine")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and password == users[username]:

            st.session_state.login = True
            st.session_state.hotel = username

        else:
            st.error("Credenziali non valide")

    st.stop()

# -------------------------
# SIDEBAR MENU
# -------------------------

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Forecast", "Pricing", "Revenue Forecast", "AI Copilot"]
)

if st.session_state.hotel:
    st.sidebar.write("Hotel:", st.session_state.hotel)

uploaded_file = st.sidebar.file_uploader(
    "Carica dati hotel CSV",
    type="csv"
)

# -------------------------
# SE NON C'È FILE
# -------------------------

if not uploaded_file:

    st.title("Carica i dati hotel")

    st.info("Carica un file CSV per iniziare l'analisi revenue.")

    st.stop()

# -------------------------
# CARICAMENTO DATI
# -------------------------

data = pd.read_csv(uploaded_file)

# KPI BASE

data["occupancy"] = data["rooms_sold"] / data["rooms_available"]

avg_occ = data["occupancy"].mean() * 100
adr = data["ADR"].mean()
revpar = adr * (avg_occ / 100)

# -------------------------
# MACHINE LEARNING FORECAST
# -------------------------

data["day"] = np.arange(len(data))

X = data[["day"]]
y = data["rooms_sold"]

model = LinearRegression()
model.fit(X, y)

future_days = np.arange(len(data), len(data) + 365).reshape(-1, 1)

forecast = model.predict(future_days)

predicted_demand = forecast.mean()

# -------------------------
# PRICING ENGINE
# -------------------------

if predicted_demand > 90:
    suggested_price = adr * 1.2
elif predicted_demand > 75:
    suggested_price = adr * 1.1
else:
    suggested_price = adr * 0.9

rooms = data["rooms_available"].iloc[0]

occupancy_forecast = predicted_demand / rooms

revpar_forecast = suggested_price * occupancy_forecast

# -------------------------
# REVENUE FORECAST
# -------------------------

forecast_revenue = forecast * suggested_price

total_revenue_365 = forecast_revenue.sum()

# -------------------------
# DASHBOARD
# -------------------------

if menu == "Dashboard":

    st.title("Revenue Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Occupancy", f"{avg_occ:.1f}%")
    col2.metric("ADR", f"{adr:.0f}€")
    col3.metric("RevPAR", f"{revpar:.0f}€")

    st.subheader("Trend prenotazioni")

    st.line_chart(data["rooms_sold"])

# -------------------------
# FORECAST
# -------------------------

elif menu == "Forecast":

    st.title("Demand Forecast 365 giorni")

    st.line_chart(forecast)

    st.metric("Domanda prevista media", f"{predicted_demand:.0f} camere")

# -------------------------
# PRICING ENGINE
# -------------------------

elif menu == "Pricing":

    st.title("AI Pricing Engine")

    col1, col2 = st.columns(2)

    col1.metric("ADR attuale", f"{adr:.0f}€")
    col2.metric("Prezzo suggerito AI", f"{suggested_price:.0f}€")

    competitor_price = adr * 1.1

    st.subheader("Analisi Competitor")

    st.metric("Prezzo medio competitor", f"{competitor_price:.0f}€")

    if suggested_price < competitor_price:
        st.warning("Prezzo sotto la media competitor")
    else:
        st.success("Prezzo competitivo rispetto al mercato")

    st.subheader("Simulatore prezzo")

    new_price = st.slider(
        "Simula nuovo prezzo camera",
        50,
        400,
        int(suggested_price)
    )

    simulated_revpar = new_price * occupancy_forecast

    simulated_revenue = new_price * rooms * occupancy_forecast

    col3, col4 = st.columns(2)

    col3.metric("RevPAR simulato", f"{simulated_revpar:.0f}€")
    col4.metric("Revenue stimato", f"{simulated_revenue:.0f}€")

# -------------------------
# REVENUE FORECAST
# -------------------------

elif menu == "Revenue Forecast":

    st.title("Revenue Forecast 365 giorni")

    st.line_chart(forecast_revenue)

    st.metric("Revenue totale stimato anno", f"{total_revenue_365:,.0f}€")

# -------------------------
# AI REVENUE COPILOT
# -------------------------

elif menu == "AI Copilot":

    st.title("AI Revenue Copilot")

    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = []

    question = st.chat_input("Chiedi all'AI Revenue Copilot")

    if question:

        st.session_state.copilot_history.append(("user", question))

        weekend_demand = data["rooms_sold"].tail(7).mean()

        if predicted_demand > weekend_demand:
            strategy = "aumentare i prezzi nei giorni di alta domanda"
        else:
            strategy = "mantenere prezzi competitivi"

        answer = f"""
Analisi AI completata.

Domanda prevista media: {predicted_demand:.0f} camere
Prezzo suggerito: {suggested_price:.0f} €

ADR attuale: {adr:.0f} €

Revenue stimato 365 giorni:
{total_revenue_365:,.0f} €

Strategia consigliata:
{strategy}
"""

        st.session_state.copilot_history.append(("ai", answer))

    for role, text in st.session_state.copilot_history:

        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(text)
