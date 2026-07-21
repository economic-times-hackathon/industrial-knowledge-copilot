import os
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

print("Loading embeddings...")
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

print("Connecting to ChromaDB...")
old_store = Chroma(
    collection_name="industrial_knowledge",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

print("Fetching all valid records from SQLite...")
data = old_store.get()
ids = data["ids"]
metadatas = data["metadatas"]
documents = data["documents"]
print(f"Found {len(ids)} intact records.")

print("Creating new repaired collection...")
new_store = Chroma(
    collection_name="industrial_knowledge_repaired",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

batch_size = 500
total = len(ids)
for i in range(0, total, batch_size):
    print(f"  Inserting {i} to {min(i+batch_size, total)} ...")
    new_store.add_texts(
        texts=documents[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )

print("Repaired! Now updating retriever to use the new collection.")
