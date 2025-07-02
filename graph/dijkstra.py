import sys
import os

# Ajoute le dossier parent du dossier 'graph' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import pickle

# Initialiser les distances et prédécesseurs
def init_plus_court_chemin(s, graphe):
    d = {n: math.inf for n in graphe}
    d[s] = 0
    pred = {n: None for n in graphe}
    return d, pred

# Relaxation avec mise à jour du prédécesseur
def relaxation(graphe, x, y, d, pred):
    if d[y] > d[x] + graphe[x][y]["duration"]:
        d[y] = d[x] + graphe[x][y]["duration"]
        pred[y] = x

# Algorithme de Dijkstra
def dijkstra(graphe, s):
    d, pred = init_plus_court_chemin(s, graphe)
    T = set(graphe.keys())
    while T:
        x = min(T, key=lambda n: d[n])
        T.remove(x)
        for y in graphe[x]:
            if y in T:
                relaxation(graphe, x, y, d, pred)
    return d, pred

# Fonction pour reconstruire le chemin
def reconstruire_chemin(pred, s, v):
    chemin = []
    while v is not None:
        chemin.insert(0, v)
        v = pred[v]
    if chemin[0] == s:
        return chemin
    else:
        return []

# Exemple d'utilisation
graphe = {
    's1': {'s2': 7, 's5': 6, 's6': 2},
    's2': {'s1': 7, 's3': 4, 's5': 5},
    's3': {'s2': 4, 's4': 1, 's5': 2},
    's4': {'s3': 1, 's5': 3},
    's5': {'s1': 6, 's2': 5, 's3': 2, 's4': 3, 's6': 1},
    's6': {'s1': 2, 's5': 1}
}


path = os.path.join(os.path.dirname(__file__), "../data/metro_graph.pkl")
with open(path, "rb") as f:
    metroGraph = pickle.load(f)

source = metroGraph.get_stop_by_name('Châtelet')
distances, pred = dijkstra(metroGraph.graph, source)

# Affichage des résultats
'''
print(f"Plus courts chemins depuis {source} :")

for noeud in metroGraph.graph:
    chemin = reconstruire_chemin(pred, source, noeud)
    if chemin:
        chemin_str = " → ".join(str(stop) for stop in chemin)
        print(f"{source} → {noeud} = {distances[noeud]} | Chemin : {chemin_str}")
    else:
        print(f"{source} → {noeud} : pas de chemin")
'''
dest = metroGraph.get_stop_by_name('Nation')

chemin = reconstruire_chemin(pred, source, dest)
if chemin:
    chemin_str = " → ".join(str(stop) for stop in chemin)
    print(f"{source} → {dest} = {distances[dest]} | Chemin : {chemin_str}")
#print(metroGraph.graph)
