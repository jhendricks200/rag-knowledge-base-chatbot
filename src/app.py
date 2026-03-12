"""
FastAPI server for the RAG Knowledge Base Assistant.

Serves the chat UI and handles API calls for chat and file upload.
"""

import shutil
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ingest import _ingest_pdf, _ingest_text
from embed import add_chunks
from query import ask

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Knowledge Base Assistant")

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    answer: str
    history: list[dict]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ingest_file(filepath: str) -> list[dict]:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return _ingest_pdf(filepath)
    elif ext in (".md", ".txt", ".markdown"):
        return _ingest_text(filepath)
    return []

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer, history = ask(req.message, req.history)
    return ChatResponse(answer=answer, history=history)


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    DOCS_DIR.mkdir(exist_ok=True)
    results = []

    for upload_file in files:
        # Save to temp then move to docs/
        suffix = Path(upload_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await upload_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        dest = DOCS_DIR / upload_file.filename
        shutil.move(tmp_path, dest)

        chunks = _ingest_file(str(dest))
        name = Path(upload_file.filename).stem

        if chunks:
            added = add_chunks(chunks)
            results.append(f"Document added: {name} ({added} chunks indexed)")
        else:
            results.append(f"Could not extract text from {name}")

    return {"results": results}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
