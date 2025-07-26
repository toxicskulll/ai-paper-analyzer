import os
import time
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from docx import Document
from fpdf import FPDF
import subprocess
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import tiktoken  # Tokenizer for chunking
import re
import logging
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ------------------- Configuration -------------------
EXTRACTED_DIR = "extracted_data"
SUMMARY_DIR = "summaries"
PDF_DIR = "pdf_summaries"
LOG_FILE = "summarizer_debug.log"

os.makedirs(EXTRACTED_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

OLLAMA_PATH = r"C:\\Users\\aadis\\AppData\\Local\\Programs\\Ollama\\ollama.exe"
MODEL_NAME = "mistral"

MAX_TOKENS_PER_CHUNK = 800
SUMMARY_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# ------------------- UI Setup -------------------
st.set_page_config(page_title="📄 AI Paper Analyzer", layout="wide")
st.title("📄 AI Research Paper Analyzer")

with st.sidebar:
    st.markdown("### ⚙️ Analysis Settings")
    depth = st.radio("Summary Style", ["bullet-point", "paragraph", "detailed"], index=0)
    show_chunks = st.checkbox("🔍 Show individual chunk summaries")
    show_keywords = st.checkbox("🔑 Extract and show keywords")
    show_logs = st.checkbox("🛠 Show Debug Logs")
    
    st.markdown("### 📊 Advanced Options")
    keyword_count = st.slider("Number of keywords to extract", 5, 20, 10)
    chunk_display_mode = st.radio("Chunk display mode", ["Grid View", "Expandable Cards"], index=0)

# ------------------- Helper Functions -------------------
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
        # Fallback to character-based chunking
        chunk_size = max_tokens * 4  # Rough estimate
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract most frequent keywords from text, excluding stop words"""
    try:
        # Find words with 4+ characters
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        # Filter out stop words
        filtered_words = [word for word in words if word not in ENGLISH_STOP_WORDS]
        # Count frequency
        word_counter = Counter(filtered_words)
        # Return top N most common words
        return [word for word, count in word_counter.most_common(top_n)]
    except Exception as e:
        logging.exception(f"Keyword extraction failed: {e}")
        return []

def detect_paper_sections(text: str) -> dict:
    """Detect common paper sections in the text"""
    sections = {
        "Abstract": [],
        "Introduction": [],
        "Methodology": [],
        "Results": [],
        "Discussion": [],
        "Conclusion": [],
        "References": []
    }
    
    section_patterns = {
        "Abstract": r"(?:abstract|summary)(?:\s|:)",
        "Introduction": r"(?:introduction|background)(?:\s|:)",
        "Methodology": r"(?:method|approach|technique|algorithm)(?:\s|:)",
        "Results": r"(?:result|finding|outcome|performance)(?:\s|:)",
        "Discussion": r"(?:discussion|analysis|interpretation)(?:\s|:)",
        "Conclusion": r"(?:conclusion|summary|future\s+work)(?:\s|:)",
        "References": r"(?:reference|bibliography|citation)(?:\s|:)"
    }
    
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        line_lower = line.lower().strip()
        if len(line_lower) < 3:
            continue
            
        # Check if line matches a section header
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line_lower, re.IGNORECASE):
                current_section = section_name
                break
        
        # Add content to current section
        if current_section and line.strip():
            sections[current_section].append(line.strip())
    
    return sections

def summarize_text_local(text: str, style: str = "bullet-point", model: str = MODEL_NAME) -> str:
    """Generate summary using local Ollama model with enhanced prompts"""
    prompt_templates = {
        "bullet-point": """You are an expert research paper analyzer. Create a comprehensive bullet-point analysis of this research paper including:

• **Objective/Problem**: What problem does this paper address?
• **Methodology**: What approach, models, or techniques are used?
• **Key Contributions**: What are the main contributions or innovations?
• **Results/Findings**: What are the key results and performance metrics?
• **Limitations**: What are the acknowledged limitations or challenges?
• **Future Work**: What future research directions are suggested?

Maintain accuracy and do not fabricate information. Structure your response with clear bullet points under each category.

Text to analyze:
{text}""",

        "paragraph": """You are an expert research paper summarizer. Write a comprehensive paragraph summary of this research paper that covers:
- The main objective and problem being addressed
- The methodology and approach used
- Key findings and results with specific metrics where available
- Main contributions and significance
- Any limitations mentioned
- Future research directions

Keep the summary accurate and well-structured in paragraph form.

Text to analyze:
{text}""",

        "detailed": """You are an expert research paper analyzer. Create a detailed, structured analysis of this research paper with the following sections:

**OBJECTIVE & PROBLEM STATEMENT**
[Describe what problem this paper addresses and research objectives]

**METHODOLOGY & APPROACH**
[Detail the methods, models, datasets, and experimental setup used]

**KEY CONTRIBUTIONS**
[List the main contributions and innovations of this work]

**RESULTS & FINDINGS**
[Present key results, performance metrics, and quantitative findings]

**LIMITATIONS & CHALLENGES**
[Discuss any limitations, challenges, or areas for improvement mentioned]

**FUTURE WORK & IMPLICATIONS**
[Outline suggested future research directions and broader implications]

Ensure accuracy and do not add information not present in the original text.

Text to analyze:
{text}"""
    }
    
    prompt = prompt_templates.get(style, prompt_templates["bullet-point"]).format(text=text)
    
    for attempt in range(SUMMARY_RETRIES):
        try:
            logging.info(f"Summarization attempt {attempt + 1} for style: {style}")
            
            result = subprocess.run(
                [OLLAMA_PATH, "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                summary = result.stdout.strip()
                logging.info(f"Successfully generated summary (attempt {attempt + 1})")
                return summary
            else:
                error_msg = result.stderr if result.stderr else "No output generated"
                logging.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            logging.warning(f"Attempt {attempt + 1} timed out")
        except Exception as e:
            logging.exception(f"Attempt {attempt + 1} failed with exception: {e}")
        
        if attempt < SUMMARY_RETRIES - 1:
            time.sleep(RETRY_DELAY_SECONDS)
    
    logging.error("All summarization attempts failed")
    return None

def generate_enhanced_pdf(summary: str, output_path: str, title: str = "Research Paper Summary", 
                         keywords: list[str] = None, sections: dict = None):
    """Generate enhanced PDF with sections, keywords, and better formatting"""
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(0, 15, title, ln=True, align="C")
        pdf.ln(10)
        
        # Keywords section
        if keywords:
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(0, 10, "Keywords:", ln=True)
            pdf.set_font("Arial", size=11)
            keywords_text = ", ".join(keywords)
            pdf.multi_cell(0, 8, keywords_text)
            pdf.ln(5)
        
        # Main summary
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Arial", size=11)
        
        # Process summary text with better formatting
        lines = summary.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            
            # Check if line is a section header (contains keywords like "Objective", "Methodology", etc.)
            if any(keyword in line.upper() for keyword in ["OBJECTIVE", "METHODOLOGY", "RESULTS", "CONCLUSION", "CONTRIBUTION", "LIMITATION", "FUTURE"]):
                pdf.set_font("Arial", "B", size=11)
                pdf.ln(3)
            else:
                pdf.set_font("Arial", size=11)
            
            # Handle long lines
            if len(line) > 100:
                pdf.multi_cell(0, 6, line)
            else:
                pdf.cell(0, 6, line, ln=True)
        
        pdf.output(output_path)
        logging.info(f"PDF generated successfully: {output_path}")
        
    except Exception as e:
        logging.exception(f"PDF generation failed: {e}")
        # Fallback to simple PDF generation
        generate_simple_pdf(summary, output_path, title)

def generate_simple_pdf(text: str, output_path: str, title: str = "Summary"):
    """Fallback simple PDF generation"""
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        for line in text.split("\n"):
            if line.strip():
                pdf.multi_cell(0, 8, line.strip())
        pdf.output(output_path)
    except Exception as e:
        logging.exception(f"Simple PDF generation also failed: {e}")

# ------------------- Main Application Flow -------------------
uploaded_files = st.file_uploader(
    "Upload Research Papers (PDF, DOCX, or TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True,
    help="Select one or more research papers to analyze"
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        st.markdown(f"### 📄 Processing: **{filename}**")
        
        # Save uploaded file
        file_path = os.path.join(EXTRACTED_DIR, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"Failed to save file: {e}")
            continue

        # Processing steps explanation
        with st.expander("🔎 Analysis Process Overview"):
            st.markdown("""
            **Step-by-step processing:**
            1. ✅ **Text Extraction**: Extract plain text from PDF/DOCX/TXT files
            2. ✅ **Text Cleaning**: Remove non-ASCII characters and normalize formatting
            3. ✅ **Tokenization**: Split content using GPT-2 tokenizer for optimal chunking
            4. ✅ **Smart Chunking**: Create ~800 token chunks with context preservation
            5. ✅ **AI Summarization**: Process each chunk with local Mistral model
            6. ✅ **Keyword Extraction**: Identify key terms and concepts
            7. ✅ **Section Detection**: Automatically identify paper sections
            8. ✅ **Summary Synthesis**: Combine chunk summaries into final analysis
            9. ✅ **PDF Generation**: Create downloadable summary with enhanced formatting
            """)

        # Text extraction and processing
        with st.spinner("Extracting and preprocessing text..."):
            raw_text = extract_text_from_file(file_path)
            if not raw_text:
                st.error("Failed to extract text from file. Please check the file format.")
                continue
            
            cleaned_text = clean_text(raw_text)
            chunks = chunk_text_by_tokens(cleaned_text)
            
            # Extract keywords if requested
            keywords = extract_keywords(cleaned_text, keyword_count) if show_keywords else []
            
            # Detect sections
            sections = detect_paper_sections(cleaned_text)

        # Display file statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Characters", f"{len(cleaned_text):,}")
        with col2:
            st.metric("🧩 Chunks Created", len(chunks))
        with col3:
            st.metric("📝 Estimated Tokens", f"{len(cleaned_text)//4:,}")
        with col4:
            st.metric("🔑 Keywords Found", len(keywords))

        # Show keywords if enabled
        if show_keywords and keywords:
            st.markdown("#### 🔑 Extracted Keywords")
            keyword_cols = st.columns(min(5, len(keywords)))
            for i, keyword in enumerate(keywords):
                with keyword_cols[i % len(keyword_cols)]:
                    st.badge(keyword.title())

        # Process chunks with progress tracking
        st.markdown("#### 🤖 AI Analysis in Progress")
        partial_summaries = []
        chunk_data = []
        
        chunk_progress = st.progress(0, text="Initializing summarization...")
        
        for i, chunk in enumerate(chunks):
            chunk_progress.progress(
                (i) / len(chunks), 
                text=f"Analyzing chunk {i+1} of {len(chunks)}..."
            )
            
            summary = summarize_text_local(chunk, style=depth)
            if not summary:
                summary = f"[Error generating summary for chunk {i+1}]"
                logging.warning(f"Failed to generate summary for chunk {i+1}")
            
            partial_summaries.append(summary)
            chunk_data.append({
                "Chunk #": i+1,
                "Token Count": f"~{len(chunk)//4}",
                "Summary": summary[:200] + "..." if len(summary) > 200 else summary
            })
        
        chunk_progress.progress(1.0, text="Completing analysis...")
        time.sleep(0.5)  # Brief pause for UX
        chunk_progress.empty()
        
        st.success(f"✅ Successfully analyzed {len(chunks)} chunks!")

        # Display chunk summaries if requested
        if show_chunks and chunk_data:
            st.markdown("#### 🧩 Individual Chunk Analysis")
            
            if chunk_display_mode == "Grid View":
                df = pd.DataFrame(chunk_data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_pagination(paginationPageSize=10)
                gb.configure_default_column(wrapText=True, autoHeight=True)
                gb.configure_column("Summary", width=400)
                grid_options = gb.build()
                AgGrid(df, gridOptions=grid_options, theme="streamlit")
            else:
                # Expandable cards view
                for i, summary in enumerate(partial_summaries):
                    with st.expander(f"📄 Chunk {i+1} Summary ({len(chunks[i])//4}~tokens)"):
                        st.write(summary)

        # Generate final comprehensive summary
        st.markdown("#### 🧠 Generating Final Analysis")
        with st.spinner("Synthesizing comprehensive summary..."):
            # Combine all partial summaries for final processing
            combined_summaries = "\n\n---CHUNK SEPARATOR---\n\n".join(partial_summaries)
            
            # Create enhanced prompt for final summary
            final_prompt_context = f"""
            The following are summaries of different sections of a research paper. 
            Please create a comprehensive, structured summary that synthesizes all the information:
            
            {combined_summaries}
            """
            
            final_summary = summarize_text_local(final_prompt_context, style=depth)
            
            # Fallback if final summary fails
            if not final_summary:
                st.warning("Final synthesis failed, using combined chunk summaries")
                final_summary = "\n\n".join(partial_summaries)

        # Display final summary
        st.markdown("#### 📋 Comprehensive Analysis Results")
        st.text_area(
            "Generated Summary:", 
            value=final_summary, 
            height=400,
            help="This is the final comprehensive analysis of your research paper"
        )

        # Generate and offer PDF download
        pdf_filename = filename.rsplit(".", 1)[0] + "_analysis.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        
        with st.spinner("Generating PDF report..."):
            generate_enhanced_pdf(
                summary=final_summary,
                output_path=pdf_path,
                title=f"Analysis: {filename}",
                keywords=keywords,
                sections=sections
            )

        # Download button
        try:
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Analysis Report (PDF)",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    help="Download the complete analysis as a formatted PDF"
                )
        except Exception as e:
            st.error(f"Failed to prepare PDF download: {e}")

        st.markdown("---")  # Separator between files

# Debug logs section
if show_logs:
    st.markdown("### 🛠️ Debug Information")
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as log_file:
                log_content = log_file.read()
                if log_content:
                    st.text_area("Debug Logs:", value=log_content, height=300)
                else:
                    st.info("No debug logs available")
        except Exception as e:
            st.error(f"Failed to read log file: {e}")
    else:
        st.info("No log file found")

# Footer information
st.markdown("---")
st.markdown("""
**📄 AI Research Paper Analyzer** - Advanced document analysis powered by local AI models.
- Supports PDF, DOCX, and TXT formats
- Intelligent chunking and summarization
- Keyword extraction and section detection
- Enhanced PDF report generation
""")