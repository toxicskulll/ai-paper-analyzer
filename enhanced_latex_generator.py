import os
import json
import re
from typing import Dict, List, Tuple, Optional
import yaml

class LaTeXDatasetGenerator:
    """
    Enhanced LaTeX dataset generator for fine-tuning models to generate
    academic papers from structured summaries.
    """
    
    def __init__(self, latex_dir: str, output_jsonl: str):
        self.latex_dir = latex_dir
        self.output_jsonl = output_jsonl
        self.dataset = []
        
    def extract_latex_structure(self, latex_text: str) -> Dict:
        """Extract key structural elements from LaTeX text for better understanding."""
        structure = {
            'documentclass': self._extract_documentclass(latex_text),
            'packages': self._extract_packages(latex_text),
            'title': self._extract_title(latex_text),
            'authors': self._extract_authors(latex_text),
            'abstract': self._extract_abstract(latex_text),
            'sections': self._extract_sections(latex_text),
            'references_count': self._count_references(latex_text),
            'has_tables': '\\begin{table' in latex_text,
            'has_figures': '\\begin{figure' in latex_text,
        }
        return structure
    
    def _extract_documentclass(self, text: str) -> str:
        """Extract document class from LaTeX."""
        match = re.search(r'\\documentclass\[([^\]]*)\]\{([^}]*)\}', text)
        return f"{match.group(2)}[{match.group(1)}]" if match else "article"
    
    def _extract_packages(self, text: str) -> List[str]:
        """Extract used packages."""
        packages = re.findall(r'\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}', text)
        return list(set(packages))
    
    def _extract_title(self, text: str) -> str:
        """Extract paper title."""
        match = re.search(r'\\title\{([^}]+)\}', text, re.DOTALL)
        if match:
            title = match.group(1).strip()
            # Clean up LaTeX formatting
            title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
            return title
        return ""
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract author information."""
        authors = []
        # Look for IEEE author blocks
        author_blocks = re.findall(r'\\IEEEauthorblockN\{([^}]+)\}', text)
        for block in author_blocks:
            # Clean up author names
            author = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', block)
            authors.append(author.strip())
        
        # Fallback to generic author extraction
        if not authors:
            match = re.search(r'\\author\{([^}]+)\}', text, re.DOTALL)
            if match:
                author_text = match.group(1)
                # Simple parsing - can be enhanced
                authors = [author_text.strip()]
        
        return authors
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract content."""
        match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            # Clean up LaTeX commands
            abstract = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', abstract)
            return abstract
        return ""
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract section titles and approximate content."""
        sections = {}
        
        # Find all section declarations
        section_pattern = r'\\section\{([^}]+)\}(.*?)(?=\\section\{|\\begin\{thebibliography\}|\\end\{document\}|$)'
        matches = re.findall(section_pattern, text, re.DOTALL)
        
        for title, content in matches:
            # Clean title
            clean_title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title).strip()
            # Get first paragraph or summary of content
            content_lines = [line.strip() for line in content.split('\n') if line.strip()]
            content_preview = ' '.join(content_lines[:3])[:200] + "..." if content_lines else ""
            sections[clean_title] = content_preview
        
        return sections
    
    def _count_references(self, text: str) -> int:
        """Count bibliography references."""
        matches = re.findall(r'\\bibitem\{[^}]+\}', text)
        return len(matches)
    
    def create_enhanced_prompt(self, structure: Dict, metadata: Dict) -> str:
        """Create a more sophisticated prompt based on extracted structure."""
        
        prompt = """You are an expert academic writing assistant specializing in generating well-formatted LaTeX research papers. Generate a complete LaTeX document based on the following specifications:

DOCUMENT REQUIREMENTS:
- Document Class: IEEE Conference format with proper formatting
- Include essential packages for academic writing (graphicx, cite, amsmath, etc.)
- Follow IEEE citation and reference style
- Use proper sectioning hierarchy and numbering

PAPER DETAILS:"""
        
        # Add paper metadata
        prompt += f"\nTitle: {metadata.get('title', 'Research Paper Title')}"
        
        if metadata.get('authors'):
            prompt += f"\nAuthors: {', '.join(metadata['authors'])}"
        
        if metadata.get('keywords'):
            prompt += f"\nKeywords: {', '.join(metadata['keywords'])}"
        
        # Add content structure
        prompt += "\n\nCONTENT STRUCTURE:"
        
        if metadata.get('abstract'):
            prompt += f"\nAbstract: {metadata['abstract']}"
        
        if metadata.get('sections'):
            prompt += "\n\nSections to include:"
            for section, content in metadata['sections'].items():
                prompt += f"\n- {section}: {content}"
        
        # Add formatting requirements
        prompt += """

FORMATTING REQUIREMENTS:
- Use proper IEEE conference template structure
- Include complete document preamble with necessary packages
- Format author affiliations properly with IEEEauthorblock commands
- Include abstract and keywords sections
- Use proper section numbering and hierarchy
- Add placeholder citations where appropriate (\\cite{ref})
- Include bibliography section with sample references
- Ensure mathematical equations are properly formatted
- Add tables or figures if mentioned in the content
- Use proper LaTeX syntax throughout

OUTPUT: Generate the complete LaTeX source code ready for compilation."""

        return prompt.strip()
    
    def generate_dataset_from_examples(self, examples_file: Optional[str] = None) -> None:
        """Generate dataset from existing LaTeX examples in the directory."""
        
        latex_files = [f for f in os.listdir(self.latex_dir) if f.endswith('.tex')]
        
        if not latex_files:
            print("❌ No LaTeX files found in the directory")
            return
        
        for tex_file in latex_files:
            tex_path = os.path.join(self.latex_dir, tex_file)
            
            try:
                with open(tex_path, "r", encoding="utf-8") as f:
                    latex_content = f.read()
                
                # Extract structure from existing LaTeX
                structure = self.extract_latex_structure(latex_content)
                
                # Create metadata from extracted structure
                metadata = {
                    'title': structure['title'],
                    'authors': structure['authors'],
                    'abstract': structure['abstract'],
                    'sections': structure['sections'],
                    'keywords': ['Deep Learning', 'Medical Imaging', 'AI'],  # Default keywords
                }
                
                # Generate enhanced prompt
                prompt = self.create_enhanced_prompt(structure, metadata)
                
                # Add to dataset
                self.dataset.append({
                    'prompt': prompt,
                    'completion': latex_content.strip(),
                    'metadata': {
                        'source_file': tex_file,
                        'structure': structure,
                        'word_count': len(latex_content.split()),
                        'line_count': len(latex_content.split('\n'))
                    }
                })
                
                print(f"✅ Processed: {tex_file}")
                
            except Exception as e:
                print(f"❌ Error processing {tex_file}: {str(e)}")
    
    def add_manual_examples(self, manual_examples: List[Dict]) -> None:
        """Add manually curated examples to the dataset."""
        
        for example in manual_examples:
            structure = {
                'title': example['title'],
                'authors': example.get('authors', []),
                'abstract': example.get('abstract', ''),
                'sections': example.get('sections', {}),
            }
            
            prompt = self.create_enhanced_prompt(structure, example)
            
            self.dataset.append({
                'prompt': prompt,
                'completion': example['latex_content'],
                'metadata': {
                    'source': 'manual',
                    'domain': example.get('domain', 'general'),
                }
            })
    
    def augment_dataset(self) -> None:
        """Create variations of existing examples for data augmentation."""
        
        original_size = len(self.dataset)
        augmented_examples = []
        
        for item in self.dataset[:original_size]:  # Only augment original items
            # Create a variation with different phrasing in the prompt
            modified_prompt = item['prompt'].replace(
                "Generate a complete LaTeX document",
                "Create a well-structured academic paper in LaTeX format"
            ).replace(
                "academic writing assistant",
                "LaTeX document generation expert"
            )
            
            augmented_examples.append({
                'prompt': modified_prompt,
                'completion': item['completion'],
                'metadata': {**item['metadata'], 'augmented': True}
            })
        
        self.dataset.extend(augmented_examples)
        print(f"📈 Dataset augmented: {original_size} → {len(self.dataset)} examples")
    
    def validate_dataset(self) -> Dict[str, int]:
        """Validate the generated dataset and return statistics."""
        
        stats = {
            'total_examples': len(self.dataset),
            'avg_prompt_length': 0,
            'avg_completion_length': 0,
            'examples_with_tables': 0,
            'examples_with_figures': 0,
            'unique_titles': 0,
        }
        
        if not self.dataset:
            return stats
        
        prompt_lengths = [len(item['prompt']) for item in self.dataset]
        completion_lengths = [len(item['completion']) for item in self.dataset]
        
        stats['avg_prompt_length'] = sum(prompt_lengths) // len(prompt_lengths)
        stats['avg_completion_length'] = sum(completion_lengths) // len(completion_lengths)
        
        # Count examples with tables/figures
        for item in self.dataset:
            if '\\begin{table' in item['completion']:
                stats['examples_with_tables'] += 1
            if '\\begin{figure' in item['completion']:
                stats['examples_with_figures'] += 1
        
        # Count unique titles
        titles = set()
        for item in self.dataset:
            if 'structure' in item.get('metadata', {}):
                title = item['metadata']['structure'].get('title', '')
                if title:
                    titles.add(title)
        stats['unique_titles'] = len(titles)
        
        return stats
    
    def save_dataset(self, include_metadata: bool = True) -> None:
        """Save the dataset to JSONL format."""
        
        os.makedirs(os.path.dirname(self.output_jsonl), exist_ok=True)
        
        with open(self.output_jsonl, "w", encoding="utf-8") as f:
            for item in self.dataset:
                # Prepare output item
                output_item = {
                    'prompt': item['prompt'],
                    'completion': item['completion']
                }
                
                # Optionally include metadata
                if include_metadata and 'metadata' in item:
                    output_item['metadata'] = item['metadata']
                
                f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
        
        print(f"💾 Dataset saved to: {self.output_jsonl}")
    
    def generate_complete_dataset(self) -> None:
        """Complete pipeline to generate the fine-tuning dataset."""
        
        print("🚀 Starting LaTeX fine-tuning dataset generation...")
        
        # Step 1: Process existing LaTeX files
        self.generate_dataset_from_examples()
        
        # Step 2: Add manual examples (you can extend this)
        manual_examples = [
            {
                'title': 'Advanced Neural Network Architectures for Computer Vision',
                'authors': ['Dr. Sarah Johnson', 'Michael Chen'],
                'abstract': 'This paper presents novel neural network architectures...',
                'sections': {
                    'Introduction': 'Computer vision has evolved significantly...',
                    'Methodology': 'We propose a hybrid CNN-Transformer approach...',
                    'Results': 'Our experiments show 95.2% accuracy on ImageNet...',
                    'Conclusion': 'The proposed architecture demonstrates superior performance...'
                },
                'keywords': ['Neural Networks', 'Computer Vision', 'Deep Learning'],
                'latex_content': '''\\documentclass[conference]{IEEEtran}
\\usepackage{graphicx}
\\usepackage{cite}
\\title{Advanced Neural Network Architectures for Computer Vision}
\\author{\\IEEEauthorblockN{Dr. Sarah Johnson}\\and\\IEEEauthorblockN{Michael Chen}}
\\begin{document}
\\maketitle
\\begin{abstract}
This paper presents novel neural network architectures...
\\end{abstract}
\\section{Introduction}
Computer vision has evolved significantly...
\\end{document}'''
            }
        ]
        
        self.add_manual_examples(manual_examples)
        
        # Step 3: Augment dataset
        self.augment_dataset()
        
        # Step 4: Validate and show statistics
        stats = self.validate_dataset()
        print("\n📊 Dataset Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Step 5: Save dataset
        self.save_dataset(include_metadata=True)
        
        print("\n✅ Dataset generation completed successfully!")


# Configuration and execution
def main():
    """Main execution function."""
    
    # Configuration
    latex_dir = r"D:\hack\ai-paper-analyzer\latex"
    output_jsonl = os.path.join(latex_dir, "enhanced_latex_dataset.jsonl")
    
    # Create generator instance
    generator = LaTeXDatasetGenerator(latex_dir, output_jsonl)
    
    # Generate complete dataset
    generator.generate_complete_dataset()
    
    # Additional: Create a smaller validation set
    validation_size = max(1, len(generator.dataset) // 10)  # 10% for validation
    validation_dataset = generator.dataset[-validation_size:]
    training_dataset = generator.dataset[:-validation_size]
    
    # Save training set
    training_jsonl = output_jsonl.replace('.jsonl', '_train.jsonl')
    with open(training_jsonl, "w", encoding="utf-8") as f:
        for item in training_dataset:
            output_item = {'prompt': item['prompt'], 'completion': item['completion']}
            f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
    
    # Save validation set
    validation_jsonl = output_jsonl.replace('.jsonl', '_val.jsonl')
    with open(validation_jsonl, "w", encoding="utf-8") as f:
        for item in validation_dataset:
            output_item = {'prompt': item['prompt'], 'completion': item['completion']}
            f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
    
    print(f"\n📂 Files created:")
    print(f"  Full dataset: {output_jsonl}")
    print(f"  Training set ({len(training_dataset)} examples): {training_jsonl}")
    print(f"  Validation set ({len(validation_dataset)} examples): {validation_jsonl}")

if __name__ == "__main__":
    main()