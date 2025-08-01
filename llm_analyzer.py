import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from transformers import AutoTokenizer
from datetime import datetime
import fitz  # PyMuPDF
from docx import Document
from tqdm import tqdm
import subprocess

EXTRACTED_DIR = "extracted_data"
SUMMARY_DIR = "summaries"
PDF_DIR = "pdf_summaries"

os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

def chunk_text_by_tokens(text, max_tokens=900):
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokenizer.decode(tokens[i:i+max_tokens], skip_special_tokens=True)
        chunks.append(chunk)
    return chunks

def extract_text_from_file(filepath):
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.endswith(".docx"):
        doc = Document(filepath)
        return "\n\n".join([para.text for para in doc.paragraphs])
    elif filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return "\n\n".join([page.get_text() for page in doc])
    else:
        raise ValueError("Unsupported file format.")

def get_summary_params(depth):
    return {
        "short": {"max_length": 100, "min_length": 30},
        "medium": {"max_length": 200, "min_length": 60},
        "detailed": {"max_length": 300, "min_length": 100}
    }.get(depth, {"max_length": 300, "min_length": 100})

def summarize_text_local(text, depth="medium", model="mistral", use_gpu=None):
    """
    Summarize text using Ollama with proper UTF-8 encoding and optional GPU control.
    
    Args:
        text: The text to summarize
        depth: Summary depth (short, medium, detailed)
        model: The Ollama model to use
        use_gpu: Control GPU usage (None=auto, True=force GPU, False=CPU only)
    """
    prompt_map = {
        "short": "Summarize the following text in 1-2 lines:",
        "medium": "Summarize the following text in a paragraph:",
        "detailed": "Summarize the following text in detail, covering all important points:"
    }
    prompt = f"{prompt_map.get(depth, 'Summarize the following text:')}\n\n{text}"
    
    # Base command
    cmd = ["ollama", "run"]
    
    # Add GPU control if specified
    if use_gpu is not None:
        if use_gpu:
            cmd.append("--gpu")
        else:
            cmd.append("--cpu-only")
    
    # Add model name
    cmd.append(model)
    
    try:
        # Use explicit encoding for input and output
        result = subprocess.run(
            cmd,
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=180
        )
        
        # Decode output with error handling
        if result.returncode == 0:
            return result.stdout.decode('utf-8', errors='replace').strip()
        else:
            error = result.stderr.decode('utf-8', errors='replace')
            print(f"Ollama error: {error}")
            return None
    except Exception as e:
        print(f"Ollama summarization error: {e}")
        return None

def generate_pdf(text, output_path, title="Summary", author="AI Analyzer"):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    doc.title = title
    doc.author = author
    doc.subject = "AI-generated summary"
    doc.keywords = "AI, summary, research"
    doc.creator = "AI Analyzer"
    doc.producer = "AI Analyzer PDF Generator"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    styles = getSampleStyleSheet()
    story = [Paragraph(f"<b>{title}</b><br/><i>Generated on: {timestamp}</i>", styles['Title']), Spacer(1, 24)]

    normal_style = ParagraphStyle(name='Justify', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=12, leading=15)
    for para in text.split('\n\n'):
        story.append(Paragraph(para.replace('\n', '<br/>').strip(), normal_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"✅ PDF saved to {output_path}")

def analyze_and_summarize_paper(filepath, filename, chunk_depth="medium", final_depth="detailed"):
    try:
        text = extract_text_from_file(filepath)
    except Exception as e:
        print(f"❌ Failed to extract text from {filename}: {e}")
        return

    if not text.strip():
        print(f"⚠️ {filename} is empty. Skipping.")
        return

    chunks = chunk_text_by_tokens(text)
    partial_summaries = []

    for i, chunk in enumerate(tqdm(chunks, desc=f"⏳ Summarizing chunks of {filename}", unit="chunk")):
        summary = summarize_text_local(chunk, depth=chunk_depth)
        if summary:
            partial_summaries.append(summary)
        else:
            print(f"⚠️ Failed to summarize chunk {i+1} of {filename}")

    if not partial_summaries:
        print(f"❌ No chunk summaries generated for {filename}")
        return

    print(f"📚 Summarizing combined chunks for final summary of {filename}...")
    combined_summary_text = "\n".join(partial_summaries)
    final_summary = summarize_text_local(combined_summary_text, depth=final_depth)
    if not final_summary:
        final_summary = combined_summary_text

    summary_path = os.path.join(SUMMARY_DIR, filename.replace(".pdf", ".txt").replace(".docx", ".txt"))
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(final_summary)

    pdf_path = os.path.join(PDF_DIR, filename.replace(".txt", ".pdf").replace(".docx", ".pdf"))
    generate_pdf(final_summary, pdf_path)

def analyze_all_papers():
    for filename in os.listdir(EXTRACTED_DIR):
        if filename.endswith((".txt", ".pdf", ".docx")):
            paper_path = os.path.join(EXTRACTED_DIR, filename)
            pdf_path = os.path.join(PDF_DIR, filename.replace(".txt", ".pdf")
                                                   .replace(".pdf", ".pdf")
                                                   .replace(".docx", ".pdf"))

            if os.path.exists(pdf_path):
                print(f"✅ PDF summary for {filename} exists. Skipping.")
                continue

            print(f"\n🔍 Processing {filename}...")
            analyze_and_summarize_paper(
                paper_path,
                filename,
                chunk_depth="detailed",  # Customize summarization depth here
                final_depth="detailed"
            )

if __name__ == "__main__":
    analyze_all_papers()