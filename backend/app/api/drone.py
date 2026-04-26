# routes/drone.py

from flask import Blueprint, jsonify, g
from app.services.simulation.sim_state import SIMULATION_STATE
from app.services.simulation.telemetry_emitter import telemetry_engine
# from app.services.simulation.telemetry_emitter import telemetry_engine, TelemetryEmitter
from app.auth.decorators import require_auth
from app.services.farmer_service import farmer_service

drone_bp = Blueprint("drone", __name__)

@drone_bp.route("/drone/status", methods=["GET"])
def drone_status():
    if not SIMULATION_STATE["drone"]:
        return jsonify({
            "status": "INITIALIZING"
        })

    return jsonify({
        "drone": SIMULATION_STATE["drone"],
        "last_updated": SIMULATION_STATE["last_updated"],
        "mission": {
            "status": SIMULATION_STATE["mission"]["mission_status"],
            "progress": SIMULATION_STATE["mission"]["completion_percentage"]
        }
    })

@drone_bp.route("/drone/zones", methods=["GET"])
def get_zones():
    zones = list(SIMULATION_STATE.get("zones", {}).values())
    return jsonify({"zones": zones})

@drone_bp.route("/drone/start", methods=["POST"])
@require_auth
def start_mission():
    # Get user's real farm_id and wire it to telemetry engine
    ids = farmer_service.get_or_create_for_user(
        user_id=g.user_id,
        farm_type="general"  # default since drone start doesn't know farm type
    )
    farm_id = ids["farm_id"]
    # Wire farm_id into the running telemetry engine
    telemetry_engine.farm_id = farm_id
    
    SIMULATION_STATE["mission"]["is_running"] = True
    SIMULATION_STATE["mission"]["mission_status"] = "IN_PROGRESS"
    return jsonify({"message": "Mission started"})

@drone_bp.route("/drone/stop", methods=["POST"])
@require_auth
def stop_mission():
    SIMULATION_STATE["mission"]["is_running"] = False
    SIMULATION_STATE["mission"]["mission_status"] = "STOPPED"
    # Clear farm_id when mission stops
    telemetry_engine.farm_id = None
    return jsonify({"message": "Mission stopped"})

@drone_bp.route("/drone/reset", methods=["POST"])
@require_auth
def reset_mission():
    
    # Clear farm_id on reset
    telemetry_engine.farm_id = None
    # Reset drone simulator position
    if telemetry_engine.drone:
        telemetry_engine.drone.x = 1
        telemetry_engine.drone.y = 1
        telemetry_engine.drone.battery = 100
        telemetry_engine.drone.status = "IDLE"
        telemetry_engine.drone.decision_state = "IDLE"
        telemetry_engine.drone.last_scan_time = None
        
    SIMULATION_STATE["drone"] = None
    SIMULATION_STATE["last_updated"] = None

    SIMULATION_STATE["mission"] = {
        "total_zones": len(SIMULATION_STATE["zones"]),
        "scanned_zones": set(),
        "poor_zones_detected": set(),
        "mission_status": "NOT_STARTED",
        "completion_percentage": 0,
        "is_running": False
    }

    return jsonify({"message": "Mission reset"})
