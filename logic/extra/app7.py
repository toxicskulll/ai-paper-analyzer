import os
import time
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import subprocess
from docx import Document
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import tiktoken  # Tokenizer for chunking
import re
import logging
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import markdown2
import re
from pdf_integration import pdf_export_ui, comparison_pdf_export_ui
from st_aggrid import AgGrid, GridOptionsBuilder
import threading
import traceback
import sys
import json

# ------------------- Configuration -------------------
EXTRACTED_DIR = "extracted_data"
SUMMARY_DIR = "summaries"
PDF_DIR = "pdf_summaries"
COMPARISON_DIR = "comparisons"
LOG_FILE = "summarizer_debug.log"

# Create directories
for directory in [EXTRACTED_DIR, SUMMARY_DIR, PDF_DIR, COMPARISON_DIR]:
    os.makedirs(directory, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

OLLAMA_PATH = r"C:\\Users\\aadis\\AppData\\Local\\Programs\\Ollama\\ollama.exe"
MODEL_NAME = "mistral"

MAX_TOKENS_PER_CHUNK = 1024  # Adjusted for Mistral model
SUMMARY_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# ------------------- Enhanced UI Setup -------------------
st.set_page_config(
    page_title="🧠 AI Research Paper Analyzer Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .process-step {
        background: #e8f4fd;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        border-left: 3px solid #2196F3;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
    }
    .timer-display {
        font-family: 'Courier New', monospace;
        font-size: 1.2em;
        color: #667eea;
        font-weight: bold;
    }
    .comparison-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧠 AI Research Paper Analyzer Pro</h1>
    <p>Advanced Multi-Paper Analysis with Real-time Processing & Comparison Tools</p>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar
with st.sidebar:
    st.markdown("### ⚙️ Analysis Configuration")
    
    # Processing mode
    processing_mode = st.radio(
        "Processing Mode", 
        ["Single Paper Analysis", "Batch Processing", "Comparative Analysis"], 
        index=0
    )
    
    # Analysis settings
    depth = st.selectbox(
        "Summary Style", 
        ["comprehensive", "bullet-point", "paragraph", "detailed"], 
        index=0,
        key="summary_style_dropdown"
    )
    st.markdown("---")

    st.markdown("**🧮 Max Tokens per Chunk**")
    MAX_TOKENS_PER_CHUNK = st.slider(
    "⚠️ Larger chunks take more memory & time", 
    min_value=256, max_value=2048, step=128, 
    value=1024,
    help="Controls how much text (in tokens) is sent to the model per chunk. Default is 1024."
    )

    
    # Advanced options
    with st.expander("🔧 Advanced Settings"):
        show_chunks = st.checkbox("🔍 Show individual chunk summaries", value=False)
        show_keywords = st.checkbox("🔑 Extract and show keywords", value=True)
        show_logs = st.checkbox("🛠 Show Debug Logs", value=False)
        show_realtime = st.checkbox("⏱️ Show Real-time Processing", value=True)
        
        keyword_count = st.slider("Number of keywords to extract", 5, 30, 15)
    
    # Comparison settings (only show when comparative analysis is selected)
    if processing_mode == "Comparative Analysis":
        st.markdown("### 📊 Comparison Settings")
        comparison_metrics = st.multiselect(
            "Compare by:",
            ["Keywords", "Summary Length", "Processing Time", "Paper Sections", "Key Findings"],
            default=["Keywords", "Key Findings"]
        )

# ------------------- Enhanced Helper Functions -------------------

import streamlit as st
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx
from threading import Thread
import queue

class RealTimeLogger:
    def __init__(self, max_logs=1000):
        self.logs = []
        self.log_queue = queue.Queue()
        self.max_logs = max_logs
        self.start_time = None
        self.step_times = {}
        self.update_thread = None

    def start_process(self, process_name: str):
        self.start_time = time.time()
        self.log_step("🚀 Starting Process", process_name)

    def log_step(self, step_name: str, details: str = ""):
        current_time = time.time()
        if self.start_time:
            elapsed = current_time - self.start_time
            self.step_times[step_name] = elapsed
            timestamp = f"[{elapsed:.2f}s]"
        else:
            timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"

        log_entry = f"{timestamp} {step_name}"
        if details:
            log_entry += f": {details}"

        if len(self.logs) >= self.max_logs:
            self.logs.pop(0)
        self.logs.append(log_entry)
        self.log_queue.put(log_entry)
        logging.info(log_entry)

    def display_logs(self, container, typing_speed=0.04, cursor_blink_interval=0.5):
        placeholder = container.empty()

        def stream_logs():
            displayed_lines = []  # list of all full lines logged so far
            current_line = ""
            cursor_visible = True
            last_update_time = time.time()

            while True:
                try:
                    new_log = self.log_queue.get_nowait()

                    # Typewriter animate new log on a new line
                    if current_line:
                        displayed_lines.append(current_line)  # save previous line
                    current_line = ""

                    for char in new_log:
                        current_line += char
                        # Join all previous lines + current typing line + blinking cursor
                        full_text = "\n".join(displayed_lines + [current_line + ("▐" if cursor_visible else " ")])
                        placeholder.code(full_text, language="log")
                        time.sleep(typing_speed)
                    # After typing is done, keep current_line complete with cursor
                    last_update_time = time.time()

                except queue.Empty:
                    # No new logs, blink cursor only on current line end
                    if time.time() - last_update_time >= cursor_blink_interval:
                        cursor_visible = not cursor_visible
                        full_text = "\n".join(displayed_lines + [current_line + ("▐" if cursor_visible else " ")])
                        placeholder.code(full_text, language="log")
                        last_update_time = time.time()
                    time.sleep(0.1)

        if not self.update_thread or not self.update_thread.is_alive():
            self.update_thread = Thread(target=stream_logs, daemon=True)
            add_script_run_ctx(self.update_thread)
            self.update_thread.start()

def extract_paper_metadata(text: str) -> dict:
    metadata = {
        "title": "",
        "authors": [],
        "abstract": "",
        "publication_year": "",
        "keywords": [],
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    first_lines = lines[:50]

    # --- Title: first line longer than 5 words, no URL
    for line in first_lines:
        if 5 <= len(line.split()) <= 20 and not re.search(r'http|www|elsevier|license', line.lower()):
            metadata["title"] = line.strip()
            break

    # --- Authors: extract names before "Abstract"
    for line in first_lines:
        if re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", line) and not re.search(r'abstract|doi|journal|published', line.lower()):
            candidates = [x.strip() for x in re.split(r",| and ", line)]
            metadata["authors"] = [c for c in candidates if len(c.split()) <= 4 and any(w[0].isupper() for w in c.split())]
            break

    # --- Year: First 4-digit number (real year)
    year_match = re.search(r'\b(19|20)\d{2}\b', "\n".join(first_lines))
    if year_match:
        metadata["publication_year"] = year_match.group(0)

    return metadata

def enhanced_chunk_text(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> List[dict]:
    """Enhanced chunking with context preservation and metadata"""
    try:
        encoder = tiktoken.get_encoding("gpt2")
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_metadata = {"start_sentence": 0, "end_sentence": 0, "section": "unknown"}
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = len(encoder.encode(sentence))
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "token_count": current_tokens,
                    "metadata": chunk_metadata.copy()
                })
                
                # Start new chunk
                current_chunk = sentence + " "
                current_tokens = sentence_tokens
                chunk_metadata = {"start_sentence": i, "end_sentence": i, "section": "unknown"}
            else:
                current_chunk += sentence + " "
                current_tokens += sentence_tokens
                chunk_metadata["end_sentence"] = i
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "token_count": current_tokens,
                "metadata": chunk_metadata
            })
        
        return chunks
        
    except Exception as e:
        logging.exception(f"Enhanced chunking failed: {e}")
        # Fallback to simple chunking
        simple_chunks = chunk_text_by_tokens(text, max_tokens)
        return [{"text": chunk, "token_count": len(chunk)//4, "metadata": {}} for chunk in simple_chunks]

def chunk_text_by_tokens(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> list[str]:
    """Split text into chunks based on token count"""
    try:
        encoder = tiktoken.get_encoding("gpt2")
        tokens = encoder.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i+max_tokens]
            chunk_text = encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks
    except Exception as e:
        logging.exception(f"Chunking failed: {e}")
        chunk_size = max_tokens * 4
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
def enhanced_summarize_text(text: str, style: str = "comprehensive", metadata: dict = None, model: str = MODEL_NAME) -> str:
    """Enhanced summarization with structured prompts and UTF-8 safe subprocess handling."""

    # Create context from metadata
    context_info = ""
    if metadata:
        if metadata.get("title"):
            context_info += f"Paper Title: {metadata['title']}\n"
        if metadata.get("authors"):
            context_info += f"Authors: {', '.join(metadata['authors'])}\n"
        if metadata.get("publication_year"):
            context_info += f"Publication Year: {metadata['publication_year']}\n"
        if context_info:
            context_info += "\n"

    # Rich prompt templates for deep analysis
    prompt_templates = {
        "comprehensive": f"""You are an expert research paper analyzer. Analyze this research paper section and provide a comprehensive analysis.

{context_info}ANALYZE THE FOLLOWING RESEARCH PAPER CONTENT:

**REQUIRED ANALYSIS STRUCTURE:**

🎯 **RESEARCH OBJECTIVE & PROBLEM**
- What specific problem does this research address?
- What are the research questions or hypotheses?
- What gap in knowledge does this fill?

🔬 **METHODOLOGY & APPROACH**
- What research methods, algorithms, or techniques are employed?
- What datasets, tools, or experimental setup is used?
- What is the overall research design and approach?

💡 **KEY CONTRIBUTIONS & INNOVATIONS**
- What are the main contributions of this work?
- What novel techniques, algorithms, or insights are introduced?
- How does this advance the field?

📊 **RESULTS & FINDINGS**
- What are the key quantitative and qualitative results?
- What performance metrics, statistics, or outcomes are reported?
- What are the main findings and their significance?

⚠️ **LIMITATIONS & CHALLENGES**
- What limitations does the study acknowledge?
- What challenges or constraints were encountered?
- What aspects need further investigation?

🔮 **FUTURE DIRECTIONS & IMPLICATIONS**
- What future research directions are suggested?
- What are the broader implications for the field?
- What practical applications are possible?

Be specific, accurate, and extract concrete details. Do not fabricate information not present in the text.
You must strictly analyze only the following content. Do not add anything not present in the input.

CONTENT TO ANALYZE:
{text}""",

        "bullet-point": f"""{context_info}Analyze the provided content and produce a structured, factual bullet-point summary using the following format. Start each point in a new line. Do not include interpretations or assumptions:

• **Problem Statement**: Clearly state the research problem being addressed.  
• **Methodology**: Summarize the specific methods or approaches used in the work.  
• **Key Contributions**: Highlight the main innovations or unique contributions.  
• **Results**: Provide the primary findings and performance metrics, if any.  
• **Limitations**: List the limitations acknowledged in the content.  
• **Future Work**: Mention any proposed directions for future research. 

Content: {text}""",

        "paragraph": f"""{context_info}Strictly summarize the content in a single, coherent paragraph. The paragraph must objectively include the research objective, methodology, key findings, contributions, limitations, and future work—without interpretation or added commentary.

Content: {text}""",

        "detailed": f"""{context_info}Produce a detailed, structured analysis of the content using the following strict format. Do not include any external assumptions—only use the given content:

• **Objective**:  
• **Methodology**:  
• **Key Contributions**:  
• **Results**:  
• **Limitations**:  
• **Future Work**:

Content: {text}"""
    }

    prompt = prompt_templates.get(style, prompt_templates["comprehensive"])

    for attempt in range(SUMMARY_RETRIES):
        try:
            logging.debug(f"Attempt {attempt + 1}: Running ollama subprocess")
            logging.debug(f"Prompt length: {len(prompt)}")
            logging.debug(f"Prompt preview:\n{prompt[:300]}")

            result = subprocess.run(
                [OLLAMA_PATH, "run", model],
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=180,
                check=False
            )

            stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
            stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""

            logging.debug(f"Return code: {result.returncode}")
            logging.debug(f"STDOUT preview:\n{stdout[:300]}")
            logging.debug(f"STDERR preview:\n{stderr[:300]}")

            if result.returncode == 0 and stdout.strip():
                return stdout.strip()
            else:
                logging.warning(f"Ollama returned non-zero or empty result: {result.returncode} | stderr: {stderr}")

        except subprocess.TimeoutExpired:
            logging.warning(f"Summarization attempt {attempt + 1} timed out.")
        except Exception as e:
            logging.exception(f"Summarization attempt {attempt + 1} failed: {e}")

        if attempt < SUMMARY_RETRIES - 1:
            time.sleep(RETRY_DELAY_SECONDS)

    return "⚠️ Failed to generate summary after multiple attempts."

def clean_text(text: str) -> str:
    """Clean text by removing non-ASCII characters and normalizing whitespace"""
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT files"""
    ext = file_path.split(".")[-1].lower()
    try:
        if ext == "pdf":
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        elif ext == "docx":
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        elif ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            logging.warning(f"Unsupported file type: {ext}")
            return ""
    except Exception as e:
        logging.exception(f"Text extraction failed for {file_path}: {e}")
        return ""

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract most frequent keywords from text, excluding stop words"""
    try:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        filtered_words = [word for word in words if word not in ENGLISH_STOP_WORDS]
        word_counter = Counter(filtered_words)
        return [word for word, count in word_counter.most_common(top_n)]
    except Exception as e:
        logging.exception(f"Keyword extraction failed: {e}")
        return []
    
def extract_structured_fields(summary: str) -> dict:
    """Extract specific fields from the AI-generated summary"""
    fields = {
        "dataset": "",
        "modality": "",
        "methodology": "",
        "metrics": "",
        "results": "",
        "contributions": "",
        "limitations": ""
    }

    patterns = {
        "dataset": r"(?:dataset[s]? used|dataset[s]?|data used):?\s*(.*?)(?:\n|$)",
        "modality": r"(?:modality|data type|scan type):?\s*(.*?)(?:\n|$)",
        "methodology": r"(?:methodology|approach|technique[s]?):?\s*(.*?)(?:\n|$)",
        "metrics": r"(?:evaluation metrics|metrics used|measured by):?\s*(.*?)(?:\n|$)",
        "results": r"(?:result[s]?|findings):?\s*(.*?)(?:\n|$)",
        "contributions": r"(?:contribution[s]?|novelty):?\s*(.*?)(?:\n|$)",
        "limitations": r"(?:limitation[s]?|weaknesses):?\s*(.*?)(?:\n|$)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).strip()

    return fields

def generate_comparison_report(papers_data: List[dict]) -> dict:
    """Generate comprehensive comparison report"""
    comparison = {
        "summary_stats": {},
        "keyword_overlap": {},
        "processing_times": {},
        "paper_similarities": []
    }
    
    # Basic statistics
    comparison["summary_stats"] = {
        "total_papers": len(papers_data),
        "avg_processing_time": sum(p.get("processing_time", 0) for p in papers_data) / len(papers_data),
        "total_keywords": sum(len(p.get("keywords", [])) for p in papers_data),
        "avg_chunks": sum(p.get("chunk_count", 0) for p in papers_data) / len(papers_data)
    }
    
    # Keyword overlap analysis
    all_keywords = {}
    for paper in papers_data:
        for keyword in paper.get("keywords", []):
            if keyword not in all_keywords:
                all_keywords[keyword] = []
            all_keywords[keyword].append(paper["filename"])
    
    # Find common keywords across papers
    common_keywords = {k: v for k, v in all_keywords.items() if len(v) > 1}
    comparison["keyword_overlap"] = common_keywords
    
    return comparison

def gpt_extract_fields(summary_text: str, model: str = MODEL_NAME) -> dict:
    """Use GPT (via Ollama) to extract structured fields from a paper summary."""
    prompt = f"""
You are a smart research paper extractor. Analyze the following research paper summary and extract the key fields. 
Return ONLY a Python dictionary in this format:

{{
  "dataset": "...",
  "modality": "...",
  "methodology": "...",
  "metrics": "...",
  "results": "...",
  "contributions": "...",
  "limitations": "..."
}}

Be specific and concise. Avoid vague text like 'this paper' or 'the authors'. If a field is not mentioned, write "N/A".

SUMMARY:
{summary_text}
"""

    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=90,
            check=False
        )
        output = result.stdout.decode("utf-8", errors="replace").strip()

        # Try to extract a Python dict from model output
        match = re.search(r"\{.*?\}", output, re.DOTALL)
        if match:
            extracted_json = match.group(0)
            return json.loads(extracted_json)
        else:
            return {key: "N/A" for key in ["dataset", "modality", "methodology", "metrics", "results", "contributions", "limitations"]}
    except Exception as e:
        logging.error(f"Field extraction failed: {e}")
        return {key: "N/A" for key in ["dataset", "modality", "methodology", "metrics", "results", "contributions", "limitations"]}

def generate_literature_survey_with_table(papers_data: List[dict], depth="comprehensive") -> str:
    """Generate a markdown table + unified comparative summary of all papers"""
    # Generate table headers
    headers = [
        "Author (Year)", "Dataset", "Modality", "Method", 
        "Metrics", "Results", "Contribution", "Limitations"
    ]
    table_md = "| " + " | ".join(headers) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for paper in papers_data:
        title = paper.get("title", "Untitled")
        year = paper.get("publication_year", "n.d.")
        authors = ", ".join(paper.get("authors", [])) or "Unknown"
        dataset = paper.get("dataset", "N/A")
        modality = paper.get("modality", "N/A")
        method = paper.get("methodology", "N/A")
        metrics = paper.get("metrics", "N/A")
        results = paper.get("results", "N/A")
        contrib = paper.get("contributions", "N/A")
        limits = paper.get("limitations", "N/A")

        row = f"{authors} ({year}) | {dataset} | {modality} | {method} | {metrics} | {results} | {contrib} | {limits}"
        table_md += f"| {row} |\n"

    # Now generate the narrative summary
    summary_text = generate_combined_comparative_summary(papers_data, depth)

    final_output = f"### 📊 Comparative Table\n\n```\n{table_md}\n```\n\n---\n\n### 📝 Literature Summary\n{summary_text}"
    return final_output

def generate_combined_comparative_summary(papers_data: List[dict], depth="comprehensive") -> str:
    """Create a unified, thesis-grade literature review using only paper titles for references"""
    summaries = [paper["summary"] for paper in papers_data]
    titles = [paper["title"] for paper in papers_data]
    years = [paper["publication_year"] for paper in papers_data]
    keywords = [paper["keywords"] for paper in papers_data]

    combined_prompt = f"""
You are a skilled academic researcher writing the **Related Work** section of a master's thesis or research paper. You are given structured summaries of multiple existing papers.

🎯 Your job is to write a **unified and critical literature review**, **only referring to papers by their titles**. Do NOT use "this study", author names, or generic phrases like "the paper". Always refer to each paper like: *"The paper titled XYZ explores..."*.

You must compare, contrast, and synthesize the following aspects:
- 🎯 Research Objectives
- 🧠 Methodologies
- 📊 Results & Metrics
- 💡 Key Contributions
- ⚠️ Limitations
- 🔮 Future Scope

📁 The papers are:

{"\n\n".join([f"📄 Title: {t}\n🗓 Year: {y}\n🔑 Keywords: {', '.join(k)}\n📝 Summary:\n{s}" for t, y, k, s in zip(titles, years, keywords, summaries)])}

---

🧠 **Write a polished, structured Related Work section** that:
- Follows an academic tone
- Groups papers by similarity
- Highlights differences sharply
- Refers to each paper by title only (no "the authors", no "this study")

Output in Markdown. Avoid repetition. Use section headers if useful.

Now begin.
"""
    return enhanced_summarize_text(combined_prompt, style=depth)

# ------------------- PDF Generation Integration -------------------
# Professional PDF generation
from pdf_generator import pdf_generator

def create_pdf(summary_text, formatted=True, metadata=None):
    """Create a professional conference-style PDF with proper formatting."""
    return pdf_generator.create_pdf(summary_text, metadata=metadata)


def create_comparison_visualization(papers_data: List[dict]):
    """Create visualizations for paper comparison"""
    if len(papers_data) < 2:
        return None
    
    # Processing time comparison
    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(
        x=[p["filename"] for p in papers_data],
        y=[p.get("processing_time", 0) for p in papers_data],
        name="Processing Time (seconds)",
        marker_color='skyblue'
    ))
    fig_time.update_layout(
        title="Processing Time Comparison",
        xaxis_title="Papers",
        yaxis_title="Time (seconds)"
    )
    
    # Keyword count comparison
    fig_keywords = go.Figure()
    fig_keywords.add_trace(go.Bar(
        x=[p["filename"] for p in papers_data],
        y=[len(p.get("keywords", [])) for p in papers_data],
        name="Keyword Count",
        marker_color='lightcoral'
    ))
    fig_keywords.update_layout(
        title="Keyword Count Comparison",
        xaxis_title="Papers",
        yaxis_title="Number of Keywords"
    )
    
    return fig_time, fig_keywords

# ------------------- Main Application Logic -------------------

# File upload section with enhanced UI
st.markdown("### 📁 Upload Research Papers")

upload_col1, upload_col2 = st.columns([2, 1])

with upload_col1:
    uploaded_files = st.file_uploader(
        "Select Research Papers", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        help="Upload one or more research papers for analysis. Supports PDF, DOCX, and TXT formats."
    )

with upload_col2:
    if uploaded_files:
        st.markdown(f"**📊 Files Selected:** {len(uploaded_files)}")
        for file in uploaded_files:
            st.markdown(f"• {file.name} ({file.size/1024:.1f} KB)")

# Precompute total chunks for progress tracking
total_chunks_all = 0
for f in uploaded_files:
    raw = extract_text_from_file(os.path.join(EXTRACTED_DIR, f.name))
    cleaned = clean_text(raw)
    chunks = enhanced_chunk_text(cleaned)
    total_chunks_all += len(chunks)

if "chunk_times" not in st.session_state:
    st.session_state.chunk_times = []

processed_chunk_count = 0

# Processing section
if uploaded_files:
    # Initialize session state for storing results
    if 'papers_data' not in st.session_state:
        st.session_state.papers_data = []
    
    # Process files button
    if st.button("🚀 Start Analysis", type="primary"):
        st.session_state.papers_data = []  # Reset previous results

        # Real-time processing section
        if show_realtime:
            realtime_container = st.container()
            with realtime_container:
                st.markdown("### ⏱️ Real-time Processing Monitor")
                
                # Create columns for timer and logs
                timer_col, log_col = st.columns([1, 2])
                
                with timer_col:
                    timer_placeholder = st.empty()
                    stats_placeholder = st.empty()
                
                with log_col:
                    log_placeholder = st.empty()
        
        # Initialize logger
        logger = RealTimeLogger()
        logger.start_process("Multi-Paper Analysis")
        
        # Process each file
        global_start_time = time.time()
        for file_idx, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            logger.log_step(f"📄 Processing File {file_idx + 1}/{len(uploaded_files)}", filename)
            
            # Save file
            file_path = os.path.join(EXTRACTED_DIR, filename)
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                logger.log_step("✅ File saved successfully")
            except Exception as e:
                logger.log_step("❌ File save failed", str(e))
                continue
            
            # Extract and process text
            logger.log_step("🔍 Extracting text content")
            raw_text = extract_text_from_file(file_path)
            
            if not raw_text:
                logger.log_step("❌ Text extraction failed")
                continue
            
            cleaned_text = clean_text(raw_text)
            logger.log_step("🧹 Text cleaned", f"{len(cleaned_text):,} characters")
            
            # Extract metadata
            logger.log_step("📋 Extracting metadata")
            metadata = extract_paper_metadata(cleaned_text)
            
            # Create chunks
            logger.log_step("🧩 Creating text chunks")
            chunks = enhanced_chunk_text(cleaned_text)
            logger.log_step("✅ Chunking complete", f"{len(chunks)} chunks created")
            
            # Extract keywords
            if show_keywords:
                logger.log_step("🔑 Extracting keywords")
                keywords = extract_keywords(cleaned_text, keyword_count)
                logger.log_step("✅ Keywords extracted", f"{len(keywords)} keywords found")
            else:
                keywords = []
            
            # Process chunks with AI
            logger.log_step("🤖 Starting AI analysis")
            partial_summaries = []
            chunk_start_time = time.time()
            
            for i, chunk in enumerate(chunks):
                chunk_start_time = time.time()
                logger.log_step("🔄 Processing Chunk", f"File {file_idx + 1}, Chunk {i + 1}/{len(chunks)}")

                # === Your chunk processing code here ===
                # e.g. summary = enhanced_summarize_text(chunk)
                # For demo, let's simulate some work with time.sleep(0.1)
                time.sleep(0.1)
                # =======================================

                processed_chunk_count += 1
                progress_percent = (processed_chunk_count / total_chunks_all) * 100
                elapsed_total = time.time() - logger.start_time

                with stats_placeholder.container():
                    st.markdown(f"""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

                    .neo-terminal {{
                        background: rgba(17, 24, 39, 0.85);
                        padding: 1.6rem;
                        border-radius: 14px;
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 0.95rem;
                        color: #D1FAE5;
                        line-height: 1.9;
                        box-shadow: 0 0 12px rgba(0, 255, 150, 0.2);
                        border: 1px solid rgba(0, 255, 150, 0.15);
                        backdrop-filter: blur(6px);
                        position: relative;
                    }}

                    .neo-terminal .label {{
                        color: #7DD3FC;
                        font-weight: 600;
                    }}

                    .animated-progress {{
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 2.6rem;
                        font-weight: 700;
                        text-align: center;
                        margin-top: 1.2rem;
                        background: linear-gradient(90deg, #60A5FA, #8B5CF6, #EC4899);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        animation: pulseGlow 3s ease-in-out infinite;
                    }}

                    @keyframes pulseGlow {{
                        0% {{ text-shadow: 0 0 4px #60A5FA; }}
                        50% {{ text-shadow: 0 0 12px #EC4899; }}
                        100% {{ text-shadow: 0 0 4px #60A5FA; }}
                    }}
                    </style>

                    <div class="neo-terminal">
                        > <span class="label">Total Time</span>: {elapsed_total:.1f}s<br>
                        > <span class="label">File</span>: {file_idx + 1}/{len(uploaded_files)}<br>
                        > <span class="label">Chunk</span>: {i + 1}/{len(chunks)}
                    </div>

                    <div class="animated-progress">
                        {progress_percent:.1f}%
                    </div>
                    """, unsafe_allow_html=True)

                    logger.display_logs(log_placeholder)


                # Summarize chunk
                chunk_timer_start = time.time()
                summary = enhanced_summarize_text(
                    chunk["text"], 
                    style=depth, 
                    metadata=metadata
                )
                
                if summary:
                    partial_summaries.append(summary)
                    chunk_time = time.time() - chunk_timer_start
                    logger.log_step("✅ Chunk processed", f"{chunk_time:.2f}s")
                else:
                    logger.log_step("⚠️ Chunk processing failed")
                    partial_summaries.append(f"[Error processing chunk {i+1}]")
            
            # Generate final summary
            logger.log_step("🧠 Generating comprehensive summary")
            combined_summaries = "\n\n---SECTION---\n\n".join(partial_summaries)
            
            final_summary_prompt = f"""
            Based on the following section summaries from a research paper, create a comprehensive final analysis:
            
            Paper Title: {metadata.get('title', 'Unknown')}
            Authors: {', '.join(metadata.get('authors', ['Unknown']))}
            Publication Year: {metadata.get('publication_year', 'Unknown')}
            
            Section Summaries:
            {combined_summaries}
            
            Provide a unified, comprehensive analysis that synthesizes all sections.
            """
            
            final_summary = enhanced_summarize_text(final_summary_prompt, style=depth, metadata=metadata)
            
            if not final_summary:
                final_summary = "\n\n".join(partial_summaries)
            
            structured_fields = gpt_extract_fields(final_summary)
            processing_time = time.time() - chunk_start_time
            logger.log_step("✅ Analysis complete", f"Total: {processing_time:.2f}s")
            
            # Store results
            paper_data = {
                "filename": filename,
                "title": metadata.get("title", filename),
                "authors": metadata.get("authors", []),
                "publication_year": metadata.get("publication_year", ""),
                "abstract": metadata.get("abstract", ""),
                "keywords": keywords,
                "summary": final_summary,
                "chunk_count": len(chunks),
                "processing_time": processing_time,
                "chunks": chunks if show_chunks else [],
                "partial_summaries": partial_summaries if show_chunks else []
            }
            
            # ✅ Merge GPT extracted fields
            paper_data.update(structured_fields)
            
            st.session_state.papers_data.append(paper_data)

            # Pre-generate all comparative outputs for session
            if "literature_survey_output" not in st.session_state:
                st.session_state.literature_survey_output = generate_literature_survey_with_table(st.session_state.papers_data, depth)

            if "research_paper_output" not in st.session_state:
                st.session_state.research_paper_output = generate_combined_comparative_summary(st.session_state.papers_data, depth)

            if "narrative_literature_review" not in st.session_state:
                st.session_state.narrative_literature_review = generate_combined_comparative_summary(st.session_state.papers_data, depth)

        
        logger.log_step("🎉 All files processed successfully!")
    
    # Display results if available
    if st.session_state.papers_data:
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Results display mode
        display_mode = st.radio(
            "Choose display mode:",
            ["Individual Papers", "Comparative Analysis", "Summary Dashboard"],
            horizontal=True
        )
        
        if display_mode == "Individual Papers":
            # Display each paper individually
            for i, paper in enumerate(st.session_state.papers_data):
                with st.expander(f"📄 {paper['title'][:100]}..." if len(paper['title']) > 100 else f"📄 {paper['title']}", expanded=i==0):
                    
                    # Paper metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**👥 Authors:** {', '.join(paper['authors']) if paper['authors'] else 'Unknown'}")
                    with col2:
                        st.markdown(f"**📅 Year:** {paper['publication_year'] or 'Unknown'}")
                    with col3:
                        st.markdown(f"**⏱️ Processing Time:** {paper['processing_time']:.2f}s")
                    
                    # Keywords
                    if paper['keywords']:
                        st.markdown("**🔑 Keywords:**")
                        keyword_cols = st.columns(min(5, len(paper['keywords'])))
                        for j, keyword in enumerate(paper['keywords'][:10]):
                            with keyword_cols[j % len(keyword_cols)]:
                                st.badge(keyword.title())
                    
                    # Abstract (if available)
                    if paper['abstract']:
                        st.markdown("**📝 Abstract:**")
                        st.info(paper['abstract'])
                    
                    # Summary
                    st.markdown("**🧠 AI Analysis:**")
                    st.markdown(paper['summary'])
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download Summary (TXT)",
                            data=paper['summary'],
                            file_name=f"{paper['filename']}_summary.txt",
                            mime="text/plain"
                        )
                    with col2:
                        try:
                            export_formatted = st.toggle(
                                "🎨 Export Fancy Formatted PDF", 
                                value=True, 
                                key=f"format_toggle_{i}"
                            )
                            
                            pdf_bytes = create_pdf(
                                summary_text=paper['summary'],
                                formatted=export_formatted,
                                metadata={
                                    "title": paper.get("title", ""),
                                    "authors": paper.get("authors", []),
                                    "publication_year": paper.get("publication_year", "")
                                }
                            )

                            if pdf_bytes:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                clean_filename = re.sub(r'[^\w\-_\.]', '_', paper['filename'])
                                filename = f"{clean_filename}_summary_{timestamp}.pdf"

                                st.download_button(
                                    label="📥 Download PDF Summary",
                                    data=pdf_bytes,
                                    file_name=filename,
                                    mime="application/pdf",
                                    key=f"pdf_dl_{i}",
                                    help="Download summary as PDF"
                                )
                            else:
                                st.error("Failed to generate PDF")

                        except Exception as e:
                            st.error(f"PDF generation error: {str(e)}")
                            logging.error(f"PDF download error for {paper.get('filename', 'unknown')}: {e}")

        
        elif display_mode == "Comparative Analysis":
            if len(st.session_state.papers_data) < 2:
                st.warning("⚠️ Comparative analysis requires at least 2 papers.")
            else:
                st.markdown("### 📊 Paper Comparison")
                
                # Generate comparison report
                comparison_report = generate_comparison_report(st.session_state.papers_data)
                
                # Display comparison statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Papers", comparison_report["summary_stats"]["total_papers"])
                with col2:
                    st.metric("Avg Processing Time", f"{comparison_report['summary_stats']['avg_processing_time']:.2f}s")
                with col3:
                    st.metric("Total Keywords", comparison_report["summary_stats"]["total_keywords"])
                with col4:
                    st.metric("Avg Chunks", f"{comparison_report['summary_stats']['avg_chunks']:.1f}")
                
                # Visualizations
                if len(st.session_state.papers_data) >= 2:
                    fig_time, fig_keywords = create_comparison_visualization(st.session_state.papers_data)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(fig_time, use_container_width=True)
                    with col2:
                        st.plotly_chart(fig_keywords, use_container_width=True)
                
                # Common keywords analysis
                if comparison_report["keyword_overlap"]:
                    st.markdown("#### 🔗 Common Keywords Across Papers")
                    overlap_df = pd.DataFrame([
                        {"Keyword": keyword, "Papers": ", ".join(papers), "Count": len(papers)}
                        for keyword, papers in comparison_report["keyword_overlap"].items()
                    ])
                    overlap_df = overlap_df.sort_values("Count", ascending=False)
                    st.dataframe(overlap_df, use_container_width=True)

                # Generate literature survey with table
                st.markdown("#### ✨ Literature Survey Mode")
                comparison_output_type = st.radio("Generate As:", ["📄 Literature Survey (Table + Summary)", "🧠 Full Research Paper"], index=0)

                if comparison_output_type == "📄 Literature Survey (Table + Summary)":
                    st.markdown("##### 📋 Literature Survey Output")
                    with st.expander("📄 View Literature Survey", expanded=True):
                        st.code(st.session_state.literature_survey_output, language="markdown")                        

                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            st.download_button("⬇️ TXT", st.session_state.literature_survey_output, "literature_survey.txt", "text/plain")
                        with col2:
                            st.download_button("📄 PDF", create_pdf(st.session_state.literature_survey_output, formatted=True), "literature_survey.pdf", "application/pdf")
                        with col3:
                            st.button("📋 Copy to Clipboard", key="copy_survey", help="Select text above and press Ctrl+C")

                elif comparison_output_type == "🧠 Full Research Paper":
                    st.markdown("##### 🧠 Research Paper Output")
                    with st.expander("📄 View Research Paper", expanded=True):
                        st.code(st.session_state.research_paper_output, language="markdown")

                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            st.download_button("⬇️ TXT", st.session_state.research_paper_output, "comparative_research_paper.txt", "text/plain")
                        with col2:
                            st.download_button("📄 PDF", create_pdf(st.session_state.research_paper_output, formatted=True), "comparative_research_paper.pdf", "application/pdf")
                        with col3:
                            st.button("📋 Copy to Clipboard", key="copy_paper", help="Select text above and press Ctrl+C")

                # Unified Literature Review Generator
                st.markdown("#### 📚 Unified Literature Review (Synthesized)")
                st.markdown("##### 📝 Literature Review Output")
                st.markdown(st.session_state.narrative_literature_review)

                st.download_button(
                    label="📄 Download Literature Review (TXT)",
                    data=st.session_state.narrative_literature_review,
                    file_name="unified_literature_review.txt",
                    mime="text/plain"
                )

                # Side-by-side comparison
                st.markdown("#### 📊 Side-by-Side Comparison")

                for i, paper in enumerate(st.session_state.papers_data):
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #444; 
                            padding: 1rem; 
                            border-radius: 10px; 
                            margin-bottom: 1rem;
                            background-color: #1e1e1e;
                            transition: 0.3s;
                        " onmouseover="this.style.backgroundColor='#2b2b2b'" onmouseout="this.style.backgroundColor='#1e1e1e'">
                        """, unsafe_allow_html=True)

                        st.markdown(f"**📄 Title:** {paper.get('title', 'Untitled')}")
                        st.markdown(f"**👥 Authors:** {', '.join(paper.get('authors', [])) or 'Unknown'}")
                        st.markdown(f"**📅 Year:** {paper.get('publication_year', 'N/A')}")
                        st.markdown(f"**🔑 Keywords:** {', '.join(paper.get('keywords', [])[:5]) or 'N/A'}")

                        findings = paper.get("summary", "")
                        bullet_points = re.findall(r"[-*•]\s+(.*)", findings)
                        if not bullet_points:
                            bullet_points = [s.strip() for s in findings.split(". ") if len(s.strip()) > 10]

                        st.markdown("**✅ Key Findings:**")
                        for bullet in bullet_points[:5]:
                            st.markdown(f"- {bullet}")

                        st.markdown("</div>", unsafe_allow_html=True)
        
        elif display_mode == "Summary Dashboard":
            st.markdown("### 📈 Analysis Dashboard")
            
            # Overview metrics
            total_papers = len(st.session_state.papers_data)
            total_processing_time = sum(p['processing_time'] for p in st.session_state.papers_data)
            total_chunks = sum(p['chunk_count'] for p in st.session_state.papers_data)
            all_keywords = [kw for p in st.session_state.papers_data for kw in p['keywords']]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Papers Analyzed", total_papers)
            with col2:
                st.metric("⏱️ Total Processing Time", f"{total_processing_time:.1f}s")
            with col3:
                st.metric("🧩 Total Chunks", total_chunks)
            with col4:
                st.metric("🔑 Unique Keywords", len(set(all_keywords)))
            
            # Papers overview table
            st.markdown("#### 📊 Papers Overview")
            overview_data = []
            for paper in st.session_state.papers_data:
                overview_data.append({
                    "Title": paper['title'][:50] + "..." if len(paper['title']) > 50 else paper['title'],
                    "Authors": ', '.join(paper['authors'][:2]) + ("..." if len(paper['authors']) > 2 else ""),
                    "Year": paper['publication_year'] or "Unknown",
                    "Keywords": len(paper['keywords']),
                    "Chunks": paper['chunk_count'],
                    "Processing Time (s)": f"{paper['processing_time']:.2f}"
                })
            
            overview_df = pd.DataFrame(overview_data)
            st.dataframe(overview_df, use_container_width=True)
            
            # Word cloud of most common keywords
            if all_keywords:
                st.markdown("#### ☁️ Most Common Keywords")
                keyword_freq = Counter(all_keywords)
                most_common = keyword_freq.most_common(20)
                
                # Create a simple bar chart for keywords
                keyword_df = pd.DataFrame(most_common, columns=['Keyword', 'Frequency'])
                fig_bar = px.bar(keyword_df, x='Keyword', y='Frequency', 
                               title="Top 20 Keywords Across All Papers")
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Processing time analysis
            st.markdown("#### ⏱️ Processing Performance")
            time_data = [(p['title'][:30], p['processing_time'], p['chunk_count']) 
                        for p in st.session_state.papers_data]
            time_df = pd.DataFrame(time_data, columns=['Paper', 'Processing Time', 'Chunks'])
            
            fig_scatter = px.scatter(time_df, x='Chunks', y='Processing Time', 
                                   hover_name='Paper',
                                   title="Processing Time vs Number of Chunks")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Bulk operations
        st.markdown("---")
        st.markdown("### 🔧 Bulk Operations")
        
        bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
        
        with bulk_col1:
            if st.button("📥 Download All Summaries (ZIP)", type="secondary"):
                st.info("Bulk download feature will be implemented")
        
        with bulk_col2:
            if st.button("📊 Generate Comparison Report", type="secondary"):
                st.info("Detailed comparison report generation will be implemented")
        
        with bulk_col3:
            if st.button("🔄 Reprocess All", type="secondary"):
                st.session_state.papers_data = []
                st.rerun()

# Debug logs section (if enabled)
if show_logs:
    st.markdown("---")
    st.markdown("### 🛠️ Debug Information")
    
    debug_tabs = st.tabs(["📋 Current Session", "📁 Log Files", "⚙️ System Info"])
    
    with debug_tabs[0]:
        if st.session_state.get('papers_data'):
            st.json({
                "papers_processed": len(st.session_state.papers_data),
                "total_chunks": sum(p['chunk_count'] for p in st.session_state.papers_data),
                "total_processing_time": sum(p['processing_time'] for p in st.session_state.papers_data),
                "papers": [{"title": p['title'], "status": "completed"} for p in st.session_state.papers_data]
            })
        else:
            st.info("No processing data available in current session")
    
    with debug_tabs[1]:
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as log_file:
                    log_content = log_file.read()
                    if log_content:
                        st.text_area("Debug Logs:", value=log_content[-2000:], height=300)  # Show last 2000 chars
                    else:
                        st.info("Log file is empty")
            except Exception as e:
                st.error(f"Failed to read log file: {e}")
        else:
            st.info("No log file found")
    
    with debug_tabs[2]:
        st.markdown("**System Configuration:**")
        system_info = {
            "Ollama Path": OLLAMA_PATH,
            "Model": MODEL_NAME,
            "Max Tokens per Chunk": MAX_TOKENS_PER_CHUNK,
            "Summary Retries": SUMMARY_RETRIES,
            "Processing Directories": {
                "Extracted Data": EXTRACTED_DIR,
                "Summaries": SUMMARY_DIR,
                "PDF Output": PDF_DIR,
                "Comparisons": COMPARISON_DIR
            }
        }
        st.json(system_info)

# Footer with enhanced information
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-top: 2rem;">
    <h4>🧠 AI Research Paper Analyzer Pro</h4>
    <p><strong>Features:</strong> Multi-paper batch processing • Real-time analysis monitoring • Comparative analysis • Enhanced metadata extraction • Advanced summarization with context</p>
    <p><strong>Supported Formats:</strong> PDF, DOCX, TXT • <strong>AI Model:</strong> Local Mistral via Ollama • <strong>Processing:</strong> Smart chunking with GPT-2 tokenizer</p>
</div>
""", unsafe_allow_html=True)