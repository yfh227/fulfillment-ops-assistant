"""Structure-aware chunking for the Meridian reference documents.

Splits on markdown structure — headings and sections — rather than a fixed
character count. A size cap applies only as a fallback, when a single section
has no internal headings to split on.

Every chunk carries its source filename in metadata. This is load-bearing: the
system prompt's citation rule requires the model to cite the .md filename, and
a chunk that reaches the model without its source cannot be cited correctly.

No embeddings, no vector store, no retrieval here. Chunking only.
"""

import re
from dataclasses import dataclass, field

# Fallback cap, applied only inside a section that has no further headings to
# split on. Roughly 1,100 tokens at the corpus's ~3.5 chars/token.
MAX_CHARS = 4000

# Below this a chunk is merged into its neighbour rather than left as a stub.
MIN_CHARS = 300

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
TABLE_RE = re.compile(r"^\s*\|")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
FENCE_RE = re.compile(r"^\s*```")


@dataclass
class Block:
    """An atomic unit of markdown. Never split internally."""

    kind: str  # heading | table | list | para | fence | blockquote
    text: str
    level: int = 0  # heading level, 0 for non-headings


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)

    @property
    def source(self) -> str:
        return self.metadata["source"]

    def __len__(self) -> int:
        return len(self.text)


def parse_blocks(text: str) -> list[Block]:
    """Break markdown into atomic blocks.

    Tables, lists, and fenced code are kept whole — these are the structures
    that lose their meaning when split. A table separated from its header row
    is unreadable; a numbered step separated from its sub-detail is worse than
    unreadable, because it looks complete.
    """
    lines = text.splitlines()
    blocks: list[Block] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        m = HEADING_RE.match(line)
        if m:
            blocks.append(Block("heading", line, len(m.group(1))))
            i += 1
            continue

        if FENCE_RE.match(line):
            buf = [line]
            i += 1
            while i < len(lines):
                buf.append(lines[i])
                if FENCE_RE.match(lines[i]):
                    i += 1
                    break
                i += 1
            blocks.append(Block("fence", "\n".join(buf)))
            continue

        if TABLE_RE.match(line):
            buf = []
            while i < len(lines) and (TABLE_RE.match(lines[i])
                                      or (buf and not lines[i].strip())):
                if not lines[i].strip():
                    # blank line ends the table unless the next line resumes it
                    if not (i + 1 < len(lines) and TABLE_RE.match(lines[i + 1])):
                        break
                buf.append(lines[i])
                i += 1
            blocks.append(Block("table", "\n".join(buf).rstrip()))
            continue

        if LIST_RE.match(line):
            # A list runs until a blank line followed by something that is not
            # a list item or an indented continuation. Sub-details indented
            # under an item stay with the item.
            buf = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    after = lines[i + 1] if i + 1 < len(lines) else ""
                    if LIST_RE.match(after) or after.startswith(("  ", "\t")):
                        buf.append(nxt)
                        i += 1
                        continue
                    break
                if (LIST_RE.match(nxt) or nxt.startswith(("  ", "\t"))
                        or TABLE_RE.match(nxt)):
                    buf.append(nxt)
                    i += 1
                    continue
                break
            blocks.append(Block("list", "\n".join(buf).rstrip()))
            continue

        if line.lstrip().startswith(">"):
            buf = [line]
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(lines[i])
                i += 1
            blocks.append(Block("blockquote", "\n".join(buf)))
            continue

        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            if (HEADING_RE.match(lines[i]) or TABLE_RE.match(lines[i])
                    or FENCE_RE.match(lines[i])):
                break
            buf.append(lines[i])
            i += 1
        blocks.append(Block("para", "\n".join(buf)))

    return blocks


def _doc_title(blocks: list[Block]) -> str:
    for b in blocks:
        if b.kind == "heading" and b.level == 1:
            return b.text.lstrip("# ").strip()
    return ""


def _section_path(stack: list[tuple[int, str]]) -> str:
    return " > ".join(t for _, t in stack)


def _chunk_header(filename: str, title: str, path: str) -> str:
    """Breadcrumb prefixed to every chunk so it is self-describing.

    Carries the source filename in the text as well as in metadata — a chunk
    that reaches the model without its filename cannot satisfy the citation
    rule, and metadata alone does not survive being concatenated into a prompt.
    """
    header = f"[{filename}]"
    if title:
        header += f" {title}"
    if path:
        header += f" — {path}"
    return header


def chunk_document(filename: str, text: str,
                   max_chars: int = MAX_CHARS,
                   min_chars: int = MIN_CHARS) -> list[Chunk]:
    """Split one document into chunks, each tagged with its source filename."""
    blocks = parse_blocks(text)
    title = _doc_title(blocks)

    # Group blocks into sections, opening a new section at any heading of
    # level 2 or 3. Level 1 is the document title; level 4+ stays inline.
    sections: list[dict] = []
    stack: list[tuple[int, str]] = []
    current = {"path": "", "blocks": []}

    for b in blocks:
        if b.kind == "heading" and b.level in (2, 3):
            if current["blocks"]:
                sections.append(current)
            while stack and stack[-1][0] >= b.level:
                stack.pop()
            stack.append((b.level, b.text.lstrip("# ").strip()))
            current = {"path": _section_path(stack), "blocks": [b]}
        else:
            if b.kind == "heading" and b.level == 1:
                stack.clear()
            current["blocks"].append(b)
    if current["blocks"]:
        sections.append(current)

    # A heading immediately followed by a deeper heading yields a section with
    # nothing in it but that heading. Carry those forward onto the next
    # section so the heading leads its own content. Folding them backward
    # instead would leave the previous chunk ending on a heading — a step
    # title severed from its step.
    carried: list[Block] = []
    folded: list[dict] = []
    for sec in sections:
        if all(b.kind == "heading" for b in sec["blocks"]):
            carried.extend(sec["blocks"])
            continue
        if carried:
            sec = {"path": sec["path"], "blocks": carried + sec["blocks"]}
            carried = []
        folded.append(sec)
    if carried:
        if folded:
            folded[-1]["blocks"].extend(carried)
        else:
            folded.append({"path": "", "blocks": carried})
    sections = folded

    # Assemble chunks. A section becomes one chunk unless it exceeds the cap,
    # in which case it splits at block boundaries — never inside a block, and
    # never leaving a heading as the final block of a chunk.
    raw: list[dict] = []
    for sec in sections:
        # Each finished chunk is prefixed with "[file] Title — Section", so
        # that prefix comes out of the budget. Otherwise the cap governs the
        # body while the emitted chunk quietly exceeds it.
        header_len = len(_chunk_header(filename, title, sec["path"])) + 2
        budget = max(500, max_chars - header_len)
        buf: list[Block] = []
        size = 0
        for b in sec["blocks"]:
            blen = len(b.text) + 2
            if buf and size + blen > budget:
                # Any headings trailing this chunk belong with what follows.
                moved: list[Block] = []
                while buf and buf[-1].kind == "heading":
                    moved.insert(0, buf.pop())
                if buf:
                    raw.append({"path": sec["path"], "blocks": list(buf)})
                buf = moved + [b]
                size = sum(len(x.text) + 2 for x in buf)
            else:
                buf.append(b)
                size += blen
        if buf:
            raw.append({"path": sec["path"], "blocks": buf})

    # Merge undersized chunks forward, but only within the same section, so a
    # merge never silently joins unrelated material.
    merged: list[dict] = []
    for r in raw:
        body = "\n\n".join(b.text for b in r["blocks"]).strip()
        # Merge an undersized chunk backward only within the same section, so
        # a merge never joins unrelated material. Heading-only chunks are
        # already folded forward above and must never be merged backward.
        if (merged and len(body) < min_chars
                and merged[-1]["path"] == r["path"]
                and not all(b.kind == "heading" for b in r["blocks"])):
            merged[-1]["blocks"].extend(r["blocks"])
            continue
        merged.append(r)

    chunks: list[Chunk] = []
    for idx, r in enumerate(merged):
        body = "\n\n".join(b.text for b in r["blocks"]).strip()
        if not body:
            continue
        header = _chunk_header(filename, title, r["path"])
        chunks.append(Chunk(
            text=f"{header}\n\n{body}",
            metadata={
                "source": filename,          # non-negotiable, drives citation
                "doc_title": title,
                "section": r["path"],
                "chunk_index": idx,
                "block_kinds": sorted({b.kind for b in r["blocks"]}),
                "chars": len(body),
            },
        ))

    for c in chunks:
        c.metadata["chunk_total"] = len(chunks)
    return chunks


def chunk_corpus(docs: list[tuple[str, str]], **kw) -> list[Chunk]:
    """Chunk every (filename, text) pair. Order is preserved."""
    out: list[Chunk] = []
    for name, text in docs:
        out.extend(chunk_document(name, text, **kw))
    return out
