# Knowledge Base Assistant

A RAG (Retrieval-Augmented Generation) chatbot that answers questions grounded entirely in your uploaded documents. No hallucination — every answer is sourced and cited.

Upload PDFs or Markdown files, and the system automatically ingests, chunks, embeds, and indexes them. Ask a question in the chat and get accurate answers drawn only from your knowledge base.

![Chat Interface](screenshot.png)

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

```bash
git clone https://github.com/YOUR_USERNAME/rag-knowledge-base-chatbot.git
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

## Project Structure

```
├── docs/                     # Document store (PDFs, Markdown, text)
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
