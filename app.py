import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI Revenue Engine", layout="wide")

st.title("🏨 AI Revenue Engine")
st.subheader("AI Revenue Management Dashboard")

uploaded_file = st.file_uploader("Carica dati hotel CSV", type="csv")

if uploaded_file:

    data = pd.read_csv(uploaded_file)

    data["occupancy"] = data["rooms_sold"] / data["rooms_available"]

    avg_occ = data["occupancy"].mean()*100
    adr = data["ADR"].mean()
    revpar = adr * (avg_occ/100)

    st.header("KPI Hotel")

    col1, col2, col3 = st.columns(3)

    col1.metric("Occupancy", f"{avg_occ:.1f}%")
    col2.metric("ADR", f"{adr:.0f}€")
    col3.metric("RevPAR", f"{revpar:.0f}€")

    st.header("Trend prenotazioni")

    st.line_chart(data["rooms_sold"])

    st.header("Trend occupazione")

    st.line_chart(data["occupancy"])

    data["day"] = np.arange(len(data))

    X = data[["day"]]
    y = data["rooms_sold"]

    model = LinearRegression()
    model.fit(X,y)

    future_days = np.arange(len(data), len(data)+365).reshape(-1,1)

    forecast = model.predict(future_days)

    st.header("Forecast domanda 30 giorni")

    st.line_chart(forecast)

    predicted_demand = forecast.mean()

    if predicted_demand > 90:
        suggested_price = adr * 1.25
        alert = "Alta domanda prevista: aumentare prezzi"
    elif predicted_demand > 75:
        suggested_price = adr * 1.15
        alert = "Domanda stabile"
    else:
        suggested_price = adr * 0.9
        alert = "Domanda debole: ridurre prezzi"

    occupancy_forecast = predicted_demand / data["rooms_available"].iloc[0]

    revpar_forecast = suggested_price * occupancy_forecast

    # Competitor pricing simulation

    competitor_price = adr * 1.1

    st.subheader("Analisi Competitor")

    st.metric("Prezzo medio competitor", f"{competitor_price:.0f}€")

   if suggested_price < competitor_price:
    st.warning("Prezzo sotto la media competitor")
   else:
    st.success("Prezzo competitivo rispetto al mercato")


    st.header("AI Pricing Recommendation")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Occupancy", f"{avg_occ:.1f}%")
    col2.metric("ADR", f"{adr:.0f}€")
    col3.metric("RevPAR", f"{revpar:.0f}€")
    col4.metric("Forecast Demand", f"{predicted_demand:.0f}")

    
    

    st.success(alert)

    st.header("Simulatore prezzo")

    new_price = st.slider("Simula prezzo camera", 50, 400, int(suggested_price))

    rooms = data["rooms_available"].iloc[0]

    simulated_revenue = new_price * rooms * occupancy_forecast

    st.metric("Revenue stimato", f"{simulated_revenue:.0f}€")


    simulated_revpar = new_price * occupancy_forecast

    st.metric("RevPAR simulato", f"{simulated_revpar:.0f}€")


