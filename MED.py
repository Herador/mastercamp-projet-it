def est_connexe(graphe):
    aretes = creer_liste_aretes(graphe)  # Conversion du dictionnaire vers liste d’arêtes
    visites = set()
    sommets = liste_sommets(graphe)
    dfs(aretes, sommets[0], visites)  # On utilise ta fonction DFS existante
    return len(visites) == len(sommets)

# Fonction pour récupérer la liste des sommets du graphe
def liste_sommets(graphe):
    # On retourne simplement les clés du dictionnaire, qui représentent les sommets
    return list(graphe.keys())

# Fonction pour créer une liste d’arêtes à partir du dictionnaire du graphe
def creer_liste_aretes(graphe):
    aretes = []  # Liste vide pour stocker les arêtes
    for sommet in graphe:
        voisins = graphe[sommet]  # Dictionnaire des voisins du sommet
        for voisin in voisins:
            poids = voisins[voisin]  # Poids de l'arête entre sommet et voisin
            # Pour éviter les doublons (car graphe non orienté)
            if sommet < voisin:
                arete = (sommet, voisin, poids)
            else:
                arete = (voisin, sommet, poids)
            # On ajoute l'arête seulement si elle n'existe pas déjà
            if arete not in aretes:
                aretes.append(arete)
    return aretes

# Fonction DFS (parcours en profondeur) pour explorer les connexions dans l'arbre partiel
def dfs(graphe, sommet_depart, visites):
    visites.add(sommet_depart)  # On marque le sommet comme visité
    for s1, s2, poids in graphe:  # On parcourt les arêtes de l'arbre partiel
        voisin = None
        # On cherche un sommet adjacent non encore visité
        if s1 == sommet_depart and s2 not in visites:
            voisin = s2
        elif s2 == sommet_depart and s1 not in visites:
            voisin = s1
        # Si un voisin est trouvé, on continue le parcours récursif
        if voisin:
            dfs(graphe, voisin, visites)


# Vérifie si l'ajout d'une arête créerait un cycle dans l'arbre partiel
def est_acyclique(graphe, sommet1, sommet2):
    visites = set()  # Ensemble des sommets visités
    dfs(graphe, sommet1, visites)  # On lance un DFS depuis sommet1
    # Si sommet2 a déjà été visité, l'ajout de l'arête formerait un cycle
    return sommet2 not in visites

# Algorithme de Kruskal pour construire l’arbre couvrant minimal
def kruskal(graphe):
    # Étape 1 : obtenir la liste des arêtes sans doublons
    aretes = creer_liste_aretes(graphe)

    # Étape 2 : trier les arêtes par poids croissant
    aretes.sort(key=lambda x: x[2])

    arbre = []  # Liste des arêtes qui formeront l’arbre couvrant minimal

    # Étape 3 : ajouter les arêtes une par une si elles ne forment pas de cycle
    for sommet1, sommet2, poids in aretes:
        if est_acyclique(arbre, sommet1, sommet2):
            arbre.append((sommet1, sommet2, poids))  # On ajoute l'arête à l'arbre

    return arbre  # On retourne l’arbre couvrant minimal

# Test
import pickle
from MetroGraph import MetroGraph

with open("metro_graph.pkl", "rb") as f:
    metroGraph = pickle.load(f)

# Exécution de l'algorithme de Kruskal
arbre = kruskal(metroGraph.graph)

# Affichage des résultats
if est_connexe(metroGraph.graph):
    print("Le graphe est connexe.")
else:
    print("Le graphe n'est pas connexe.")

print("Sommets :", liste_sommets(metroGraph.graph))
print("Arbre couvrant minimal (Kruskal) :")
poids_total = 0
for s1, s2, poids in arbre:
    print(f"{s1} — {s2} : {poids}")
    poids_total += poids
print(f"Poids total : {poids_total}")
