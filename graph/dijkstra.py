import math

# Initialiser les distances et prédécesseurs
def init_plus_court_chemin(s, graphe):
    d = {n: math.inf for n in graphe}
    d[s] = 0
    pred = {n: None for n in graphe}
    return d, pred

# Relaxation avec mise à jour du prédécesseur
def relaxation(graphe, x, y, d, pred):
    if d[y] > d[x] + graphe[x][y]:
        d[y] = d[x] + graphe[x][y]
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

source = 's1'
distances, pred = dijkstra(graphe, source)

# Affichage des résultats
print(f"Plus courts chemins depuis {source} :")
for noeud in graphe:
    chemin = reconstruire_chemin(pred, source, noeud)
    if chemin:
        chemin_str = " → ".join(chemin)
        print(f"{source} → {noeud} = {distances[noeud]} | Chemin : {chemin_str}")
    else:
        print(f"{source} → {noeud} : pas de chemin")

#for noeud in metroGraph.graph:
 #   print(f"{source} → {noeud} = {distances[noeud]}")