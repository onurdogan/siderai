from pypdf import PdfReader
from ollama import chat

PDF_PATH = "papers/An_Updated_Zooplankton_Biodiversity_of_Turkish_Inland_Waters.pdf"

# PDF oku
reader = PdfReader(PDF_PATH)

text = ""

for page in reader.pages:
    text += page.extract_text() + "\n"

print("PDF loaded")
print(f"Characters extracted: {len(text)}")

# Çok uzun metni şimdilik kısalt
context = text[:12000]

question = input("\nAsk about the paper: ")

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": "You are a scientific assistant. Answer using the provided paper text."
        },
        {
            "role": "user",
            "content": f"""
Here is the paper text:

{context}

Question:
{question}
"""
        }
    ]
)

print("\nConsiderAI:")
print(response.message.content)
