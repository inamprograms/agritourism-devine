# services/simulation/farm_world.py

import random
from datetime import datetime

class FarmWorld:
    def __init__(self, width=100, height=100, zone_size=20):
        self.width = width
        self.height = height
        self.zone_size = zone_size
        self.zones = self._create_zones()

    def _create_zones(self):
        zones = {}
        zone_id = 0

        for x in range(0, self.width, self.zone_size):
            for y in range(0, self.height, self.zone_size):
                zones[zone_id] = {
                    "id": zone_id,
                    "x_range": (x, x + self.zone_size),
                    "y_range": (y, y + self.zone_size),
                    "base_health": random.uniform(0.55, 0.85),
                    "stress_factor": random.uniform(0.0, 0.25),
                    "last_updated": datetime.utcnow()
                }
                zone_id += 1

        return zones

    def get_zone_by_position(self, x, y):
        for zone in self.zones.values():
            if zone["x_range"][0] <= x < zone["x_range"][1] and \
               zone["y_range"][0] <= y < zone["y_range"][1]:
                return zone
        return None

    def simulate_health(self, zone):
        noise = random.uniform(-0.05, 0.05)
        health = zone["base_health"] - zone["stress_factor"] + noise
        return max(0.0, min(1.0, health))
