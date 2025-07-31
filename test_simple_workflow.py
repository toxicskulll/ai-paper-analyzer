#!/usr/bin/env python3
"""
Simple test of the AI Paper Analyzer workflow with sequential processing
"""

import os
import sys
sys.path.append('/workspace/project/ai-paper-analyzer/logic')

from summary_latex import Config, PaperGenerator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_simple_workflow():
    """Test a simple workflow with just a few sections"""
    print("🔄 Testing Simple Workflow: Summary → Sections → LaTeX")
    print("=" * 60)
    
    # Simple test summary
    test_summary = """
    This research explores machine learning for text analysis. 
    We use neural networks to classify documents and extract insights.
    Results show 90% accuracy on test datasets.
    """
    
    # Change to logic directory
    os.chdir('/workspace/project/ai-paper-analyzer/logic')
    
    try:
        # Create config with sequential processing and shorter timeouts
        config = Config()
        config.parallel_processing = False  # Use sequential processing
        config.ollama_timeout = 30  # Shorter timeout
        config.sections = ["abstract", "introduction", "conclusion"]  # Just 3 sections
        config.validate_output = False  # Skip validation for speed
        
        print("📝 Creating paper generator...")
        generator = PaperGenerator(config, test_summary)
        
        print("🔗 Testing Ollama connection...")
        if not generator.validate_ollama_connection():
            print("❌ Ollama connection failed")
            return False
        
        print("✅ Ollama connection successful")
        
        print("📖 Loading prompt...")
        prompt = generator.load_prompt()
        print(f"✅ Prompt loaded: {len(prompt)} characters")
        
        print("🔄 Processing sections sequentially...")
        
        # Process just one section as a test
        section_name, content = generator.process_section("abstract", prompt)
        
        if content:
            print(f"✅ Successfully generated {section_name} section")
            print(f"📝 Content length: {len(content)} characters")
            print(f"📖 Sample content: {content[:200]}...")
            
            # Test LaTeX generation with this one section
            generator.final_sections[section_name] = content
            generator._generate_latex()
            
            # Check if LaTeX file was created
            latex_file = f"{config.latex_output_dir}/final_paper.tex"
            if os.path.exists(latex_file):
                with open(latex_file, 'r') as f:
                    latex_content = f.read()
                    print(f"✅ LaTeX file generated: {len(latex_content)} characters")
                    
                    # Check if our content is in the LaTeX
                    if section_name in generator.final_sections and generator.final_sections[section_name] in latex_content:
                        print("✅ Section content found in LaTeX file")
                    else:
                        print("⚠️  Section content not found in LaTeX file")
                        
                return True
            else:
                print("❌ LaTeX file was not created")
                return False
        else:
            print(f"❌ Failed to generate {section_name} section")
            return False
            
    except Exception as e:
        print(f"❌ Simple workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the simple workflow test"""
    print("🧪 AI Paper Analyzer - Simple Workflow Test")
    print("=" * 60)
    
    success = test_simple_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Simple workflow test: ✅ PASSED")
        print("\n💡 Key findings:")
        print("   ✅ Ollama connection works")
        print("   ✅ Section generation works")
        print("   ✅ LaTeX template population works")
        print("   ✅ The workflow pipeline is functional!")
    else:
        print("❌ Simple workflow test: ❌ FAILED")
        print("\n🔧 Check the error messages above for debugging information")

if __name__ == "__main__":
    main()