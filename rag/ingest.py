from pathlib import Path
import pandas as pd

from haystack import Document
from haystack.components.preprocessors import DocumentSplitter

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder

PAPER_DIR = Path("papers")
KNOWLEDGE_DIR = Path("knowledge")
DB_DIR = "database/qdrant"


documents = []


# -------------------------
# Read PDF parsed markdown
# -------------------------

for md_file in PAPER_DIR.glob("*/parsed.md"):

    paper_name = md_file.parent.name

    print("Reading PDF:", paper_name)

    text = md_file.read_text(
        encoding="utf-8"
    )

    documents.append(
        Document(
            content=text,
            meta={
                "source": md_file.name,
                "paper": paper_name,
                "type": "pdf"
            }
        )
    )



# -------------------------
# Read XLSX files
# -------------------------

for xlsx_file in list(PAPER_DIR.rglob("*.xlsx")) + list(KNOWLEDGE_DIR.rglob("*.xlsx")):

    print("Reading XLSX:", xlsx_file.name)

    excel = pd.ExcelFile(xlsx_file)


    for sheet in excel.sheet_names:

        df = pd.read_excel(
            xlsx_file,
            sheet_name=sheet
        )


        # remove empty rows
        df = df.dropna(
            how="all"
        )


        # -------------------------
        # Spreadsheet summary
        # -------------------------

        documents.append(
            Document(
                content=f"""
Source file:
{xlsx_file.name}

Spreadsheet information:

Sheet:
{sheet}

Columns:
{', '.join(df.columns.astype(str))}

Number of rows:
{len(df)}

This document contains structured tabular data.
""",
meta={
    "source": xlsx_file.name,
    "sheet": sheet,
    "type": "xlsx_summary",
    "knowledge": str(KNOWLEDGE_DIR in xlsx_file.parents)
                }
            )
        )


        # -------------------------
        # Spreadsheet rows
        # -------------------------

        for index, row in df.iterrows():

            values = row.dropna().to_dict()

            row_text = f"""
Source file:
{xlsx_file.name}

Sheet:
{sheet}

Row:
{index}

Data:
"""

            for col, value in values.items():

                row_text += f"\n{col}: {value}"


            documents.append(
                Document(
                    content=row_text,
                    meta={
                        "source": xlsx_file.name,
                        "sheet": sheet,
                        "row": int(index),
                        "type": "xlsx"
                    }
                )
            )

print(
    len(documents),
    "documents before chunking"
)



# -------------------------
# Split only long documents
# -------------------------

splitter = DocumentSplitter(
    split_by="word",
    split_length=120,
    split_overlap=30,
)


documents = splitter.run(
    documents
)["documents"]


print(
    len(documents),
    "chunks"
)


# -------------------------
# Qdrant
# -------------------------

document_store = QdrantDocumentStore(
    path=DB_DIR,
    embedding_dim=768
)



# -------------------------
# Embeddings
# -------------------------

embedder = OllamaDocumentEmbedder(
    model="nomic-embed-text:latest"
)


documents = embedder.run(
    documents
)["documents"]



# -------------------------
# Save
# -------------------------

document_store.write_documents(
    documents
)


print(
    "Finished indexing"
)
