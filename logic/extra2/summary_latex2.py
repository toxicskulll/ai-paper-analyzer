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

            # Mathematical expressions
            'inline_math': r'\$([^$]+)\$',
            'display_math': r'\$\$([^$]+)\$\$',
            'equation': r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}',
            'align': r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}',
            'eqnarray': r'\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}',

            # Citations and references
            'cite': r'\\cite\{([^}]+)\}',
            'citep': r'\\citep\{([^}]+)\}',
            'citet': r'\\citet\{([^}]+)\}',
            'ref': r'\\ref\{([^}]+)\}',
            'eqref': r'\\eqref\{([^}]+)\}',
            'label': r'\\label\{([^}]+)\}',

            # Figure and table references
            'figure': r'\\begin\{figure\}(.*?)\\end\{figure\}',
            'table': r'\\begin\{table\}(.*?)\\end\{table\}',
            'includegraphics': r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}',

            # Special LaTeX commands
            'textbf': r'\\textbf\{([^}]+)\}',
            'textit': r'\\textit\{([^}]+)\}',
            'emph': r'\\emph\{([^}]+)\}',
            'url': r'\\url\{([^}]+)\}',
            'href': r'\\href\{([^}]+)\}\{([^}]+)\}',

            # Math symbols and commands
            'math_commands': r'\\(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|phi|omega|sum|int|frac|sqrt|partial|nabla|infty)\\b',

            # Sectioning commands
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
        """
        Validate that masking and unmasking preserved LaTeX content
        
        Args:
            original: Original text
            masked: Text after masking
            restored: Text after unmasking
            
        Returns:
            True if validation passes
        """
        # Check that all placeholders were used
        placeholders_in_masked = re.findall(r'\[LATEX_MASK_\d+\]', masked)
        expected_placeholders = [token.placeholder for token in self.masked_tokens]
        
        if set(placeholders_in_masked) != set(expected_placeholders):
            logging.warning("Placeholder mismatch detected during validation")
            return False
        
        # Check that no placeholders remain in restored text
        remaining_placeholders = re.findall(r'\[LATEX_MASK_\d+\]', restored)
        if remaining_placeholders:
            logging.warning(f"Unrestored placeholders found: {remaining_placeholders}")
            return False
        
        # Basic length check (restored should be similar length to original)
        length_ratio = len(restored) / len(original) if original else 1
        if not (0.8 <= length_ratio <= 1.2):
            logging.warning(f"Suspicious length change: {len(original)} -> {len(restored)}")
        
        return True
@dataclass
class Config:
    """Configuration class for the research paper generator"""
    sections: List[str] = field(default_factory=lambda: [
        "abstract", "introduction", "background", "literature_review",
        "figures_tables", "methodology", "challenges", "future",
        "results", "conclusion"
    ])
    
    # API Configuration
    #humanize_api_key: str = "sk_c70dclklm4jpampvrk5z7"
    ollama_model: str = "mistral"
    ollama_timeout: int = 120  # Increased timeout
    max_retries: int = 3
    allow_offline: bool = False  # Continue even if Ollama is unavailable
    
    # File paths
    prompt_file: str = "prompt.txt"
    output_dir: str = "humanized"
    latex_output_dir: str = "final_latex_output"
    log_file: str = "paper_generation.log"
    
    # Processing options
    parallel_processing: bool = False
    max_workers: int = 2
    save_intermediate: bool = True
    validate_output: bool = True

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
        """Check if Ollama is running and model is available"""
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
                if self.config.ollama_model in models:
                    self.logger.info("Ollama connection and model validated")
                    return True
                else:
                    self.logger.warning(f"Model {self.config.ollama_model} not found")
                    return False
            return False
        except Exception as e:
            self.logger.error(f"Ollama validation failed: {e}")
            if self.config.allow_offline:
                self.logger.warning("Proceeding without Ollama (allow_offline=True).")
                return True
            return False
    
    def expand_with_ollama(self, section_name: str, summary: str, attempt: int = 1) -> Optional[str]:
        """Generate a highly structured and unified section using Ollama with retry logic and better formatting control."""

        section_prompts = {
            "abstract": """Write a comprehensive Abstract (150–250 words) summarizing:
            - Purpose of the research
            - Main methods used
            - Key findings
            - Broader implications""",

            "introduction": """Write an Introduction with subheadings:
            1. Research Context
            2. Problem Statement
            3. Objectives of the Study
            4. Significance of the Research""",

            "literature_review": """Write a Literature Review with subheadings:
            1. Overview of Previous Work
            2. Gaps in Existing Literature
            3. How This Study Addresses These Gaps""",

            "methodology": """Write a Methodology section with subheadings:
            1. Research Design
            2. Data Collection
            3. Tools and Technologies Used
            4. Data Analysis Techniques""",

            "results": """Write a Results section with subheadings:
            1. Key Findings
            2. Comparative Analysis (if applicable)
            3. Statistical Significance""",

            "conclusion": """Write a Conclusion with subheadings:
            1. Summary of Findings
            2. Contributions to the Field
            3. Limitations
            4. Future Work"""
        }

        # Generic fallback for unknown sections
        if section_name not in section_prompts:
            section_prompts[section_name] = f"""Write a detailed '{section_name.replace('_', ' ').title()}' section with:
            1. Clear subheadings
            2. Bullet points for key information
            3. In-depth explanations for each point"""

        # Build final unified prompt
        specific_prompt = section_prompts[section_name]
        base_prompt = (
            f"{specific_prompt}\n\n"
            f"Unify and synthesize information from ALL provided research papers into a single coherent narrative. "
            f"Compare, contrast, and integrate insights, avoiding paper-by-paper summaries.\n\n"
            f"Based on this combined research summary:\n{summary}\n\n"
            f"Formatting requirements:\n"
            f"- Use Markdown headings (#, ##, ###) for sections and subsections.\n"
            f"- Ensure the structure matches the subheadings provided.\n"
            f"- Avoid vague terms like 'this study'—refer to specific content instead.\n"
            f"- Make the section rich in detail (minimum ~300 words where applicable)."
        )

        for retry in range(self.config.max_retries):
            try:
                # Adjust prompt size on later retries to avoid repeated timeouts
                full_prompt = base_prompt
                if retry >= 2:
                    self.logger.warning(f"Reducing prompt size for {section_name} (attempt {attempt + retry}) to avoid repeated timeouts...")
                    full_prompt = base_prompt[:int(len(base_prompt) * 0.7)]

                self.logger.info(f"Generating {section_name} section (attempt {attempt + retry})")

                process = subprocess.Popen(
                    ["ollama", "run", self.config.ollama_model],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace"
                )

                try:
                    output, error = process.communicate(input=full_prompt, timeout=self.config.ollama_timeout)

                    if process.returncode == 0:
                        output = output.strip()
                        if self._validate_section_output(output, section_name):
                            self.logger.info(f"Successfully generated {section_name}")
                            return output
                        else:
                            self.logger.warning(f"Generated content for {section_name} failed validation")
                    else:
                        self.logger.error(f"Ollama returned non-zero exit code for {section_name}: {error.strip()}")

                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Timeout on {section_name} (attempt {retry + 1})")
                    process.kill()
                    process.wait()

            except Exception as e:
                self.logger.error(f"Error generating {section_name}: {e}")

            if retry < self.config.max_retries - 1:
                time.sleep(2 ** retry)  # exponential backoff

        self.logger.error(f"Failed to generate {section_name} after {self.config.max_retries} attempts. Skipping this section.")
        return None
    
    def _validate_section_output(self, output: str, section_name: str) -> bool:
        """Validate that the generated section meets minimum quality standards"""
        if not self.config.validate_output:
            return True
            
        # Basic validation checks
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
        
        # Check for common error patterns
        error_patterns = ["[ERROR", "I cannot", "I'm unable", "Sorry,"]
        if any(pattern in output for pattern in error_patterns):
            return False
            
        return True
    
    def rewrite_with_prompt(self, guideline_prompt: str, raw_text: str) -> Optional[str]:
        """Enhanced prompt-based rewriting with better error handling"""
        if not guideline_prompt:
            return None
            
        combined_prompt = f"{guideline_prompt}\n\nOriginal Text:\n{raw_text}\n\nRewritten Text:"
        
        try:
            # Use Popen for better process control
            process = subprocess.Popen(
                ["ollama", "run", self.config.ollama_model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace"
            )
            
            try:
                output, error = process.communicate(input=combined_prompt, timeout=self.config.ollama_timeout)
                
                if process.returncode == 0:
                    output = output.strip()
                    if output and len(output) > len(raw_text) * 0.5:  # Ensure reasonable output length
                        return output
                else:
                    self.logger.error(f"Ollama error in rewrite: {error.strip()}")
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("Timeout in prompt-based rewriting")
                process.kill()  # Force kill the hanging process
                process.wait()  # Wait for process to terminate
                    
        except Exception as e:
            self.logger.error(f"Error in prompt-based rewriting: {e}")
        
        return None
    
    def rewrite_with_humanize_api(self, text: str) -> Optional[str]:
        """Enhanced API rewriting with better error handling and rate limiting"""
        """ url = "https://api.humanizeai.in/v1/rewrite"
        headers = {
            "Authorization": f"Bearer {self.config.humanize_api_key}",
            "Content-Type": "application/json"
        }
        payload = {"text": text}
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Calling HumanizeAI API (attempt {attempt + 1})")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json().get("rewritten_text", "")
                    if result:
                        return result
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"API error: {response.status_code} - {response.text}")
                    
            except requests.RequestException as e:
                self.logger.error(f"Request error: {e}")
            
            if attempt < self.config.max_retries - 1:
                time.sleep(1) """
        self.logger.info("HumanizeAI API call skipped (API integration disabled)")
        return None
    
    def process_section(self, section: str, prompt_guidelines: str) -> Tuple[str, Optional[str]]:
        """Process a single section with full pipeline, improved error handling and no API call"""
        self.logger.info(f"Processing section: {section}")

        # Step 1: Generate raw content
        raw_expansion = self.expand_with_ollama(section, self.summary)
        if not raw_expansion:
            self.logger.warning(f"Skipping section '{section}' due to failed model call.")
            return section, None

        # Step 2: Try prompt-based humanization
        humanized = self.rewrite_with_prompt(prompt_guidelines, raw_expansion)

        # Step 3: API call removed, fallback to raw content if needed
        if not humanized:
            self.logger.warning(f"Humanization failed for '{section}', using raw content.")
            humanized = raw_expansion

        # Step 4: Save intermediate results if configured
        if self.config.save_intermediate:
            self._save_section_files(section, raw_expansion, humanized)

        return section, humanized
    
    def _save_section_files(self, section: str, raw_content: str, humanized_content: str):
        """Save intermediate processing files"""
        try:
            # Save raw content
            with open(f"{self.config.output_dir}/{section}_raw.txt", "w", encoding="utf-8") as f:
                f.write(raw_content)
            
            # Save humanized content
            with open(f"{self.config.output_dir}/{section}.txt", "w", encoding="utf-8") as f:
                f.write(humanized_content)
                
        except Exception as e:
            self.logger.error(f"Error saving section files for {section}: {e}")
    
    def generate_paper(self) -> Dict[str, str]:
        """Main pipeline for generating the research paper"""
        self.logger.info("Starting research paper generation")
        
        # Validate prerequisites
        if not self.validate_ollama_connection():
            if not self.config.allow_offline:
                raise RuntimeError("Ollama connection failed. Please ensure Ollama is running or set allow_offline=True.")
            # offline mode: use raw summary in every section
            self.logger.warning("Offline mode: filling all sections with the raw summary.")
            for section in self.config.sections:
                self.final_sections[section] = self.summary
        
        # Load prompt guidelines
        prompt_guidelines = self.load_prompt()
        
        # Process sections
        if self.config.parallel_processing:
            self._process_sections_parallel(prompt_guidelines)
        else:
            self._process_sections_sequential(prompt_guidelines)
        
        # Generate LaTeX
        if self.final_sections:
            self._generate_latex()
        else:
            raise RuntimeError("No sections were successfully generated")
        
        return self.final_sections
    
    def _process_sections_parallel(self, prompt_guidelines: str):
        """Process sections in parallel for better performance"""
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
        """Process sections sequentially"""
        for section in self.config.sections:
            section_name, content = self.process_section(section, prompt_guidelines)
            if content:
                self.final_sections[section_name] = content
            else:
                self.failed_sections.append(section_name)
    
    def _generate_latex(self):
        """Generate the final LaTeX document"""
        try:
            # Use the new LaTeX generation function
            self.logger.info("Generating LaTeX file from research paper output")
            output_path = f"{self.config.latex_output_dir}/final_paper.tex"
            render_latex_template(self.final_sections, template_path="paper_template.tex", output_path=output_path)
            
            self.logger.info(f"LaTeX document generated successfully")
            self.logger.info(f"Output location: {output_path}")
        except Exception as e:
            self.logger.error(f"LaTeX generation failed: {e}")
            raise
    
    def get_generation_summary(self) -> Dict:
        """Get a summary of the generation process"""
        return {
            "total_sections": len(self.config.sections),
            "successful_sections": len(self.final_sections),
            "failed_sections": len(self.failed_sections),
            "failed_section_names": self.failed_sections,
            "success_rate": len(self.final_sections) / len(self.config.sections) * 100
        }

# ------------------ MAIN FUNCTION ------------------ #
def main():
    """Main function with enhanced error handling and configuration"""
    try:
        # Get summary from Streamlit session (fallback for testing)
        try:
            import streamlit as st
            summary = st.session_state.get("research_paper_output", "")
            if not summary:
                st.warning("⚠️ No research paper summary found in session. Please generate one first.")
                return
        except (ImportError, AttributeError):
            # Fallback for testing without Streamlit
            summary = "Sample research summary for testing purposes."
            print("Warning: Using sample summary. In production, this should come from Streamlit.")
        
        # Initialize configuration
        config = Config()
        
        # Create and run generator
        generator = PaperGenerator(config, summary)
        sections = generator.generate_paper()
        
        # Print summary
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

def generate_latex_from_research_paper_output(summary_text, paper_data_list=None, output_path="final_latex_output/final_paper.tex"):
    """
    Generate a LaTeX file from the research paper output summary and paper data list.
    Args:
        summary_text (str): The combined research paper summary in markdown or text.
        paper_data_list (list, optional): List of dicts with paper metadata. Not required for basic output.
        output_path (str): Path to save the generated LaTeX file.
    Returns:
        str: Path to the generated LaTeX file.
    """
    # Simple implementation: wrap summary in a LaTeX document
    latex_content = r"""
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{hyperref}
\\title{Unified Research Paper Summary}
\\date{\\today}
\\begin{document}
\\maketitle
"""
    if paper_data_list:
        latex_content += "\\section*{Included Papers}\n"
        for paper in paper_data_list:
            title = paper.get("title", "Untitled")
            authors = ", ".join(paper.get("authors", [])) or "Unknown"
            year = paper.get("publication_year", "n.d.")
            latex_content += f"\\textbf{{{title}}} ({year}) -- {authors} \\ \\ \n"
        latex_content += "\n"
    latex_content += "\\section*{Summary}\n" + summary_text.replace("\n", "\\\n") + "\n\\end{document}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_content)
    return output_path

def generate_full_latex_from_summary(summary_text, paper_data_list=None, output_path="final_latex_output/final_paper.tex", progress_callback=None):
    """
    Use the advanced PaperGenerator pipeline to generate a LaTeX file from the research paper summary.
    Args:
        summary_text (str): The combined research paper summary in markdown or text.
        paper_data_list (list, optional): List of dicts with paper metadata. Not required for basic output.
        output_path (str): Path to save the generated LaTeX file.
        progress_callback (callable, optional): Function to call with progress updates (float 0.0-1.0).
    Returns:
        str: Path to the generated LaTeX file.
    """
    config = Config()
    config.latex_output_dir = os.path.dirname(output_path)
    generator = PaperGenerator(config, summary_text)
    if progress_callback:
        # Patch the generator to call the progress callback after each section
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