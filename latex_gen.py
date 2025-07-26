import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound, nodes
from jinja2.exceptions import TemplateError, UndefinedError


class LaTeXGenerator:
    """
    Enhanced LaTeX document generator with flexible templating and validation.
    """
    
    def __init__(self, template_dir: str = "paper_template.tex", output_dir: str = "final_latex_output/final_paper.tex"):
        """
        Initialize the LaTeX generator.
        
        Args:
            template_dir: Directory containing LaTeX templates
            output_dir: Directory for output files
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.logger = self._setup_logging()
        
        # Create directories if they don't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment with LaTeX-friendly settings
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            keep_trailing_newline=True
        )
        
        # Add custom filters
        self.env.filters['latex_escape'] = self._latex_escape
        self.env.filters['format_date'] = self._format_date
        self.env.filters['clean_text'] = self._clean_text
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('latex_generator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _latex_escape(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for LaTeX
        """
        if not isinstance(text, str):
            text = str(text)
        
        # LaTeX special characters and their escapes
        escapes = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, escape in escapes.items():
            text = text.replace(char, escape)
        
        return text
    
    def _format_date(self, date_obj: Union[str, datetime], format_str: str = "%B %d, %Y") -> str:
        """
        Format date for LaTeX output.
        
        Args:
            date_obj: Date object or string
            format_str: Format string for date
            
        Returns:
            Formatted date string
        """
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except ValueError:
                return date_obj
        
        if isinstance(date_obj, datetime):
            return date_obj.strftime(format_str)
        
        return str(date_obj)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for LaTeX.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])\s*([,.;:!?])', r'\1\2', text)
        
        return text
    
    def validate_template(self, template_name: str) -> List[str]:
        """
        Validate template and return list of required variables.
        
        Args:
            template_name: Name of template file
            
        Returns:
            List of required template variables
        """
        try:
            template = self.env.get_template(template_name)
            # Get undeclared variables (template variables without defaults)
            undeclared = template.environment.parse(template.source).find_all(
                nodes.Name
            )
            return [node.name for node in undeclared if isinstance(node.ctx, nodes.Load)]
        except TemplateNotFound:
            self.logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error validating template: {e}")
            return []
    
    def render_latex(self, 
                    section_data: Dict[str, Any],
                    template_name: str = "paper_template.tex",
                    output_filename: str = None,
                    validate_output: bool = True,
                    backup_existing: bool = True) -> Path:
        """
        Render LaTeX template with provided data.
        
        Args:
            section_data: Dictionary of template variables and their values
            template_name: Name of template file in template directory
            output_filename: Name of output file (auto-generated if None)
            validate_output: Whether to validate the generated LaTeX
            backup_existing: Whether to backup existing output files
            
        Returns:
            Path to generated LaTeX file
        """
        try:
            # Generate output filename if not provided
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(template_name).stem
                output_filename = f"{base_name}_{timestamp}.tex"
            
            output_path = self.output_dir / output_filename
            
            # Backup existing file if requested
            if backup_existing and output_path.exists():
                backup_path = output_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex")
                output_path.rename(backup_path)
                self.logger.info(f"Backed up existing file to: {backup_path}")
            
            # Load and render template
            template = self.env.get_template(template_name)
            
            # Prepare render data with automatic key mapping
            render_data = self._prepare_render_data(section_data)
            
            # Add metadata
            render_data.update({
                'generated_at': datetime.now(),
                'generator_version': '2.0',
                'template_name': template_name
            })
            
            # Render template
            self.logger.info(f"Rendering template: {template_name}")
            rendered_content = template.render(render_data)
            
            # Validate output if requested
            if validate_output:
                validation_errors = self._validate_latex_output(rendered_content)
                if validation_errors:
                    self.logger.warning(f"LaTeX validation warnings: {validation_errors}")
            
            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            self.logger.info(f"✅ LaTeX successfully rendered to: {output_path}")
            return output_path
            
        except TemplateNotFound:
            error_msg = f"Template not found: {template_name}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        except TemplateError as e:
            error_msg = f"Template rendering error: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error during LaTeX generation: {e}"
            self.logger.error(error_msg)
            raise
    
    def _prepare_render_data(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare and enhance section data for template rendering.
        
        Args:
            section_data: Raw section data
            
        Returns:
            Enhanced render data
        """
        render_data = {}
        
        for key, value in section_data.items():
            # Handle different value types
            if isinstance(value, str):
                # Clean and escape text content
                cleaned_value = self._clean_text(value)
                render_data[key] = cleaned_value
                render_data[f"{key}_escaped"] = self._latex_escape(cleaned_value)
                render_data[f"{key}_raw"] = value
            elif isinstance(value, (list, tuple)):
                # Handle lists (e.g., for bibliographies, author lists)
                render_data[key] = value
                render_data[f"{key}_joined"] = ', '.join(str(item) for item in value)
            else:
                render_data[key] = value
        
        return render_data
    
    def _validate_latex_output(self, content: str) -> List[str]:
        """
        Basic validation of generated LaTeX content.
        
        Args:
            content: Generated LaTeX content
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for balanced braces
        if content.count('{') != content.count('}'):
            warnings.append("Unbalanced braces detected")
        
        # Check for balanced math delimiters
        if content.count('$') % 2 != 0:
            warnings.append("Unbalanced math delimiters ($)")
        
        # Check for common LaTeX commands
        required_commands = [r'\documentclass', r'\begin{document}', r'\end{document}']
        for cmd in required_commands:
            if cmd not in content:
                warnings.append(f"Missing required command: {cmd}")
        
        # Check for undefined variables (still containing Jinja syntax)
        if '\\VAR{' in content or '\\BLOCK{' in content:
            warnings.append("Template variables may not have been fully rendered")
        
        return warnings
    
    def render_multiple_templates(self, 
                                templates_data: Dict[str, Dict[str, Any]],
                                output_prefix: str = "batch") -> List[Path]:
        """
        Render multiple templates in batch.
        
        Args:
            templates_data: Dict mapping template names to their data
            output_prefix: Prefix for output filenames
            
        Returns:
            List of paths to generated files
        """
        output_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, (template_name, data) in enumerate(templates_data.items()):
            output_filename = f"{output_prefix}_{i+1:02d}_{timestamp}.tex"
            try:
                output_path = self.render_latex(
                    section_data=data,
                    template_name=template_name,
                    output_filename=output_filename
                )
                output_files.append(output_path)
            except Exception as e:
                self.logger.error(f"Failed to render {template_name}: {e}")
        
        self.logger.info(f"Batch rendering complete. Generated {len(output_files)} files.")
        return output_files
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List of template filenames
        """
        if not self.template_dir.exists():
            return []
        
        return [f.name for f in self.template_dir.glob("*.tex")]
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a template.
        
        Args:
            template_name: Name of template file
            
        Returns:
            Dictionary with template information
        """
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        info = {
            'name': template_name,
            'size': template_path.stat().st_size,
            'modified': datetime.fromtimestamp(template_path.stat().st_mtime),
            'path': str(template_path)
        }
        
        # Try to extract template variables
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all template variables
            var_pattern = r'\\VAR\{([^}]+)\}'
            variables = list(set(re.findall(var_pattern, content)))
            info['variables'] = variables
            
        except Exception as e:
            self.logger.warning(f"Could not analyze template variables: {e}")
            info['variables'] = []
        
        return info


# Convenience function for backward compatibility
def render_latex(section_data: dict, 
                template_path: str = "paper_template.tex", 
                output_path: str = "final_latex_output/final_paper.tex") -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        section_data: Dictionary of section content
        template_path: Path to template (can include directory)
        output_path: Output file path
        
    Returns:
        Path to generated file
    """
    # Extract template directory and filename
    template_path = Path(template_path)
    template_dir = template_path.parent if template_path.parent != Path('.') else 'templates'
    template_name = template_path.name
    
    output_path = Path(output_path)
    output_dir = output_path.parent
    output_filename = output_path.name
    
    # Create generator and render
    generator = LaTeXGenerator(template_dir=str(template_dir), output_dir=str(output_dir))
    result_path = generator.render_latex(
        section_data=section_data,
        template_name=template_name,
        output_filename=output_filename
    )
    
    return str(result_path)


# Example usage
if __name__ == "__main__":
    # Example with the enhanced generator
    generator = LaTeXGenerator()
    
    # Sample data
    sample_data = {
        'title': 'Advanced Research in Machine Learning',
        'author': 'Dr. Jane Smith',
        'date': datetime.now(),
        'abstract': 'This paper presents novel approaches to machine learning...',
        'introduction': 'Machine learning has revolutionized many fields...',
        'methodology': 'Our approach combines several techniques...',
        'results': 'The experimental results demonstrate...',
        'conclusion': 'In conclusion, we have shown that...',
        'keywords': ['machine learning', 'neural networks', 'optimization']
    }
    
    try:
        output_file = generator.render_latex(
            section_data=sample_data,
            template_name='academic_paper.tex'
        )
        print(f"Generated LaTeX file: {output_file}")
        
        # List available templates
        templates = generator.list_templates()
        print(f"Available templates: {templates}")
        
    except Exception as e:
        print(f"Error: {e}")