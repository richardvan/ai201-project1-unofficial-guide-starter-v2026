# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

The Unofficial Guide is a retrieval-augmented Q&A tool built on the
`city_guides` corpus — 14 sectioned guides to towns in one fictional region
(getting there, eating, sights, seasons, accessibility). It answers specific,
single-fact questions a guidebook would actually cover — how to reach a town,
what's open when, where to eat — by retrieving the most relevant chunks and
having the model answer only from those, citing the source file. Questions the
corpus doesn't cover are refused by a relevance gate before any model call is
made, rather than answered by guesswork.

## Chunking Strategy

**Chunk size:** 400
**Overlap:** 60

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

To compare candidate `(CHUNK_SIZE, CHUNK_OVERLAP)` pairs against real chunk
content instead of guessing, `chunk_size_sweep.py` builds an index variant per
pair and saves every retrieved chunk, in full, to `my_runs/`:

```
python chunk_size_sweep.py
```

This runs the four pairs currently in `PARAM_PAIRS` — `(800, 120)`,
`(400, 60)`, `(300, 45)`, `(200, 30)` — against the 5 questions in
`questions.py`, and writes one file per pair:

```
my_runs/cs800_ov120.md
my_runs/cs400_ov60.md
my_runs/cs300_ov45.md
my_runs/cs200_ov30.md
```

Edit `PARAM_PAIRS` at the top of the file to try other combinations. No
`GEMINI_API_KEY` is needed — it's retrieval only, no model call.

**Why 400/60, out of the four pairs tested:**

The Milestone 3 test is "could someone answer a question using only this,
without reading what came before or after?" — I read every chunk in each of
the four `my_runs/` files against that test before looking at distances.
`(300, 45)` and `(200, 30)` fail it constantly: most of their chunks start or
end mid-sentence or mid-word (e.g. a Halden Bay chunk in
`my_runs/cs200_ov30.md` that opens on "o 2 and 6 to 8:30 and there is nowhere
to eat," with no readable subject). At 400 characters, most chunks hold one
complete paragraph instead of a slice of one — this matches the corpus
directly: 115 paragraphs measured across the 14 guides average 233
characters, longest 451, so a 400-char window is sized to hold a whole
paragraph rather than cut through it. `(800, 120)` also passes this
readability test, since its chunks are large enough to hold a full paragraph
too, but that's exactly its problem below.

On the numbers, `(800, 120)` is the only pair that fails outright: for "What
region hub does every train go through," its own top-ranked chunk is the
correct Marchwood intro, but merging that intro with unrelated paragraphs into
one 800-char window dilutes the embedding enough that the best distance
(0.673) misses the 0.6 gate cutoff — the system refuses to answer a question
the corpus clearly covers. `(400, 60)`, `(300, 45)`, and `(200, 30)` all pass
the gate on every one of the 5 real questions (best distances 0.452–0.479 on
that same question, see `my_runs/`).

So `(400, 60)` is the only pair of the four that both reads as complete
thoughts and passes the gate on every real question.

One honest gap this sweep didn't fix at any size: none of the four pairs
retrieve the actual answer to "what time of year is Pellew Sands mostly
closed" (`guide_pellew_sands.md`'s "Winter is bleak, largely closed") in the
top 5 — all four instead surface a decoy sentence about Givens Mill closing
in winter. That miss is identical at 800, 400, 300, and 200, so it isn't a
chunk-size problem in this range; it's a retrieval-ranking issue for a later
milestone, not a reason to pick a different size here.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `guide_elder_ness.md#0` — produced by: `chunker.py::fallback_split(chunk_size=400, overlap=60)`

```
# Elder Ness

Elder Ness is a headland with a village of 300 on it, a lighthouse, a bird observatory, and very little else. People come for one of three reasons — birds, walking, or a deliberate absence of things to do.

## Getting there

A single road in, which floods at the highest spring tides roughly six times a year for about two hours either side of high water. Tide tables are posted at the
```

**Chunk 2** — source: `guide_halden_bay.md#0` — produced by: `chunker.py::fallback_split(chunk_size=400, overlap=60)`

```
# Halden Bay

Halden Bay is a working fishing port of 8,000 that has picked up a second life as a weekend destination. The two economies sit somewhat awkwardly beside each other and the town is candid about it.

## Getting there

The coast road is the only approach and it is slow — 40 minutes for 22 miles, with the last stretch cut into the cliff. Buses run four times a day. Parking in the town it
```

**Chunk 3** — source: `guide_kestrelford.md#0` — produced by: `chunker.py::fallback_split(chunk_size=400, overlap=60)`

```
# Kestrelford

Kestrelford is a hill town of 12,000, an hour inland from Brightwater. It has been a market town since the 1200s and the street plan has not meaningfully changed since. This is charming on foot and difficult in a car.

## Getting there

No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, ever
```

**Chunk 4** — source: `guide_marchwood.md#0` — produced by: `chunker.py::fallback_split(chunk_size=400, overlap=60)`

```
# Marchwood

Marchwood is the regional hub — 180,000 people, the junction everyone changes trains at, and a city most visitors pass through rather than stop in. That is a mistake, though an understandable one, since almost nothing of interest is near the station.

## Getting there

Every railway line in the region meets here, which is the city's defining feature. Trains to Brightwater run every 40
```

**Chunk 5** — source: `guide_pellew_sands.md#0` — produced by: `chunker.py::fallback_split(chunk_size=400, overlap=60)`

```
# Pellew Sands

Pellew Sands is a Victorian seaside resort that has been through three distinct lives: fashionable, then neglected, and now something in between. The architecture is from the first period and much of the infrastructure from the second.

## Getting there

The branch line runs from the regional hub in 70 minutes, seven times a day, and the station is on the seafront, which is rare an
```

**Why these five, and why hand-picked instead of the `-n 5` stride sample:**

The first pass (`python app.py chunks -n 5`) took an evenly-spaced stride across
all 93 chunks. Two of those five happened to be a document's opening chunk and
read as complete thoughts; the other three landed mid-document and were cut
off mid-sentence or mid-heading (one chunk even ended on a bare `##`). Rather
than leave that to stride luck, these five were chosen with
`python app.py chunks --indices 29,42,49,56,63` — the global chunk-list
position of chunk `#0` for five of the nine individual town guides
(`elder_ness`, `halden_bay`, `kestrelford`, `marchwood`, `pellew_sands`),
found by counting each document's chunk total in order. A document's `#0`
chunk always opens with its `# Title` heading plus the full introductory
paragraph, so it reliably passes the "could someone answer using only this,
without reading what came before or after?" test at the front — though, as
with the first sample, the fixed 400-character cutoff still cuts every one of
these off mid-sentence at the tail, since `fallback_split` doesn't look for a
sentence boundary before stopping.

## Sample Answer

**Question:** how do you get to Elder Ness

**Answer:**

```
To get to Elder Ness, you take a single road in, which floods at the highest
spring tides roughly six times a year for about two hours either side of high
water (from `guide_elder_ness.md`).
```

Source: `guide_elder_ness.md` (produced by `python app.py ask "how do you get
to Elder Ness"`, best distance 0.318, cutoff 0.65 — full retrieved-chunk list
and system prompt available via `--show-prompt`).

**My relevance cutoff:** `THRESHOLD = 0.65`, up from the starter's 0.6.

I ran all 5 `QUESTIONS` and all 5 `OUT_OF_SCOPE` questions through
`python app.py retrieve "..."` against the freshly rebuilt 400/60 index and
recorded the best distance each printed. The two groups didn't just avoid
overlapping, they landed nowhere near each other: every in-corpus question's
best chunk was under 0.48, every out-of-scope question's best chunk was over
0.79 — a gap almost 0.32 wide with nothing in it. 0.65 sits close to the
middle of that gap (`(0.479 + 0.799) / 2 ≈ 0.64`), giving roughly equal margin
against a real question that retrieves worse than expected and against an
off-topic question that happens to share more vocabulary with the corpus than
these five did. The starter's default of 0.6 would have worked too — it also
falls inside the gap — but 0.65 isn't riding the edge of either group.

On top-k: `TOP_K` stayed at 5. Reading the three questions below (and the two
not shown) at `top_k=5`, the correct chunk was always in position 1–3 when it
appeared at all. The one exception — the Pellew Sands/Winter question — never
surfaces its correct chunk (`guide_pellew_sands.md#5`, the one sentence that
says "Winter is bleak, largely closed") even at `--top-k 10`; the slots that
opened up going from 5 to 10 filled with progressively less relevant chunks
instead. That's a ranking problem, not a top-k depth problem, so raising
top-k bought nothing here and would only have diluted the other four
questions with more borderline material.

| Question | In corpus? | Best distance |
|---|---|---|
| how do you get to Elder Ness | Yes | 0.318 |
| what is there is eat in Halden Bay? | Yes | 0.320 |
| what is there to see in Kestrelford | Yes | 0.383 |
| what time of the year is Pellew Sands mostly closed? | Yes | 0.416 |
| What region hub does every train go through | Yes | 0.479 |
| What is the capital of Mongolia? | No | 0.799 |
| How do I write a for loop in Rust? | No | 0.828 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.839 |
| How do I change the oil in a diesel engine? | No | 0.890 |
| Who won the 1994 World Cup? | No | 0.903 |

## How I Used AI

**1.** I asked Claude to build a permanent tool (`chunk_size_sweep.py`) that
reruns my five test questions against four `(CHUNK_SIZE, CHUNK_OVERLAP)`
pairs — (800,120), (400,60), (300,45), (200,30) — each built as its own
Chroma index variant, and save the full, untruncated retrieved chunks for
every question into one Markdown file per pair under `my_runs/`, with each
chunk block labeled by the parameters that produced it so I can copy specific
chunks out to compare against other configs. Three of the four pairs
technically passed the gate, so the numeric output alone didn't decide it — I
read every chunk in each `my_runs/` file myself and ruled out 300/45 and
200/30 because their chunks kept starting or ending mid-sentence, which the
tool doesn't measure automatically. I picked 400/60.

**2.** For Milestone 4, I asked Claude whether raising `top_k` would fix a
known miss — the answer to "what time of year is Pellew Sands mostly closed?"
never showed up in the top 5 retrieved chunks. It ran the same query at
`--top-k 10` instead of just asserting an answer, and the correct chunk still
didn't appear — the extra slots filled with progressively less relevant
material instead. That result is what kept me from bumping `TOP_K` up "to be
safe"; I left it at 5 and wrote the miss down as a ranking issue instead.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 3/5 | 3/5 | 3/5 | MISSED |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. My retreived chunk sizes averages between 180 to 380 tokens. | 5 of 5 | 0/5 | 0/5 | 0/5 | MISSED |
| 5. When a question is asked about payment method accepted, 5 out of 5 answers should mention cash. | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |

Criterion 1 is retrieval, not the generated answer, so it's judged by whether
one of the top-5 retrieved chunks contains the literal answer, not by whether
`scorer.py` passed the final answer. Same 5 questions, checked against
`my_runs/cs400_ov60.md` (top_k=5, current 400/60 chunking) and the source
documents in `corpora/city_guides/documents/`:

| Question | Answer in corpus | Retrieved? |
|---|---|---|
| how do you get to Elder Ness | "single road in, floods at highest spring tides... about two hours" (`guide_elder_ness.md`) | ✅ chunk 1, distance 0.318 |
| what is there is eat in Halden Bay? | "harbour restaurants buy directly from boats that land in the early morning" (`guide_eating.md`) | ✅ chunk 2, distance 0.357 |
| what is there to see in Kestrelford | "Everything is within a ten-minute walk of the market square" (`guide_kestrelford.md`) | ❌ not in top 5 — chunk 1 is the doc's opening ("Getting there") chunk; the market-square sentence is a later chunk that never surfaces |
| what time of the year is Pellew Sands mostly closed? | "Winter is bleak, largely closed" (`guide_pellew_sands.md`) | ❌ not in top 5 — same failure mode: opening chunk (`#0`) and a later chunk (`#3`) win instead |
| What region hub does every train go through | "Every railway line in the region meets here" (`guide_marchwood.md`) | ✅ chunk 1, distance 0.479 |

3 of 5 against a target of 4 of 5. This is a real miss, not just the one
`criteria.md` predicted (Pellew Sands) — Kestrelford misses for the identical
reason: the fact-bearing chunk isn't the document's opening chunk, and the
opening chunk keeps beating it on similarity.

Produced by: retrieval config in `chunk_size_sweep.py` (city_guides corpus,
CHUNK_SIZE=400/CHUNK_OVERLAP=60), raw chunk dump in `my_runs/cs400_ov60.md`.
Criteria 2 and 3 evidence: `results/run_2026-09-23_1801_before.md`, produced by
`run_eval.py::main` (criterion 2 — every "Real output" entry cites a source
inline) and `run_eval.py::check_out_of_scope` (criterion 3 — "Refused 5 of 5").

**Criterion 5** — measured with a new standalone script, `check_payment.py`.
`QUESTIONS`/`OUT_OF_SCOPE` are already spoken for by criteria 1-3, so this
asks five new town-specific payment questions (one per town already used in
`QUESTIONS`) through the same retrieval → gate → `generate.py::answer_from_chunks`
pipeline as `run_eval.py`, three times each, caching off, and checks for
"cash" in the answer. Real output:

```
How do you pay for things in Elder Ness?
  run 1: cash
    Cash is still useful at markets and in smaller places, and cards are accepted almost everywhere now.

    Source: `guide_elder_ness.md`

How do you pay for things in Halden Bay?
  run 1: no cash
    I do not have enough information to answer how you pay for things in Halden Bay.

    Source: guide_halden_bay.md, guide_eating.md, guide_regional_transport.md, guide_seasons.md
  run 2: no cash
    I do not have enough information to answer how you pay for things in Halden Bay.

    Source: guide_halden_bay.md, guide_eating.md, guide_regional_transport.md, guide_seasons.md
  run 3: no cash
    I don't have enough information to answer how you pay for things in Halden Bay, as the provided documents do not mention payment methods.

How do you pay for things in Kestrelford?
  run 1: cash
    Cash is still useful at markets and in smaller places, though cards are accepted almost everywhere now.

    Source: guide_elder_ness.md

How do you pay for things in Pellew Sands?
  run 1: cash
    According to `guide_halden_bay.md`, cash is still useful at the market and smaller places, though cards are accepted almost everywhere now.

How do you pay for things in Marchwood?
  run 1: cash
    Based on the documents, cards are accepted almost everywhere now, though cash is still useful at the market and in smaller places (*guide_thornby_wells.md*).

-> 4 of 5 questions mentioned cash in every run
```

4 of 5 against a target of 5 of 5 — MISSED, but by one question, and not by
hallucination: Halden Bay's retrieved chunks don't actually contain a
cash/payment sentence for that town (its own guide's chunks are about the
harbour, parking, and fishing — the cash mention lives in `guide_eating.md`
and other towns' guides), so the model correctly refuses rather than
inventing a payment method. That's arguably the system working as intended
(grounding held) even though the criterion's specific target was missed —
the fix would be a retrieval/chunking one (surface Halden Bay's actual
payment-relevant chunk, if one exists), not a generation one. Also worth
noting: Elder Ness, Kestrelford, and Pellew Sands all answered by citing
`guide_elder_ness.md` or `guide_halden_bay.md`'s cash sentence rather than
their own town's guide — the underlying fact is a regional one repeated
in `guide_eating.md`/`guide_thornby_wells.md`, not something unique to each
town's own document, so the citation is technically correct but not always
the town-specific source you'd expect.

**Criterion 4** — measured with a new standalone script, `check_chunk_sizes.py`
(retrieval only, via `store.py::search`; token count approximated as
chars/4, since no tokenizer dependency exists in this repo). Deterministic
like criteria 1 and 3, so one pass covers all three run columns. Real output:

```
Target: 180-380 tokens (approx, chars/4)

how do you get to Elder Ness
  chunks: [100, 100, 100, 100, 91]  avg=98.0  OUT OF RANGE

what is there is eat in Halden Bay?
  chunks: [100, 100, 100, 100, 100]  avg=100.0  OUT OF RANGE

what is there to see in Kestrelford
  chunks: [100, 100, 100, 74, 100]  avg=94.8  OUT OF RANGE

what time of the year is Pellew Sands mostly closed?
  chunks: [100, 100, 6, 100, 100]  avg=81.0  OUT OF RANGE

What region hub does every train go through
  chunks: [100, 100, 100, 100, 100]  avg=100.0  OUT OF RANGE

-> 0 of 5 questions had an in-range average
```

0 of 5 against a target of 5 of 5 — MISSED, and not close. `CHUNK_SIZE = 400`
in `config.py` is measured in **characters**, and 400 characters lands around
100 tokens, not the ~280 tokens the 180-380 range assumes. The 400/60 setting
was tuned in Milestone 3 against paragraph length in characters (city_guides'
paragraphs average 233 chars), not against a token-count target — those two
goals point in different directions, and retrieval quality was the one that
won. Hitting 180-380 tokens would need `CHUNK_SIZE` closer to 700-1500
characters, which would undo that Milestone 3 decision.

### Real output

**Criterion 1** — produced by the retrieval step in `run_eval.py::run_once`
(`store.py::search`), raw dump in `my_runs/cs400_ov60.md`. The two misses,
verbatim, top chunk returned for each:

```
## what is there to see in Kestrelford
expects: market square

[CHUNK 1 | cs400_ov60 | distance=0.3831 | source=guide_kestrelford.md#0]
# Kestrelford

Kestrelford is a hill town of 12,000, an hour inland from Brightwater. It has been a market town since the 1200s and the street plan has not meaningfully changed since. This is charming on foot and difficult in a car.

## Getting there

No railway station; the line was closed in 1963 and the trackbed is now a walking route. Buses run from Brightwater roughly hourly on weekdays, ever
```

```
## what time of the year is Pellew Sands mostly closed?
expects: Winter

[CHUNK 1 | cs400_ov60 | distance=0.4162 | source=guide_pellew_sands.md#0]
# Pellew Sands

Pellew Sands is a Victorian seaside resort that has been through three distinct lives: fashionable, then neglected, and now something in between. The architecture is from the first period and much of the infrastructure from the second.

## Getting there

The branch line runs from the regional hub in 70 minutes, seven times a day, and the station is on the seafront, which is rare an
```

**Criterion 2** — produced by `run_eval.py::main` (`generate.py::answer_from_chunks`),
`results/run_2026-09-23_1801_before.md`. Every answer names a source; two
representative runs:

```
### how do you get to Elder Ness — run 1

You get to Elder Ness by a single road, which floods at the highest spring tides roughly six times a year for about two hours either side of high water (from `guide_elder_ness.md`).
```

```
### What region hub does every train go through — run 3

Every railway line in the region meets at Marchwood, making it the regional hub.

Source: `guide_marchwood.md`
```

**Criterion 3** — produced by `run_eval.py::check_out_of_scope` (`gate.py::check`),
`results/run_2026-09-23_1801_before.md`:

```
## The relevance gate on out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.65. Refused 5 of 5.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.799 | refused |
| How do I change the oil in a diesel engine? | 0.890 | refused |
| Who won the 1994 World Cup? | 0.903 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.839 | refused |
| How do I write a for loop in Rust? | 0.828 | refused |
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MISSED | Compared the run log count against the target. |
| 2 | Every answer names a source | MET | Compared the run log count against the target. |
| 3 | Gate stops out-of-corpus questions | MET | Compared the run log count against the target. |
| 4 | Chunk size averages 180-380 tokens | MISSED | Wrote a separate script to measure this, then compared its count against the target. |
| 5 | Payment questions mention cash | MISSED | Wrote a separate script to measure this, then compared its count against the target. |

## Diagnoses

**Criterion 1 — Kestrelford ("what is there to see")**
**Stage: retrieval.** The chunk that actually contains "market square"
(`guide_kestrelford.md#3`) doesn't even place in the top 20 results for this
query — I checked. Instead, the document's own opening chunk (`#0`, generic
town description) ranks first at distance 0.383, and the next four slots go
to thematically-adjacent chunks from *other* documents (`guide_seasons.md`,
`guide_accessibility.md`). The embedding favors broad topical similarity over
the chunk that names the specific sight.

**Criterion 1 — Pellew Sands ("what time of year is mostly closed")**
**Stage: retrieval.** The "Winter is bleak, largely closed" sentence lives in
`guide_pellew_sands.md#5`, which ranks 18th of 20 at distance 0.626 — barely
inside a top-20 window, nowhere near top-5. I'd already tested this at
`top_k=10` in Milestone 4 and it still didn't surface; checking to rank 20
now confirms it isn't a top_k tuning problem, it's a hard ranking loss.

**Criterion 5 — Halden Bay ("how do you pay")**
**Stage: retrieval**, same mechanism. `guide_halden_bay.md`'s own cash
sentence (`#5`) does exist and does get embedded reasonably (distance
0.607) — but it ranks 11th, pushed out of `top_k=5` by the document's
opening chunk (0.441) and two other documents' loosely-related chunks about
eating and transport (0.442, 0.483). The model then correctly refused rather
than hallucinating, which is why this looked like a generation problem at
first but isn't one.

**Pattern:** all three misses share one mechanism, not three separate ones —
a chunk containing a specific fact consistently loses the similarity race to
(a) that document's own broad, generic opening chunk, and (b) other
documents' chunks that are topically adjacent but don't contain the answer.
`top_k=5` isn't generous enough to reach past that, and for Kestrelford even
`top_k=20` wasn't. This points at retrieval ranking (the embedding model /
similarity metric), not at chunking or a `top_k` tuning issue.

**Criterion 4 — chunk size**
**Stage: chunking**, a different mechanism entirely. `CHUNK_SIZE=400` in
`config.py` is a character count, tuned in Milestone 3 against paragraph
length in characters (city_guides paragraphs average 233 chars). But
criterion 4's target (180-380 tokens) is a token count, and 400 characters
of this corpus's prose measures out to roughly 100 tokens — nowhere close.
This isn't a ranking or embedding issue at all; the chunks are simply sized
on the wrong unit for what the criterion asks.

## The Improvement

**What I changed:** Replaced `chunker.py::split_documents`'s body — it used
to just call `fallback_split` (fixed 400/60-character windows). Now it
splits on whole `## ` section boundaries (never mid-sentence), merges
consecutive short sections up to ~1500 characters so chunks land near
criterion 4's token target, and prepends the document's `# Title` to every
chunk.

**Why I picked it:** Directly targets the mechanism from Diagnoses — a fact
chunk losing to a document's own generic opening chunk, because only that
opening chunk still contained the document's title after a fixed-window
split stripped it out of every later piece.

### Run Log — After

`python run_eval.py --label after` → `results/run_2026-09-23_1847_after.md`;
criterion 4 via `check_chunk_sizes.py`; criterion 5 via `check_payment.py`.
Same index rebuilt with the new `split_documents`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk size averages 180-380 tokens | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Payment questions mention cash | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Real output — the two questions that flipped, and the one that broke:

```
### what is there to see in Kestrelford — run 1
Based on the provided documents, what there is to see in Kestrelford includes:
- The market square on a Saturday morning, which has run continuously since the 1400s (guide_kestrelford.md).
- The parish church, which features a 13th-century tower you can climb for £2 (guide_kestrelford.md).
- The old trackbed walk, which runs six miles to the next village along an easy gradient (guide_kestrelford.md).
```

```
### what time of the year is Pellew Sands mostly closed? — run 1
According to `guide_pellew_sands.md`, winter is the time of year when Pellew Sands is largely closed.
```

```
### What region hub does every train go through — run 1
Best distance: 0.7098 (refused by the gate)
I don't have enough information about that.
```

**Did it help?** Mostly, but it broke something else. Criteria 1, 4, and 5
all flipped from MISSED to MET — the merged, title-prefixed chunks are
exactly what surfaced Kestrelford's market square and Pellew Sands' winter
closure in the top 5, fixing the two questions Diagnoses named. But
criterion 2 flipped from MET (5/5) to MISSED (4/5): "What region hub does
every train go through" used to pass easily (distance 0.479) because its
answer sat alone in a small chunk; now that chunk is merged with two
unrelated sections ("Getting around", "Eat and drink"), and the extra text
pulls its distance to 0.725 — over the 0.65 gate threshold — so a real
in-corpus question now gets refused outright, with no source to cite. The
fact is still in the retrieved chunk (confirmed directly), so the miss isn't
retrieval failing to find it, it's a side effect of MAX_CHARS=1500 letting
enough unrelated material into one chunk to tip a previously-easy pass over
the gate's cutoff. Net effect: a real improvement, not a wash — before, two
questions failed outright (Kestrelford, Pellew Sands); after, only one does
(region hub) — but it's a genuine new regression, not a clean win, and worth
fixing before calling this done (see What's Still Broken).

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
