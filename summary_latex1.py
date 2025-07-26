import subprocess
import os
import requests
import time
from pathlib import Path
from latex_gen import render_latex

# ------------------ CONFIG ------------------ #
SECTIONS = [
    "abstract", "introduction", "background", "literature_review",
    "figures_tables", "methodology", "challenges", "future",
    "results", "conclusion"
]

HUMANIZE_API_KEY = "sk_c70dclklm4jpampvrk5z7"
OLLAMA_MODEL = "mistral"
PROMPT_FILE = "prompt.txt"

# INPUT FROM YOUR STREAMLIT APP
from streamlit import session_state
SUMMARY = session_state.research_paper_output  # <-- Comes from app.py

Path("humanized").mkdir(exist_ok=True)
Path("final_latex_output").mkdir(exist_ok=True)

# ------------------ HELPER FUNCTIONS ------------------ #

def load_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def expand_with_ollama(section_name, summary):
    """Call Ollama to expand summary into a specific section"""
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
    """Try rewriting using the in-context prompt style"""
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
    url = "https://api.humanizeai.in/v1/rewrite"
    headers = {
        "Authorization": f"Bearer {HUMANIZE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        return response.json().get("rewritten_text", "")
    return "[ERROR: Humanize API failed]"

# ------------------ MAIN PIPELINE ------------------ #

def main():
    prompt_guidelines = load_prompt()
    final_sections = {}

    for section in SECTIONS:
        print(f"\n--- Processing Section: {section.title()} ---")

        # 1. Expand section using Ollama
        raw_expansion = expand_with_ollama(section, SUMMARY)
        if "[ERROR" in raw_expansion:
            print(f"❌ Failed to generate section: {section}")
            continue

        # 2. Try rewriting using prompt
        humanized = rewrite_with_prompt(prompt_guidelines, raw_expansion)

        # 3. If rewrite fails, fallback to Humanize API
        if not humanized or "error" in humanized.lower():
            print(f"⚠️  Prompt-based rewrite failed, falling back to HumanizeAI for: {section}")
            humanized = rewrite_with_humanize_api(raw_expansion)

        # 4. Save humanized output to file for inspection
        with open(f"humanized/{section}.txt", "w", encoding="utf-8") as f:
            f.write(humanized)

        final_sections[section] = humanized

    # 5. Render LaTeX with all filled sections
    render_latex(final_sections)

    print("\n✅ Final LaTeX file saved at: final_latex_output/final_paper.tex")

if __name__ == "__main__":
    main()
