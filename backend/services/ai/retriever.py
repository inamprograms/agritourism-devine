from data.supabase_client import supabase
from services.ai.embeddings.factory import get_embedding_provider

class ContextRetriever:
    def __init__(self):
        self.provider = get_embedding_provider()
    
    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        query_embedding = self.provider.embed(query)
        if not query_embedding:
            return []
        
        result = supabase.rpc("match_chunks", {
            "query_embedding": query_embedding,
            "match_count": top_k
        }).execute()
        
        if not result.data:
            return []
        
        return [row["content"] for row in result.data]

# RUN: python -m services.ai.retriever 
# if __name__ == "__main__":
#     context_retriever = ContextRetriever()
#     results = context_retriever.retrieve("Query here to test the script")
#     for r in results:
#         print(r)
#         print("---")