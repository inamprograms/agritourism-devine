# services/simulation/telemetry_repository.py

from data.supabase_client import supabase

class TelemetryRepository:
    @staticmethod
    def save_telemetry(telemetry, farm_id=None):
        payload = {
            "farm_id": farm_id,
            "zone_id": telemetry["zone_id"],
            "drone_status": telemetry["status"],
            "battery": telemetry["battery"],
            "position_x": telemetry["position"]["x"],
            "position_y": telemetry["position"]["y"],
            "ndvi_score": telemetry["ndvi_score"],
            "health_label": telemetry["health_label"],
        }

        supabase.table("drone_telemetry").insert(payload).execute()
