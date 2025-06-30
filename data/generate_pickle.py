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

# Étapes identiques à celles de votre notebook
metro_routes = routes[routes['route_type'] == 1]['route_id']
metro_trips = trips[trips['route_id'].isin(metro_routes)]
selected_trips = metro_trips.groupby(['route_id', 'direction_id']).head(16).reset_index()
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
    key = row.parent_station if pd.notna(row.parent_station) else row.stop_id
    if key not in stop_dict:
        stop_dict[row.stop_id] = Stop(key, name, row.stop_lat, row.stop_lon)

stop_times = stop_times.merge(physical_stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id', how='left')
stop_times = stop_times.sort_values(['trip_id', 'stop_sequence'])
stop_times['next_stop_id'] = stop_times.groupby('trip_id')['stop_id'].shift(-1)
stop_times['next_arr_sec'] = stop_times.groupby('trip_id')['arr_sec'].shift(-1)
stop_times['duration'] = stop_times['next_arr_sec'] - stop_times['dep_sec']

edges = stop_times.dropna(subset=['next_stop_id']).copy()
edges['duration'] = edges['next_arr_sec'] - edges['dep_sec']
edges['u'] = edges['stop_id'].map(stop_dict)
edges['v'] = edges['next_stop_id'].map(stop_dict)

graph = defaultdict(dict)
for row in edges.itertuples(index=False):
    u, v, w = row.u, row.v, row.duration
    if pd.notnull(u) and pd.notnull(v):
        if v not in graph[u] or graph[u][v] > w:
            graph[u][v] = w
            graph[v][u] = w

# Création du MetroGraph
g = MetroGraph(stop_dict, edges)

# Sauvegarde dans le dossier data/
import pickle
with open("data/metro_graph.pkl", "wb") as f:
    pickle.dump(g, f)

print("✅ Graph généré et sauvegardé dans data/metro_graph.pkl")
