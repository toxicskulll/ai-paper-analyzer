#!/usr/bin/env python3
"""
Test script to debug the AI Paper Analyzer workflow
"""

import os
import sys
sys.path.append('/workspace/project/ai-paper-analyzer/logic')

from summary_latex import generate_full_latex_from_summary, Config, PaperGenerator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_template_rendering():
    """Test the template rendering with mock data"""
    print("=== Testing Template Rendering ===")
    
    # Mock section data
    mock_sections = {
        'abstract': 'This is a test abstract for the AI paper analyzer.',
        'introduction': 'This is the introduction section with detailed background information.',
        'background': 'Background information about the research domain.',
        'literature_review': 'Review of existing literature in the field.',
        'methodology': 'Description of the research methodology used.',
        'results': 'Presentation of the research results and findings.',
        'figures_tables': 'Description of figures and tables used in the research.',
        'challenges': 'Challenges and limitations encountered during the research.',
        'future': 'Future work and research directions.',
        'conclusion': 'Conclusions drawn from the research findings.'
    }
    
    # Test the LaTeX generation
    try:
        from latex_gen import render_latex
        output_path = render_latex(
            section_data=mock_sections,
            template_path="paper_template.tex",
            output_path="test_output.tex"
        )
        print(f"✅ Template rendering successful: {output_path}")
        
        # Check if file was created and has content
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                content = f.read()
                print(f"Generated file size: {len(content)} characters")
                
                # Check if variables were replaced
                if '\\VAR{' in content:
                    print("❌ Warning: Some template variables were not replaced")
                    # Find unreplaced variables
                    import re
                    unreplaced = re.findall(r'\\VAR\{([^}]+)\}', content)
                    print(f"Unreplaced variables: {unreplaced}")
                else:
                    print("✅ All template variables were replaced")
        else:
            print("❌ Output file was not created")
            
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n=== Testing Ollama Connection ===")
    
    config = Config()
    generator = PaperGenerator(config, "test summary")
    
    if generator.validate_ollama_connection():
        print("✅ Ollama connection successful")
        return True
    else:
        print("❌ Ollama connection failed")
        print("Note: This is expected if Ollama is not installed")
        return False

def test_section_processing():
    """Test section processing with mock data"""
    print("\n=== Testing Section Processing ===")
    
    # Test with a simple summary
    test_summary = """
    This research paper explores advanced machine learning techniques for natural language processing.
    The study focuses on transformer architectures and their applications in text analysis.
    Key findings include improved accuracy in sentiment analysis and text classification tasks.
    The methodology involves training deep neural networks on large datasets.
    Results show significant improvements over baseline methods.
    """
    
    try:
        config = Config()
        config.validate_output = False  # Skip validation for testing
        
        # Test if we can create the generator
        generator = PaperGenerator(config, test_summary)
        print("✅ PaperGenerator created successfully")
        
        # Test prompt loading
        prompt = generator.load_prompt()
        if prompt:
            print(f"✅ Prompt loaded: {len(prompt)} characters")
        else:
            print("❌ Failed to load prompt")
            
        return True
        
    except Exception as e:
        print(f"❌ Section processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 AI Paper Analyzer Workflow Debug Test")
    print("=" * 50)
    
    # Change to logic directory
    os.chdir('/workspace/project/ai-paper-analyzer/logic')
    
    # Run tests
    test_template_rendering()
    ollama_available = test_ollama_connection()
    test_section_processing()
    
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    print("- Template rendering: Check output above")
    print(f"- Ollama connection: {'✅ Available' if ollama_available else '❌ Not available'}")
    print("- Section processing: Check output above")
    
    if not ollama_available:
        print("\n💡 To fix Ollama issues:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Pull Mistral model: ollama pull mistral")
        print("3. Test connection: ollama list")

if __name__ == "__main__":
    main()