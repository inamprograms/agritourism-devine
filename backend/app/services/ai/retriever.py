from app.core.supabase import supabase
from app.services.ai.embeddings.factory import get_embedding_provider

class ContextRetriever:
    SIMILARITY_THRESHOLD = 0.5
    
    def __init__(self):
        self.provider = get_embedding_provider()
    
    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.provider.embed(query)
        if not query_embedding:
            return []
        
        result = supabase.rpc("match_chunks", {
            "query_embedding": query_embedding,
            "match_count": top_k
        }).execute()
        
        if not result.data:
            return []

        filtered = [
            row for row in result.data
            if row.get("similarity", 1.0) >= self.SIMILARITY_THRESHOLD
        ]

        return [
            {"content": row["content"], "similarity": round(row.get("similarity", 0.0), 4)}
            for row in filtered
        ]

# RUN: python -m services.ai.retriever 
# if __name__ == "__main__":
#     context_retriever = ContextRetriever()
#     results = context_retriever.retrieve("Query here to test the script")
#     for r in results:
#         print(r)
#         print("---")