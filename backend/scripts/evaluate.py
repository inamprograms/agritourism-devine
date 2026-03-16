import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from ragas.llms import llm_factory
from ragas.metrics import DiscreteMetric
from data.supabase_client import supabase
from config import Config

def get_unevaluated_logs():
    result = supabase.table("unevaluated_rag_logs").select("*").execute()
    return result.data

def run_evaluation():
    logs = get_unevaluated_logs()

    if not logs:
        print("No new logs to evaluate.")
        return

    print(f"Evaluating {len(logs)} interactions...")

    client = OpenAI(
        api_key=Config.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    llm = llm_factory(Config.GROQ_MODEL, provider="openai", client=client)

    faithfulness_metric = DiscreteMetric(
        name="faithfulness",
        prompt="Given the context and response, is the response faithful to the context? Does it avoid making claims not supported by the context? Return 'pass' or 'fail'.\nContext: {context}\nResponse: {response}",
        allowed_values=["pass", "fail"],
    )

    relevance_metric = DiscreteMetric(
        name="answer_relevance",
        prompt="Given the question and response, does the response directly answer the question asked? Return 'pass' or 'fail'.\nQuestion: {question}\nResponse: {response}",
        allowed_values=["pass", "fail"],
    )

    context_metric = DiscreteMetric(
        name="context_precision",
        prompt="Given the question and context, is the context relevant and useful for answering the question? Return 'pass' or 'fail'.\nQuestion: {question}\nContext: {context}",
        allowed_values=["pass", "fail"],
    )

    for log in logs:
        try:
            question = log["user_message"]
            response = log["ai_response"]
            context = log["retrieved_context"]

            faithfulness_score = faithfulness_metric.score(
                llm=llm,
                context=context,
                response=response
            )

            relevance_score = relevance_metric.score(
                llm=llm,
                question=question,
                response=response
            )

            context_score = context_metric.score(
                llm=llm,
                question=question,
                context=context
            )

            supabase.table("evaluation_results").insert({
                "log_id":            log["id"],
                "faithfulness":      1.0 if faithfulness_score.value == "pass" else 0.0,
                "answer_relevance":  1.0 if relevance_score.value == "pass" else 0.0,
                "context_precision": 1.0 if context_score.value == "pass" else 0.0,
            }).execute()

            print(
                f"Log {log['id'][:8]}... → "
                f"faithfulness: {faithfulness_score.value} | "
                f"relevance: {relevance_score.value} | "
                f"precision: {context_score.value}"
            )

        except Exception as e:
            print(f"Failed to evaluate log {log['id'][:8]}...: {e}")
            continue

    print("Evaluation complete.")


if __name__ == "__main__":
    run_evaluation()