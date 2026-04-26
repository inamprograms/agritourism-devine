import json
from datetime import datetime, timezone
from app.core.supabase import supabase
from app.services.plan_service import plan_service

class InteractionLogger:
    """
    Logs every AI chat interaction to Supabase.
    Structured for observability and RAG evaluation.
    """

    def log(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        language: str,
        latency_ms: int,
        source: str = "web",
        rag_hit: bool = False,
        response_length: int = 0,
        retrieved_context: str = None,
        user_id: str = None,
        ai_type: str = "assistant",
    ) -> str | None:
        try:
            response = supabase.table("ai_interaction_logs").insert({
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "language": language,
                "latency_ms": latency_ms,
                "source": source,
                "rag_hit": rag_hit,
                "response_length": response_length,
                "retrieved_context": retrieved_context,
                "user_id": user_id,
            }).execute()
            
            log_id = response.data[0]["id"] if response.data else None
            # Increment counter if user is known
            if user_id:
                plan_service.increment_ai_counter(user_id, ai_type)
                
            return log_id

        except Exception as e:
            print(f"[AI_LOG_ERROR] Failed to log interaction: {e}")
            
        # record = {
        #     "timestamp": datetime.now(timezone.utc).isoformat(),
        #     "session_id": session_id,
        #     "language": language,
        #     "user_message": user_message,
        #     "ai_response": ai_response[:200], 
        #     "latency_ms": latency_ms,
        #     "source": source,
        #     "rag_hit": rag_hit,
        #     "response_length": response_length,
        #     "retrieved_context": retrieved_context,
        # }
        # print(f"[AI_LOG] {json.dumps(record)}")