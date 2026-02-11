# routes/drone.py

from flask import Blueprint, jsonify
from services.simulation.sim_state import SIMULATION_STATE

drone_bp = Blueprint("drone", __name__)

@drone_bp.route("/drone/status", methods=["GET"])
def drone_status():
    if not SIMULATION_STATE["drone"]:
        return jsonify({
            "status": "INITIALIZING"
        })

    return jsonify({
        "drone": SIMULATION_STATE["drone"],
        "last_updated": SIMULATION_STATE["last_updated"]
    })

@drone_bp.route("/drone/zones", methods=["GET"])
def get_zones():
    zones = list(SIMULATION_STATE.get("zones", {}).values())
    return jsonify({"zones": zones})
