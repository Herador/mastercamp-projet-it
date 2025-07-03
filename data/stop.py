class Stop:
    def __init__(self, stop_id, name, lat, lon):
        self.id = stop_id
        self.name = name
        self.lat = float(lat)
        self.lon = float(lon)
        self.pollution = None

    def __eq__(self, other):
        return isinstance(other, Stop) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.name} ({self.id}), pollution: {getattr(self, 'pollution', 'N/A')}"

    
    def __lt__(self, other):
        return self.id < other.id
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "pollution": self.pollution
        }

