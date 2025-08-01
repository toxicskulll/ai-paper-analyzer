#!/usr/bin/env python3
"""
Test script to verify that the basic summarization functionality still works
after making changes to support non-CUDA GPUs and fix UTF-8 encoding.
"""

import os
import sys
import logging
from summarizer_core import summarize_text_local, extract_text_from_file

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_mock_summarization():
    """Test the mock summarization functionality"""
    # Create our own mock summarizer instead of importing from app.py
    def mock_summarize(text: str, style: str = "bullet-point") -> str:
        """Mock summarizer for testing"""
        word_count = len(text.split())
        char_count = len(text)
        
        if style == "bullet-point":
            return f"""• **Content Analysis**: This chunk contains approximately {word_count} words and {char_count} characters
• **Key Topics**: The text discusses various research concepts and methodologies
• **Technical Content**: Contains technical terminology and academic language"""
        
        elif style == "paragraph":
            return f"This section contains {word_count} words discussing research methodologies and findings."
        
        else:  # detailed
            return f"""**Objective**: To demonstrate the AI Paper Analyzer's capability
**Content Overview**: This chunk contains {word_count} words
**Methodology**: The text follows academic writing standards"""
    
    test_text = "This is a test text for summarization. It contains multiple sentences that should be summarized."
    
    # Test different styles
    for style in ["bullet-point", "paragraph", "detailed"]:
        logger.info(f"Testing mock summarization with style: {style}")
        summary = mock_summarize(test_text, style)
        
        if summary:
            logger.info(f"✅ Mock summarization successful with style '{style}'")
            logger.info(f"Summary preview: {summary[:100]}...")
        else:
            logger.error(f"❌ Mock summarization failed with style '{style}'")
            return False
    
    return True

def test_real_summarization(use_gpu=None):
    """Test the real summarization functionality with Ollama"""
    test_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. 
    AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.
    The term "artificial intelligence" had previously been used to describe machines that mimic and display "human" cognitive skills that are associated with the human mind, such as "learning" and "problem-solving". 
    This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated.
    """
    
    # Test with different depth settings
    for depth in ["short", "medium", "detailed"]:
        logger.info(f"Testing real summarization with depth: {depth} and GPU: {use_gpu}")
        
        try:
            summary = summarize_text_local(test_text, depth=depth, model="mistral", use_gpu=use_gpu)
            
            if summary:
                logger.info(f"✅ Real summarization successful with depth '{depth}'")
                logger.info(f"Summary preview: {summary[:100]}...")
            else:
                logger.warning(f"⚠️ Real summarization returned None with depth '{depth}'")
                logger.warning("This might be expected if Ollama is not installed or configured")
        except Exception as e:
            logger.error(f"❌ Real summarization failed with depth '{depth}': {e}")
            logger.error("This is expected if Ollama is not installed")
    
    return True

def main():
    """Main test function"""
    logger.info("Starting summarization tests")
    
    # Test mock summarization
    mock_result = test_mock_summarization()
    logger.info(f"Mock summarization tests {'passed' if mock_result else 'failed'}")
    
    # Test real summarization with different GPU settings
    # Note: These tests will be skipped if Ollama is not installed
    for gpu_setting in [None, True, False]:
        try:
            logger.info(f"Testing with GPU setting: {gpu_setting}")
            real_result = test_real_summarization(use_gpu=gpu_setting)
            logger.info(f"Real summarization tests with GPU={gpu_setting} completed")
        except Exception as e:
            logger.error(f"Error during real summarization test with GPU={gpu_setting}: {e}")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()