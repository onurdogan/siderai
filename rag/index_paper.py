from haystack import Pipeline
from haystack.dataclasses import Document

from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter

from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


PDF_PATH = "papers/An_Updated_Zooplankton_Biodiversity_of_Turkish_Inland_Waters.pdf"


document_store = QdrantDocumentStore(
    path="database/qdrant",
    embedding_dim=768
)


converter = PyPDFToDocument()

splitter = DocumentSplitter(
    split_by="word",
    split_length=200,
    split_overlap=40
)

embedder = OllamaDocumentEmbedder(
    model="nomic-embed-text:latest"
)


pipeline = Pipeline()

pipeline.add_component("converter", converter)
pipeline.add_component("splitter", splitter)
pipeline.add_component("embedder", embedder)

pipeline.connect(
    "converter.documents",
    "splitter.documents"
)

pipeline.connect(
    "splitter.documents",
    "embedder.documents"
)


result = pipeline.run(
    {
        "converter": {
            "sources": [PDF_PATH]
        }
    }
)


documents = result["embedder"]["documents"]

document_store.write_documents(documents)

print(f"SiderAI indexed {len(documents)} document chunks.")
