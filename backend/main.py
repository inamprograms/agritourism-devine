from app import create_app
import threading
import time

from services.simulation.telemetry_emitter import telemetry_engine
from services.simulation.sim_state import SIMULATION_STATE

app = create_app()

# # --- Digital Twin Simulation ---
def simulation_loop():
    while True:
        if not SIMULATION_STATE["mission"]["is_running"]:
            time.sleep(1)
            continue

        telemetry = telemetry_engine.generate_telemetry()

        if telemetry:
            # For now: log
            print("[SIMULATION]", telemetry)
        time.sleep(2)


# Start simulation ONLY once (important for Flask reloads)
if not app.debug or not threading.current_thread().name == "MainThread":
    simulation_thread = threading.Thread(
        target=simulation_loop,
        daemon=True
    )
    simulation_thread.start()

# --- Flask App Runner ---
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=app.config["FLASK_RUN_PORT"],
        debug=True
    )
