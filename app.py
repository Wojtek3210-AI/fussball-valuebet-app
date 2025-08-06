import streamlit as st
import asyncio
import aiohttp
from understat import Understat
import pandas as pd

st.set_page_config(page_title="ValueBet App mit Ligaauswahl", layout="centered")
st.title("⚽ Fußball ValueBet Finder mit Ligaauswahl")
st.markdown("Ermittle automatisch Value-Bets anhand von xG-Daten und Quoten.")

# Ligen in Understat
LEAGUES = {
    "🇩🇪 Bundesliga": "Bundesliga",
    "🏴 Premier League": "EPL",
    "🇪🇸 La Liga": "La_liga",
    "🇮🇹 Serie A": "Serie_A",
    "🇫🇷 Ligue 1": "Ligue_1",
    "🇷🇺 Russian Premier League": "RFPL"
}

SEASON = 2023  # letzte abgeschlossene Saison bei Understat (oft eine Verzögerung)

# Async Funktionen
async def get_league_matches(league_name, season):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        matches = await understat.get_matches(league_name, season)
        return matches

async def get_team_avg_xg(team_name, season):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        matches = await understat.get_team_results(team_name, season)
        xg_for = [float(match['xG']) for match in matches]
        return round(sum(xg_for) / len(xg_for), 2) if xg_for else 0.0

def load_matches_sync(league_code, season):
    return asyncio.run(get_league_matches(league_code, season))

def get_team_xg_sync(team_name, season):
    return asyncio.run(get_team_avg_xg(team_name, season))

# UI – Schritt 1: Liga wählen
league_display = st.selectbox("Wähle eine Liga", list(LEAGUES.keys()))
league_code = LEAGUES[league_display]

# Schritt 2: Spiel wählen
st.markdown("### 📆 Spielauswahl")
matches = load_matches_sync(league_code, SEASON)
match_options = [f"{m['h']['title']} vs {m['a']['title']} ({m['datetime'][:10]})" for m in matches]
selected_match = st.selectbox("Wähle ein Spiel", match_options)

# Match extrahieren
match_data = matches[match_options.index(selected_match)]
home_team = match_data['h']['title']
away_team = match_data['a']['title']

# Schritt 3: Quoten eingeben
st.markdown("### 💰 Quoten eingeben")
col1, col2 = st.columns(2)
with col1:
    home_odds = st.number_input(f"Quote für {home_team}", min_value=1.01, step=0.01)
with col2:
    away_odds = st.number_input(f"Quote für {away_team}", min_value=1.01, step=0.01)

# Schritt 4: Value-Berechnung
if st.button("🔍 Berechne Value und Prognose"):
    with st.spinner("Hole xG-Daten..."):
        home_xg = get_team_xg_sync(home_team, SEASON)
        away_xg = get_team_xg_sync(away_team, SEASON)

    st.markdown(f"**xG {home_team}:** {home_xg} | **xG {away_team}:** {away_xg}")

    total_xg = home_xg + away_xg
    p_home = home_xg / total_xg
    p_away = away_xg / total_xg

    fair_home_odds = 1 / p_home
    fair_away_odds = 1 / p_away

    value_home = (p_home * home_odds) - 1
    value_away = (p_away * away_odds) - 1

    st.markdown("### 📈 Ergebnisse")

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

    if p_home > p_away:
        st.info(f"📊 Prognose: **{home_team}** wird mit höherer Wahrscheinlichkeit gewinnen.")
    else:
        st.info(f"📊 Prognose: **{away_team}** wird mit höherer Wahrscheinlichkeit gewinnen.")
