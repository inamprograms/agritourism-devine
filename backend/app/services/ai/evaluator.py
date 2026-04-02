from openai import OpenAI
from ragas.llms import llm_factory
from ragas.metrics import DiscreteMetric
from app.core.supabase import supabase
from config import Config


class EvaluatorService:
    """
    Real-time RAG evaluation service.
    Runs in background thread after each interaction - does not block user response.
    Scores faithfulness, answer relevance, and context precision using Groq as judge.
    """

    def __init__(self):
        client = OpenAI(
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.llm = llm_factory(Config.GROQ_MODEL, provider="openai", client=client)

        self.faithfulness_metric = DiscreteMetric(
            name="faithfulness",
            prompt="Given the context and response, is the response faithful to the context? Does it avoid making claims not supported by the context? Return 'pass' or 'fail'.\nContext: {context}\nResponse: {response}",
            allowed_values=["pass", "fail"],
        )
        self.relevance_metric = DiscreteMetric(
            name="answer_relevance",
            prompt="Given the question and response, does the response directly answer the question asked? Return 'pass' or 'fail'.\nQuestion: {question}\nResponse: {response}",
            allowed_values=["pass", "fail"],
        )
        self.context_metric = DiscreteMetric(
            name="context_precision",
            prompt="Given the question and context, is the context relevant and useful for answering the question? Return 'pass' or 'fail'.\nQuestion: {question}\nContext: {context}",
            allowed_values=["pass", "fail"],
        )

    def evaluate_async(
        self,
        log_id: str,
        user_message: str,
        ai_response: str,
        retrieved_context: str,
    ):
        """
        Evaluate a single interaction and store scores in evaluation_results.
        Designed to run in a background thread - never raises, always fails silently.
        """
        if not log_id or not retrieved_context:
            return

        try:
            faithfulness_score = self.faithfulness_metric.score(
                llm=self.llm,
                context=retrieved_context,
                response=ai_response
            )
            relevance_score = self.relevance_metric.score(
                llm=self.llm,
                question=user_message,
                response=ai_response
            )
            context_score = self.context_metric.score(
                llm=self.llm,
                question=user_message,
                context=retrieved_context
            )

            supabase.table("evaluation_results").insert({
                "log_id":            log_id,
                "faithfulness":      1.0 if faithfulness_score.value == "pass" else 0.0,
                "answer_relevance":  1.0 if relevance_score.value == "pass" else 0.0,
                "context_precision": 1.0 if context_score.value == "pass" else 0.0,
            }).execute()

        except Exception as e:
            print(f"[EVAL_ERROR] Failed to evaluate log {str(log_id)[:8]}...: {e}")


evaluator_service = EvaluatorService()