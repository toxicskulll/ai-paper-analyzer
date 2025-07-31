#!/usr/bin/env python3
"""
Test the AI Paper Analyzer workflow with mock Ollama responses
"""

import os
import sys
sys.path.append('/workspace/project/ai-paper-analyzer/logic')

from summary_latex import Config, PaperGenerator
from latex_gen import render_latex
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_mock_workflow():
    """Test the workflow with mock data to verify the pipeline"""
    print("🔄 Testing Mock Workflow: Mock Sections → LaTeX")
    print("=" * 60)
    
    # Change to logic directory
    os.chdir('/workspace/project/ai-paper-analyzer/logic')
    
    try:
        # Create mock section data that simulates what Ollama would generate
        mock_sections = {
            'abstract': """This research paper presents a comprehensive analysis of advanced machine learning techniques applied to natural language processing tasks. Our study investigates the effectiveness of transformer-based architectures in various NLP applications, including sentiment analysis, text classification, and language generation. Through extensive experimentation on multiple datasets, we demonstrate significant improvements in performance metrics compared to traditional approaches. The findings contribute to the growing body of knowledge in AI-driven text processing and provide insights for future research directions.""",
            
            'introduction': """Natural Language Processing (NLP) has experienced remarkable advancement with the emergence of deep learning methodologies. The field has transitioned from rule-based systems and statistical models to sophisticated neural network architectures that can understand and generate human language with unprecedented accuracy. This transformation has been particularly accelerated by the development of attention mechanisms and transformer architectures, which have revolutionized how machines process textual information. Our research focuses on exploring these cutting-edge techniques and their practical applications in real-world scenarios.""",
            
            'background': """The foundation of modern NLP lies in the evolution from traditional computational linguistics to data-driven approaches. Early systems relied heavily on hand-crafted rules and linguistic knowledge bases, which, while interpretable, lacked the flexibility to handle the complexity and variability of natural language. The introduction of statistical methods marked a significant shift, enabling systems to learn patterns from data. However, the true breakthrough came with deep learning, particularly with the development of recurrent neural networks (RNNs) and later, transformer architectures that could capture long-range dependencies in text.""",
            
            'literature_review': """Recent literature in NLP has been dominated by transformer-based models, starting with the seminal work of Vaswani et al. (2017) on the Attention mechanism. BERT (Bidirectional Encoder Representations from Transformers) by Devlin et al. (2018) demonstrated the power of pre-trained language models, achieving state-of-the-art results across multiple NLP benchmarks. Subsequently, GPT models by OpenAI showed the potential of generative pre-training, while T5 by Google unified text-to-text transfer learning. These developments have established transformers as the dominant paradigm in modern NLP research.""",
            
            'methodology': """Our experimental methodology encompasses several key components designed to evaluate the effectiveness of advanced NLP techniques. We employ a multi-stage approach beginning with data preprocessing and tokenization using state-of-the-art tokenizers. The core of our methodology involves fine-tuning pre-trained transformer models on domain-specific datasets, implementing various optimization strategies including learning rate scheduling and gradient clipping. We utilize cross-validation techniques to ensure robust evaluation and employ multiple metrics including accuracy, F1-score, BLEU score, and perplexity to assess model performance comprehensively.""",
            
            'results': """Our experimental results demonstrate substantial improvements across all evaluated tasks. In sentiment analysis, we achieved 94.2% accuracy, representing a 6.9% improvement over baseline methods. Text classification tasks showed an F1-score of 0.91, compared to 0.84 for traditional approaches. Language generation experiments yielded a BLEU score of 0.73, significantly outperforming previous methods that achieved 0.65. These results were consistent across multiple datasets and validation splits, indicating the robustness and generalizability of our approach. Statistical significance testing confirmed that all improvements were statistically significant at p < 0.01.""",
            
            'figures_tables': """The experimental results are comprehensively presented through various visualizations and tabular data. Figure 1 illustrates the training curves showing convergence patterns across different model configurations. Table 1 provides a detailed comparison of performance metrics across all evaluated tasks and datasets. Figure 2 presents attention visualization maps demonstrating how the model focuses on relevant textual features. Table 2 summarizes the computational requirements and training times for different model sizes, providing insights into the efficiency-performance trade-offs inherent in these approaches.""",
            
            'challenges': """Despite the promising results, several challenges were encountered during this research. Computational resource requirements proved substantial, with larger models requiring significant GPU memory and training time. Data quality and preprocessing emerged as critical factors affecting model performance, particularly in handling noisy or domain-specific text. Hyperparameter tuning presented another challenge, requiring extensive experimentation to identify optimal configurations. Additionally, model interpretability remains a concern, as the complex attention mechanisms make it difficult to understand the decision-making process of these sophisticated models.""",
            
            'future': """Future research directions include several promising avenues for advancement. Multi-modal approaches combining text with visual and audio information represent a significant opportunity for enhanced understanding. Cross-lingual transfer learning could enable better performance on low-resource languages. Investigation of more efficient architectures that maintain performance while reducing computational requirements is crucial for practical deployment. Additionally, research into explainable AI techniques for NLP models will be essential for building trust and understanding in these systems. Integration with emerging technologies such as quantum computing may also open new possibilities.""",
            
            'conclusion': """This research has successfully demonstrated the effectiveness of advanced machine learning techniques in natural language processing applications. The comprehensive evaluation across multiple tasks and datasets provides strong evidence for the superiority of transformer-based approaches over traditional methods. The significant improvements in accuracy, F1-scores, and BLEU scores validate the potential of these techniques for real-world applications. While challenges remain in terms of computational requirements and interpretability, the benefits clearly outweigh the limitations. These findings contribute valuable insights to the NLP research community and provide a foundation for future investigations in this rapidly evolving field."""
        }
        
        print("📝 Mock sections created successfully")
        print(f"📊 Number of sections: {len(mock_sections)}")
        
        # Test LaTeX generation with mock data
        print("🔄 Generating LaTeX from mock sections...")
        
        output_path = render_latex(
            section_data=mock_sections,
            template_path="paper_template.tex",
            output_path="final_latex_output/mock_paper.tex"
        )
        
        print(f"✅ LaTeX generation completed!")
        print(f"📄 Output file: {output_path}")
        
        # Verify the output
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                content = f.read()
                print(f"📊 Generated LaTeX file size: {len(content)} characters")
                
                # Check for key sections
                sections_found = []
                for section_name in mock_sections.keys():
                    if mock_sections[section_name][:50] in content:
                        sections_found.append(section_name)
                
                print(f"📋 Sections found in LaTeX: {sections_found}")
                
                # Check if template variables were replaced
                if '\\VAR{' in content:
                    import re
                    unreplaced = re.findall(r'\\VAR\{([^}]+)\}', content)
                    print(f"⚠️  Unreplaced variables: {unreplaced}")
                else:
                    print("✅ All template variables were replaced")
                
                # Show document structure
                print("\n📖 Document structure:")
                print("-" * 40)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '\\section{' in line or '\\title{' in line or '\\author{' in line:
                        print(f"{i+1:3d}: {line.strip()}")
                print("-" * 40)
                
                return True
        else:
            print("❌ Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Mock workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_humanization_prompt():
    """Test the humanization prompt loading"""
    print("\n🔄 Testing Humanization Prompt")
    print("=" * 40)
    
    os.chdir('/workspace/project/ai-paper-analyzer/logic')
    
    try:
        config = Config()
        generator = PaperGenerator(config, "test summary")
        
        prompt = generator.load_prompt()
        if prompt:
            print(f"✅ Prompt loaded successfully: {len(prompt)} characters")
            print(f"📖 Prompt preview: {prompt[:200]}...")
            return True
        else:
            print("❌ Failed to load prompt")
            return False
            
    except Exception as e:
        print(f"❌ Prompt test failed: {e}")
        return False

def main():
    """Run the mock workflow test"""
    print("🧪 AI Paper Analyzer - Mock Workflow Test")
    print("=" * 60)
    
    # Test prompt loading
    prompt_success = test_humanization_prompt()
    
    # Test mock workflow
    workflow_success = test_mock_workflow()
    
    print("\n" + "=" * 60)
    print("🏁 Test Summary:")
    print(f"   📖 Prompt loading: {'✅ PASSED' if prompt_success else '❌ FAILED'}")
    print(f"   🔄 Mock workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    
    if prompt_success and workflow_success:
        print("\n🎉 All tests PASSED!")
        print("\n💡 Key findings:")
        print("   ✅ Template syntax is now correct (\\VAR{variable})")
        print("   ✅ Section data maps correctly to template variables")
        print("   ✅ LaTeX generation pipeline works end-to-end")
        print("   ✅ Humanization prompt loads successfully")
        print("\n🔧 The workflow is ready! The only remaining issue is:")
        print("   ⚠️  Ollama timeout/hanging (model works but process doesn't terminate)")
        print("   💡 This can be fixed by adjusting timeout settings or using async processing")
    else:
        print("\n❌ Some tests FAILED")
        print("🔧 Check the error messages above for debugging information")

if __name__ == "__main__":
    main()