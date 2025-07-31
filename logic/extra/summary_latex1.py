import subprocess
import os
import requests
import time
from pathlib import Path
from latex_gen1 import render_latex

# ------------------ CONFIG ------------------ #
SECTIONS = [
    "abstract", "introduction", "background", "literature_review",
    "figures_tables", "methodology", "challenges", "future",
    "results", "conclusion"
]

HUMANIZE_API_KEY = "sk_c70dclklm4jpampvrk5z7"
OLLAMA_MODEL = "mistral"
PROMPT_FILE = "prompt.txt"

# Create directories
Path("humanized").mkdir(exist_ok=True)
Path("final_latex_output").mkdir(exist_ok=True)

# ------------------ HELPER FUNCTIONS ------------------ #

def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def expand_with_ollama(section_name, summary):
    prompt = f"Generate the {section_name.replace('_', ' ').title()} section of a research paper from the following summary:\n\n{summary}"
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        output = result.stdout.decode("utf-8")
        return output.strip()
    except subprocess.TimeoutExpired:
        return f"[ERROR: Timeout on {section_name}]"

def rewrite_with_prompt(guideline_prompt, raw_text):
    combined_prompt = f"{guideline_prompt}\n\nText:\n{raw_text}"
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=combined_prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except Exception:
        return None

def rewrite_with_humanize_api(text):
    return text  # API integration disabled for now

# ------------------ MAIN PIPELINE ------------------ #

def main():
    try:
        from streamlit import session_state as st_session
        summary = st_session.get("research_paper_output", "")
        if not summary:
            import streamlit as st
            st.warning("⚠️ No research paper summary found in session. Please generate one first.")
            return
    except ImportError:
        # For CLI/testing
        print("⚠️ Streamlit not found. Using sample summary.")
        summary = "This is a sample research paper summary for CLI testing."

    prompt_guidelines = load_prompt()
    final_sections = {}

    for section in SECTIONS:
        print(f"\n--- Processing Section: {section.title()} ---")

        raw_expansion = expand_with_ollama(section, summary)
        if "[ERROR" in raw_expansion:
            print(f"❌ Failed to generate section: {section}")
            continue

        humanized = rewrite_with_prompt(prompt_guidelines, raw_expansion)

        if not humanized or "error" in humanized.lower():
            print(f"⚠️  Prompt-based rewrite failed, using raw expansion for: {section}")
            humanized = rewrite_with_humanize_api(raw_expansion)

        with open(f"humanized/{section}.txt", "w", encoding="utf-8") as f:
            f.write(humanized)

        final_sections[section] = humanized

    render_latex(final_sections)
    print("\n✅ Final LaTeX file saved at: final_latex_output/final_paper.tex")

if __name__ == "__main__":
    main()
