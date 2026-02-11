# services/simulation/telemetry_emitter.py
# Simulation now feeds shared live state

from datetime import datetime
from services.simulation.sim_state import SIMULATION_STATE
from services.simulation.telemetry_repository import TelemetryRepository
from services.simulation.drone_simulator import DroneSimulator
from services.simulation.farm_world import FarmWorld

class TelemetryEmitter:
    def __init__(self, supabase_client=None):
        self.farm = FarmWorld()
        self.drone = DroneSimulator(self.farm)
        self.db = supabase_client

    def generate_telemetry(self):
        
        # Move the drone first
        self.drone.tick()
        # scan if ready
        if not self.drone.should_scan():
            return None

        zone = self.drone.scan()
        if not zone:
            return None

        ndvi = self.farm.simulate_health(zone)

        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.drone.status,
            "battery": round(self.drone.battery, 2),
            "position": {"x": self.drone.x, "y": self.drone.y},
            "zone_id": zone["id"],
            "ndvi_score": round(ndvi, 3),
            "health_label": self._label_health(ndvi)
        }
        
        # Store live state for APIs / UI
        SIMULATION_STATE["drone"] = telemetry
        SIMULATION_STATE["last_updated"] = telemetry["timestamp"]
        
        # Persistent state (credibility)
        TelemetryRepository.save_telemetry(
            telemetry=telemetry,
            farm_id=101  # later link to dynamic real farm
        )
        
        return telemetry

    def _label_health(self, ndvi):
        if ndvi > 0.65:
            return "Good"
        elif ndvi > 0.4:
            return "Moderate"
        return "Poor"
