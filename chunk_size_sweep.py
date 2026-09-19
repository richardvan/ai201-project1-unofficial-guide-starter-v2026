"""
Compare retrieval across (CHUNK_SIZE, CHUNK_OVERLAP) pairs.

For each pair in PARAM_PAIRS, rebuilds the corpus into its own index variant
sized to that pair, then runs every question in questions.QUESTIONS through
retrieval and the relevance gate. Writes one Markdown file per pair into
my_runs/, with the full, untruncated text of every retrieved chunk in a
fenced block you can copy straight into your README or into criteria.md.
Each chunk block is labeled with the params that produced it, so it stays
traceable even if you copy it out on its own.

Retrieval only — no calls to generate.py, so this costs no API quota and
needs no GEMINI_API_KEY.

Run: python chunk_size_sweep.py
Edit PARAM_PAIRS below to try other combinations.
"""

import config
from ingest import load_documents
from chunker import fallback_split
from store import build_index, search
import gate
from questions import answered

PARAM_PAIRS = [(800, 120), (400, 60), (300, 45), (200, 30)]

OUT_DIR = config.ROOT / "my_runs"


def variant_name(chunk_size: int, overlap: int) -> str:
    return f"cs{chunk_size}_ov{overlap}"


def run_pair(chunk_size: int, overlap: int, corpus: str, documents) -> None:
    variant = variant_name(chunk_size, overlap)
    chunks = fallback_split(documents, chunk_size=chunk_size, overlap=overlap)
    build_index(chunks, corpus=corpus, variant=variant)

    lines = [
        f"# Chunk sweep — CHUNK_SIZE={chunk_size}, CHUNK_OVERLAP={overlap}",
        "",
        f"corpus: `{corpus}`  |  chunks produced: {len(chunks)}  |  "
        f"chunker: `chunker.py::fallback_split`",
        "",
    ]

    questions = answered()
    for q in questions:
        question = q["question"]
        results = search(question, top_k=config.TOP_K, corpus=corpus, variant=variant)
        decision = gate.check(results)

        lines.append(f"## {question}")
        lines.append(f"expects: {q.get('expects', '')}")
        lines.append("")
        lines.append(f"[GATE {variant}] {decision.explanation}")
        lines.append("")

        for i, r in enumerate(results, 1):
            lines.append(
                f"[CHUNK {i} | {variant} | distance={r.distance:.4f} "
                f"| source={r.label}]"
            )
            lines.append("```")
            lines.append(r.text)
            lines.append("```")
            lines.append("")

    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"{variant}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}  ({len(chunks)} chunks, {len(questions)} questions)")


def main() -> None:
    corpus = config.CORPUS
    documents = load_documents(corpus)
    for chunk_size, overlap in PARAM_PAIRS:
        run_pair(chunk_size, overlap, corpus, documents)


if __name__ == "__main__":
    main()
