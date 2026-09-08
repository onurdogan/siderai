from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever


DB_DIR = "database/qdrant"


document_store = QdrantDocumentStore(
    path=DB_DIR,
    embedding_dim=768
)


def retrieve_context(query, active_documents=None):

    embedder = OllamaTextEmbedder(
        model="nomic-embed-text:latest"
    )

    embedding_result = embedder.run(
        text=query
    )

    retriever = QdrantEmbeddingRetriever(
        document_store=document_store
    )

    if active_documents:

        filters = {
            "operator": "OR",
            "conditions": [
                {
                    "field": "meta.source",
                    "operator": "==",
                    "value": doc
                }
                for doc in active_documents
            ]
        }

        results = retriever.run(
            query_embedding=embedding_result["embedding"],
            top_k=5,
            filters=filters
        )

    else:

        results = retriever.run(
            query_embedding=embedding_result["embedding"],
            top_k=5
        )

    return results["documents"]
