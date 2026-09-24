"""
Measure criterion 4: do retrieved chunks average 180-380 tokens?

For every question in questions.QUESTIONS, runs retrieval against the current
index (whatever CHUNK_SIZE/CHUNK_OVERLAP config.py and the index were built
with) and counts tokens in each of the top-k chunks returned. No tokenizer
dependency is assumed, so token count is approximated as chars / 4, which is
close enough for English prose to sanity-check a target this wide.

Retrieval only - no calls to generate.py, so this costs no API quota.

Run: python check_chunk_sizes.py
"""

import config
from store import search
from questions import answered

LOW, HIGH = 180, 380


def approx_tokens(text: str) -> float:
    return len(text) / 4


def main():
    items = answered()
    if not items:
        print("questions.py has no questions in it yet.")
        return

    in_range = 0
    print(f"Target: {LOW}-{HIGH} tokens (approx, chars/4)\n")

    for item in items:
        question = item["question"]
        results = search(question, corpus=config.CORPUS)
        token_counts = [approx_tokens(r.text) for r in results]
        avg = sum(token_counts) / len(token_counts)
        ok = LOW <= avg <= HIGH
        in_range += ok
        mark = "in range" if ok else "OUT OF RANGE"
        print(f"{question}")
        print(f"  chunks: {[round(t) for t in token_counts]}  avg={avg:.1f}  {mark}\n")

    print(f"-> {in_range} of {len(items)} questions had an in-range average")


if __name__ == "__main__":
    main()
