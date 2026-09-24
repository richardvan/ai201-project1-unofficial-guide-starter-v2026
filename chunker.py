"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# Milestone 4 tuning: merge whole "## " sections up to MAX_CHARS before
# starting a new chunk, so a chunk is never smaller than MIN_CHARS unless
# it's the last one in the document. Chosen to land retrieved chunks in
# criterion 4's 180-380 token range (roughly 720-1520 chars at ~4 chars/token
# for this corpus's prose) while never cutting a section in half.
MIN_CHARS = 700
MAX_CHARS = 1500


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _title(text: str) -> str:
    """The document's '# Heading' line, or '' if it doesn't have one."""
    first_line = text.split("\n", 1)[0]
    return first_line[2:].strip() if first_line.startswith("# ") else ""


def _sections(text: str) -> list[str]:
    """Split a document into its '## ' sections, dropping the title line."""
    if text.startswith("# "):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    parts = re.split(r"\n(?=## )", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _merge_sections(sections: list[str], min_chars: int, max_chars: int) -> list[str]:
    """
    Greedily pack whole sections into chunks, never splitting one in half.

    Keeps adding sections to the current chunk while it stays under
    max_chars. A section bigger than max_chars on its own still becomes its
    own chunk rather than being cut mid-sentence.
    """
    merged: list[str] = []
    current = ""
    for section in sections:
        candidate = f"{current}\n\n{section}" if current else section
        if current and len(candidate) > max_chars and len(current) >= min_chars:
            merged.append(current)
            current = section
        else:
            current = candidate
    if current:
        merged.append(current)
    return merged


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split on '## ' section boundaries instead of a fixed character count.

    Milestone 3's `fallback_split` cuts mid-sentence and mid-word (its own
    windows overlap by character count, not by meaning), and it also strips
    a section's identity: only chunk #0 of a document contains that
    document's own title, since the title only appears once at the top of
    the file. That's why fixed-window chunks compete poorly against a
    document's own opening chunk in retrieval — the opening chunk is the
    only one that still says which town it's about.

    This version splits on whole '## ' sections (never mid-sentence), merges
    consecutive short sections up to MAX_CHARS so chunks land near
    criterion 4's token target, and prepends the document's title to every
    chunk so none of them lose their subject.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        title = _title(doc.text)
        sections = _sections(doc.text)
        if not sections:
            continue

        for index, body in enumerate(_merge_sections(sections, MIN_CHARS, MAX_CHARS)):
            text = f"# {title}\n\n{body}" if title else body
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
