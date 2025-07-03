import pandas as pd
import requests
import unicodedata
import re
import json

def normalize_name(name):
    name = name.strip().lower()
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r"[’'`]", "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# Backend
response = requests.get("http://localhost:80/stops")
data = response.json()

# ✅ Dictionnaire de correspondance normalisé → original
backend_names_map = {
    normalize_name(stop["name"]): stop["name"]
    for stop in data
    if stop.get("name")
}

allowed_stations = set(backend_names_map.keys())
print("✅ Stations backend (normalisées) :", list(allowed_stations)[:10])

# CSV
df = pd.read_csv("../data/qualite-de-lair-dans-le-reseau-de-transport-francilien.csv", sep=";")

csv_stations = set()
for _, row in df.iterrows():
    station = row["Nom de la Station"]
    if isinstance(station, str):
        csv_stations.add(normalize_name(station))

print("📄 Stations CSV (normalisées) :", list(csv_stations)[:10])

# Intersection
intersection = allowed_stations.intersection(csv_stations)
print("🔎 Intersection (stations communes) :", list(intersection)[:10])

pollution_map = {
    "faible": 1,
    "moyenne": 2,
    "élevée": 3,
    "forte": 3,
    "station aérienne": 0
}

station_pollution = {}

for _, row in df.iterrows():
    niveau = row["Niveau de pollution"]
    station = row["Nom de la Station"]

    if isinstance(niveau, str) and isinstance(station, str):
        niveau_clean = niveau.strip().lower()
        station_clean = normalize_name(station)

        if station_clean in intersection and niveau_clean in pollution_map:
            if station_clean in backend_names_map:
                original_name = backend_names_map[station_clean]
                station_pollution[original_name] = pollution_map[niveau_clean]

# ✅ Affichage final
for station, value in station_pollution.items():
    print(f"Station: {station}, Pollution: {value}")

# ✅ Sauvegarde
with open("station_pollution.json", "w", encoding="utf-8") as f:
    json.dump(station_pollution, f, ensure_ascii=False, indent=2)

print("✅ Dictionnaire sauvegardé dans 'station_pollution.json'.")
