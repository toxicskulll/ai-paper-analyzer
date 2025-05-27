import fitz  # PyMuPDF
import os

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "extracted_data"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_text_from_pdfs():
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(UPLOAD_DIR, filename)
            text_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".txt"))

            doc = fitz.open(pdf_path)
            full_text = ""

            for page in doc:
                full_text += page.get_text()

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            print(f"[✓] Extracted: {filename} → {text_path}")
