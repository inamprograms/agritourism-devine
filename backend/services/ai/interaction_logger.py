import time
import json
from datetime import datetime, timezone


class InteractionLogger:
    """
    Logs every AI chat interaction.
    Currently logs to console — can later connect to DB, CloudWatch, or analytics.
    The structure is already designed for future use.
    """

    def log(
        self,
        session_id: str,
        user_message: str,
        model_response: str,
        language: str,
        latency_ms: int,
    ):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "language": language,
            "user_message": user_message,
            "model_response": model_response[:200],  # truncate for log readability
            "latency_ms": latency_ms,
        }
        # Currently prints to console
        # Later: save to Supabase, CloudWatch, or analytics DB
        print(f"[AI_LOG] {json.dumps(record)}")