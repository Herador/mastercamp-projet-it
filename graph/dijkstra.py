import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.stop import Stop
import pickle
from data.MetroGraph import MetroGraph
#from graph import graph

# Fonction pour initialiser les distances
def init_plus_court_chemin(s, graphe):
    d = {n: math.inf for n in graphe}
    d[s] = 0
    return d

# Fonction de relaxation
def relaxation(graphe, x, y, d):
    if d[y] > d[x] + graphe[x][y]:
        d[y] = d[x] + graphe[x][y]

# Algorithme de Dijkstra
def dijkstra(graphe, s):
    d = init_plus_court_chemin(s, graphe)
    T = set(graphe.keys())
    F = []
    while T:
        # Choisir x avec la plus petite distance
        x = min(T, key=lambda n: d[n])
        F.append(x)
        T.remove(x)
        # Successeurs directs encore dans T
        successeurs = [y for y in graphe[x] if y in T]
        for y in successeurs:
            relaxation(graphe, x, y, d)
    return d

# Test
with open("data/metro_graph.pkl", "rb") as f:
    metroGraph = pickle.load(f)


source = metroGraph.get_stops_by_name('Châtelet')[0]
distances = dijkstra(metroGraph.graph, source)

# Affichage des résultats
print(f"Plus courts chemins depuis {source} :")
for noeud in metroGraph.graph:
    print(f"{source} → {noeud} = {distances[noeud]}")