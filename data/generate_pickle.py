import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from collections import defaultdict
from data.stop import Stop
from data.MetroGraph import MetroGraph

# Chargement des fichiers GTFS
routes = pd.read_csv('IDFM-gtfs/routes.txt')
trips = pd.read_csv('IDFM-gtfs/trips.txt')
stop_times = pd.read_csv('IDFM-gtfs/stop_times.txt')
stops = pd.read_csv('IDFM-gtfs/stops.txt')
transfers = pd.read_csv('IDFM-gtfs/transfers.txt')

trips = trips.merge(routes[['route_id', 'route_short_name']], on='route_id', how='left')

# Étapes identiques à celles de votre notebook
metro_routes = routes[routes['route_type'] == 1]['route_id']
metro_trips = trips[trips['route_id'].isin(metro_routes)]
selected_trips = metro_trips.groupby(['route_short_name', 'direction_id']).head(16).reset_index()
stop_times = stop_times[stop_times['trip_id'].isin(selected_trips['trip_id'])]
stop_times = stop_times.sort_values(['trip_id', 'stop_sequence'])

def to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

stop_times['arr_sec'] = stop_times['arrival_time'].apply(to_seconds)
stop_times['dep_sec'] = stop_times['departure_time'].apply(to_seconds)

stops_metro = stops[stops['stop_id'].isin(stop_times['stop_id'])]
stops_commercial = stops_metro[stops_metro['location_type'] == 1][['stop_id', 'stop_name']]
parent_dict = stops_commercial.set_index('stop_id')['stop_name'].to_dict()

physical_stops = stops_metro[stops_metro["location_type"] == 0]
stop_dict = {}

for row in physical_stops.itertuples(index=False):
    name = parent_dict.get(row.parent_station, row.stop_name)
    accessible = True if row.wheelchair_boarding == 1 else False
    
    stop = Stop(row.stop_id, name, row.stop_lat, row.stop_lon, accessible)
    stop.parent_station = row.parent_station
    stop_dict[row.stop_id] = stop
    

stop_times = stop_times.merge(physical_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id', how='left')
stop_times = stop_times.sort_values(['trip_id', 'stop_sequence'])
stop_times['next_stop_id'] = stop_times.groupby('trip_id')['stop_id'].shift(-1)
stop_times['next_arr_sec'] = stop_times.groupby('trip_id')['arr_sec'].shift(-1)
stop_times['duration'] = stop_times['next_arr_sec'] - stop_times['dep_sec']
stop_times = stop_times.merge(trips[['trip_id', 'route_short_name']], on='trip_id', how='left')

edges = stop_times.dropna(subset=['next_stop_id']).copy()
edges['duration'] = edges['next_arr_sec'] - edges['dep_sec']
edges['u'] = edges['stop_id'].map(stop_dict)
edges['v'] = edges['next_stop_id'].map(stop_dict)

graph = defaultdict(dict)
for row in edges.itertuples(index=False):
    u, v, w, route = row.u, row.v, row.duration, row.route_short_name
    if pd.notnull(u) and pd.notnull(v):
        if v not in graph[u] or graph[u][v]["duration"] > w:
            graph[u][v] = {"duration": w, "routes": set([route])}
        else:
            graph[u][v]["routes"].add(route)
        
        if u not in graph[v] or graph[v][u]["duration"] > w:
            graph[v][u] = {"duration": w, "routes": set([route])}
        else:
            graph[v][u]["routes"].add(route)

transfers = transfers[transfers["transfer_type"] == 2]

for _, row in transfers.iterrows():
    from_stop = stop_dict.get(row["from_stop_id"])
    to_stop = stop_dict.get(row["to_stop_id"])
    duration = int(row["min_transfer_time"])

    if from_stop and to_stop and from_stop != to_stop:
        # Un seul sens (ou tu peux ajouter l'autre aussi)
        if to_stop not in graph[from_stop] or graph[from_stop][to_stop]["duration"] > duration:
            graph[from_stop][to_stop] = {"duration": duration, "routes": set(["transfer"])}

# Ajout des correspondances au DataFrame edges
transfer_rows = []

for _, row in transfers.iterrows():
    from_stop = stop_dict.get(row["from_stop_id"])
    to_stop = stop_dict.get(row["to_stop_id"])
    duration = int(row["min_transfer_time"])

    if from_stop and to_stop and from_stop != to_stop:
        # Graphe visuel (optionnel, pour debug)
        if to_stop not in graph[from_stop] or graph[from_stop][to_stop]["duration"] > duration:
            graph[from_stop][to_stop] = {"duration": duration, "routes": set(["transfer"])}

        # Graphe réel utilisé par MetroGraph
        transfer_rows.append({
            "stop_id": from_stop.id,
            "next_stop_id": to_stop.id,
            "duration": duration,
            "u": from_stop,
            "v": to_stop,
            "route_short_name": "transfer"
        })

# Fusion avec edges
if transfer_rows:
    transfers_df = pd.DataFrame(transfer_rows)
    edges = pd.concat([edges, transfers_df], ignore_index=True)

# 1. Construire les objets Stop commerciaux
commercial_stops_grouped = defaultdict(list)
for stop in stop_dict.values():
    parent_id = stop.parent_station or stop.id
    commercial_stops_grouped[parent_id].append(stop)

stop_commercial_dict = {}
for parent_id, group in commercial_stops_grouped.items():
    avg_lat = sum(s.lat for s in group) / len(group)
    avg_lon = sum(s.lon for s in group) / len(group)
    name = group[0].name
    accessible = any(s.accessible for s in group)
    commercial_stop = Stop(parent_id, name, avg_lat, avg_lon, accessible)
    stop_commercial_dict[parent_id] = commercial_stop

#======2======
graph_reduit = defaultdict(dict)

for u, voisins in graph.items():
    parent_u = u.parent_station or u.id
    stop_u = stop_commercial_dict[parent_u]

    for v, info in voisins.items():
        parent_v = v.parent_station or v.id
        stop_v = stop_commercial_dict[parent_v]

        if stop_u == stop_v:
            continue  # même station commerciale

        # éviter doublons et garder la meilleure durée
        if stop_v not in graph_reduit[stop_u] or info["duration"] < graph_reduit[stop_u][stop_v]["duration"]:
            graph_reduit[stop_u][stop_v] = {
                "duration": info["duration"],
                "routes": set(info["routes"])
            }
            graph_reduit[stop_v][stop_u] = {
                "duration": info["duration"],
                "routes": set(info["routes"])
            }


edges_reduits_rows = []

for stop1, voisins in graph_reduit.items():
    for stop2, info in voisins.items():
        if stop1.id >= stop2.id:
            continue  # éviter doublons (graph non orienté)

        edges_reduits_rows.append({
            "stop_id": stop1.id,
            "next_stop_id": stop2.id,
            "duration": info["duration"],
            "u": stop1,
            "v": stop2,
            "route_short_name": next(iter(info["routes"]))  # prendre une ligne arbitraire
        })

edges_reduits_df = pd.DataFrame(edges_reduits_rows)

# Création du MetroGraph
g = MetroGraph(stop_dict, edges)

# Sauvegarde dans le dossier data/
import pickle
with open("data/metro_graph.pkl", "wb") as f:
    pickle.dump(g, f)

print("✅ Graph généré et sauvegardé dans data/metro_graph.pkl")

g_reduit = MetroGraph(stop_commercial_dict, edges_reduits_df)

with open("data/metro_graph_reduit.pkl", "wb") as f:
    pickle.dump(g_reduit, f)

print("✅ Graphe réduit (stations commerciales uniquement) sauvegardé.")