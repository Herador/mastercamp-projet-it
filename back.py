import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify, request
#from stop import Stop
import pickle
from flask_cors import CORS
from flask import render_template
from data.MetroGraph import MetroGraph
from graph.dijkstra import dijkstra, reconstruire_chemin

path = os.path.join(os.path.dirname(__file__), "data/metro_graph.pkl")
with open(path, "rb") as f:
    metroGraph = pickle.load(f)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("accueil.html")

@app.route("/carte")
def show_carte():
    return render_template("carte.html")

@app.route("/stops")
def get_stops():
    return jsonify([stop.to_dict() for stop in metroGraph.stops.values()])

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


@app.route("/neighbors/<stop_id>")
def get_neighbors(stop_id):
    stop = metroGraph.stops.get(stop_id)
    if stop is None:
        return jsonify({"error": "Stop not found"}), 404

    voisins = metroGraph.voisins(stop)  # dict {Stop: durée}
    results = []

    for voisin_obj, duration in voisins.items():
        results.append({
            "id": voisin_obj.id,
            "name": voisin_obj.name,
            "duration": duration
        })

    return jsonify(results)


@app.route("/shortest-path")
def get_shortest_path():
    start_name = request.args.get("from", "")
    end_name = request.args.get("to", "")

    start_stop = metroGraph.get_stop_by_name(start_name)
    end_stop = metroGraph.get_stop_by_name(end_name)
    print(start_stop)

    if not start_stop or not end_stop:
        return jsonify({"error": "Arrêts invalides."}), 400
    
    distances, pred = dijkstra(metroGraph.graph, start_stop)
    chemin = reconstruire_chemin(pred, start_stop, end_stop)

    if not chemin:
        return jsonify({"error": "Aucun chemin trouvé"}), 404

    chemin_json = [s.to_dict() for s in chemin]
    return jsonify(chemin_json)


CORS(app)
app.run(host='0.0.0.0', port=80)