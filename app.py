import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="Economie Flashcards v4", layout="wide")
st.title("🧠 Begrippen Oefenen – Flashcards v4")

begrip_bestanden = {
    "Thema 1: Consument & Producent": "data/begrippen_t1.json",
    "Thema 2: Werking van een onderneming": "data/begrippen_t2.json",
    "Thema 3: Boekhoudkundig beheer": "data/begrippen_t3.json",
    "Thema 4: Personeelsbeheer": "data/begrippen_t4.json",
    "Thema 5: Logistiek & Transport": "data/begrippen_t5.json"
}

st.sidebar.header("Instellingen")
gekozen_thema = st.sidebar.selectbox("Welk thema wil je oefenen?", list(begrip_bestanden.keys()))
richting = st.sidebar.radio("Oefenrichting:", ["Begrip ➝ Uitleg", "Uitleg ➝ Begrip"])
sessiegrootte = st.sidebar.selectbox("Aantal kaarten in deze sessie:", [5, 10, 20])

begrip_pad = Path(begrip_bestanden[gekozen_thema])

def laad_json(pad):
    if pad.exists():
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def bewaar_json(pad, data):
    with open(pad, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def prioriteit(kaart):
    if kaart["laatste_keer_juist"]:
        laatst = datetime.fromisoformat(kaart["laatste_keer_juist"])
        due = laatst + timedelta(days=kaart["interval"])
        return (datetime.now() - due).total_seconds() + kaart["teller_fout"] * 1000
    else:
        return 1e6  # prioriteit voor nieuwe kaarten

def genereer_audio(text):
    tts = gTTS(text, lang='nl')
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer

# Data laden
begrippen = laad_json(begrip_pad)
begrippen = sorted(begrippen, key=prioriteit, reverse=True)[:sessiegrootte]

if begrippen:
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.herhaal = []
        st.session_state.volgorde = begrippen.copy()
        random.shuffle(st.session_state.volgorde)

    if st.session_state.volgorde:
        kaart = st.session_state.volgorde[0]
        vraag = kaart["begrip"] if richting == "Begrip ➝ Uitleg" else kaart["uitleg"]
        antwoord = kaart["uitleg"] if richting == "Begrip ➝ Uitleg" else kaart["begrip"]

        st.subheader(f"🔹 Vraag {st.session_state.index + 1}")
        col1, col2 = st.columns([8,1])
        with col1:
            st.markdown(f"### {vraag}")
        with col2:
            if st.button("🔊", key="vraag_audio"):
                st.audio(genereer_audio(vraag), format="audio/mp3")

        if st.button("💡 Toon antwoord"):
            cola, colb = st.columns([8,1])
            with cola:
                st.markdown(f"**Antwoord:** {antwoord}")
            with colb:
                if st.button("🔊", key="antwoord_audio"):
                    st.audio(genereer_audio(antwoord), format="audio/mp3")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Ik wist dit"):
                    kaart["teller_juist"] += 1
                    kaart["laatste_keer_juist"] = datetime.now().isoformat()
                    kaart["interval"] = min(karte["interval"] * 2, 30)
                    st.session_state.volgorde.pop(0)
                    st.session_state.index += 1
                with c2:
                    if st.button("❌ Ik wist dit niet"):
                        kaart["teller_fout"] += 1
                        kaart["interval"] = 1
                        st.session_state.volgorde.append(st.session_state.volgorde.pop(0))

        st.progress(st.session_state.index / sessiegrootte)

    else:
        bewaar_json(begrip_pad, begrippen)
        st.success("🎉 Alle begrippen juist beantwoord!")
        if st.button("🔁 Opnieuw starten"):
            del st.session_state.index
            del st.session_state.herhaal
            del st.session_state.volgorde