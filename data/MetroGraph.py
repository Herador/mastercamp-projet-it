from collections import defaultdict
import pandas as pd

class MetroGraph:
    def __init__(self, stop_dict, edges):
        self.graph = defaultdict(dict)  
        self.stops = {}
        for s in stop_dict.values():
            self.stops[s.id] = s
        for row in edges.itertuples(index=False):
            u, v, w, route= row.u, row.v, row.duration, row.route_short_name
            if pd.notnull(u) and pd.notnull(v):
                # u->v
                if v not in self.graph[u] or self.graph[u][v]["duration"] > w:
                    self.graph[u][v] = {"duration": w, "routes": set([route])}
                else:
                    self.graph[u][v]["routes"].add(route)

                # v → u
                if u not in self.graph[v] or self.graph[v][u]["duration"] > w:
                    self.graph[v][u] = {"duration": w, "routes": set([route])}
                else:
                    self.graph[v][u]["routes"].add(route)
        

    def ajouter_stop(self, stop):
        self.stops[stop.id] = stop

    def ajouter_arete(self, stop1, stop2, duration, route):
        if stop2 not in self.graph[stop1] or self.graph[stop1][stop2] > duration:
            self.graph[stop1][stop2] = {"duration": duration, "routes": set([route])}
        else:
            self.graph[stop1][stop2]["routes"].add(route)
        if stop1 not in self.graph[stop2] or self.graph[stop2][stop1]["duration"] > duration:
            self.graph[stop2][stop1] = {"duration": duration, "routes": set([route])}
        else:
            self.graph[stop2][stop1]["routes"].add(route)

    
    def get_stop_by_name(self,name):
        for stop in self.stops.values():
            if stop.name.lower() == name.lower():
                return stop
        return None

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
