# latex_gen.py
# Optimized lightweight LaTeX template processor
# Designed to integrate seamlessly with summary_latex.py pipeline

import os
import tempfile
import shutil
import logging
import re
from pathlib import Path
from typing import Dict, Optional, List, Union
from dataclasses import dataclass


@dataclass
class ProcessingStats:
    """Statistics for template processing operations"""
    total_placeholders: int = 0
    successful_replacements: int = 0
    failed_replacements: int = 0
    temp_files_created: int = 0
    temp_files_cleaned: int = 0


class FastTemplateProcessor:
    """
    Ultra-lightweight template processor using native string operations.
    Optimized for speed with minimal memory footprint and automatic cleanup.
    """
    
    def __init__(self, cleanup_temp: bool = True, debug: bool = False):
        """
        Initialize the processor.
        
        Args:
            cleanup_temp: Whether to automatically cleanup temporary files
            debug: Enable debug logging
        """
        self.cleanup_temp = cleanup_temp
        self.debug = debug
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []
        self.stats = ProcessingStats()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup lightweight logger"""
        logger = logging.getLogger(f"{__name__}.{id(self)}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
            
        return logger
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_temp:
            self.cleanup_all()
    
    def process_template_fast(self, template_content: str, 
                             sections: Dict[str, str]) -> str:
        """
        Ultra-fast template processing using simple string replacement.
        
        Args:
            template_content: LaTeX template as string
            sections: Dictionary mapping section names to content
            
        Returns:
            Processed LaTeX content
        """
        # Map sections to template variables based on your paper_template.tex
        var_mapping = {
            'paper_title': sections.get('title', sections.get('paper_title', 'Research Paper')),
            'author_block': sections.get('authors', sections.get('author_block', 'Author Name')),
            'abstract': sections.get('abstract', ''),
            'keywords': sections.get('keywords', ''),
            'introduction': sections.get('introduction', ''),
            'background': sections.get('background', ''),
            'literature_review': sections.get('literature_review', ''),
            'methodology': sections.get('methodology', ''),
            'results': sections.get('results', ''),
            'figures_tables': sections.get('figures_tables', ''),
            'challenges': sections.get('challenges', ''),
            'future': sections.get('future', ''),
            'conclusion': sections.get('conclusion', ''),
            'acknowledgments': sections.get('acknowledgments', ''),
            'bibliography_entries': sections.get('bibliography', sections.get('bibliography_entries', ''))
        }
        
        processed_content = template_content
        self.stats.total_placeholders = len(var_mapping)
        
        # Fast replacement using built-in string methods
        for var_name, content in var_mapping.items():
            placeholder = f'\\VAR{{{var_name}}}'
            
            if placeholder in processed_content:
                if content:
                    # Clean and escape content for LaTeX
                    clean_content = self._escape_latex_fast(str(content))
                    processed_content = processed_content.replace(placeholder, clean_content)
                    self.stats.successful_replacements += 1
                else:
                    # Remove placeholder if no content
                    processed_content = processed_content.replace(placeholder, '')
                    self.stats.successful_replacements += 1
            else:
                self.stats.failed_replacements += 1
                
        self.logger.info(f"Processed {self.stats.successful_replacements}/{self.stats.total_placeholders} placeholders")
        return processed_content
    
    def _escape_latex_fast(self, text: str) -> str:
        """
        Fast LaTeX escaping using string replacement chain.
        Optimized for speed over comprehensive escaping.
        
        Args:
            text: Raw text content
            
        Returns:
            LaTeX-escaped content
        """
        if not text:
            return ""
        
        # Fast escaping for most common problematic characters
        # Order matters - do backslash first to avoid double escaping
        escaped = (text
                  .replace('\\', '\\textbackslash{}')
                  .replace('{', '\\{')
                  .replace('}', '\\}')
                  .replace('$', '\\$')
                  .replace('&', '\\&')
                  .replace('%', '\\%')
                  .replace('#', '\\#')
                  .replace('_', '\\_')
                  .replace('^', '\\textasciicircum{}')
                  .replace('~', '\\textasciitilde{}'))
        
        return escaped
    
    def create_temp_file(self, content: str, suffix: str = '.txt') -> str:
        """
        Create temporary file with content.
        
        Args:
            content: Content to write
            suffix: File suffix
            
        Returns:
            Path to temporary file
        """
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=suffix, 
                delete=False, 
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            self.temp_files.append(temp_path)
            self.stats.temp_files_created += 1
            
            if self.debug:
                self.logger.debug(f"Created temp file: {temp_path}")
                
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Failed to create temp file: {e}")
            raise
    
    def create_temp_dir(self, prefix: str = 'latex_proc_') -> str:
        """
        Create temporary directory.
        
        Args:
            prefix: Directory name prefix
            
        Returns:
            Path to temporary directory
        """
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            self.temp_dirs.append(temp_dir)
            
            if self.debug:
                self.logger.debug(f"Created temp dir: {temp_dir}")
                
            return temp_dir
            
        except Exception as e:
            self.logger.error(f"Failed to create temp dir: {e}")
            raise
    
    def cleanup_all(self):
        """Clean up all temporary files and directories"""
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    self.stats.temp_files_cleaned += 1
                    if self.debug:
                        self.logger.debug(f"Cleaned temp file: {temp_file}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {temp_file}: {e}")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    if self.debug:
                        self.logger.debug(f"Cleaned temp dir: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {temp_dir}: {e}")
        
        self.temp_files.clear()
        self.temp_dirs.clear()
        
        if self.stats.temp_files_created > 0:
            self.logger.info(f"Cleaned up {self.stats.temp_files_cleaned}/{self.stats.temp_files_created} temp files")


def render_latex_template(sections: Dict[str, str], 
                         template_path: str = "paper_template.tex",
                         output_path: str = "final_latex_output/final_paper.tex") -> str:
    """
    Main function compatible with summary_latex.py - replaces Jinja2 approach.
    Uses fast string replacement with automatic cleanup.
    
    Args:
        sections: Dictionary containing section content from PaperGenerator
        template_path: Path to LaTeX template file with \VAR{} placeholders
        output_path: Output path for generated LaTeX file
        
    Returns:
        Path to generated LaTeX file
    """
    
    # Ensure logging is configured
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
    
    logger.info(f"Starting LaTeX template rendering with {len(sections)} sections")
    
    try:
        # Read template file
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        logger.info(f"Loaded template: {template_path} ({len(template_content)} chars)")
        
        # Process template with fast processor
        with FastTemplateProcessor(cleanup_temp=True, debug=False) as processor:
            processed_content = processor.process_template_fast(template_content, sections)
            
            # Create output directory
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Write final LaTeX file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            logger.info(f"LaTeX file generated: {output_path} ({len(processed_content)} chars)")
            
            # Log processing stats
            stats = processor.stats
            logger.info(f"Processing stats - Placeholders: {stats.successful_replacements}/{stats.total_placeholders}")
            
            return output_path
            
    except Exception as e:
        logger.error(f"Failed to render LaTeX template: {e}")
        raise


def render_latex(sections: Dict[str, str], 
                template_path: str = "paper_template.tex",
                output_path: str = "final_latex_output/final_paper.tex") -> str:
    """
    Alternative entry point - alias for render_latex_template.
    Maintains compatibility with any existing imports.
    """
    return render_latex_template(sections, template_path, output_path)


# Utility functions for advanced workflows
def batch_process_with_temp_files(sections: Dict[str, str], 
                                 processor_func: callable,
                                 temp_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Process sections using temporary files for intermediate storage.
    Useful when integrating with Ollama processing pipeline.
    
    Args:
        sections: Raw section content  
        processor_func: Function that takes (section_name, temp_file_path) and returns processed content
        temp_dir: Optional temporary directory path
        
    Returns:
        Dictionary of processed section content
    """
    processed_sections = {}
    
    with FastTemplateProcessor(cleanup_temp=True) as processor:
        # Create temp directory if not provided
        if temp_dir is None:
            temp_dir = processor.create_temp_dir()
        
        temp_file_map = {}
        
        try:
            # Create temp files for each section
            for section_name, content in sections.items():
                if content:  # Only process non-empty content
                    temp_file = processor.create_temp_file(content, suffix=f'_{section_name}.txt')
                    temp_file_map[section_name] = temp_file
            
            # Process each section
            for section_name, temp_file_path in temp_file_map.items():
                try:
                    processed_content = processor_func(section_name, temp_file_path)
                    if processed_content:
                        processed_sections[section_name] = processed_content
                except Exception as e:
                    logging.warning(f"Failed to process section {section_name}: {e}")
                    # Continue with other sections
                    
        except Exception as e:
            logging.error(f"Error in batch processing: {e}")
            raise
        
        # Cleanup happens automatically via context manager
    
    return processed_sections


def create_section_files(sections: Dict[str, str], output_dir: str) -> Dict[str, str]:
    """
    Create individual files for each section (not temporary).
    Useful for debugging or manual inspection.
    
    Args:
        sections: Section content dictionary
        output_dir: Directory to create section files
        
    Returns:
        Dictionary mapping section names to file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    file_paths = {}
    for section_name, content in sections.items():
        if content:
            file_path = os.path.join(output_dir, f"{section_name}.txt")
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                file_paths[section_name] = file_path
            except Exception as e:
                logging.warning(f"Failed to create file for {section_name}: {e}")
    
    return file_paths


def validate_template_placeholders(template_path: str) -> List[str]:
    """
    Extract and validate placeholders in template file.
    
    Args:
        template_path: Path to template file
        
    Returns:
        List of placeholder names found in template
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Find all \VAR{} placeholders
        placeholder_pattern = r'\\VAR\{([^}]+)\}'
        placeholders = re.findall(placeholder_pattern, template_content)
        
        return placeholders
        
    except Exception as e:
        logging.error(f"Failed to validate template placeholders: {e}")
        return []


if __name__ == "__main__":
    # Test the processor
    print("Testing FastTemplateProcessor...")
    
    # Test section data
    test_sections = {
        'abstract': 'This is a test abstract with special characters: $, &, %, #',
        'introduction': 'This is a test introduction.',
        'conclusion': 'This is a test conclusion.',
        'title': 'Test Paper Title',
        'authors': 'Test Author'
    }
    
    # Test placeholder validation
    if os.path.exists("paper_template.tex"):
        placeholders = validate_template_placeholders("paper_template.tex")
        print(f"Found placeholders: {placeholders}")
        
        # Test full processing
        try:
            output_path = render_latex_template(
                sections=test_sections,
                template_path="paper_template.tex",
                output_path="test_output/test_paper.tex"
            )
            print(f"✅ Test successful! Generated: {output_path}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("⚠️ paper_template.tex not found - skipping full test")
        
    # Test temp file processing
    with FastTemplateProcessor() as processor:
        temp_file = processor.create_temp_file("Test content", ".txt")
        print(f"✅ Created temp file: {temp_file}")
        
    print("✅ All tests completed!")