# Knowledge Base Assistant

A RAG (Retrieval-Augmented Generation) chatbot that answers questions grounded in your uploaded documents. Answers only from your documents, with citations.

Upload PDFs or Markdown files, and the system automatically ingests, chunks, embeds, and indexes them. Ask a question in the chat and get accurate answers drawn only from your knowledge base.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Custom HTML/CSS/JS — modern chat UI with dark mode support |
| **Backend** | FastAPI + Uvicorn |
| **Ingestion** | PyPDF2 (PDFs), standard I/O (Markdown/text) |
| **Chunking** | ~300-token chunks with 50-token overlap, per-page/per-section metadata |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Vector Store** | ChromaDB (persistent to disk, cosine similarity) |
| **LLM** | Claude via Anthropic API — grounded Q&A with source citations |

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/jhendricks200/rag-knowledge-base-chatbot.git
cd rag-knowledge-base-chatbot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-key-here
```

## Running

```bash
source venv/bin/activate
python src/app.py
```

Open http://localhost:7860. Upload documents using the paperclip icon in the input bar.

## How It Works

1. **Ingest** — Drop documents into `docs/` or upload via the chat UI. PDFs are read page-by-page; Markdown files are split by heading.
2. **Chunk** — Documents are split into ~300-token chunks with 50-token overlap to preserve context at boundaries.
3. **Embed** — Each chunk is embedded using `all-MiniLM-L6-v2` and stored in ChromaDB on disk. Duplicate detection prevents re-embedding existing content.
4. **Retrieve** — When you ask a question, the query is embedded and the top 5 most similar chunks are retrieved via cosine similarity.
5. **Generate** — Retrieved chunks are passed as context to Claude, which generates a grounded answer with inline source citations. If the answer isn't in the documents, it says so.

Conversation memory keeps the last 5 exchanges so follow-up questions work naturally.

## Evaluation

The repo includes a small, reproducible test set so the chatbot's quality is measured instead of assumed.

- **`eval/questions.jsonl`**: 35 questions written against the four documents in `docs/`. 31 have a known answer, the document and section it lives in, and the facts the answer must contain. 4 are questions the documents cannot answer (for example "Who is the CEO?"), where the correct behavior is to say so instead of guessing.
- **`eval/run_eval.py`**: runs every question through the real pipeline and scores it.

| Metric | What it checks |
|--------|----------------|
| Retrieval hit rate @1 / @5 | The chunk holding the answer (right document **and** section) is the first result / in the top 5 |
| MRR | Mean reciprocal rank of that chunk (1.0 = always first) |
| Answer accuracy | Claude's answer contains every expected fact and does not wrongly refuse |
| Citation rate | The answer cites the correct source document |
| Refusal accuracy | Unanswerable questions get "I don't have that information" |

Scoring is deterministic string matching on key facts (numbers, names), so results are transparent and repeatable. The eval builds its own index from `docs/` in `eval/.chroma_eval`, so uploads made through the chat UI don't change the scores.

```bash
python eval/run_eval.py                  # full run (needs ANTHROPIC_API_KEY in .env)
python eval/run_eval.py --retrieval-only # retrieval only, no API key needed
```

A GitHub Actions workflow (`.github/workflows/eval.yml`) runs the evaluation on every pull request and push to `main` and uploads `eval/results/latest.json`. In CI, answer scoring authenticates to the Claude API with Workload Identity Federation (GitHub OIDC), so no API key is stored in the repo or its secrets. It runs when the federation IDs are set as repository variables.

### Results

Retrieval results from the GitHub Actions run on 12 Nov 2026 (`all-MiniLM-L6-v2`, top 5 chunks, 31 answerable questions):

| Metric | Result |
|--------|--------|
| Hit rate @1 | 97% (30 / 31) |
| Hit rate @5 | 100% (31 / 31) |
| MRR | 0.98 |
| Right document in top 5 | 100% |

The one question not ranked first was "How much does the Professional plan cost per user per month?", where the pricing section came back 4th behind other plan-related FAQ chunks. It was still in the top 5, so Claude received it as context.

Caveat: this is a small corpus (4 documents) with questions written by the author, so these numbers show the pipeline works end to end. They are not a benchmark. Answer accuracy, citation and refusal scores will be added once the workflow runs with an API key.

## Project Structure

```
├── docs/                     # Document store (PDFs, Markdown, text)
├── eval/
│   ├── questions.jsonl       # Test questions with expected sources and facts
│   └── run_eval.py           # Evaluation harness
├── src/
│   ├── static/
│   │   └── index.html        # Chat UI (HTML/CSS/JS)
│   ├── app.py                # FastAPI server
│   ├── ingest.py             # Document reading and chunking
│   ├── embed.py              # Embedding, ChromaDB storage, semantic search
│   └── query.py              # Claude API, RAG prompt, conversation memory
├── .env.example
├── requirements.txt
└── README.md
```

## API

The FastAPI backend exposes two endpoints:

- `POST /api/chat` — Send `{ "message": "...", "history": [] }`, returns `{ "answer": "...", "history": [...] }`
- `POST /api/upload` — Multipart file upload, returns `{ "results": ["Document added: ..."] }`

## CLI

Each module also works standalone:

```bash
python src/ingest.py          # Ingest docs/ and print chunk summary
python src/embed.py           # Embed chunks and test vector search
python src/query.py           # Interactive terminal chat
```
