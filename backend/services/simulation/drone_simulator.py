# services/simulation/drone_simulator.py

import time
from datetime import datetime

class DroneSimulator:
    def __init__(self, farm_world):
        self.farm = farm_world
        self.x = 0
        self.y = 0
        self.altitude = 30
        self.battery = 100
        self.status = "IDLE"
        self.last_scan_time = None
        self.step_size = 10
        self.low_battery_threshold = 20
        self.decision_state = "PATROL"

    def start_mission(self):
        self.status = "FLYING"

    def move(self):
        if self.x + self.step_size < self.farm.width:
            self.x += self.step_size
        else:
            self.x = 0
            self.y += self.step_size

        if self.y >= self.farm.height:
            self.status = "RETURNING"
        
        if self.battery <= self.low_battery_threshold:
            self.status = "RETURNING"
            self.decision_state = "LOW_BATTERY_RETURN"

        self.battery -= 0.5

    def should_scan(self):
        if not self.last_scan_time:
            return True
        return (datetime.utcnow() - self.last_scan_time).seconds >= 5

    def scan(self):
        zone = self.farm.get_zone_by_position(self.x, self.y)
        self.last_scan_time = datetime.utcnow()
        self.status = "SCANNING"
        return zone

    def tick(self):
        # if self.status == "IDLE":
            # self.start_mission()

        self.decision_state = "PATROL"
        
        if self.status in ["FLYING", "SCANNING"]:
            self.move()

        if self.status == "RETURNING":
            self.status = "IDLE"
            self.battery = 100
            self.x = 0
            self.y = 0
            self.decision_state = "RECHARGED"
