import pandas as pd
from collections import defaultdict

# === 1. Chargement des fichiers GTFS ===
routes = pd.read_csv('IDFM-gtfs/routes.txt')
trips = pd.read_csv('IDFM-gtfs/trips.txt')
stop_times = pd.read_csv('IDFM-gtfs/stop_times.txt')
stops = pd.read_csv('IDFM-gtfs/stops.txt')

# === 2. Filtrage des lignes de métro ===
metro_routes = routes[routes['route_type'] == 1]['route_id']
metro_trips = trips[trips['route_id'].isin(metro_routes)]

# === 3. Sélection d'un trip par direction pour chaque ligne ===
selected_trips = metro_trips.groupby(['route_id', 'direction_id']).first().reset_index()

# === 4. Filtrer les stop_times avec les trips sélectionnés ===
stop_times = stop_times[stop_times['trip_id'].isin(selected_trips['trip_id'])]
stop_times = stop_times.sort_values(['trip_id', 'stop_sequence'])

# === 5. Conversion des horaires en secondes ===
def to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s

stop_times['arr_sec'] = stop_times['arrival_time'].apply(to_seconds)
stop_times['dep_sec'] = stop_times['departure_time'].apply(to_seconds)

# === 6. Joindre les noms d’arrêts ===
stop_times = stop_times.merge(stops[['stop_id', 'stop_name']], on='stop_id', how='left')

# === 7. Créer les transitions entre arrêts consécutifs ===
stop_times['next_stop_name'] = stop_times.groupby('trip_id')['stop_name'].shift(-1)
stop_times['next_arr_sec'] = stop_times.groupby('trip_id')['arr_sec'].shift(-1)

# === 8. Calcul de la durée entre deux arrêts consécutifs ===
edges = stop_times.dropna(subset=['next_stop_name'])
edges['duration'] = edges['next_arr_sec'] - edges['dep_sec']

# === 9. Préparation des arêtes (u, v, w) ===
edges = edges[['stop_name', 'next_stop_name', 'duration']]
edges.columns = ['u', 'v', 'w']

# === 10. Construction du graphe {station_u: {station_v: durée}} ===
graph = defaultdict(dict)
for row in edges.itertuples(index=False):
    u, v, w = row.u, row.v, row.w
    if v not in graph[u] or graph[u][v] > w:
        graph[u][v] = w
        graph[v][u] = w

# === 11. Exemple d'affichage ===
print(graph)