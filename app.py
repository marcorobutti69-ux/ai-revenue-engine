import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="AI Revenue Engine PRO", layout="wide")

# ---------------------------
# DATABASE
# ---------------------------

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT,
hotel TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hotel_data(
hotel TEXT,
date TEXT,
rooms_available INTEGER,
rooms_sold INTEGER,
ADR REAL
)
""")

conn.commit()

# ---------------------------
# LOGIN
# ---------------------------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("AI Revenue Engine")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        ).fetchone()

        if user:

            st.session_state.login = True
            st.session_state.hotel = user[3]

        else:

            st.error("Credenziali non valide")

    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Forecast",
        "Pricing Engine",
        "Revenue Forecast",
        "AI Copilot"
    ]
)

st.sidebar.write("Hotel:", st.session_state.hotel)

# ---------------------------
# UPLOAD DATA
# ---------------------------

uploaded_file = st.sidebar.file_uploader("Carica dati hotel CSV", type="csv")

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    df["hotel"] = st.session_state.hotel

    df.to_sql("hotel_data", conn, if_exists="append", index=False)

    st.sidebar.success("Dati caricati")

# ---------------------------
# LOAD DATA
# ---------------------------

data = pd.read_sql(
    f"SELECT * FROM hotel_data WHERE hotel='{st.session_state.hotel}'",
    conn
)

if len(data) == 0:

    st.title("Nessun dato hotel")

    st.info("Carica un CSV per iniziare")

    st.stop()

data["date"] = pd.to_datetime(data["date"])

# ---------------------------
# KPI
# ---------------------------

data["occupancy"] = data["rooms_sold"] / data["rooms_available"]

avg_occ = data["occupancy"].mean()*100
adr = data["ADR"].mean()
revpar = adr*(avg_occ/100)

rooms = data["rooms_available"].iloc[0]

# ---------------------------
# FORECAST AI
# ---------------------------

data["day"] = np.arange(len(data))

X = data[["day"]]
y = data["rooms_sold"]

model = LinearRegression()
model.fit(X,y)

future_days = np.arange(len(data), len(data)+365).reshape(-1,1)

forecast = model.predict(future_days)

predicted_demand = forecast.mean()

# ---------------------------
# PRICING ENGINE
# ---------------------------

if predicted_demand > 90:
    suggested_price = adr*1.2
elif predicted_demand > 75:
    suggested_price = adr*1.1
else:
    suggested_price = adr*0.9

occupancy_forecast = predicted_demand/rooms

# ---------------------------
# REVENUE FORECAST
# ---------------------------

forecast_revenue = forecast*suggested_price

total_revenue_365 = forecast_revenue.sum()

# ---------------------------
# DASHBOARD
# ---------------------------

if menu == "Dashboard":

    st.title("Revenue Dashboard")

    col1,col2,col3 = st.columns(3)

    col1.metric("Occupancy", f"{avg_occ:.1f}%")
    col2.metric("ADR", f"{adr:.0f}€")
    col3.metric("RevPAR", f"{revpar:.0f}€")

    fig = px.line(data, x="date", y="rooms_sold", title="Trend prenotazioni")

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# FORECAST
# ---------------------------

elif menu == "Forecast":

    st.title("Demand Forecast 365 giorni")

    forecast_df = pd.DataFrame({
        "day":future_days.flatten(),
        "forecast":forecast
    })

    fig = px.line(forecast_df, x="day", y="forecast")

    st.plotly_chart(fig, use_container_width=True)

    st.metric("Domanda prevista media", f"{predicted_demand:.0f} camere")

# ---------------------------
# PRICING ENGINE
# ---------------------------

elif menu == "Pricing Engine":

    st.title("AI Pricing Engine")

    col1,col2 = st.columns(2)

    col1.metric("ADR attuale", f"{adr:.0f}€")
    col2.metric("Prezzo suggerito AI", f"{suggested_price:.0f}€")

    competitor_price = adr*1.1

    st.metric("Prezzo competitor medio", f"{competitor_price:.0f}€")

    if suggested_price < competitor_price:
        st.warning("Prezzo sotto mercato")
    else:
        st.success("Prezzo competitivo")

    new_price = st.slider("Simula nuovo prezzo",50,400,int(suggested_price))

    simulated_revenue = new_price*rooms*occupancy_forecast

    st.metric("Revenue simulato", f"{simulated_revenue:.0f}€")

# ---------------------------
# REVENUE FORECAST
# ---------------------------

elif menu == "Revenue Forecast":

    st.title("Revenue Forecast 365 giorni")

    revenue_df = pd.DataFrame({
        "day":future_days.flatten(),
        "revenue":forecast_revenue
    })

    fig = px.line(revenue_df, x="day", y="revenue")

    st.plotly_chart(fig, use_container_width=True)

    st.metric("Revenue previsto anno", f"{total_revenue_365:,.0f}€")

# ---------------------------
# AI REVENUE COPILOT
# ---------------------------

elif menu == "AI Copilot":

    st.title("AI Revenue Copilot")

    if "chat" not in st.session_state:
        st.session_state.chat=[]

    question = st.chat_input("Fai una domanda al Revenue Copilot")

    if question:

        st.session_state.chat.append(("user",question))

        answer = f"""
Analisi AI completata.

Domanda prevista media:
{predicted_demand:.0f} camere

Prezzo suggerito:
{suggested_price:.0f} €

Revenue previsto 365 giorni:
{total_revenue_365:,.0f} €

Strategia suggerita:
aumentare prezzi nei giorni con alta domanda.
"""

        st.session_state.chat.append(("ai",answer))

    for role,text in st.session_state.chat:

        with st.chat_message("user" if role=="user" else "assistant"):
            st.write(text)
            
