import pandas as pd
import requests
import unicodedata
import re

def normalize_name(name):
    name = name.strip().lower()
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r"[’'`]", "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# Backend
response = requests.get("http://localhost/stops")
data = response.json()
allowed_stations = set(normalize_name(stop["name"]) for stop in data if stop.get("name"))

print("✅ Stations backend (normalisées) :", list(allowed_stations)[:20])

# CSV
df = pd.read_csv("../data/qualite-de-lair-dans-le-reseau-de-transport-francilien.csv", sep=";")

csv_stations = set()
for _, row in df.iterrows():
    station = row["Nom de la Station"]
    if isinstance(station, str):
        csv_stations.add(normalize_name(station))

print("📄 Stations CSV (normalisées) :", list(csv_stations)[:20])

# Intersection
intersection = allowed_stations.intersection(csv_stations)
print("🔎 Intersection (stations communes) :", list(intersection)[:20])

pollution_map = {
    "pollution faible": 1,
    "pollution moyenne": 2,
    "pollution élevée": 3,
    "pollution forte": 3,
    "station aérienne": 0
}

station_pollution = {}

for _, row in df.iterrows():
    niveau = row["Niveau de pollution"]
    station = row["Nom de la Station"]

    if isinstance(niveau, str) and isinstance(station, str):
        niveau_clean = niveau.strip().lower()
        station_clean = normalize_name(station)

        print(f"Test station: {station_clean}, niveau: {niveau_clean}")

        if station_clean in intersection and niveau_clean in pollution_map:
            station_pollution[station_clean] = pollution_map[niveau_clean]

if station_pollution:
    print("✅ Dictionnaire pollution (extrait) :", list(station_pollution.items())[:60])
else:
    print("❌ Aucun résultat — aucune station matchée.")




