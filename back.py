from flask import Flask, jsonify, request
#from stop import Stop
import pickle

with open("metro_graph.pkl", "rb") as f:
    metroGraph = pickle.load(f)

app = Flask(__name__)

@app.route("/")
def home():
    return 'Hello, World!'

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

'''
@app.route("/shortest-path")
def get_shortest_path():
    start = request.args.get("from", "").lower()
    end = request.args.get("to", "").lower()
'''


app.run(host='0.0.0.0', port=80)