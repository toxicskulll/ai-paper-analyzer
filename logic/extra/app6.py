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
    
    # Advanced options
    with st.expander("🔧 Advanced Settings"):
        show_chunks = st.checkbox("🔍 Show individual chunk summaries", value=False)
        show_keywords = st.checkbox("🔑 Extract and show keywords", value=True)
        show_logs = st.checkbox("🛠 Show Debug Logs", value=False)
        show_realtime = st.checkbox("⏱️ Show Real-time Processing", value=True)
        
        keyword_count = st.slider("Number of keywords to extract", 5, 30, 15)
        chunk_display_mode = st.radio("Chunk display mode", ["Grid View", "Expandable Cards"], index=0)
    
    # Comparison settings (only show when comparative analysis is selected)
    if processing_mode == "Comparative Analysis":
        st.markdown("### 📊 Comparison Settings")
        comparison_metrics = st.multiselect(
            "Compare by:",
            ["Keywords", "Summary Length", "Processing Time", "Paper Sections", "Key Findings"],
            default=["Keywords", "Key Findings"]
        )

# ------------------- Enhanced Helper Functions -------------------

class RealTimeLogger:
    """Enhanced real-time logging with Streamlit integration"""
    def __init__(self):
        self.logs = []
        self.start_time = None
        self.step_times = {}
    
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
        
        self.logs.append(log_entry)
        logging.info(log_entry)
    
    def get_elapsed_time(self) -> float:
        if self.start_time:
            return time.time() - self.start_time
        return 0
    
    def display_logs(self, container):
        if self.logs:
            log_text = "\n".join(self.logs)
            container.code(log_text, language="log")

def extract_paper_metadata(text: str) -> dict:
    """Enhanced metadata extraction including title, authors, abstract"""
    metadata = {
        "title": "",
        "authors": [],
        "abstract": "",
        "publication_year": "",
        "keywords": [],
        "sections_detected": []
    }
    
    lines = text.split('\n')[:50]  # Check first 50 lines for metadata
    text_lower = text.lower()
    
    # Extract title (usually first meaningful line)
    for line in lines:
        line = line.strip()
        if len(line) > 10 and not line.lower().startswith(('abstract', 'introduction')):
            if not re.match(r'^\d+', line):  # Skip lines starting with numbers
                metadata["title"] = line
                break
    
    # Extract authors (look for common patterns)
    author_patterns = [
        r'(?:author[s]?[:]*\s*)(.*)',
        r'(?:by\s+)(.*?)(?:\n|$)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)'
    ]
    
    for pattern in author_patterns:
        matches = re.findall(pattern, text[:1000], re.IGNORECASE | re.MULTILINE)
        if matches:
            authors_text = matches[0].strip()
            metadata["authors"] = [author.strip() for author in re.split(r'[,;&]', authors_text)]
            break
    
    # Extract abstract
    abstract_match = re.search(r'abstract[:\s]*\n?(.*?)(?:\n\s*\n|\nintroduction|\nkeywords)', text_lower, re.DOTALL | re.IGNORECASE)
    if abstract_match:
        metadata["abstract"] = abstract_match.group(1).strip()[:500]  # Limit abstract length
    
    # Extract publication year
    year_matches = re.findall(r'\b(20\d{2}|19\d{2})\b', text[:1000])
    if year_matches:
        metadata["publication_year"] = year_matches[0]
    
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

        "bullet-point": f"""{context_info}Analyze the provided content and produce a structured, factual bullet-point summary using the following format. Do not include interpretations or assumptions:

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

def generate_combined_comparative_summary(papers_data: List[dict], depth="comprehensive") -> str:
    """Create a unified, academic-style literature review comparing all papers"""
    summaries = [paper["summary"] for paper in papers_data]
    titles = [paper["title"] for paper in papers_data]
    years = [paper["publication_year"] for paper in papers_data]
    keywords = [paper["keywords"] for paper in papers_data]

    combined_prompt = f"""
You are a world-class AI researcher tasked with writing the *ultimate related work section* of a thesis, based on several cutting-edge research papers.

You are given the following research paper summaries, each analyzing a different work. Your job is to **compare, contrast, and synthesize** these papers to form a single, insightful, cohesive narrative that highlights their **similarities, differences, strengths, weaknesses, and gaps**.

You must behave like a real student writing the "RELATED WORK" or "LITERATURE REVIEW" section of their thesis.

🎯 **Your writing must include**:
- A **thematic comparison** of research objectives.
- A **comparative breakdown of methodologies**, highlighting novel vs traditional approaches.
- A **cross-paper synthesis** of results, findings, and performance metrics.
- Clear **contrast of limitations** and how different papers attempt to address challenges.
- A **discussion of gaps and what future research could unite or explore further.**

💡 **Advanced Instructions**:
- Use phrases like *"Unlike prior work..."*, *"In contrast..."*, *"Building upon..."*, *"All papers agree on..."*, *"However, Paper X diverges by..."*
- Mention authors and years if available (e.g., *"The 2023 study by Wang et al."*)
- Treat the papers as if you’re critiquing them for a thesis.

📁 **Paper Summaries**:
{"\n\n".join([f"📄 Title: {t}\n🗓 Year: {y}\n🔑 Keywords: {', '.join(k)}\n📝 Summary:\n{s}" for t, y, k, s in zip(titles, years, keywords, summaries)])}

Now write the full narrative. Structure it with clear sections, academic tone, and depth expected from a top university student.
"""
    return enhanced_summarize_text(combined_prompt, style=depth)

export_formatted = st.toggle("🎨 Export Fancy Formatted PDF", value=True)
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
                chunk_timer_start = time.time()
                logger.log_step(f"🔄 Processing chunk {i+1}/{len(chunks)}")
                
                # Update real-time display
                if show_realtime:
                    elapsed_total = logger.get_elapsed_time()
                    with timer_placeholder.container():
                        st.markdown(f"""
                        <div class="timer-display">
                        ⏱️ Total Time: {elapsed_total:.1f}s<br>
                        📄 File: {file_idx + 1}/{len(uploaded_files)}<br>
                        🧩 Chunk: {i + 1}/{len(chunks)}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with stats_placeholder.container():
                        st.metric("Processing Progress", f"{((file_idx * len(chunks) + i + 1) / (len(uploaded_files) * sum(len(enhanced_chunk_text(clean_text(extract_text_from_file(os.path.join(EXTRACTED_DIR, f.name))))) for f in uploaded_files))) * 100:.1f}%")
                    
                    logger.display_logs(log_placeholder)
                
                # Summarize chunk
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
            
            st.session_state.papers_data.append(paper_data)
        
        logger.log_step("🎉 All files processed successfully!")
        
        # Final update to real-time display
        if show_realtime:
            total_time = logger.get_elapsed_time()
            with timer_placeholder.container():
                st.markdown(f"""
                <div class="timer-display">
                ✅ COMPLETE: {total_time:.1f}s<br>
                📄 Files: {len(uploaded_files)}<br>
                🎯 Success Rate: 100%
                </div>
                """, unsafe_allow_html=True)
    
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

                # Unified Literature Review Generator
                st.markdown("#### 📚 Unified Literature Review (Synthesized)")
                if st.button("🧠 Generate Unified Academic Narrative"):
                    with st.spinner("Analyzing and synthesizing all papers..."):
                        narrative_summary = generate_combined_comparative_summary(st.session_state.papers_data, depth=depth)
                        st.markdown("##### 📝 Literature Review Output")
                        st.markdown(narrative_summary)

                        st.download_button(
                            label="📄 Download Literature Review (TXT)",
                            data=narrative_summary,
                            file_name="unified_literature_review.txt",
                            mime="text/plain"
                        )

                # Side-by-side comparison
                st.markdown("#### 📋 Side-by-Side Comparison")
                if len(st.session_state.papers_data) >= 2:
                    paper1, paper2 = st.selectbox("Select Paper 1", [p['title'] for p in st.session_state.papers_data]), st.selectbox("Select Paper 2", [p['title'] for p in st.session_state.papers_data])
                    
                    paper1_data = next(p for p in st.session_state.papers_data if p['title'] == paper1)
                    paper2_data = next(p for p in st.session_state.papers_data if p['title'] == paper2)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**📄 {paper1_data['title']}**")
                        st.markdown(f"**Authors:** {', '.join(paper1_data['authors']) if paper1_data['authors'] else 'Unknown'}")
                        st.markdown(f"**Year:** {paper1_data['publication_year'] or 'Unknown'}")
                        st.markdown(f"**Keywords:** {', '.join(paper1_data['keywords'][:5])}")
                        st.markdown("**Summary:**")
                        st.text_area("", paper1_data['summary'][:500] + "...", height=200, key="summary1")
                    
                    with col2:
                        st.markdown(f"**📄 {paper2_data['title']}**")
                        st.markdown(f"**Authors:** {', '.join(paper2_data['authors']) if paper2_data['authors'] else 'Unknown'}")
                        st.markdown(f"**Year:** {paper2_data['publication_year'] or 'Unknown'}")
                        st.markdown(f"**Keywords:** {', '.join(paper2_data['keywords'][:5])}")
                        st.markdown("**Summary:**")
                        st.text_area("", paper2_data['summary'][:500] + "...", height=200, key="summary2")
        
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

# Advanced chunk analysis (if enabled)
if show_chunks and st.session_state.get('papers_data'):
    st.markdown("---")
    st.markdown("### 🧩 Detailed Chunk Analysis")
    
    selected_paper = st.selectbox(
        "Select paper for chunk analysis:",
        [p['title'] for p in st.session_state.papers_data if p.get('chunks')]
    )
    
    if selected_paper:
        paper_data = next(p for p in st.session_state.papers_data if p['title'] == selected_paper)
        
        if paper_data.get('chunks'):
            st.markdown(f"#### Chunks for: {selected_paper}")
            
            if chunk_display_mode == "Grid View":
                chunk_data = []
                for i, chunk in enumerate(paper_data['chunks']):
                    chunk_data.append({
                        "Chunk #": i + 1,
                        "Tokens": chunk.get('token_count', 'Unknown'),
                        "Preview": chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'],
                        "Summary": paper_data['partial_summaries'][i][:150] + "..." if i < len(paper_data['partial_summaries']) and len(paper_data['partial_summaries'][i]) > 150 else paper_data['partial_summaries'][i] if i < len(paper_data['partial_summaries']) else "No summary"
                    })
                
                chunk_df = pd.DataFrame(chunk_data)
                gb = GridOptionsBuilder.from_dataframe(chunk_df)
                gb.configure_pagination(paginationPageSize=10)
                gb.configure_default_column(wrapText=True, autoHeight=True)
                gb.configure_column("Preview", width=200)
                gb.configure_column("Summary", width=300)
                grid_options = gb.build()
                AgGrid(chunk_df, gridOptions=grid_options, theme="streamlit")
            
            else:  # Expandable Cards
                for i, chunk in enumerate(paper_data['chunks']):
                    with st.expander(f"📄 Chunk {i+1} ({chunk.get('token_count', 'Unknown')} tokens)"):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown("**Original Text:**")
                            st.text_area("", chunk['text'], height=200, key=f"chunk_text_{i}")
                        with col2:
                            st.markdown("**AI Summary:**")
                            summary = paper_data['partial_summaries'][i] if i < len(paper_data['partial_summaries']) else "No summary available"
                            st.text_area("", summary, height=200, key=f"chunk_summary_{i}")

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