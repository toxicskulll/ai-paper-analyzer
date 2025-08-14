import subprocess
import os
import requests
import time
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from latex_gen_optimized import render_latex as render_latex_template

# ------------------ LATEX MASKING UTILITIES ------------------ #
class MaskToken(NamedTuple):
    """Structure to hold masked content and its replacement"""
    placeholder: str
    original: str
    token_type: str

class LaTeXMasker:
    """Handles masking and unmasking of LaTeX elements during text processing"""
    
    def __init__(self):
        self.mask_patterns = {
            'inline_math': r'\$([^$]+)\$',
            'display_math': r'\$\$([^$]+)\$\$',
            'equation': r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}',
            'align': r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}',
            'eqnarray': r'\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}',
            'cite': r'\\cite\{([^}]+)\}',
            'citep': r'\\citep\{([^}]+)\}',
            'citet': r'\\citet\{([^}]+)\}',
            'ref': r'\\ref\{([^}]+)\}',
            'eqref': r'\\eqref\{([^}]+)\}',
            'label': r'\\label\{([^}]+)\}',
            'figure': r'\\begin\{figure\}(.*?)\\end\{figure\}',
            'table': r'\\begin\{table\}(.*?)\\end\{table\}',
            'includegraphics': r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}',
            'textbf': r'\\textbf\{([^}]+)\}',
            'textit': r'\\textit\{([^}]+)\}',
            'emph': r'\\emph\{([^}]+)\}',
            'url': r'\\url\{([^}]+)\}',
            'href': r'\\href\{([^}]+)\}\{([^}]+)\}',
            'math_commands': r'\\(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|phi|omega|sum|int|frac|sqrt|partial|nabla|infty)\\b',
            'section': r'\\(?:section|subsection|subsubsection)\{([^}]+)\}',
        }
        self.masked_tokens: List[MaskToken] = []
        self.token_counter = 0

    def mask_latex_elements(self, text: str) -> str:
        self.masked_tokens.clear()
        self.token_counter = 0
        masked_text = text
        for pattern_name, pattern in self.mask_patterns.items():
            masked_text = self._mask_pattern(masked_text, pattern, pattern_name)
        self._log_masking_stats()
        return masked_text

    def _mask_pattern(self, text: str, pattern: str, pattern_type: str) -> str:
        def replace_match(match):
            self.token_counter += 1
            placeholder = f"[LATEX_MASK_{self.token_counter:04d}]"
            token = MaskToken(
                placeholder=placeholder,
                original=match.group(0),
                token_type=pattern_type
            )
            self.masked_tokens.append(token)
            return placeholder
        return re.sub(pattern, replace_match, text, flags=re.DOTALL | re.IGNORECASE)

    def unmask_latex_elements(self, processed_text: str) -> str:
        restored_text = processed_text
        for token in reversed(self.masked_tokens):
            restored_text = restored_text.replace(token.placeholder, token.original)
        return restored_text
    
    def _log_masking_stats(self):
        """Log statistics about masked elements"""
        if not self.masked_tokens:
            return
            
        stats = {}
        for token in self.masked_tokens:
            stats[token.token_type] = stats.get(token.token_type, 0) + 1
        
        logging.info(f"Masked {len(self.masked_tokens)} LaTeX elements:")
        for element_type, count in stats.items():
            logging.info(f"  - {element_type}: {count}")

    def get_masking_report(self) -> Dict[str, int]:
        """Get a report of what was masked"""
        stats = {}
        for token in self.masked_tokens:
            stats[token.token_type] = stats.get(token.token_type, 0) + 1
        return stats

    def validate_masking(self, original: str, masked: str, restored: str) -> bool:
        placeholders_in_masked = re.findall(r'\[LATEX_MASK_\d+\]', masked)
        expected_placeholders = [token.placeholder for token in self.masked_tokens]
        if set(placeholders_in_masked) != set(expected_placeholders):
            logging.warning("Placeholder mismatch detected during validation")
            return False
        remaining_placeholders = re.findall(r'\[LATEX_MASK_\d+\]', restored)
        if remaining_placeholders:
            logging.warning(f"Unrestored placeholders found: {remaining_placeholders}")
            return False
        length_ratio = len(restored) / len(original) if original else 1
        if not (0.8 <= length_ratio <= 1.2):
            logging.warning(f"Suspicious length change: {len(original)} -> {len(restored)}")
        return True

@dataclass
class Config:
    sections: List[str] = field(default_factory=lambda: [
        "abstract", "introduction", "background", "literature_review",
        "figures_tables", "methodology", "challenges", "future",
        "results", "conclusion"
    ])
    
    # Main model for unified synthesis
    ollama_main_model: str = "mistral:latest"
    # Model for section expansion and humanization
    ollama_section_model: str = "llama3.2:3b"
    ollama_humanize_model: str = "llama3.2:3b"

    # Timeouts (seconds)
    ollama_main_timeout: int = 600
    ollama_section_timeout: int = 300
    ollama_humanize_timeout: int = 180

    max_retries: int = 3
    allow_offline: bool = False
    prompt_file: str = "prompt.txt"
    output_dir: str = "humanized"
    latex_output_dir: str = "final_latex_output"
    log_file: str = "paper_generation.log"
    parallel_processing: bool = False
    max_workers: int = 2
    save_intermediate: bool = True
    validate_output: bool = True

# ------------------ SECTION PROCESSING UTILITIES ------------------ #
# Section trimming for llama3.2:3b context window
def _prepare_section_input(full_summary: str, section_name: str, max_tokens: int = 3000) -> str:
    section_marker = f"## {section_name.replace('_', ' ').title()}"
    start_idx = full_summary.find(section_marker)
    if start_idx == -1:
        return full_summary[:max_tokens]
    return full_summary[start_idx:start_idx + max_tokens]

# Prompt builder using external prompt file
def _build_section_prompt(section_name: str, summary_chunk: str) -> str:
    with open("prompt.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read().strip()
    return (
        f"{base_prompt}\n\n"
        f"[Tone Consistency] Maintain the same style, structure, and terminology as previous sections.\n"
        f"[Section Target] {section_name.replace('_', ' ').title()}\n"
        f"[Section Content]\n{summary_chunk}"
    )

# Batched section expansion
def expand_sections_with_batch(sections: list, unified_summary: str, config: Config):
    from ollama import Client
    client = Client()
    for section_name in sections:
        section_input = _prepare_section_input(unified_summary, section_name)
        prompt = _build_section_prompt(section_name, section_input)
        output = client.generate(model=config.ollama_section_model, prompt=prompt, timeout=config.ollama_section_timeout)
        yield section_name, output

# ------------------ LOGGING SETUP ------------------ #
def setup_logging(config: Config) -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ------------------ ENHANCED CLASSES ------------------ #
class PaperGenerator:
    """Enhanced research paper generator with better error handling and features"""
    
    def __init__(self, config: Config, summary: str):
        self.config = config
        self.summary = summary
        self.logger = setup_logging(config)
        self.final_sections = {}
        self.failed_sections = []
        self.latex_masker = LaTeXMasker()  # Initialize LaTeX masker
        
        # Create necessary directories
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary output directories"""
        Path(self.config.output_dir).mkdir(exist_ok=True)
        Path(self.config.latex_output_dir).mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
    def load_prompt(self) -> str:
        """Load prompt guidelines with error handling"""
        try:
            with open(self.config.prompt_file, "r", encoding="utf-8", errors="replace") as f:
                prompt = f.read().strip()
            self.logger.info(f"Loaded prompt from {self.config.prompt_file}")
            return prompt
        except FileNotFoundError:
            self.logger.warning(f"Prompt file {self.config.prompt_file} not found, using default")
            return "Please rewrite the following text to be more human-like and academic."
        except Exception as e:
            self.logger.error(f"Error loading prompt: {e}")
            return ""
    
    def validate_ollama_connection(self) -> bool:
        """Check if Ollama is running and at least the configured models are available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
                timeout=10
            )
            if result.returncode == 0:
                models = result.stdout
                missing = []
                for m in [self.config.ollama_main_model, self.config.ollama_section_model, self.config.ollama_humanize_model]:
                    if m and m not in models:
                        missing.append(m)
                if missing:
                    self.logger.warning(f"Models not found locally: {missing}")
                    # still return True if allow_offline is set
                    return False
                self.logger.info("Ollama connection and models validated")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ollama validation failed: {e}")
            if self.config.allow_offline:
                self.logger.warning("Proceeding without Ollama (allow_offline=True).")
                return True
            return False

    def _call_ollama(self, model: str, prompt: str, timeout: int) -> Tuple[Optional[str], Optional[str], int]:
        """Helper to call Ollama subprocess with model and timeout"""
        try:
            process = subprocess.Popen(
                ["ollama", "run", model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace"
            )
            output, error = process.communicate(input=prompt, timeout=timeout)
            return output, error, process.returncode
        except subprocess.TimeoutExpired:
            self.logger.warning("Ollama call timed out")
            try:
                process.kill()
                process.wait()
            except Exception:
                pass
            return None, None, -1
        except Exception as e:
            self.logger.error(f"Ollama call error: {e}")
            return None, str(e), -1

    def _extract_section_context(self, section_name: str, master_summary: str, max_chars: int = 4000) -> str:
        """Naive extraction of relevant sentences for a section.
        This can be replaced with a smarter extractor (keyword/sent-embedding) later.
        """
        # simple heuristic: pick sentences that contain keywords related to section
        keywords_map = {
            'methodology': ['method', 'methodology', 'approach', 'experiment', 'dataset'],
            'results': ['result', 'finding', 'performance', 'accuracy', 'improve'],
            'literature_review': ['related work', 'previous', 'prior work', 'study', 'approach'],
            'introduction': ['motivation', 'objective', 'goal', 'problem', 'context'],
            'abstract': [],
            'background': ['background', 'theory', 'foundation'],
            'conclusion': ['conclusion', 'summary', 'future work', 'limitations']
        }
        keywords = keywords_map.get(section_name, [])
        sentences = re.split(r'(?<=[.!?])\s+', master_summary)
        selected = []
        for s in sentences:
            s_low = s.lower()
            if not keywords and len(selected) < 6:
                selected.append(s)
            else:
                for kw in keywords:
                    if kw in s_low:
                        selected.append(s)
                        break
            if sum(len(x) for x in selected) > max_chars:
                break
        if not selected:
            # fallback to first N sentences
            selected = sentences[:6]
        return ' '.join(selected)[:max_chars]

    def expand_with_ollama(self, section_name: str, master_summary: str, attempt: int = 1) -> Optional[str]:
        """Two-stage approach:
        1) If section_name == '__master__' -> call main model to produce a unified master summary.
        2) Otherwise -> call section model (gemma2) to expand relevant part into structured section.
        """
        # If asking for master summary, use main model
        if section_name == '__master__':
            prompt = (
                "Produce a unified, structured, academic-quality summary that synthesizes all provided papers.\n\n"
                f"Input summary:\n{master_summary}\n\n"
                "Output: Provide a detailed master summary. Use headings where appropriate."
            )
            out, err, code = self._call_ollama(self.config.ollama_main_model, prompt, self.config.ollama_main_timeout)
            if code == 0 and out:
                return out.strip()
            return None

        # For section expansion, build a strict section prompt
        section_prompts = {
            "abstract": "Write a comprehensive Abstract (150–250 words) summarizing: - Purpose - Methods - Key findings - Implications",
            "introduction": "Write an Introduction with subheadings: 1. Research Context 2. Problem Statement 3. Objectives 4. Significance",
            "literature_review": "Write a Literature Review with subheadings: 1. Overview of Previous Work 2. Gaps 3. How This Study Addresses Gaps",
            "methodology": "Write a Methodology section with subheadings: 1. Research Design 2. Data Collection 3. Tools 4. Analysis",
            "results": "Write Results with subheadings: 1. Key Findings 2. Comparative Analysis 3. Metrics",
            "conclusion": "Write a Conclusion with subheadings: 1. Summary 2. Contributions 3. Limitations 4. Future Work",
        }

        specific = section_prompts.get(section_name, f"Write a detailed {section_name} section with clear subheadings and bullet points.")

        # Extract relevant context from the master summary to reduce tokens
        context = self._extract_section_context(section_name, master_summary, max_chars=4000)

        full_prompt = (
            f"{specific}\n\n"
            f"Use the following extracted context (do not invent facts):\n{context}\n\n"
            "Instructions:\n- Use Markdown headings (#, ##) for sections and subsections.\n"
            "- Be faithful to the facts in the context. Do not change numeric values.\n"
            "- Provide detailed explanations and, where relevant, short bullet lists.\n"
            "- Keep output technical and academic in tone."
        )

        # Try with section model (fast). Implement trimming on retries.
        for retry in range(self.config.max_retries):
            prompt_to_send = full_prompt
            if retry >= 2:
                self.logger.warning(f"Trimming prompt for {section_name} on retry {retry}")
                prompt_to_send = full_prompt[:int(len(full_prompt) * 0.7)]

            out, err, code = self._call_ollama(self.config.ollama_section_model, prompt_to_send, self.config.ollama_section_timeout)
            if code == 0 and out:
                out = out.strip()
                if self._validate_section_output(out, section_name):
                    return out
                else:
                    self.logger.warning(f"Section {section_name} failed validation after expansion; will consider humanize step")
                    return out
            elif code == -1:
                self.logger.warning(f"Timeout/err calling section model for {section_name} (retry {retry})")
            else:
                self.logger.error(f"Section model returned non-zero code for {section_name}: {err}")

            if retry < self.config.max_retries - 1:
                time.sleep(2 ** retry)

        self.logger.error(f"Failed to expand section {section_name} after {self.config.max_retries} attempts")
        return None

    def _validate_section_output(self, output: str, section_name: str) -> bool:
        if not self.config.validate_output:
            return True
        min_lengths = {
            "abstract": 100,
            "introduction": 200,
            "background": 150,
            "methodology": 200,
            "results": 150,
            "conclusion": 100
        }
        min_length = min_lengths.get(section_name, 50)
        if len(output) < min_length:
            return False
        error_patterns = ["[ERROR", "I cannot", "I'm unable", "Sorry,"]
        if any(pattern in output for pattern in error_patterns):
            return False
        return True

    def rewrite_with_prompt(self, guideline_prompt: str, raw_text: str) -> Optional[str]:
        """Use a faster humanize model (gemma2) to rewrite/polish content. Will split if too long."""
        if not guideline_prompt:
            return None

        # If raw_text already passes validation, skip rewrite
        if self._validate_section_output(raw_text, 'introduction'):
            # we choose 'introduction' as proxy; ideally pass section name
            self.logger.info("Skipping humanization because output passes validation")
            return raw_text

        # Build concise rewrite prompt
        combined_prompt = f"{guideline_prompt}\n\nOriginal Text:\n{raw_text}\n\nRewritten Text:" 

        # If too long, split into paragraphs and rewrite per chunk
        max_chunk = 3000
        if len(combined_prompt) <= max_chunk:
            out, err, code = self._call_ollama(self.config.ollama_humanize_model, combined_prompt, self.config.ollama_humanize_timeout)
            if code == 0 and out:
                return out.strip()
            elif code == -1:
                self.logger.warning("Timeout in prompt-based rewriting")
                return None
            else:
                self.logger.error(f"Humanize model error: {err}")
                return None

        # chunked rewrite
        paragraphs = re.split(r'\n\n+', raw_text)
        rewritten_parts = []
        for p in paragraphs:
            if not p.strip():
                continue
            chunk_prompt = f"{guideline_prompt}\n\nOriginal Text:\n{p}\n\nRewritten Text:"[:max_chunk]
            out, err, code = self._call_ollama(self.config.ollama_humanize_model, chunk_prompt, self.config.ollama_humanize_timeout)
            if code == 0 and out:
                rewritten_parts.append(out.strip())
            else:
                self.logger.warning("Chunk humanize failed; using original paragraph")
                rewritten_parts.append(p)

        return '\n\n'.join(rewritten_parts)

    def rewrite_with_humanize_api(self, text: str) -> Optional[str]:
        self.logger.info("HumanizeAI API call skipped (API integration disabled)")
        return None

    def process_section(self, section: str, prompt_guidelines: str) -> Tuple[str, Optional[str]]:
        """Process a single section with: expand (gemma) and optional humanize (gemma)."""
        self.logger.info(f"Processing section: {section}")

        # Step 1: Ensure we have a master summary generated by main model
        master = self.summary
        if '__master__' not in self.final_sections:
            self.logger.info("Generating master summary with main model...")
            master_out = self.expand_with_ollama('__master__', master)
            if master_out:
                self.final_sections['__master__'] = master_out
                master = master_out
            else:
                self.logger.warning("Master summary generation failed; falling back to provided summary")

        # Step 2: Expand section using section model
        raw_expansion = self.expand_with_ollama(section, master)
        if not raw_expansion:
            self.logger.warning(f"Skipping section '{section}' due to failed model call.")
            return section, None

        # Step 3: Validate and optionally humanize using fast model
        if self._validate_section_output(raw_expansion, section):
            humanized = raw_expansion
        else:
            self.logger.info(f"Attempting humanization for section {section}")
            humanized = self.rewrite_with_prompt(prompt_guidelines, raw_expansion)
            if not humanized:
                self.logger.warning(f"Humanization failed for '{section}', using raw content.")
                humanized = raw_expansion

        # Step 4: Save intermediate results if configured
        if self.config.save_intermediate:
            self._save_section_files(section, raw_expansion, humanized)

        return section, humanized

    def _save_section_files(self, section: str, raw_content: str, humanized_content: str):
        try:
            with open(f"{self.config.output_dir}/{section}_raw.txt", "w", encoding="utf-8") as f:
                f.write(raw_content)
            with open(f"{self.config.output_dir}/{section}.txt", "w", encoding="utf-8") as f:
                f.write(humanized_content)
        except Exception as e:
            self.logger.error(f"Error saving section files for {section}: {e}")

    def generate_paper(self) -> Dict[str, str]:
        self.logger.info("Starting research paper generation")
        if not self.validate_ollama_connection():
            if not self.config.allow_offline:
                raise RuntimeError("Ollama connection failed. Please ensure Ollama is running or set allow_offline=True.")
            self.logger.warning("Offline mode: filling all sections with the raw summary.")
            for section in self.config.sections:
                self.final_sections[section] = self.summary

        prompt_guidelines = self.load_prompt()
        if self.config.parallel_processing:
            self._process_sections_parallel(prompt_guidelines)
        else:
            self._process_sections_sequential(prompt_guidelines)

        if self.final_sections:
            self._generate_latex()
        else:
            raise RuntimeError("No sections were successfully generated")

        return self.final_sections

    def _process_sections_parallel(self, prompt_guidelines: str):
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_section = {
                executor.submit(self.process_section, section, prompt_guidelines): section
                for section in self.config.sections
            }
            for future in as_completed(future_to_section):
                section, content = future.result()
                if content:
                    self.final_sections[section] = content
                else:
                    self.failed_sections.append(section)

    def _process_sections_sequential(self, prompt_guidelines: str):
        for section in self.config.sections:
            section_name, content = self.process_section(section, prompt_guidelines)
            if content:
                self.final_sections[section_name] = content
            else:
                self.failed_sections.append(section_name)

    def _generate_latex(self):
        try:
            self.logger.info("Generating LaTeX file from research paper output")
            output_path = f"{self.config.latex_output_dir}/final_paper.tex"
            render_latex_template(self.final_sections, template_path="paper_template.tex", output_path=output_path)
            self.logger.info(f"LaTeX document generated successfully")
            self.logger.info(f"Output location: {output_path}")
        except Exception as e:
            self.logger.error(f"LaTeX generation failed: {e}")
            raise

    def get_generation_summary(self) -> Dict:
        return {
            "total_sections": len(self.config.sections),
            "successful_sections": len(self.final_sections),
            "failed_sections": len(self.failed_sections),
            "failed_section_names": self.failed_sections,
            "success_rate": len(self.final_sections) / len(self.config.sections) * 100
        }

# ------------------ MAIN FUNCTION ------------------ #
def main():
    try:
        try:
            import streamlit as st
            summary = st.session_state.get("research_paper_output", "")
            if not summary:
                st.warning("⚠️ No research paper summary found in session. Please generate one first.")
                return
        except (ImportError, AttributeError):
            summary = "Sample research summary for testing purposes."
            print("Warning: Using sample summary. In production, this should come from Streamlit.")
        
        config = Config()
        generator = PaperGenerator(config, summary)
        sections = generator.generate_paper()
        
        summary_stats = generator.get_generation_summary()
        print(f"\n{'='*50}")
        print("GENERATION SUMMARY")
        print(f"{'='*50}")
        print(f"Total sections: {summary_stats['total_sections']}")
        print(f"Successful: {summary_stats['successful_sections']}")
        print(f"Failed: {summary_stats['failed_sections']}")
        print(f"Success rate: {summary_stats['success_rate']:.1f}%")
        
        if summary_stats['failed_sections'] > 0:
            print(f"Failed sections: {', '.join(summary_stats['failed_section_names'])}")
        
        print(f"\n✅ Process completed!")
        print(f"📄 LaTeX file: {config.latex_output_dir}/final_paper.tex")
        print(f"📁 Intermediate files: {config.output_dir}/")
        print(f"📋 Log file: {config.log_file}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise

def generate_latex_from_research_paper_output(summary_text, paper_data_list=None, output_path="final_latex_output/final_paper.tex", progress_callback=None):
    config = Config()
    config.latex_output_dir = os.path.dirname(output_path)
    generator = PaperGenerator(config, summary_text)
    if progress_callback:
        orig_process_section = generator.process_section
        total = len(config.sections)
        def process_section_with_progress(section, prompt_guidelines):
            idx = len(generator.final_sections) + len(generator.failed_sections)
            result = orig_process_section(section, prompt_guidelines)
            idx = len(generator.final_sections) + len(generator.failed_sections)
            progress_callback(min(idx / total, 1.0))
            return result
        generator.process_section = process_section_with_progress
    generator.generate_paper()
    return output_path

if __name__ == "__main__":
    main()
