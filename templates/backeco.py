import pickle
import sys
import os

# Ajoute le dossier parent du dossier 'graph' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
path = os.path.join(os.path.dirname(__file__), "../data/metro_graph.pkl")
with open(path, "rb") as f:
    G = pickle.load(f)

# ✅ Dictionnaire de correspondance normalisé → original
backend_names_map = {
    normalize_name(stop.name): stop.name
    for stop in G.stops.values()
    if stop.name
}

allowed_stations = set(backend_names_map.keys())
print("✅ Stations backend (normalisées) :", list(allowed_stations)[:10])

# CSV
df = pd.read_csv("data/qualite-de-lair-dans-le-reseau-de-transport-francilien.csv", sep=";")

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
    "faible": 2,
    "moyenne": 3,
    "eleve": 4,
    "forte": 4,
    "station aérienne": 1
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


# Ajout des pollutions au graphe
count = 0

for stop in G.stops.values():
    if stop.name in station_pollution:
        stop.pollution = station_pollution[stop.name]
        count += 1
print(f"Pollution ajouté à {count} stations.")

output_path = os.path.join(os.path.dirname(__file__), "../data/metro_graph_with_pollution.pkl")
with open(output_path, "wb") as f:
    pickle.dump(G, f)

print(f"✅ Graphe enrichi sauvegardé dans : {output_path}")