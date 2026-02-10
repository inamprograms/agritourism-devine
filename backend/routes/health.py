from flask import Blueprint, jsonify

from services.simulation.sim_state import SIMULATION_STATE

health_bp = Blueprint("health", __name__)
health_live_bp = Blueprint("health_live", __name__)

@health_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Agritourism Devine backend is running"
    })
    
    

@health_live_bp.route("/health/live", methods=["GET"])
def health_live():
    drone = SIMULATION_STATE.get("drone")

    if not drone:
        return jsonify({"status": "NO_DATA"})

    return jsonify({
        "zone_id": drone["zone_id"],
        "ndvi_score": drone["ndvi_score"],
        "health_label": drone["health_label"],
        "timestamp": drone["timestamp"]
    })
