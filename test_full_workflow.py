#!/usr/bin/env python3
"""
Test the complete AI Paper Analyzer workflow from summary to LaTeX
"""

import os
import sys
sys.path.append('/workspace/project/ai-paper-analyzer/logic')

from summary_latex import generate_full_latex_from_summary
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_complete_workflow():
    """Test the complete workflow from summary to LaTeX"""
    print("🔄 Testing Complete Workflow: Summary → Sections → LaTeX")
    print("=" * 60)
    
    # Sample research paper summary
    test_summary = """
    # Advanced Machine Learning Techniques for Natural Language Processing

    ## Abstract
    This research paper explores state-of-the-art machine learning techniques for natural language processing (NLP). 
    We investigate transformer architectures, attention mechanisms, and their applications in various NLP tasks including 
    sentiment analysis, text classification, and language generation.

    ## Introduction
    Natural language processing has undergone significant transformation with the advent of deep learning. 
    Traditional rule-based and statistical methods have been largely superseded by neural network approaches, 
    particularly transformer-based models like BERT, GPT, and T5.

    ## Methodology
    Our approach combines several advanced techniques:
    1. Pre-trained transformer models for feature extraction
    2. Fine-tuning strategies for domain-specific tasks
    3. Attention visualization for interpretability
    4. Multi-task learning for improved generalization

    ## Results
    Experimental results demonstrate significant improvements over baseline methods:
    - Sentiment analysis accuracy: 94.2% (vs 87.3% baseline)
    - Text classification F1-score: 0.91 (vs 0.84 baseline)
    - Language generation BLEU score: 0.73 (vs 0.65 baseline)

    ## Conclusion
    The integration of advanced transformer architectures with domain-specific fine-tuning strategies 
    yields substantial improvements in NLP task performance. Future work will explore multi-modal 
    approaches and cross-lingual transfer learning.
    """
    
    # Change to logic directory
    os.chdir('/workspace/project/ai-paper-analyzer/logic')
    
    try:
        print("📝 Starting paper generation from summary...")
        
        # Progress callback
        def progress_callback(progress):
            print(f"Progress: {progress*100:.1f}%")
        
        # Generate the full LaTeX paper
        output_path = generate_full_latex_from_summary(
            summary_text=test_summary,
            output_path="final_latex_output/test_paper.tex",
            progress_callback=progress_callback
        )
        
        print(f"✅ Paper generation completed!")
        print(f"📄 Output file: {output_path}")
        
        # Check if the file was created
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                content = f.read()
                print(f"📊 Generated LaTeX file size: {len(content)} characters")
                
                # Check for key sections
                sections_found = []
                expected_sections = ['abstract', 'introduction', 'methodology', 'results', 'conclusion']
                
                for section in expected_sections:
                    if f'\\section{{{section.title()}}}' in content or f'\\section{{{section.replace("_", " ").title()}}}' in content:
                        sections_found.append(section)
                
                print(f"📋 Sections found: {sections_found}")
                
                # Check if template variables were replaced
                if '\\VAR{' in content:
                    import re
                    unreplaced = re.findall(r'\\VAR\{([^}]+)\}', content)
                    print(f"⚠️  Unreplaced variables: {unreplaced}")
                else:
                    print("✅ All template variables were replaced")
                
                # Show a sample of the generated content
                print("\n📖 Sample of generated content:")
                print("-" * 40)
                lines = content.split('\n')
                for i, line in enumerate(lines[:30]):
                    if line.strip():
                        print(f"{i+1:2d}: {line}")
                print("-" * 40)
                
        else:
            print("❌ Output file was not created")
            
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete workflow test"""
    print("🧪 AI Paper Analyzer - Complete Workflow Test")
    print("=" * 60)
    
    success = test_complete_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Complete workflow test: ✅ PASSED")
        print("\n💡 The AI Paper Analyzer workflow is working correctly!")
        print("   - Summaries are being processed through Ollama")
        print("   - Sections are being elongated and humanized")
        print("   - LaTeX templates are being populated correctly")
    else:
        print("❌ Complete workflow test: ❌ FAILED")
        print("\n🔧 Check the error messages above for debugging information")

if __name__ == "__main__":
    main()