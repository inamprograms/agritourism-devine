from app import create_app
import threading
import time

from services.simulation.telemetry_emitter import TelemetryEmitter

app = create_app()

# --- Digital Twin Simulation Setup ---
telemetry_engine = TelemetryEmitter()

def simulation_loop():
    """
    Autonomous drone simulation loop
    Runs independently of HTTP requests
    """
    while True:
        telemetry = telemetry_engine.generate_telemetry()

        if telemetry:
            # For now: log (next step = DB + services)
            print("[SIMULATION]", telemetry)

        time.sleep(2)  # scan interval (seconds)

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
