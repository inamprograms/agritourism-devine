# services/simulation/sim_state.py

SIMULATION_STATE = {
    "drone": None,
    "zones": {},
    "last_updated": None,
    "mission": {
        "total_zones": 0,
        "scanned_zones": set(),
        "poor_zones_detected": set(),
        "mission_status": "NOT_STARTED",
        "completion_percentage": 0,
        "is_running": False
    }
}
