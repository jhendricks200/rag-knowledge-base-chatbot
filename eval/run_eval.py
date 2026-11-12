"""
Evaluation harness for the RAG chatbot.

Runs every question in eval/questions.jsonl through the real pipeline
(src/embed.py search + src/query.py ask) and scores two things:

1. Retrieval: did the chunk that holds the answer (expected document AND
   section) come back in the top 5 results? Reports hit rate@1, @5 and MRR.
2. Answers (needs ANTHROPIC_API_KEY): does Claude's answer contain the
   expected facts, cite the right document, and refuse questions the
   documents can't answer?

The index is built in a separate folder (eval/.chroma_eval) from docs/ only,
so files you uploaded through the chat UI don't change the scores.

Usage:
    python eval/run_eval.py                  # retrieval + answers
    python eval/run_eval.py --retrieval-only # no API key needed
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = ROOT / "eval"
sys.path.insert(0, str(ROOT / "src"))

import embed  # noqa: E402
from ingest import get_chunks  # noqa: E402

# Isolated index so uploads in the main chroma_db don't affect results
embed.CHROMA_PATH = str(EVAL_DIR / ".chroma_eval")

REFUSAL_PHRASE = "don't have that information"
TOP_K = 5


def load_questions(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def normalize(text: str) -> str:
    return text.lower().replace(",", "").replace("’", "'")


def facts_found(answer: str, must_include: list[list[str]]) -> bool:
    """Every group must have at least one alternative present in the answer."""
    a = normalize(answer)
    return all(any(normalize(alt) in a for alt in group) for group in must_include)


def retrieval_rank(results: list[dict], source: str, section: str) -> int | None:
    """1-based rank of the first chunk from the expected source+section."""
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        if meta.get("source") == source and meta.get("section") == section:
            return i
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--questions", default=str(EVAL_DIR / "questions.jsonl"))
    parser.add_argument("--out", default=str(EVAL_DIR / "results" / "latest.json"))
    args = parser.parse_args()

    questions = load_questions(Path(args.questions))

    print("Building eval index from docs/ ...")
    added = embed.add_chunks(get_chunks(str(ROOT / "docs")))
    print(f"  {added} new chunks, {embed.collection_stats()['total_chunks']} total\n")

    run_answers = not args.retrieval_only
    if run_answers:
        # Either an API key (local .env) or Workload Identity Federation
        # (GitHub Actions OIDC, no stored secret) works; the SDK reads both.
        has_creds = lambda: os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_FEDERATION_RULE_ID")
        if not has_creds():
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
        if not has_creds():
            sys.exit("No Claude credentials. Add ANTHROPIC_API_KEY to .env or use --retrieval-only.")
        import query
        model = query.MODEL

    rows = []
    for q in questions:
        answerable = q.get("answerable", True)
        row = {"id": q["id"], "question": q["question"], "answerable": answerable}

        results = embed.search(q["question"], n_results=TOP_K)
        if answerable:
            rank = retrieval_rank(results, q["expected_source"], q["expected_section"])
            row["retrieval_rank"] = rank
            row["source_in_top5"] = any(
                r["metadata"].get("source") == q["expected_source"] for r in results
            )

        if run_answers:
            answer, _ = query.ask(q["question"], history=[])
            row["answer"] = answer
            refused = REFUSAL_PHRASE in normalize(answer)
            row["refused"] = refused
            if answerable:
                row["facts_correct"] = facts_found(answer, q["must_include"])
                doc_name = Path(q["expected_source"]).stem.lower()
                row["cites_source"] = doc_name in answer.lower()
                row["correct"] = row["facts_correct"] and not refused
            else:
                row["correct"] = refused
            time.sleep(0.5)

        status = []
        if answerable:
            r = row["retrieval_rank"]
            status.append(f"retrieval={'#' + str(r) if r else 'MISS'}")
        if run_answers:
            status.append("answer=" + ("PASS" if row["correct"] else "FAIL"))
        print(f"{q['id']}  {' '.join(status):28}  {q['question']}")
        rows.append(row)

    # ---- Summary ----
    ans = [r for r in rows if r["answerable"]]
    unans = [r for r in rows if not r["answerable"]]
    ranks = [r["retrieval_rank"] for r in ans]
    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "questions": len(rows),
        "answerable": len(ans),
        "unanswerable": len(unans),
        "retrieval": {
            "hit_rate_at_1": sum(1 for k in ranks if k == 1) / len(ans),
            "hit_rate_at_5": sum(1 for k in ranks if k) / len(ans),
            "mrr": sum(1 / k for k in ranks if k) / len(ans),
            "right_document_at_5": sum(r["source_in_top5"] for r in ans) / len(ans),
        },
    }
    if run_answers:
        summary["model"] = model
        summary["answers"] = {
            "answer_accuracy": sum(r["correct"] for r in ans) / len(ans),
            "citation_rate": sum(r["cites_source"] for r in ans) / len(ans),
            "refusal_accuracy": sum(r["correct"] for r in unans) / len(unans) if unans else None,
            "false_refusals": sum(r["refused"] for r in ans),
            "overall_accuracy": sum(r["correct"] for r in rows) / len(rows),
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "results": rows}, indent=2))

    print("\n" + "=" * 60)
    rt = summary["retrieval"]
    print(f"Retrieval  hit@1 {rt['hit_rate_at_1']:.0%}  hit@5 {rt['hit_rate_at_5']:.0%}  "
          f"MRR {rt['mrr']:.2f}  right doc@5 {rt['right_document_at_5']:.0%}")
    if run_answers:
        a = summary["answers"]
        print(f"Answers    accuracy {a['answer_accuracy']:.0%}  citations {a['citation_rate']:.0%}  "
              f"refusals {a['refusal_accuracy']:.0%}  false refusals {a['false_refusals']}")
        print(f"Overall    {a['overall_accuracy']:.0%} of {len(rows)} questions correct")
    print(f"\nFull results: {out}")


if __name__ == "__main__":
    main()
