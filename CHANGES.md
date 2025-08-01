# Changes in the logic-gpu-utf8-fixes Branch

## Overview
This branch adds support for non-CUDA GPUs and fixes UTF-8 encoding issues in subprocess calls throughout the codebase. It also adds a test script to verify that basic summarization functionality still works.

## Key Changes

### 1. GPU Control Options
- Added `use_gpu` parameter to `summarize_text_local()` functions in:
  - `llm_analyzer.py`
  - `summarizer_core.py`
  - `logic/summary_latex.py`
- Added UI controls in Streamlit sidebar for GPU usage selection:
  - Auto (default): Let Ollama decide based on system capabilities
  - Force GPU: Force Ollama to use GPU with `--gpu` flag
  - CPU Only: Force Ollama to use CPU with `--cpu-only` flag

### 2. UTF-8 Encoding Fixes
- Updated all subprocess calls to use explicit UTF-8 encoding/decoding with error handling
- Added `encoding='utf-8', errors='replace'` to subprocess.run() calls
- Changed subprocess.Popen() calls to use binary mode with explicit encoding/decoding
- Added proper error handling for UTF-8 decoding errors

### 3. Testing
- Added `test_summarization.py` script to verify basic functionality
- Tests both mock summarization and real summarization with different GPU settings
- Handles the case where Ollama is not installed gracefully

### 4. Other Improvements
- Fixed global variable declarations in app.py
- Updated import for streamlit-aggrid
- Added better error handling and logging for subprocess calls
- Made model selection dynamic through the UI

## Files Modified
- `app.py`: Added UI controls and updated subprocess handling
- `llm_analyzer.py`: Updated summarize_text_local() with GPU control and UTF-8 encoding
- `summarizer_core.py`: Updated summarize_text_local() with GPU control and UTF-8 encoding
- `logic/summary_latex.py`: Updated with GPU control and UTF-8 encoding

## Files Added
- `test_summarization.py`: Test script to verify functionality

## Testing
The changes have been tested with:
- Mock summarization (works without Ollama)
- Real summarization with different GPU settings (requires Ollama)
- UTF-8 encoding/decoding with error handling