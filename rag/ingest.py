from pathlib import Path

from haystack import Document
from haystack.components.preprocessors import DocumentSplitter

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder

PAPER_DIR = Path("papers")
DB_DIR = "database/qdrant"

documents = []

for md_file in PAPER_DIR.glob("*.md"):

    print("Reading", md_file.name)

    text = md_file.read_text(encoding="utf-8")

    documents.append(
        Document(
            content=text,
            meta={
                "source": md_file.name
            }
        )
    )

splitter = DocumentSplitter(
    split_by="word",
    split_length=120,
    split_overlap=30,
)

documents = splitter.run(documents)["documents"]

print(len(documents), "chunks")

document_store = QdrantDocumentStore(
    path=DB_DIR,
    embedding_dim=768
)

embedder = OllamaDocumentEmbedder(
    model="nomic-embed-text:latest"
)

documents = embedder.run(documents)["documents"]

document_store.write_documents(documents)

print("Finished indexing")
