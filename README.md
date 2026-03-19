# MSBA Smart Advisor 🎓

An AI-powered academic and career advising chatbot for the Master of Science in Business Analytics and Artificial Intelligence (MSBA) program at UT Dallas. Built on a local LLM via LM Studio with a RAG pipeline using ChromaDB and semantic embeddings.

---

## What It Does

The advisor operates across three components:

- **Degree Planner** — Helps new and continuing students map out their course path based on the 36-credit hour MSBA program requirements. Recommends specific courses based on interests, completed coursework, prerequisites, and credit type (core vs elective).

- **Career Mentor** — Provides qualitative career guidance based on a student's interests or target role. Recommends specific courses from the catalog that build toward the required technical and soft skills for that career path.

- **Skills Gap Analyzer** — Compares a student's current profile against industry-standard requirements for a target job title. Accepts either completed course IDs or a resume PDF as input, identifies missing competencies, and recommends courses to close those gaps.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Local model via LM Studio (Llama 3.1 8B recommended) |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (persistent, local) |
| PDF Parsing | PyPDF2 |
| API Client | OpenAI-compatible via LM Studio local server |

---

## Project Structure
```
msba-advisor/
├── data/
│   ├── courses.json          # 83 MSBA courses with descriptions, skills, prerequisites
│   └── skills_clean.json     # 20 job roles with technical and soft skills
├── vector_store/
│   ├── build_index.py        # Builds ChromaDB index from data files (run once)
│   ├── retriever.py          # Semantic search and context formatting
│   └── chroma_db/            # Generated — not committed to git
├── components/
│   ├── degree_planner.py
│   ├── career_mentor.py
│   └── skills_gap.py
├── utils/
│   ├── resume_parser.py      # PDF text extraction
│   └── semantic_matcher.py   # Skill comparison using embeddings
├── prompts/
│   ├── degree_planner.txt
│   ├── career_mentor.txt
│   └── skills_gap.txt
├── data_loader.py            # Trimmed context loaders per component
├── llm_client.py             # LM Studio API client
├── app.py                    # Main entry point
└── requirements.txt
```

---

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd msba-advisor
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up LM Studio

- Download LM Studio from `lmstudio.ai`
- Download `Llama-3.1-8B-Instruct` (8GB RAM minimum) or `Llama-3.2-3B-Instruct` (4GB RAM)
- Go to the **Developer** tab in LM Studio
- Select your model and click **Start Server**
- Server runs at `http://localhost:1234` by default

### 5. Build the vector index

Run this once — it indexes all courses and job roles into ChromaDB:
```bash
python vector_store/build_index.py
```

You will need to re-run this if you update `courses.json` or `skills_clean.json`.

### 6. Run the advisor
```bash
python app.py
```

---

## Usage

Select a component from the main menu:
```
🎓 MSBA Smart Advisor
==================================================
  1. Degree Planner
  2. Career Mentor
  3. Skills Gap Analyzer
  0. Exit
```

### Degree Planner
- Tell the advisor if you are a new or continuing student
- If continuing, provide your completed course IDs (e.g. `BUAN 6333, BUAN 6340`)
- The advisor maps remaining credits and recommends next courses

### Career Mentor
- Describe your career interests or name a specific job title
- The advisor explains the role, required skills, and recommends courses that build toward it

### Skills Gap Analyzer
- Choose input method: completed courses or resume PDF
- Provide your target job title
- The analyzer identifies matched skills, missing competencies, and course recommendations

---

## Data Sources

- **Course data** — Scraped from the [UTD 2024 Graduate Catalog](https://catalog.utdallas.edu/2024/graduate/programs/jsom/business-analytics)
- **Job roles data** — Manually curated from industry job postings and career resources for roles relevant to MSBA graduates

---

## Notes

- The `vector_store/chroma_db/` folder is excluded from git. Rebuild it locally using `build_index.py`
- The `UNEXPECTED` warning from `sentence-transformers` on startup is harmless and can be ignored
- The `HF Hub unauthenticated` warning is also harmless — the model is cached locally after first download
- Resume PDF parsing works best with text-based PDFs. Scanned or image-based PDFs may not extract correctly

---

## Team

Built as part of a graduate project for the Jindal School of Management — UT Dallas.
