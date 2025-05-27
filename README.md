# 📄 AI Research Paper Analyzer

An **AI-powered local tool** to analyze and summarize research papers using a local LLM (Mistral via Ollama). Upload `.pdf`, `.docx`, or `.txt` files and get structured, customizable summaries as downloadable PDFs — all running fully offline on your machine.

---

## 🚀 Features

- 📤 Upload PDFs, DOCX, or TXT files
- 🧠 Analyze using **local LLM** (via [Ollama](https://ollama.com/))
- 📑 Choose summary style: Bullet-point | Paragraph | Detailed
- 🧩 View summaries of individual chunks
- 🧾 Final PDF summary download
- 🛠 View debug logs for transparency and troubleshooting

---

## 🗂 Project Structure

```
AI-Paper-Analyzer/
│
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
│
├── extracted_data/        # Temporary uploads
├── summaries/             # Chunk-level summaries
├── pdf_summaries/         # Final generated summary PDFs
│
├── summarizer_debug.log   # Debug logs
└── README.md              # This file
```

---

## 🧑‍💻 Getting Started

> 📝 This guide assumes **no prior setup or knowledge** of Python, Ollama, or LLMs.

---

### 1. ✅ Install Python

Download and install Python 3.10+ from [https://www.python.org/downloads/](https://www.python.org/downloads/).

During installation, ensure to check **"Add Python to PATH"**.

---

### 2. ✅ Set up this Project

Open a terminal (Command Prompt or PowerShell on Windows), then run:

```bash
# Clone the repo
git clone https://github.com/toxicskulll/AI-Paper-Analyzer.git
cd AI-Paper-Analyzer

# Create a virtual environment
python -m venv venv
venv\Scripts\activate   # Use `source venv/bin/activate` on Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

---

### 3. ✅ Install Ollama & Download Mistral

**Ollama** lets you run large language models (LLMs) on your machine.

#### ➤ Step 1: Install Ollama

- Download and install Ollama from: [https://ollama.com/download](https://ollama.com/download)

#### ➤ Step 2: Run Ollama and Download Mistral

Open a new terminal and run:

```bash
ollama run mistral
```

Wait for the model to download (~4GB). You'll see a chat prompt — press `Ctrl+C` to exit.

---

### 4. ✅ Configure Ollama Path (Windows only)

If the app crashes with a path error, update this line in `app.py` with your actual path:

```python
OLLAMA_PATH = r"C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Ollama\\ollama.exe"
```

> Replace `YourUsername` with your actual Windows user name.

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Then open the link shown in your terminal (usually `http://localhost:8501`) in your browser.

---

## 📄 How It Works

1. 📤 Upload a research paper
2. 🔍 Extract & clean the text
3. 🧩 Chunk into ~800-token blocks
4. 🤖 Summarize each chunk using **Mistral** LLM locally
5. 🧱 Show intermediate chunk summaries (optional)
6. 🧾 Aggregate final summary
7. 📥 Export to PDF

---

## 🖥 UI Options

- **Summary Style:** Choose from bullet-point, paragraph, or detailed format
- **Show Chunk Summaries:** Toggle to inspect partial results
- **Show Debug Logs:** View behind-the-scenes details

---

## 🧪 Example Output

After uploading a paper, you'll get:

- 🔹 Per-chunk summaries (if enabled)
- 📄 Final structured summary (in text area)
- 📥 A downloadable PDF (`your_paper_summary.pdf`)

---

## 🧰 Dependencies

Major packages used:

- [`streamlit`](https://streamlit.io/)
- [`PyMuPDF`](https://github.com/pymupdf/PyMuPDF) for PDF extraction
- [`python-docx`](https://python-docx.readthedocs.io/en/latest/) for DOCX
- [`fpdf`](https://pyfpdf.readthedocs.io/en/latest/) for PDF generation
- [`tiktoken`](https://github.com/openai/tiktoken) for tokenization
- [`ollama`](https://ollama.com/) for running local LLMs
- [`st_aggrid`](https://github.com/PablocFonseca/streamlit-aggrid) for data tables

Install them all via:

```bash
pip install -r requirements.txt
```

---

## 📌 Notes

- The app works completely **offline** after initial setup (Ollama model download).
- Supports `.pdf`, `.docx`, `.txt` input.
- Each summary is saved in the `pdf_summaries/` directory.

---

## 🛠 Troubleshooting

- 🟥 **Ollama subprocess error?** Make sure:
  - `OLLAMA_PATH` is correct
  - Ollama is installed properly
  - The `mistral` model is downloaded

- 🟥 **Streamlit app doesn't load?**
  - Run `streamlit run app.py`
  - Use the correct Python environment (`venv`)

---

## 🤝 Contributions

Feel free to fork, open issues, and suggest features!

---

## 📃 License

[MIT](LICENSE)

---

## ✨ Made with love by [Aadishesh Padasalgi](https://aadisheshpadasalgi.in)
