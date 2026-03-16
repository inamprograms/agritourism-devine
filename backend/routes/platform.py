from flask import Blueprint
from data.supabase_client import supabase
from datetime import date

platform_bp = Blueprint("platform", __name__)

@platform_bp.route("/platform/observability/stats", methods=["GET"])
def observability_stats():
    try:
        # Total interactions
        all_logs = supabase.table("ai_interaction_logs").select("id, source, rag_hit, latency_ms, created_at").execute()
        logs = all_logs.data

        total_interactions = len(logs)
        today_str = date.today().isoformat()
        today_interactions = sum(1 for l in logs if l["created_at"].startswith(today_str))
        avg_latency_ms = int(sum(l["latency_ms"] for l in logs) / total_interactions) if total_interactions else 0
        rag_hits = sum(1 for l in logs if l["rag_hit"])
        rag_hit_rate = round(rag_hits / total_interactions, 2) if total_interactions else 0
        web_count = sum(1 for l in logs if l["source"] == "web")
        whatsapp_count = sum(1 for l in logs if l["source"] == "whatsapp")

        # Evaluation scores
        eval_result = supabase.table("evaluation_results").select("faithfulness, answer_relevance, context_precision").execute()
        evals = eval_result.data
        eval_count = len(evals)
        avg_faithfulness = round(sum(e["faithfulness"] for e in evals) / eval_count, 2) if eval_count else 0
        avg_answer_relevance = round(sum(e["answer_relevance"] for e in evals) / eval_count, 2) if eval_count else 0
        avg_context_precision = round(sum(e["context_precision"] for e in evals) / eval_count, 2) if eval_count else 0

        # Recent interactions with evaluation scores joined
        recent_result = supabase.table("ai_interaction_logs")\
            .select("id, user_message, ai_response, language, latency_ms, source, rag_hit, response_length, created_at, evaluation_results(faithfulness, answer_relevance, context_precision)")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        recent_interactions = []
        for log in recent_result.data:
            eval_data = log.get("evaluation_results")
            if isinstance(eval_data, list):
                eval_data = eval_data[0] if eval_data else None
            recent_interactions.append({
                "id": log["id"],
                "user_message": log["user_message"],
                "ai_response": log["ai_response"],
                "language": log["language"],
                "latency_ms": log["latency_ms"],
                "source": log["source"],
                "rag_hit": log["rag_hit"],
                "response_length": log["response_length"],
                "created_at": log["created_at"],
                "faithfulness": eval_data["faithfulness"] if eval_data else None,
                "answer_relevance": eval_data["answer_relevance"] if eval_data else None,
                "context_precision": eval_data["context_precision"] if eval_data else None,
            })

        return {
            "total_interactions": total_interactions,
            "today_interactions": today_interactions,
            "avg_latency_ms": avg_latency_ms,
            "rag_hit_rate": rag_hit_rate,
            "web_count": web_count,
            "whatsapp_count": whatsapp_count,
            "avg_faithfulness": avg_faithfulness,
            "avg_answer_relevance": avg_answer_relevance,
            "avg_context_precision": avg_context_precision,
            "recent_interactions": recent_interactions,
        }

    except Exception as e:
        return {"error": str(e)}, 500