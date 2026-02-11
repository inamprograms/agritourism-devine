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
        SIMULATION_STATE["mission"]["total_zones"] = len(self.farm.zones)
        SIMULATION_STATE["mission"]["mission_status"] = "IN_PROGRESS"
        self.db = supabase_client
    
    def generate_telemetry(self):
        
        # Move the drone first
        self.drone.tick()
        # scan if ready after 5 sec
        if not self.drone.should_scan():
            return None

        zone = self.drone.scan()
        if not zone:
            return None

        ndvi = self.farm.simulate_health(zone)
        
        mission = SIMULATION_STATE["mission"]

        # Track scanned zones
        mission["scanned_zones"].add(zone["id"])

        # Detect poor zones
        if ndvi < 0.4:
            mission["poor_zones_detected"].add(zone["id"])
            self.drone.decision_state = "POOR_ZONE_DETECTED"

        # Update completion %
        mission["completion_percentage"] = round(
            (len(mission["scanned_zones"]) / mission["total_zones"]) * 100, 2
        )

        # Complete mission
        if mission["completion_percentage"] >= 100:
            mission["mission_status"] = "COMPLETED"
            self.drone.decision_state = "MISSION_COMPLETED"


        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.drone.status,
            "battery": round(self.drone.battery, 2),
            "position": {"x": self.drone.x, "y": self.drone.y},
            "zone_id": zone["id"],
            "ndvi_score": round(ndvi, 3),
            "health_label": self._label_health(ndvi),
            "decision_state": self.drone.decision_state,
            "mission_progress": SIMULATION_STATE["mission"]["completion_percentage"],
            "poor_zones_detected": len(SIMULATION_STATE["mission"]["poor_zones_detected"])
        }
        
        # Store live state for APIs / UI
        SIMULATION_STATE["drone"] = telemetry
        SIMULATION_STATE["zones"] = self.farm.zones
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
