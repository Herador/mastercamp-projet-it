from collections import defaultdict
import pandas as pd

class MetroGraph:
    def __init__(self, stop_dict, edges):
        self.graph = defaultdict(dict)  
        self.stops = {}
        for s in stop_dict.values():
            self.stops[s.id] = s
        for row in edges.itertuples(index=False):
            u, v, w = row.u, row.v, row.duration
            if pd.notnull(u) and pd.notnull(v):
                if v not in self.graph[u] or self.graph[u][v] > w:
                    self.graph[u][v] = w
                    self.graph[v][u] = w
        

    def ajouter_stop(self, stop):
        self.stops[stop.id] = stop

    def ajouter_arete(self, stop1, stop2, duration):
        if stop2 not in self.graph[stop1] or self.graph[stop1][stop2] > duration:
            self.graph[stop1][stop2] = duration
            self.graph[stop2][stop1] = duration  # graphe non orienté

    def get_stops_by_name(self, name):
        return [s for s in self.stops.values() if s.name == name]

    def voisins(self, stop):
        return self.graph.get(stop, {})

    def is_connected(self):
        if not self.graph:
            return True, set()

        visited = set()
        start = next(iter(self.graph))

        def dfs(node):
            visited.add(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(start)
        return len(visited) == len(self.graph), visited
