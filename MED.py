def parcours_en_profondeur(graphe, sommet, visite, parent):
    # Ajouter le sommet courant à l'ensemble des sommets visités
    visite.add(sommet)
    # Pour chaque voisin du sommet courant
    for voisin in graphe[sommet]:
        # Si le voisin n'a pas encore été visité, on continue le parcours en profondeur
        if voisin not in visite:
            # Appel récursif, en passant le sommet courant comme parent du voisin
            if parcours_en_profondeur(graphe, voisin, visite, sommet):
                # Si un cycle est détecté dans la récursion, on remonte True
                return True
        # Si le voisin est déjà visité et ce n'est pas le parent du sommet courant,
        # cela signifie qu'on a trouvé un cycle
        elif voisin != parent:
            return True
    # Aucun cycle détecté à partir de ce sommet
    return False

def detecter_cycle(graphe):
    # Ensemble pour garder la trace des sommets déjà visités
    visite = set()
    # Parcourir tous les sommets du graphe
    for sommet in graphe:
        # Si le sommet n'a pas été visité, on lance un parcours en profondeur depuis lui
        if sommet not in visite:
            if parcours_en_profondeur(graphe, sommet, visite, None):
                # Si un cycle est détecté, on retourne True
                return True
    # Aucun cycle détecté dans tout le graphe
    return False

def Kruskal(graphe):
    # Création d'une liste d'arêtes sous forme de tuples (sommet1, sommet2, poids)
    aretes = []
    # Pour chaque sommet dans le graphe
    for sommet in graphe:
        # On récupère ses voisins
        voisins = graphe[sommet]
        # Pour chaque voisin et son poids
        for voisin in voisins:
            poids = voisins[voisin]
            # Pour éviter de compter deux fois la même arête, on ordonne les sommets
            if sommet < voisin:
                arete = (sommet, voisin, poids)
            else:
                arete = (voisin, sommet, poids)
            # Ajouter l'arête à la liste uniquement si elle n'y est pas déjà
            if arete not in aretes:
                aretes.append(arete)

    # Trier la liste d'arêtes par poids croissant (du plus léger au plus lourd)
    aretes.sort(key=lambda x: x[2])

    # Créer un graphe vide avec tous les sommets, pour stocker l'arbre couvrant minimal
    arbre_couvrant = {s: {} for s in graphe}

    # Parcourir les arêtes triées par poids
    for sommet1, sommet2, poids in aretes:
        # Ajouter temporairement cette arête dans l'arbre couvrant
        arbre_couvrant[sommet1][sommet2] = poids
        arbre_couvrant[sommet2][sommet1] = poids

        # Vérifier si l'ajout de cette arête crée un cycle dans l'arbre couvrant
        if detecter_cycle(arbre_couvrant):
            # S'il y a un cycle, on retire cette arête (on ne la garde pas)
            del arbre_couvrant[sommet1][sommet2]
            del arbre_couvrant[sommet2][sommet1]

    # Affichage final de l'arbre couvrant minimal obtenu
    print("Arbre couvrant minimal (Kruskal) :")
    # Parcourir chaque sommet de l'arbre
    for sommet1 in arbre_couvrant:
        # Parcourir ses voisins
        for sommet2 in arbre_couvrant[sommet1]:
            # Pour ne pas afficher deux fois la même arête, on n'affiche que si sommet1 < sommet2
            if sommet1 < sommet2:
                print(f"{sommet1} -- {sommet2} (poids {arbre_couvrant[sommet1][sommet2]})")

# Exemple de graphe avec poids
graphe = {
    's1': {'s2': 7, 's5': 6, 's6': 2},
    's2': {'s1': 7, 's3': 4, 's5': 5},
    's3': {'s2': 4, 's4': 1, 's5': 2},
    's4': {'s3': 1, 's5': 3},
    's5': {'s1': 6, 's2': 5, 's3': 2, 's4': 3, 's6': 1},
    's6': {'s1': 2, 's5': 1}
}

# Exécuter Kruskal sur ce graphe
Kruskal(graphe)
