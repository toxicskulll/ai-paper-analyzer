import os
from pathlib import Path
from jinja2 import Template

def render_latex(section_data: dict, 
                 template_path: str = "paper_template.tex", 
                 output_path: str = "final_latex_output/final_paper.tex"):
    """
    Fill a LaTeX template with section content and write to output file.

    Args:
        section_data (dict): Dictionary where keys match template placeholders (e.g., 'introduction')
        template_path (str): Path to the LaTeX template with Jinja-style placeholders.
        output_path (str): Final path to save rendered .tex file.
    """
    # Ensure output folder exists
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)

    # Read the template
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            latex_template = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"LaTeX template not found at: {template_path}")

    # Prepare Jinja2 template
    template = Template(latex_template)

    # Map sections to placeholders used in your .tex
    render_data = {}
    for section, content in section_data.items():
        key = f"{section}_text"  # e.g. introduction_text
        render_data[key] = content.strip()

    # Render template
    final_tex = template.render(render_data)

    # Write output file
    with open(output_path, "w", encoding="utf-8") as out_file:
        out_file.write(final_tex)

    print(f"✅ LaTeX rendered successfully to: {output_path}")
