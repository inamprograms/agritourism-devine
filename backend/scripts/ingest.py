from services.ai.embeddings.factory import get_embedding_provider
from data.supabase_client import supabase
import os

def load_document(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def chunk_text(text: str, chunk_size=500, overlap=100) -> list[str]:
    chunks = []   
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if len(chunk) < 50:
            break
        chunks.append(chunk)
    return chunks

def ingest(file_path: str, category: str, target_audience: str, provider):
    document_name = os.path.basename(file_path)
    content = load_document(file_path)
    print(f"Loaded {len(content)} characters")
    chunks = chunk_text(content)
    print(f"Created {len(chunks)} chunks")
    for index, chunk in enumerate(chunks):
        try:
            embedding = provider.embed(chunk)
            supabase.table("knowledge_chunks").insert({
                "content": chunk,
                "embedding": embedding,
                "document_name": document_name,
                "category": category,
                "target_audience": target_audience,
                "chunk_index": index
            }).execute()
            print(f"Inserted chunk {index + 1}/{len(chunks)}")
        except Exception as e:
            print(f"Failed chunk {index + 1}: {e}")
            continue
    
    
def main():
    path = input("Enter file path: ").strip()
    category = input("Enter category: ").strip()
    audience = input("Enter target audience: ").strip()
    provider = get_embedding_provider()
    
    try:
        ingest(path, category, audience, provider)
        # ingest("C:\\Users\\Dell\\Desktop\\test_doc.txt", "category", "audience")
        print("Ingestion complete.")
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()