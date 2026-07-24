import os
import json
from pypdf import PdfReader
from pathlib import Path

pdf_folder = "papers"
metadata_folder = "metadata"

os.makedirs(metadata_folder, exist_ok=True)


for pdf in Path(pdf_folder).glob("*.pdf"):

    print(f"Processing: {pdf.name}")

    reader = PdfReader(pdf)

    text = ""

    for page in reader.pages[:3]:
        text += page.extract_text() or ""

    metadata = {
        "title": pdf.stem,
        "file": str(pdf),
        "pages": len(reader.pages),
        "summary": "",
        "taxa": [],
        "ecosystem": [],
        "country": [],
        "methods": [],
        "markers": [],
        "keywords": []
    }

    output = Path(metadata_folder) / (pdf.stem + ".json")

    with open(output, "w") as f:
        json.dump(metadata, f, indent=4)

    print("Created:", output)
