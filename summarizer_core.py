# summarizer_core.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from transformers import AutoTokenizer
import fitz  # PyMuPDF
from docx import Document
import subprocess

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

def summarize_text_local(text, depth="medium", model="mistral"):
    prompt_map = {
        "short": "Summarize the following text in 1-2 lines:",
        "medium": "Summarize the following text in a paragraph:",
        "detailed": "Summarize the following text in detail, covering all important points:"
    }
    prompt = f"{prompt_map[depth]}\n\n{text}"

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
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
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        story.append(Paragraph(para.replace('\n', '<br/>').strip(), normal_style))
        story.append(Spacer(1, 12))

    doc.build(story)
    print(f"✅ PDF saved to {output_path}")
