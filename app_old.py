import streamlit as st

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

from ollama import chat


# -------------------------
# Configuration
# -------------------------

DB_DIR = "database/qdrant"


# -------------------------
# Load database
# -------------------------

@st.cache_resource
def load_database():

    document_store = QdrantDocumentStore(
        path=DB_DIR,
        embedding_dim=768
    )

    embedder = OllamaTextEmbedder(
        model="nomic-embed-text:latest"
    )

    retriever = QdrantEmbeddingRetriever(
        document_store=document_store
    )

    return document_store, embedder, retriever


document_store, embedder, retriever = load_database()


# -------------------------
# Interface
# -------------------------

st.title("SiderAI")
st.subheader("Scientific Literature Assistant")

st.write(
    """
    Local AI assistant for scientific literature analysis.
    Powered by Ollama, Qdrant and Retrieval-Augmented Generation (RAG).
    """
)


question = st.text_input(
    "Ask SiderAI:"
)


if question:


    # -------------------------
    # Embed question
    # -------------------------

    embedding_result = embedder.run(
        text=question
    )

    query_embedding = embedding_result["embedding"]


    # -------------------------
    # Retrieval
    # -------------------------

    results = retriever.run(
        query_embedding=query_embedding,
        top_k=5
    )


    documents = results["documents"]


    context = "\n\n".join(
        [
            doc.content
            for doc in documents
        ]
    )


    # -------------------------
    # Ask Ollama
    # -------------------------

    response = chat(

        model="qwen3:8b",

        messages=[

            {
                "role": "system",
                "content": """
You are SiderAI,
a scientific literature assistant.

Rules:
- Use only provided context.
- Do not use external knowledge.
- If information is missing, say so.
- Preserve scientific names exactly.
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


    st.subheader("Answer")

    st.write(
        response["message"]["content"]
    )


    # -------------------------
    # Sources
    # -------------------------

    with st.expander("Retrieved sources"):

        for i, doc in enumerate(documents):

            st.markdown(
                f"### Chunk {i+1}"
            )

            st.write(
                doc.content[:1000]
            )
