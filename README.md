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
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

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
