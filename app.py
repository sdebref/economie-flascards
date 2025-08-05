import streamlit as st
import json
from pathlib import Path
import random

st.set_page_config(page_title="Economie Coach – Begrippen Flashcards", layout="wide")
st.title("🧠 Begrippen Oefenen – Flashcards")

# Themabestand mapping
begrip_bestanden = {
    "Thema 1: Consument & Producent": "data/begrippen_t1.json",
    "Thema 2: Werking van een onderneming": "data/begrippen_t2.json",
    "Thema 3: Boekhoudkundig beheer": "data/begrippen_t3.json",
    "Thema 4: Personeelsbeheer": "data/begrippen_t4.json",
    "Thema 5: Logistiek & Transport": "data/begrippen_t5.json"
}

st.sidebar.header("📚 Kies een thema")
gekozen_thema = st.sidebar.selectbox("Welk thema wil je oefenen?", list(begrip_bestanden.keys()))

# Richting instellen
richting = st.sidebar.radio("Oefenrichting:", ["Begrip ➝ Uitleg", "Uitleg ➝ Begrip"])

# Begrippenlijst laden
def laad_begrippenlijst(pad):
    try:
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Kon begrippenlijst niet laden: {e}")
        return []

pad = begrip_bestanden[gekozen_thema]
begrippen = laad_begrippenlijst(pad)

if begrippen:
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.volgorde = random.sample(begrippen, len(begrippen))
        st.session_state.score = []

    kaart = st.session_state.volgorde[st.session_state.index]
    vraag = kaart["begrip"] if richting == "Begrip ➝ Uitleg" else kaart["uitleg"]
    antwoord = kaart["uitleg"] if richting == "Begrip ➝ Uitleg" else kaart["begrip"]

    st.subheader("🔹 Vraag:")
    st.markdown(f"### {vraag}")

    if st.button("💡 Toon antwoord"):
        st.markdown(f"**Antwoord:** {antwoord}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Ik wist dit"):
                st.session_state.score.append((vraag, True))
                st.session_state.index += 1
        with col2:
            if st.button("❌ Ik wist dit niet"):
                st.session_state.score.append((vraag, False))
                st.session_state.index += 1

    st.progress(st.session_state.index / len(begrippen))

    if st.session_state.index >= len(begrippen):
        juist = sum(1 for _, correct in st.session_state.score if correct)
        totaal = len(st.session_state.score)
        st.success(f"🎉 Je bent klaar! Eindscore: {juist} op {totaal}")
        if st.button("🔁 Opnieuw starten"):
            del st.session_state.index
            del st.session_state.score
            del st.session_state.volgorde
else:
    st.warning("⚠️ Geen begrippenlijst beschikbaar voor dit thema.")