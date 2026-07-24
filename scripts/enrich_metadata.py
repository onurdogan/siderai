import json
from pathlib import Path
from pypdf import PdfReader
import ollama


pdf_folder = Path("papers")
metadata_folder = Path("metadata")


for pdf in pdf_folder.glob("*.pdf"):

    print(f"Processing: {pdf.name}")

    # PDF text extraction
    reader = PdfReader(pdf)

    text = ""

    for page in reader.pages[:5]:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"


    prompt = f"""
You are a scientific literature assistant.

Extract metadata from this research paper.

Return ONLY valid JSON.

Fields:
title
authors
year
ecosystem
country
organisms
taxa
methods
markers
keywords
main_topics

Paper text:

{text[:12000]}
"""


    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    answer = response["message"]["content"]


    # remove possible markdown formatting
    answer = answer.replace("```json", "")
    answer = answer.replace("```", "")
    answer = answer.strip()


    try:
        metadata = json.loads(answer)

    except Exception:

        print("JSON parsing failed")
        print(answer)

        continue


    metadata["file"] = str(pdf)
    metadata["pages"] = len(reader.pages)


    output = metadata_folder / (pdf.stem + ".json")


    with open(output, "w") as f:
        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )


    print("Updated:", output)
