import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import asyncio
import aiohttp
from understat import Understat

st.set_page_config(page_title="ValueBet Finder mit xG", layout="centered")

st.title("⚽ Fußball ValueBet Finder")
st.markdown("**Automatischer Import von xG-Werten via Understat**")

# Unterstützte Teams (für Demo-Zwecke begrenzt – du kannst erweitern)
teams = [
    "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Real Madrid", "Barcelona",
    "Manchester City", "Liverpool", "Arsenal", "Juventus", "Inter", "AC Milan",
    "PSG", "Marseille", "Feyenoord", "Ajax", "Legia", "Lech Poznan"
]

seasons = [2023, 2022]

# Async Funktion zum Abrufen von Team-xG
async def get_team_avg_xg(team_name: str, season: int):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        matches = await understat.get_team_results(team_name, season)
        xg_for = [float(match['xG']) for match in matches]
        avg_xg = sum(xg_for) / len(xg_for) if xg_for else 0
        return round(avg_xg, 2)

def get_xg(team_name, season):
    return asyncio.run(get_team_avg_xg(team_name, season))

# UI
with st.form("value_form"):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Heimteam", teams)
        season = st.selectbox("Saison", seasons)
        home_odds = st.number_input("Quote Heimteam", min_value=1.01, step=0.01)
    with col2:
        away_team = st.selectbox("Auswärtsteam", teams)
        away_odds = st.number_input("Quote Auswärtsteam", min_value=1.01, step=0.01)

    st.markdown("### 🔄 Erwartete Tore automatisch laden")

    if st.form_submit_button("Lade xG-Werte automatisch"):
        with st.spinner("Hole xG-Daten von Understat..."):
            home_xg = get_xg(home_team, season)
            away_xg = get_xg(away_team, season)
            st.success(f"xG {home_team}: {home_xg} | xG {away_team}: {away_xg}")
    else:
        home_xg = st.number_input("Erwartete Tore Heimteam", min_value=0.0, step=0.1)
        away_xg = st.number_input("Erwartete Tore Auswärtsteam", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Berechne Value")

if submitted and home_xg and away_xg:
    st.markdown("### 📈 Ergebnisse")

    total = home_xg + away_xg
    p_home = home_xg / total
    p_away = away_xg / total

    fair_home_odds = 1 / p_home
    fair_away_odds = 1 / p_away

    value_home = (p_home * home_odds) - 1
    value_away = (p_away * away_odds) - 1

    st.write(f"**Faire Quote {home_team}:** {fair_home_odds:.2f}")
    st.write(f"**Faire Quote {away_team}:** {fair_away_odds:.2f}")
    st.write(f"**Value {home_team}:** {value_home*100:.2f}%")
    st.write(f"**Value {away_team}:** {value_away*100:.2f}%")

    if value_home > 0:
        st.success(f"✅ Value-Bet möglich auf: {home_team}")
    elif value_away > 0:
        st.success(f"✅ Value-Bet möglich auf: {away_team}")
    else:
        st.warning("❌ Keine Value-Bet identifiziert.")

