from ingestion.embedder import get_collection_stats
from rag_engine.retriever import retrieve

print("=== ChromaDB Stats ===")
stats = get_collection_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Categories: {stats['chunks_by_category']}")

print("\n=== Test Retrieval ===")
chunks = retrieve("process safety management", top_k=3)
print(f"Retrieved {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"  {i+1}. {chunk.filename} (score: {chunk.score})")
    print(f"     {chunk.text[:100]}...")