# AI Contract Analyzer ⚖️

A 100% local AI contract analyzer powered by Ollama and qwen3:30b. Upload any contract (PDF, Word, or text) and get a detailed risk analysis from your perspective — completely private, no data leaves your machine.

## Why Local LLM for Contracts?

Legal documents are highly sensitive. Cloud APIs (OpenAI, Claude) would expose your contracts to third parties. This runs entirely locally — zero data exposure, making it viable for law firms, enterprises, and individuals handling sensitive agreements.

## How It Works

    Upload contract (PDF/Word/Text)
    Select your role (Employee, Tenant, Client etc.)
    → Text extracted from document
    → LLM detects contract type
    → LLM identifies risky clauses from YOUR perspective
    → Risk score generated (0-100)
    → Improved language suggested for each risky clause

## Output

- Contract type detection
- Overall risk score (0-100)
- Per-clause risk level (Low/Medium/High)
- Why each clause is risky for your role
- Suggested improved language

## Tech Stack

| Component | This Project | Production Equivalent |
|---|---|---|
| LLM | Ollama qwen3:30b (local) | Azure OpenAI GPT-4 / Claude 3.5 |
| PDF parsing | pypdf | Azure Document Intelligence |
| Word parsing | python-docx | Azure Document Intelligence |
| UI | Streamlit | React enterprise portal |
| Backend | FastAPI | AWS Lambda / Azure Functions |

## Project Structure

    contract-analyzer/
    ├── backend/
    │   ├── main.py       # FastAPI app + endpoints
    │   ├── parser.py     # PDF/Word/text extraction
    │   ├── analyzer.py   # Ollama LLM analysis + risk scoring
    │   └── config.py     # Settings
    ├── frontend/
    │   └── app.py        # Streamlit UI
    └── requirements.txt

## Run Locally

### Prerequisites
- Python 3.10+
- Ollama installed ([ollama.com](https://ollama.com))
- qwen3:30b pulled and qwen3-30b-nothink created (thinking mode disabled for faster responses)

### Pull Model
```bash
ollama pull qwen3:30b
ollama show qwen3:30b --modelfile > /tmp/Modelfile
# Remove <think> line from TEMPLATE in /tmp/Modelfile
ollama create qwen3-30b-nothink -f /tmp/Modelfile
```

### Setup
```bash
git clone https://github.com/lordrajesh/contract-analyzer.git
cd contract-analyzer
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### Start
```bash
# Terminal 1
cd backend && uvicorn main:app --reload

# Terminal 2
cd frontend && streamlit run app.py
```

## Key Concepts Demonstrated
- **Local LLM inference** — Ollama as drop-in replacement for cloud APIs
- **Role-based risk analysis** — same contract, different risk profile per role
- **Multi-format document parsing** — PDF, Word, plain text
- **Air-gapped AI** — fully offline, zero data exposure
- **Production mapping** — every component maps to enterprise equivalent