from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder

from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

from ollama import chat


DB_DIR = "database/qdrant"


# -------------------------
# Load database
# -------------------------

document_store = QdrantDocumentStore(
    path=DB_DIR,
    embedding_dim=768
)


# -------------------------
# Initialize embedder
# -------------------------

embedder = OllamaTextEmbedder(
    model="nomic-embed-text:latest"
)


# -------------------------
# Initialize retriever
# -------------------------

retriever = QdrantEmbeddingRetriever(
    document_store=document_store
)


# -------------------------
# Interactive question loop
# -------------------------

while True:

    question = input(
        "\nAsk SiderAI (type exit to quit): "
    )


    if question.lower() == "exit":
        print("Closing SiderAI.")
        break



    # -------------------------
    # Embed question
    # -------------------------

    embedding_result = embedder.run(
        text=question
    )


    query_embedding = embedding_result["embedding"]



    # -------------------------
    # Dynamic retrieval
    # -------------------------

    if (
        "species" in question.lower()
        or "taxa" in question.lower()
        or "table" in question.lower()
        or "list" in question.lower()
    ):
        top_k = 20

    else:
        top_k = 5



    # -------------------------
    # Retrieve chunks
    # -------------------------

    results = retriever.run(
        query_embedding=query_embedding,
        top_k=top_k
    )


    print("\n--- Retrieved documents ---")


    for i, doc in enumerate(results["documents"]):

        print(
            f"\nCHUNK {i+1}"
        )

        print(
            doc.content[:500]
        )

        print(
            "-------------------------"
        )



    # -------------------------
    # Prepare context
    # -------------------------

    context = "\n\n".join(
        [
            doc.content
            for doc in results["documents"]
        ]
    )



    # -------------------------
    # Ask Qwen3
    # -------------------------

    response = chat(

        model="qwen3:8b",

        messages=[

            {
                "role": "system",

                "content": """

You are SiderAI,
a scientific literature extraction assistant.

Rules:

- Use ONLY the provided context.
- Do not use external knowledge.
- Do not summarize unless requested.
- For species extraction:
    * Return only scientific names.
    * Preserve all names appearing in tables.
    * Do not stop because a chunk ends.
    * If the table is incomplete, say:
      "Table incomplete in provided context"
- Ignore reference lists.

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

    print(
        response["message"]["content"]
    )
