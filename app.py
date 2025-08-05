import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Economie Flashcards v3", layout="wide")
st.title("🧠 Begrippen Oefenen – Flashcards v3")

# Themabestand mapping
begrip_bestanden = {
    "Thema 1: Consument & Producent": "data/begrippen_t1.json",
    "Thema 2: Werking van een onderneming": "data/begrippen_t2.json",
    "Thema 3: Boekhoudkundig beheer": "data/begrippen_t3.json",
    "Thema 4: Personeelsbeheer": "data/begrippen_t4.json",
    "Thema 5: Logistiek & Transport": "data/begrippen_t5.json"
}

# Instellingen
st.sidebar.header("Instellingen")
gekozen_thema = st.sidebar.selectbox("Welk thema wil je oefenen?", list(begrip_bestanden.keys()))
richting = st.sidebar.radio("Oefenrichting:", ["Begrip ➝ Uitleg", "Uitleg ➝ Begrip"])
sessiegrootte = st.sidebar.selectbox("Aantal kaarten in deze sessie:", [5, 10, 20])

# Paden
begrip_pad = Path(begrip_bestanden[gekozen_thema])
voortgang_pad = Path(f"data/voortgang_{gekozen_thema[-2:].lower()}.json")

def laad_json(pad):
    if pad.exists():
        with open(pad, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def bewaar_json(pad, data):
    with open(pad, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Slimme selectie
def selecteer_begrippen(begrippen, voortgang, aantal):
    stats = {b["begrip"]: {"teller": 0, "fouten": 0} for b in begrippen}
    for sessie in voortgang:
        begrip = sessie["begrip"]
        stats[begrip]["teller"] += 1
        if not sessie["correct"]:
            stats[begrip]["fouten"] += 1
    gesorteerd = sorted(begrippen, key=lambda b: (stats[b["begrip"]]["teller"], -stats[b["begrip"]]["fouten"]))
    return random.sample(gesorteerd[:max(aantal*2, len(gesorteerd))], min(aantal, len(gesorteerd)))

# Data laden
begrippen = laad_json(begrip_pad)
voortgang = laad_json(voortgang_pad)

# Sessielogica
if begrippen:
    if "sessie" not in st.session_state:
        geselecteerde = selecteer_begrippen(begrippen, voortgang, sessiegrootte)
        st.session_state.sessie = {
            "origineel": geselecteerde,
            "queue": geselecteerde.copy(),
            "fouten": [],
            "resultaten": [],
            "id": datetime.now().isoformat()
        }

    sessie = st.session_state.sessie
    if sessie["queue"]:
        kaart = sessie["queue"][0]
        vraag = kaart["begrip"] if richting == "Begrip ➝ Uitleg" else kaart["uitleg"]
        antwoord = kaart["uitleg"] if richting == "Begrip ➝ Uitleg" else kaart["begrip"]

        st.subheader(f"🔹 Volgende vraag ({len(sessie['origineel']) - len(sessie['queue']) + 1}/{len(sessie['origineel'])})")
        st.markdown(f"### {vraag}")

        if st.button("💡 Toon antwoord"):
            st.markdown(f"**Antwoord:** {antwoord}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Ik wist dit"):
                    sessie["resultaten"].append({
                        "sessie": sessie["id"],
                        "begrip": kaart["begrip"],
                        "tijd": datetime.now().isoformat(),
                        "poging": sessie["resultaten"].count(kaart["begrip"]) + 1,
                        "correct": True
                    })
                    sessie["queue"].pop(0)
            with col2:
                if st.button("❌ Ik wist dit niet"):
                    sessie["resultaten"].append({
                        "sessie": sessie["id"],
                        "begrip": kaart["begrip"],
                        "tijd": datetime.now().isoformat(),
                        "poging": sessie["resultaten"].count(kaart["begrip"]) + 1,
                        "correct": False
                    })
                    sessie["queue"].append(sessie["queue"].pop(0))

        st.progress((len(sessie["origineel"]) - len(sessie["queue"])) / len(sessie["origineel"]))

    else:
        st.success("🎉 Je hebt alles juist beantwoord!")
        voortgang.extend(sessie["resultaten"])
        bewaar_json(voortgang_pad, voortgang)
        if st.button("🔁 Nieuwe sessie starten"):
            del st.session_state.sessie

# Overzicht
st.markdown("---")
if st.checkbox("📋 Toon overzicht van alle begrippen en prestaties"):
    if voortgang:
        df = pd.DataFrame(voortgang)
        df["tijd"] = pd.to_datetime(df["tijd"])
        overzicht = df.groupby("begrip").agg(
            aantal_keer=("correct", "count"),
            aantal_juist=("correct", "sum"),
            laatste_keertje=("tijd", "max"),
            pogingen_tot_juist=("correct", lambda x: next((i+1 for i, v in enumerate(x[::-1]) if v), None))
        ).reset_index()
        overzicht["aantal_fout"] = overzicht["aantal_keer"] - overzicht["aantal_juist"]
        st.dataframe(overzicht.sort_values("aantal_keer", ascending=False))
    else:
        st.info("Nog geen voortgangsgegevens beschikbaar.")