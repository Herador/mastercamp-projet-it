# Fonction pour récupérer la liste des sommets du graphe (unique)
def liste_sommets(graphe):
    return list(graphe.keys())

# Fonction pour créer une liste d’arêtes à partir du dictionnaire du graphe
def creer_liste_aretes(graphe):
    aretes = []
    for sommet in graphe:
        voisins = graphe[sommet]
        for voisin in voisins:
            poids = voisins[voisin]
            # Pour éviter les doublons
            if sommet < voisin:
                arete = (sommet, voisin, poids)
            else:
                arete = (voisin, sommet, poids)
            if arete not in aretes:
                aretes.append(arete)
    return aretes

# Fonction DFS pour explorer les connexions
def dfs(graphe, sommet_depart, visites):
    visites.add(sommet_depart)
    for s1, s2, poids in graphe:
        voisin = None
        if s1 == sommet_depart and s2 not in visites:
            voisin = s2
        elif s2 == sommet_depart and s1 not in visites:
            voisin = s1
        if voisin:
            dfs(graphe, voisin, visites)

# Vérifie si une arête crée un cycle dans l'arbre partiel
def est_acyclique(graphe, sommet1, sommet2):
    visites = set()
    dfs(graphe, sommet1, visites)
    return sommet2 not in visites

# Algorithme de Kruskal
def kruskal(graphe):
    
    aretes = creer_liste_aretes(graphe)   # Liste des arêtes non redondantes
    aretes.sort(key=lambda x: x[2])       # Tri croissant par poids

    arbre = []
    for sommet1, sommet2, poids in aretes:
        if est_acyclique(arbre, sommet1, sommet2):
            arbre.append((sommet1, sommet2, poids))

    return arbre

# Graphe donné
graphe = {
    's1': {'s2': 7, 's5': 6, 's6': 2},
    's2': {'s1': 7, 's3': 4, 's5': 5},
    's3': {'s2': 4, 's4': 1, 's5': 2},
    's4': {'s3': 1, 's5': 3},
    's5': {'s1': 6, 's2': 5, 's3': 2, 's4': 3, 's6': 1},
    's6': {'s1': 2, 's5': 1}
}

# Exécution
arbre = kruskal(graphe)

# Affichage
print("Sommets :", liste_sommets(graphe))
print("Arbre couvrant minimal (Kruskal) :")
poids_total = 0
for s1, s2, poids in arbre:
    print(f"{s1} — {s2} : {poids}")
    poids_total += poids
print(f"Poids total : {poids_total}")
