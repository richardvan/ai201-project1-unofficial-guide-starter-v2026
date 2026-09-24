# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

One of my five questions ("what time of the year is Pellew Sands mostly
closed?") has its answer in a single sentence — "Winter is bleak, largely
closed" — in `guide_pellew_sands.md`'s 6th chunk (`#5`). In Milestone 4
testing, that specific chunk never appeared in the top 5 results, and raising
`top_k` to 10 didn't surface it either; the top hit is always the document's
opening chunk, which is topically close but doesn't contain the answer. That's
the one I expect to miss, which is why the target is 4 of 5 and not 5 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

Citation here isn't left to the model's judgment: `app.py::ask_pipeline`
builds `outcome["sources"]` directly from the retrieved chunks' metadata
(`Result.source`) regardless of what the model's text says, and the model is
separately instructed by `GROUNDING_INSTRUCTION` in `generate.py` to name the
file it used. A question only reaches the model at all once the relevance gate
has passed, which means real chunk metadata always exists to cite by that
point. Since the sources come from code, not model compliance, 5 of 5 is a
target I can actually expect to hit rather than one I'm hoping for.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

Clean gap, no overlap. In Milestone 4 I ran all 5 `QUESTIONS` and all 5
`OUT_OF_SCOPE` questions through retrieval: every in-corpus question's best
chunk distance was under 0.48 (range 0.318–0.479), and every out-of-scope
question's best distance was over 0.79 (range 0.799–0.903) — almost 0.32 of
daylight between the two groups, with `THRESHOLD = 0.65` set near the middle
of it. Given how wide that gap was, I'd expect all 5 out-of-scope questions to
be refused reliably. I'm keeping the target at 4 of 5 rather than 5 of 5 as a
small buffer against phrasing variation in future questions, not because I
observed a specific failure — see README.md's "My relevance cutoff" section
for the full table.

---

## 4. Something about your chunks


My retreived chunk sizes averages between 180 to 380 tokens.
<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->



**Why this target:**
I picked this range because from the slides, ~280 tokens was specified as the "Just right" value, I wanted there to be flexible lower and upper value so value that fits in this range will be valid



---

## 5. Your choice

When a question is asked about payment method accepted, 5 out of 5 answers should mention cash.
<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->



**Why this target:**
I picked 5 out of 5 because all documents for specific cities mentioned that cash is still useful.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
