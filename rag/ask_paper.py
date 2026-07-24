from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from ollama import chat


# Load database
document_store = QdrantDocumentStore(
    path="database/qdrant",
    embedding_dim=768
)


# Question
question = input("\nAsk SiderAI: ")


# Create question embedding
embedder = OllamaTextEmbedder(
    model="nomic-embed-text:latest"
)

embedding_result = embedder.run(
    text=question
)

query_embedding = embedding_result["embedding"]


# Retrieve relevant chunks
retriever = QdrantEmbeddingRetriever(
    document_store=document_store
)
results = retriever.run(
    query_embedding=query_embedding,
    top_k=20
)

print("\n--- Retrieved documents ---")

for i, doc in enumerate(results["documents"]):
    print(f"\nCHUNK {i+1}")
    print(doc.content[:1000])
    print("-------------------------")

context = "\n\n".join(
    [
        f"""
SOURCE: {doc.meta.get('source')}
PAGE: {doc.meta.get('page')}

{doc.content}
"""
        for doc in results["documents"]
    ]
)

# Ask Qwen3
response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
"content": """
You are SiderAI, a scientific literature extraction assistant.

You analyze scientific papers.

Rules:
- Use only the provided context.
- Do not use references or bibliography as evidence.
- Prioritize tables, figures, Results and Materials sections.
- For taxonomy questions, extract complete scientific names.
- Preserve italicized genus and species names.
- Do not summarize if the user asks for a list.
- If information is incomplete, clearly state which pages are missing.
"""
        },
        {
            "role": "user",
            "content": f"""
Context:

{context}

Question:
{question}
"""
        }
    ]
)


print("\nSiderAI:")
print(response["message"]["content"])
