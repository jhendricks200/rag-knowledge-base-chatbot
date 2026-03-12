"""
RAG query engine with Claude API integration.

Retrieves relevant chunks via embed.py, builds a grounded prompt,
and sends it to Claude with conversation memory (last 5 exchanges).
"""

import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from embed import search

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = "claude-sonnet-4-20250514"
MAX_HISTORY = 5  # number of exchange pairs to keep


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a helpful knowledge base assistant. Answer the user's question using \
ONLY the provided context documents. Follow these rules strictly:

1. Only use information from the context below. Do not use outside knowledge.
2. If the context does not contain enough information to answer, say: \
"I don't have that information in the provided documents."
3. Cite your sources using clean, human-readable references like: \
(Source: Employee Handbook, "Paid Time Off") or (Source: Product FAQ, "Pricing"). \
Use the document's display name (without file extension) and the section name or \
page number. Never show raw filenames like "Employee Handbook.md".
4. Be concise and direct. Use bullet points or numbered lists when listing \
multiple items.
5. If the user asks a follow-up, use conversation history for context but \
still only ground answers in the retrieved documents."""


def _display_name(filename: str) -> str:
    """Convert raw filename to clean display name (strip extension)."""
    return Path(filename).stem


def _build_context_block(results: list[dict]) -> str:
    """Format retrieved chunks into a context block for the prompt."""
    parts = []
    for i, r in enumerate(results, 1):
        source = _display_name(r["metadata"].get("source", "unknown"))
        page = r["metadata"].get("page", "")
        section = r["metadata"].get("section", "")
        location = f"Page {page}" if page else f'"{section}"'
        parts.append(
            f"--- Document {i} [Source: {source}, {location}] ---\n{r['text']}"
        )
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask(
    question: str,
    history: list[dict] | None = None,
    n_results: int = 5,
) -> tuple[str, list[dict]]:
    """
    Ask a question against the RAG knowledge base.

    Args:
        question: The user's question.
        history: Conversation history (list of {"role", "content"} dicts).
        n_results: Number of chunks to retrieve.

    Returns:
        (answer_text, updated_history)
    """
    if history is None:
        history = []

    # Retrieve relevant chunks
    results = search(question, n_results=n_results)
    context_block = _build_context_block(results)

    # Build the user message with context
    user_message = (
        f"Context documents:\n\n{context_block}\n\n"
        f"---\n\nQuestion: {question}"
    )

    # Append to history
    history.append({"role": "user", "content": user_message})

    # Trim history to last MAX_HISTORY exchanges (pairs of user+assistant)
    max_messages = MAX_HISTORY * 2
    if len(history) > max_messages:
        history = history[-max_messages:]

    # Call Claude
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history,
    )

    answer = response.content[0].text

    # Append assistant response to history
    history.append({"role": "assistant", "content": answer})

    return answer, history


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("RAG Chatbot (Sprint 3)")
    print("Type your question, or 'quit' to exit.")
    print("=" * 50)

    history = []

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nSearching documents...")
        answer, history = ask(question, history)
        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    main()
