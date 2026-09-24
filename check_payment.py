"""
Measure criterion 5: do payment questions get an answer that mentions cash?

Every QUESTIONS/OUT_OF_SCOPE question is already spoken for by criteria 1-3,
so this asks five new town-specific payment questions - one per town used in
QUESTIONS - through the same retrieval -> gate -> generate pipeline as
run_eval.py, three times each with caching off, and checks whether "cash"
appears in the answer.

Run: python check_payment.py
"""

import config
from store import search
import gate
from generate import answer_from_chunks

RUNS = 3

PAYMENT_QUESTIONS = [
    "How do you pay for things in Elder Ness?",
    "How do you pay for things in Halden Bay?",
    "How do you pay for things in Kestrelford?",
    "How do you pay for things in Pellew Sands?",
    "How do you pay for things in Marchwood?",
]


def main():
    per_question_hits = []

    for question in PAYMENT_QUESTIONS:
        print(f"\n{question}")
        results = search(question, corpus=config.CORPUS)
        decision = gate.check(results)

        hits = 0
        for run in range(1, RUNS + 1):
            if not decision.passed:
                answer = gate.REFUSAL
            else:
                answer = answer_from_chunks(question, results, cache=False)
            mentions_cash = "cash" in answer.lower()
            hits += mentions_cash
            mark = "cash" if mentions_cash else "no cash"
            print(f"  run {run}: {mark}")
            print(f"    {answer}")

        per_question_hits.append(hits == RUNS)

    total = sum(per_question_hits)
    print(f"\n-> {total} of {len(PAYMENT_QUESTIONS)} questions mentioned cash in every run")


if __name__ == "__main__":
    main()
