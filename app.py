# app.py – Erweiterte Fußball Value Bet App mit Top-Ligen und CL/EL

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# -------------------------------
# LIGEN-LISTE
# -------------------------------
ligen = [
    "Bundesliga",
    "Premier League",
    "La Liga",
    "Serie A",
    "Ligue 1",
    "Ekstraklasa",
    "Champions League",
    "Europa League",
    "Conference League"
]

# -------------------------------
# FUNKTION: Berechne Gewinnwahrscheinlichkeit und Value
# -------------------------------
def berechne_value(erwartete_tore_heim, erwartete_tore_ausw, quote_1, quote_x, quote_2):
    # Einfache Modellierung basierend auf Torverhältnis
    tor_diff = erwartete_tore_heim - erwartete_tore_ausw
    
    # Schätze Wahrscheinlichkeiten grob
    p_1 = min(max(0.4 + 0.1 * tor_diff, 0.05), 0.9)
    p_2 = min(max(0.4 - 0.1 * tor_diff, 0.05), 0.9)
    p_x = 1 - p_1 - p_2
    
    # Fair Quoten
    fair_1 = 1 / p_1
    fair_x = 1 / p_x
    fair_2 = 1 / p_2

    # Value berechnen
    value_1 = (p_1 * quote_1) - 1
    value_x = (p_x * quote_x) - 1
    value_2 = (p_2 * quote_2) - 1

    return {
        "Wahrscheinlichkeiten": {"1": round(p_1, 2), "X": round(p_x, 2), "2": round(p_2, 2)},
        "Faire Quoten": {"1": round(fair_1, 2), "X": round(fair_x, 2), "2": round(fair_2, 2)},
        "Value": {"1": round(value_1, 2), "X": round(value_x, 2), "2": round(value_2, 2)}
    }

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="Fussball Value Bet App", layout="centered")
st.title("⚽ Fussball Value Bet Rechner")

liga = st.selectbox("Wähle eine Liga oder Wettbewerb:", ligen)
st.markdown(f"**Ausgewählte Liga:** {liga}")

st.subheader("🔢 Erwartete Tore")
erwartete_tore_heim = st.number_input("Erwartete Tore Heim", value=1.5, step=0.1)
erwartete_tore_ausw = st.number_input("Erwartete Tore Auswärts", value=1.2, step=0.1)

st.subheader("💸 Buchmacherquoten")
quote_1 = st.number_input("Quote Heimsieg (1)", value=2.2)
quote_x = st.number_input("Quote Unentschieden (X)", value=3.3)
quote_2 = st.number_input("Quote Auswärtssieg (2)", value=3.0)

if st.button("🔍 Prognose & Value berechnen"):
    result = berechne_value(erwartete_tore_heim, erwartete_tore_ausw, quote_1, quote_x, quote_2)

    st.success("Ergebnisse:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔮 Wahrscheinlichkeit 1", f"{result['Wahrscheinlichkeiten']['1']*100:.1f}%")
        st.metric("🎯 Faire Quote 1", result['Faire Quoten']['1'])
        st.metric("💰 Value 1", result['Value']['1'])
    
    with col2:
        st.metric("🔮 Wahrscheinlichkeit X", f"{result['Wahrscheinlichkeiten']['X']*100:.1f}%")
        st.metric("🎯 Faire Quote X", result['Faire Quoten']['X'])
        st.metric("💰 Value X", result['Value']['X'])

    with col3:
        st.metric("🔮 Wahrscheinlichkeit 2", f"{result['Wahrscheinlichkeiten']['2']*100:.1f}%")
        st.metric("🎯 Faire Quote 2", result['Faire Quoten']['2'])
        st.metric("💰 Value 2", result['Value']['2'])

    best = max(result['Value'], key=result['Value'].get)
    if result['Value'][best] > 0:
        st.success(f"👉 Potenzielle Value-Bet: **{best}**")
    else:
        st.info("Keine Value-Bet gefunden bei diesen Quoten.")
