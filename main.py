from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from uuid import uuid4
from pdf_extractor import extract_text_from_pdfs  # <- Make sure this file exists
from llm_analyzer import analyze_all_papers

app = FastAPI()

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload_papers/")
async def upload_papers(files: list[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_ext = file.filename.split(".")[-1]
        if file_ext.lower() != "pdf":
            return JSONResponse(status_code=400, content={"message": f"File {file.filename} is not a PDF."})
        
        unique_name = f"{uuid4()}.pdf"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        saved_files.append(unique_name)
    
    return {"message": f"{len(saved_files)} files uploaded successfully.", "files": saved_files}

# 🆕 Add this route to extract text from uploaded PDFs
@app.get("/extract_texts/")
def extract_texts():
    extract_text_from_pdfs()
    return {"message": "Text extracted from all uploaded PDFs."}

@app.get("/analyze/")
def analyze_papers():
    analyze_all_papers()
    return {"message": "All papers analyzed and structured summaries saved."}
