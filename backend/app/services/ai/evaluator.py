import json
from app.services.ai.factory import get_ai_provider
from app.services.ai.prompts.system_prompts import evaluation_judge_system_prompt
from app.services.ai.prompts.user_prompts import evaluation_judge_prompt, evaluation_judge_prompt_no_context
from app.core.supabase import supabase

class EvaluatorService:
    """
    LLM-as-judge RAG evaluation service.

    Runs in background thread after each RAG interaction.
    Scores 5 dimensions with 0.0-1.0 numeric scores and reasoning.
    Never blocks the user response.
    """

    def __init__(self):
        self.provider = get_ai_provider()

    def _judge(self, question: str, context: str, response: str) -> dict | None:
        """
        Call LLM judge and parse scores.
        Returns parsed dict or None if anything fails.
        """
        try:
            raw = self.provider.complete(
                system_prompt=evaluation_judge_system_prompt(),
                user_prompt=evaluation_judge_prompt(question, context, response),
                temperature=0.0,
                max_tokens=500,
            )
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[EVAL_ERROR] Failed to parse judge response: {e}")
            return None
        except Exception as e:
            print(f"[EVAL_ERROR] Judge call failed: {e}")
            return None

    def _judge_no_context(self, question: str, response: str) -> dict | None:
        """
        Judge for non-RAG responses.
        Scores only answer_relevance, completeness, and safety.
        Returns parsed dict or None if anything fails.
        """
        try:
            raw = self.provider.complete(
                system_prompt=evaluation_judge_system_prompt(),
                user_prompt=evaluation_judge_prompt_no_context(question, response),
                temperature=0.0,
                max_tokens=300,
            )
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[EVAL_ERROR] Failed to parse no-context judge response: {e}")
            return None
        except Exception as e:
            print(f"[EVAL_ERROR] No-context judge call failed: {e}")
            return None
        
    def evaluate_async(
        self,
        log_id: str,
        user_message: str,
        ai_response: str,
        retrieved_context: str,
    ):
        """
        Evaluate a single RAG interaction and store enriched scores.
        Designed to run in background thread — never raises.
        """
        if not log_id or not retrieved_context:
            return

        scores = self._judge(user_message, retrieved_context, ai_response)
        if not scores:
            return

        try:
            def get_score(key: str) -> float | None:
                return scores.get(key, {}).get("score")

            def get_reason(key: str) -> str | None:
                return scores.get(key, {}).get("reason")

            faithfulness      = get_score("faithfulness")
            answer_relevance  = get_score("answer_relevance")
            context_precision = get_score("context_precision")
            completeness      = get_score("completeness")
            safety            = get_score("safety")

            score_values = [s for s in [faithfulness, answer_relevance, context_precision, completeness, safety] if s is not None]
            avg_score = round(sum(score_values) / len(score_values), 4) if score_values else None

            supabase.table("evaluation_results").insert({
                "log_id":                    log_id,
                "faithfulness":              faithfulness,
                "answer_relevance":          answer_relevance,
                "context_precision":         context_precision,
                "completeness":              completeness,
                "safety":                    safety,
                "faithfulness_reason":       get_reason("faithfulness"),
                "answer_relevance_reason":   get_reason("answer_relevance"),
                "context_precision_reason":  get_reason("context_precision"),
                "completeness_reason":       get_reason("completeness"),
                "safety_reason":             get_reason("safety"),
                "avg_score":                 avg_score,
            }).execute()

        except Exception as e:
            print(f"[EVAL_ERROR] Failed to store evaluation for log {str(log_id)[:8]}...: {e}")

    def evaluate_no_context_async(
        self,
        log_id: str,
        user_message: str,
        ai_response: str,
    ):
        """
        Evaluate a non-RAG interaction.
        Scores answer_relevance, completeness, safety only.
        Designed to run in background thread — never raises.
        """
        if not log_id:
            return

        scores = self._judge_no_context(user_message, ai_response)
        if not scores:
            return

        try:
            def get_score(key: str) -> float | None:
                return scores.get(key, {}).get("score")

            def get_reason(key: str) -> str | None:
                return scores.get(key, {}).get("reason")

            answer_relevance = get_score("answer_relevance")
            completeness     = get_score("completeness")
            safety           = get_score("safety")

            score_values = [s for s in [answer_relevance, completeness, safety] if s is not None]
            avg_score = round(sum(score_values) / len(score_values), 4) if score_values else None

            supabase.table("evaluation_results").insert({
                "log_id":                   log_id,
                "answer_relevance":         answer_relevance,
                "completeness":             completeness,
                "safety":                   safety,
                "answer_relevance_reason":  get_reason("answer_relevance"),
                "completeness_reason":      get_reason("completeness"),
                "safety_reason":            get_reason("safety"),
                "avg_score":                avg_score,
            }).execute()

        except Exception as e:
            print(f"[EVAL_ERROR] Failed to store no-context evaluation for log {str(log_id)[:8]}...: {e}")
        
evaluator_service = EvaluatorService()