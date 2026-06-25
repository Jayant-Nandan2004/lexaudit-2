# LexAudit — Automated Legal & Contract Compliance Auditor

LexAudit is a full-stack web application that audits contract PDFs against a configurable set of compliance rules. Upload a PDF, and the app extracts its text, retrieves the most relevant clauses for each rule using a keyword-based retrieval engine, and produces a detailed compliance report with findings, severity ratings, and suggested corrections — all without any external AI API dependency.

---

## Features

- **PDF Contract Auditing** — Upload any PDF contract (up to 10 MB) and get a structured compliance report in seconds.
- **Configurable Rules** — Create, edit, and delete compliance rules with a title, description, category (`Liability`, `Indemnity`, `Intellectual Property`, etc.), and severity (`Critical`, `Major`, `Minor`).
- **Default Rule Seeding** — The app ships with a set of sensible default compliance rules that are auto-seeded on first run.
- **Offline Audit Engine** — The audit pipeline (PDF extraction → paragraph chunking → keyword retrieval → heuristic clause analysis) runs entirely offline with no LLM or external API calls.
- **Compliance Score** — Each audit produces an overall compliance score alongside per-rule findings.
- **Audit History** — All past audit reports are persisted in a local SQLite database and accessible at any time.
- **Animated Audit Progress** — A multi-step loading UI keeps the user informed while the audit runs.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, TypeScript / JSX |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite (via Python's built-in `sqlite3`) |
| PDF Parsing | `pypdf` |
| Data Validation | Pydantic v2 |
| PDF Report Generation | ReportLab |

---

## Project Structure

```
lexaudit-2/
├── backend/
│   ├── main.py              # FastAPI app, CORS config, startup hook
│   ├── database.py          # SQLite schema, CRUD helpers, rule seeding
│   ├── audit_engine.py      # Offline audit pipeline (PDF → findings)
│   ├── routers/
│   │   ├── rules.py         # CRUD endpoints for compliance rules
│   │   └── audits.py        # Audit upload & report retrieval endpoints
│   ├── schemas.py           # Pydantic request/response models
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── main.jsx         # React entry point
│       ├── App.jsx          # Root component & routing
│       ├── constants.js     # API base URL, loading steps, categories
│       └── ...              # Pages, components
└── run.bat                  # One-click Windows launcher
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repository

```bash
git clone https://github.com/Jayant-Nandan2004/lexaudit-2.git
cd lexaudit-2
```

### 2. Set up the backend

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Set up the frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Configure environment (optional)

By default the backend runs on `http://127.0.0.1:8000` and the frontend Vite dev server on `http://localhost:5173`. To override the backend port set `VITE_API_BASE` before starting Vite:

```bash
# Example: backend on port 8008
set VITE_API_BASE=http://127.0.0.1:8008/api   # Windows
export VITE_API_BASE=http://127.0.0.1:8008/api # macOS / Linux
```

To allow additional frontend origins on the backend side, set:

```bash
set ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
```

### 5. Run the app

**Windows (one-click):**

```bash
run.bat
```

This script creates the virtual environment if needed, installs all dependencies, auto-selects a free backend port, and starts both servers in parallel.

**Manual (any OS):**

```bash
# Terminal 1 — backend
venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/rules` | List all compliance rules |
| `POST` | `/api/rules` | Create a new rule |
| `PUT` | `/api/rules/{id}` | Update an existing rule |
| `DELETE` | `/api/rules/{id}` | Delete a rule |
| `POST` | `/api/audit` | Upload a PDF and run a compliance audit |
| `GET` | `/api/audits` | List all past audit reports |
| `GET` | `/api/audits/{id}` | Fetch a specific audit report |

Interactive API docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) when the backend is running.

---

## How the Audit Engine Works

1. **PDF Extraction** — `pypdf` extracts raw text page by page; lines are reflowed into logical paragraphs.
2. **Chunking** — The document is split into overlapping paragraph-based chunks (1 200-character window, 200-character overlap) to preserve clause context across boundaries.
3. **Keyword Retrieval** — For each rule, the engine scores chunks by keyword overlap (stop-words excluded) and selects the most relevant sections.
4. **Heuristic Analysis** — Deterministic keyword/regex matchers evaluate whether the retrieved clauses satisfy the rule. No LLM or network call is made.
5. **Report Generation** — Findings are persisted to SQLite and returned as a structured JSON report including compliance score, per-rule verdicts, matched text, reasoning, and suggested corrections.

---

## Contributing

Pull requests are welcome. For major changes please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the MIT License.
