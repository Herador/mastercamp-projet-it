import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, render_template
import pickle
from flask_cors import CORS
from graph.dijkstra import dijkstra, reconstruire_chemin
from collections import defaultdict

def calculer_poids_ecologique(chemin, graphe_obj):
    poids = 0
    if len(chemin) < 2:
        return poids
    lignes_prec = set(graphe_obj.graph[chemin[0]][chemin[1]]["routes"])
    for i in range(1, len(chemin) - 1):
        u = chemin[i]
        v = chemin[i + 1]
        lignes_actuelles = set(graphe_obj.graph[u][v]["routes"])
        if lignes_actuelles != lignes_prec:
            stop_obj = graphe_obj.stops.get(u.id)
            if stop_obj and hasattr(stop_obj, "name"):
                pollution = getattr(stop_obj, "pollution", 1)
                poids += pollution
                print(f"✅ Changement détecté à {stop_obj.name}, pollution ajoutée: {pollution}")
            lignes_prec = lignes_actuelles
    return poids

path = os.path.join(os.path.dirname(__file__), "data/metro_graph_with_pollution.pkl")
with open(path, "rb") as f:
    metroGraph = pickle.load(f)
# Après le pickle.load
for stop in metroGraph.stops.values():
    if not hasattr(stop, "pollution"):
        stop.pollution = 0

# Corriger aussi les sommets dans le graph (clés)
for stop in metroGraph.graph.keys():
    if not hasattr(stop, "pollution"):
        stop.pollution = 0

# Corriger aussi les stops des voisins
for voisins in metroGraph.graph.values():
    for voisin_stop in voisins.keys():
        if not hasattr(voisin_stop, "pollution"):
            voisin_stop.pollution = 0

def graphe_pondere_ecologique(graphe):
    new_graph = {}
    for u, voisins in graphe.items():
        new_graph[u] = {}
        for v, info in voisins.items():
            pollution_u = getattr(u, "pollution", 1)
            pollution_v = getattr(v, "pollution", 1)
            poids = (pollution_u + pollution_v) / 2 + 0.1  # légère pénalisation
            new_graph[u][v] = {
                "duration": poids,
                "routes": info["routes"]
            }
    return new_graph

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("accueil.html")

@app.route("/carte")
def show_carte():
    return render_template("carte.html")

@app.route("/trajet")
def show_trajet():
    return render_template("trajet.html")

@app.route("/acpm")
def page_acpm():
    return render_template("acpm.html")


# Ne renvoie que les stops commerciaux (pas physiques)
@app.route("/stops")
def get_simplified_stops():
    from collections import defaultdict

    grouped = defaultdict(list)

    for stop in metroGraph.stops.values():
        key = stop.parent_station if stop.parent_station else stop.id
        grouped[key].append(stop)

    simplified = []
    for station_id, stops in grouped.items():
        lat = sum(s.lat for s in stops) / len(stops)
        lon = sum(s.lon for s in stops) / len(stops)
        name = stops[0].name  # tous les quais de la station ont le même nom
        pollution = next((s.pollution for s in stops if s.pollution is not None), None)
        accessible = any(s.accessible for s in stops)
        simplified.append({
            "id": station_id,
            "name": name,
            "lat": lat,
            "lon": lon,
            "pollution": pollution,
            "accessible": accessible
        })

    return jsonify(simplified)


@app.route("/stops/<stop_id>")
def get_stop(stop_id):
    stop = metroGraph.stops.get(stop_id)
    if stop is None:
        return jsonify({"error": f"Stop {stop_id} not found"}), 404
    return jsonify(stop.to_dict())

@app.route("/search")
def get_stop_by_name():
    name = request.args.get("name", "").lower()
    if not name:
        return jsonify({"error": "Missing 'name' query parameter"}), 400
    
    results = [
        stop.to_dict()
        for stop in metroGraph.stops.values()
        if stop.name.lower() == name
    ]

    if not results:
        return jsonify({"message": f"No stop found with name '{name}'"}), 404
    
    return jsonify(results)

@app.route("/edges")
def get_edges():
    results = []
    seen = set()  

    for stop1, voisins in metroGraph.graph.items():
        for stop2, info in voisins.items():
            key = tuple(sorted([stop1.id, stop2.id]))
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "from": stop1.to_dict(),
                "to": stop2.to_dict(),
                "routes": sorted(info["routes"]),
                "duration": info["duration"]
            })

    return jsonify(results)


@app.route("/neighbors/<stop_id>")
def get_neighbors(stop_id):
    stop = metroGraph.stops.get(stop_id)
    if stop is None:
        return jsonify({"error": "Stop not found"}), 404

    voisins = metroGraph.voisins(stop)  # dict {Stop: durée}
    results = []

    for voisin_obj, info in voisins.items():
        results.append({
            "id": voisin_obj.id,
            "name": voisin_obj.name,
            "duration": info["duration"],
            "routes": sorted(info["routes"])
        })

    return jsonify(results)

@app.route("/est-connexe")
def test_connexite():
    connected, visited = metroGraph.is_connected()
    return jsonify({ 
        "connected": connected,
        "visited_count": len(visited),
        "total_stops": len(metroGraph.graph),
        "unvisited_ids": [
            stop.id for stop in metroGraph.graph
            if stop not in visited
        ] if not connected else []
    })

path_apcm = os.path.join(os.path.dirname(__file__), "data/apcm.pkl")
with open(path_apcm, "rb") as f:
    arbre = pickle.load(f)

path_reduit = os.path.join(os.path.dirname(__file__), "data/metro_graph_reduit.pkl")
with open(path_reduit, "rb") as f:
    metroGraphReduit = pickle.load(f)

@app.route("/apcm")
def afficher_apcm():

    apcm_geojson = []
    for s1, s2, poids in arbre:
        infos = metroGraphReduit.graph[s1].get(s2) or metroGraphReduit.graph[s2].get(s1)
        lignes = sorted(infos["routes"]) if infos else []
        apcm_geojson.append({
            "from": {
                "id": s1.id,
                "name": s1.name,
                "lat": s1.lat,
                "lon": s1.lon,
            },
            "to": {
                "id": s2.id,
                "name": s2.name,
                "lat": s2.lat,
                "lon": s2.lon,
            },
            "routes": lignes,
            "duration": poids
        })

    return jsonify(apcm_geojson)

@app.route("/shortest-path")
def get_shortest_path():
    start_name = request.args.get("from", "")
    end_name = request.args.get("to", "")

    start_stop = metroGraph.get_stop_by_name(start_name)
    end_stop = metroGraph.get_stop_by_name(end_name)

    if not start_stop or not end_stop:
        return jsonify({"error": "Arrêts invalides."}), 400
    
    distances, pred = dijkstra(metroGraph.graph, start_stop)
    chemin = reconstruire_chemin(pred, start_stop, end_stop)

    if not chemin:
        return jsonify({"error": "Aucun chemin trouvé"}), 404
    
    def temps_inter(chemin):
        nb_sommets = len(chemin)
        return (nb_sommets * 10) - 20


    # Durée totale
    total_duration = sum(
        metroGraph.graph[chemin[i]][chemin[i+1]]["duration"]
        for i in range(len(chemin) - 1)
    )

    intermediate_time = temps_inter(chemin)

    # Détails des étapes
    steps = []
    for i in range(len(chemin) - 1):
        a, b = chemin[i], chemin[i+1]
        info = metroGraph.graph[a][b]
        steps.append({
            "from": a.to_dict(),
            "to": b.to_dict(),
            "duration": info["duration"],
            "routes": sorted(info["routes"])
        })

    return jsonify({
        "total_duration": total_duration+intermediate_time,
        "steps": steps
    })

@app.route("/api/paths", methods=["GET"])
def get_paths():
    from_name = request.args.get("from")
    to_name = request.args.get("to")

    if not from_name or not to_name:
        return jsonify({"error": "Paramètres 'from' et 'to' obligatoires"}), 400

    source = metroGraph.get_stop_by_name(from_name)
    dest = metroGraph.get_stop_by_name(to_name)

    if not source or not dest:
        return jsonify({"error": "Stations non trouvées"}), 404

    # Dijkstra
    distances, pred = dijkstra(metroGraph.graph, source)
    chemin_dijkstra = reconstruire_chemin(pred, source, dest)
    poids_dijkstra = calculer_poids_ecologique(chemin_dijkstra, metroGraph)

    def generate_steps(chemin):
        steps = []
        for i in range(len(chemin) - 1):
            u = chemin[i]
            v = chemin[i + 1]
            info = metroGraph.graph[u][v]
            steps.append({
                "from": u.to_dict(),
                "to": v.to_dict(),
                "duration": info["duration"],
                "routes": sorted(info["routes"])
            })
        return steps

    def compute_total_duration(chemin):
        total_duration = sum(
            metroGraph.graph[chemin[i]][chemin[i + 1]]["duration"]
            for i in range(len(chemin) - 1)
        )
        nb_sommets = len(chemin)
        intermediate_time = (nb_sommets * 10) - 20
        return total_duration + intermediate_time

    # Chemin respirable
    graphe_eco = graphe_pondere_ecologique(metroGraph.graph)
    distances_eco, pred_eco = dijkstra(graphe_eco, source)
    chemin_eco = reconstruire_chemin(pred_eco, source, dest)
    poids_eco = calculer_poids_ecologique(chemin_eco, metroGraph)

    best_eco_path = {
        "steps": generate_steps(chemin_eco),
        "ecological_weight": poids_eco,
        "total_duration": compute_total_duration(chemin_eco)
    }

    return jsonify({
        "fastest_path": {
            "steps": [str(stop) for stop in chemin_dijkstra],
            "ecological_weight": poids_dijkstra
        },
        "best_eco_path": best_eco_path
    })



@app.route("/api/lines")
def get_lines():

    segments_par_ligne = defaultdict(set)
    seen = set()

    # Dictionnaire pour regrouper les coordonnées par station mère
    station_coords = {}
    for stop in metroGraph.stops.values():
        parent_id = stop.parent_station if stop.parent_station else stop.id
        if parent_id not in station_coords:
            station_coords[parent_id] = {
                "name": stop.name,
                "lat": stop.lat,
                "lon": stop.lon
            }

    for stop1, voisins in metroGraph.graph.items():
        for stop2, info in voisins.items():
            key = tuple(sorted([stop1.id, stop2.id]))
            if key in seen:
                continue
            seen.add(key)

            # On récupère les stations commerciales (mères)
            parent1 = stop1.parent_station if stop1.parent_station else stop1.id
            parent2 = stop2.parent_station if stop2.parent_station else stop2.id

            # Sauter si c’est une liaison à l’intérieur de la même station commerciale
            if parent1 == parent2:
                continue

            coord1 = (round(station_coords[parent1]["lat"], 6), round(station_coords[parent1]["lon"], 6))
            coord2 = (round(station_coords[parent2]["lat"], 6), round(station_coords[parent2]["lon"], 6))
            segment = tuple(sorted([coord1, coord2]))

            for route in info["routes"]:
                if route != "transfer":  # ne pas tracer les correspondances à pied
                    segments_par_ligne[route].add(segment)

    lignes_geojson = []
    for route, segments in segments_par_ligne.items():
        for coord1, coord2 in segments:
            lignes_geojson.append({
                "name": f"Ligne {route}",
                "color": get_line_color(route),
                "coordinates": [list(coord1), list(coord2)]
            })

    return jsonify(lignes_geojson)

@app.route("/api/linesapcm")
def get_lines_apcm():
    segments_par_ligne = defaultdict(set)

    for stop1, stop2, _ in arbre:
        info = metroGraphReduit.graph[stop1].get(stop2) or metroGraphReduit.graph[stop2].get(stop1)
        if not info:
            continue

        coord1 = (round(stop1.lat, 6), round(stop1.lon, 6))
        coord2 = (round(stop2.lat, 6), round(stop2.lon, 6))
        segment = tuple(sorted([coord1, coord2]))

        for route in info["routes"]:
            if route != "transfer":
                segments_par_ligne[route].add(segment)

    lignes_geojson = []
    for route, segments in segments_par_ligne.items():
        for coord1, coord2 in segments:
            lignes_geojson.append({
                "name": f"Ligne {route}",
                "color": get_line_color(route),
                "coordinates": [list(coord1), list(coord2)]
            })

    return jsonify(lignes_geojson)



def get_line_color(name):
    palette = {
        "1": "#F6C343", "2": "#214999", "3": "#877829",
        "4": "#A9358B", "5": "#EC8040", "6": "#80B877",
        "7": "#EA90AC", "8": "#B28DBF", "9": "#ADB93D",
        "10": "#CAA23C", "11": "#6D4118", "12": "#2D6840",
        "13": "#81BDB9", "14": "#490F7B", "3B": "#81BDB9", "7B": "#80B877"
    }
    return palette.get(name, "#999999")


CORS(app)

app.run(host='0.0.0.0', port=80)




