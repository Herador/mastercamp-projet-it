import math

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
distances = dijkstra(graphe, source)

# Affichage des résultats
print(f"Plus courts chemins depuis {source} :")
for noeud in graphe:
    print(f"{source} → {noeud} = {distances[noeud]}")