from flask import Blueprint
from app.core.supabase import supabase
from datetime import date

platform_bp = Blueprint("platform", __name__)


@platform_bp.route("/platform/observability/stats", methods=["GET"])
def observability_stats():
    try:
        # All interaction logs 
        all_logs = supabase.table("ai_interaction_logs").select(
            "id, source, rag_hit, latency_ms, created_at, retrieval_scores"
        ).execute()
        logs = all_logs.data or []

        total_interactions = len(logs)
        today_str = date.today().isoformat()
        today_interactions = sum(1 for l in logs if l["created_at"].startswith(today_str))
        avg_latency_ms = int(sum(l["latency_ms"] for l in logs) / total_interactions) if total_interactions else 0
        rag_hits = sum(1 for l in logs if l["rag_hit"])
        rag_hit_rate = round(rag_hits / total_interactions, 2) if total_interactions else 0
        web_count = sum(1 for l in logs if l["source"] == "web")
        whatsapp_count = sum(1 for l in logs if l["source"] == "whatsapp")

        # All evaluation results 
        eval_result = supabase.table("evaluation_results").select(
            "faithfulness, answer_relevance, context_precision, completeness, safety, avg_score"
        ).execute()
        evals = eval_result.data or []
        eval_count = len(evals)

        def safe_avg(field):
            values = [e[field] for e in evals if e.get(field) is not None]
            return round(sum(values) / len(values), 2) if values else 0

        # RAG-only metrics (faithfulness + context_precision only exist for RAG hits)
        rag_evals = [e for e in evals if e.get("faithfulness") is not None]
        rag_eval_count = len(rag_evals)

        avg_faithfulness = round(
            sum(e["faithfulness"] for e in rag_evals) / rag_eval_count, 2
        ) if rag_eval_count else 0
        
        cp_values = [e["context_precision"] for e in rag_evals if e.get("context_precision") is not None]
        avg_context_precision = round(sum(cp_values) / len(cp_values), 2) if cp_values else 0

        # All-interaction metrics
        avg_answer_relevance  = safe_avg("answer_relevance")
        avg_completeness      = safe_avg("completeness")
        avg_safety            = safe_avg("safety")
        avg_score_overall     = safe_avg("avg_score")

        # Low scoring interactions count
        low_score_count = sum(
            1 for e in evals
            if e.get("avg_score") is not None and e["avg_score"] < 0.6
        )

        # Recent interactions with full eval data joined
        recent_result = supabase.table("ai_interaction_logs").select(
            "id, user_message, ai_response, language, latency_ms, source, "
            "rag_hit, response_length, created_at, retrieval_scores, "
            "evaluation_results("
            "  faithfulness, answer_relevance, context_precision, "
            "  completeness, safety, avg_score, "
            "  faithfulness_reason, answer_relevance_reason, "
            "  context_precision_reason, completeness_reason, safety_reason"
            ")"
        ).order("created_at", desc=True).limit(20).execute()

        recent_interactions = []
        for log in recent_result.data or []:
            eval_data = log.get("evaluation_results")
            if isinstance(eval_data, list):
                eval_data = eval_data[0] if eval_data else None

            recent_interactions.append({
                "id":               log["id"],
                "user_message":     log["user_message"],
                "ai_response":      log["ai_response"],
                "language":         log["language"],
                "latency_ms":       log["latency_ms"],
                "source":           log["source"],
                "rag_hit":          log["rag_hit"],
                "response_length":  log["response_length"],
                "created_at":       log["created_at"],
                "retrieval_scores": log.get("retrieval_scores") or [],
                # Scores
                "faithfulness":        eval_data.get("faithfulness")        if eval_data else None,
                "answer_relevance":    eval_data.get("answer_relevance")    if eval_data else None,
                "context_precision":   eval_data.get("context_precision")   if eval_data else None,
                "completeness":        eval_data.get("completeness")        if eval_data else None,
                "safety":              eval_data.get("safety")              if eval_data else None,
                "avg_score":           eval_data.get("avg_score")           if eval_data else None,
                # Reasons
                "faithfulness_reason":       eval_data.get("faithfulness_reason")       if eval_data else None,
                "answer_relevance_reason":   eval_data.get("answer_relevance_reason")   if eval_data else None,
                "context_precision_reason":  eval_data.get("context_precision_reason")  if eval_data else None,
                "completeness_reason":       eval_data.get("completeness_reason")       if eval_data else None,
                "safety_reason":             eval_data.get("safety_reason")             if eval_data else None,
            })

        return {
            # Health
            "total_interactions":   total_interactions,
            "today_interactions":   today_interactions,
            "avg_latency_ms":       avg_latency_ms,
            "rag_hit_rate":         rag_hit_rate,
            "web_count":            web_count,
            "whatsapp_count":       whatsapp_count,
            "eval_count":           eval_count,
            "low_score_count":      low_score_count,
            # Quality averages
            "avg_faithfulness":       avg_faithfulness,
            "avg_answer_relevance":   avg_answer_relevance,
            "avg_context_precision":  avg_context_precision,
            "avg_completeness":       avg_completeness,
            "avg_safety":             avg_safety,
            "avg_score_overall":      avg_score_overall,
            # Recent
            "recent_interactions":  recent_interactions,
        }

    except Exception as e:
        return {"error": str(e)}, 500