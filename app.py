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

st.subheader("AI Revenue Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Fai una domanda sul revenue dell'hotel")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    if "prezzo" in user_input.lower():
        response = f"Il prezzo suggerito è circa {suggested_price:.0f}€"

    elif "domanda" in user_input.lower():
        response = f"La domanda prevista media è {predicted_demand:.0f} camere"

    elif "revenue" in user_input.lower():
        response = f"Il revenue stimato annuale è {total_revenue_365:,.0f}€"

    else:
        response = "Posso aiutarti con forecast domanda, prezzo suggerito o revenue previsto."

    st.session_state.messages.append({"role": "assistant", "content": response})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

st.subheader("AI Revenue Manager")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.chat_input("Chiedi all'AI Revenue Manager")

if question:

    st.session_state.chat_history.append(("user", question))

    if "prezzo" in question.lower():

        answer = f"""
Analisi AI completata.

Domanda prevista: {predicted_demand:.0f} camere

Prezzo suggerito: {suggested_price:.0f} €

Strategia:
la domanda prevista è alta quindi suggerisco un aumento del prezzo.
"""

    elif "domanda" in question.lower():

        answer = f"""
Forecast domanda generato.

Domanda media prevista: {predicted_demand:.0f} camere

Suggerimento:
monitorare occupazione e aumentare i prezzi nei giorni con domanda alta.
"""

    elif "revenue" in question.lower():

        answer = f"""
Revenue forecast calcolato.

Revenue stimato 365 giorni:
{total_revenue_365:,.0f} €

Suggerimento AI:
ottimizzare prezzi nei periodi di alta domanda.
"""

    elif "strategia" in question.lower():

        answer = f"""
Strategia Revenue AI:

• prezzo medio attuale: {adr:.0f} €
• prezzo suggerito: {suggested_price:.0f} €
• domanda prevista: {predicted_demand:.0f} camere

Consiglio:
incremento prezzo nelle date con alta domanda.
"""

    else:

        answer = """
Posso aiutarti con:

• prezzo consigliato
• domanda prevista
• revenue stimato
• strategia revenue
"""

    st.session_state.chat_history.append(("ai", answer))

for role, text in st.session_state.chat_history:

    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(text)

st.subheader("AI Revenue Copilot")

if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = []

question = st.chat_input("Chiedi all'AI Revenue Copilot")

if question:

    st.session_state.copilot_history.append(("user", question))

    # analisi AI semplice

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

Suggerimento AI:
monitorare i giorni con occupazione alta e aumentare gradualmente il prezzo.
"""

    st.session_state.copilot_history.append(("ai", answer))

for role, text in st.session_state.copilot_history:

    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(text)

