"""Markdown chunking: split files into heading-scoped sections, then
sub-split any section that exceeds the embedding model's token budget."""

import re

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")


def split_into_sections(text):
    """Split markdown text into sections at H1/H2/H3 boundaries.

    Returns a list of (heading_path, body_text) tuples. heading_path is the
    " > "-joined stack of headings active at that point (e.g.
    "File Title > Section > Subsection"). Content before the first heading
    (if any) is returned with heading_path "" (rare in this KB's convention
    of always starting with an H1 title).
    """
    sections = []
    stack = []  # list of (level, text)
    body_lines = []
    has_content = False

    def flush():
        body = "\n".join(body_lines).strip()
        if body and has_content:
            heading_path = " > ".join(h for _, h in stack)
            sections.append((heading_path, body))
        body_lines.clear()

    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            flush()
            has_content = False
            level = len(m.group(1))
            heading = m.group(2).strip()
            stack = [h for h in stack if h[0] < level]
            stack.append((level, heading))
            body_lines.append(line)
        else:
            body_lines.append(line)
            if line.strip():
                has_content = True
    flush()

    return sections


def _split_paragraph_by_sentences(paragraph):
    return re.split(r"(?<=[.!?])\s+", paragraph)


def _overlap_tail(pieces, overlap_tokens, tokenizer):
    """Return the trailing pieces whose combined token count is <= overlap_tokens."""
    kept = []
    total = 0
    for piece in reversed(pieces):
        tokens = len(tokenizer.encode(piece).ids)
        if total + tokens > overlap_tokens and kept:
            break
        kept.insert(0, piece)
        total += tokens
    return kept, total


# Decoding a slice of token ids and re-encoding it can grow the token count
# slightly (e.g. boundary tokens re-merge differently, [CLS]/[SEP] handling).
# Build hard-split windows a bit under max_tokens to absorb that growth.
_HARD_SPLIT_MARGIN = 8


def _hard_split_by_tokens(text, max_tokens, overlap_tokens, tokenizer):
    """Last-resort split: slide a window over the token ids with
    overlap_tokens stride, decoding each window back to text. Guarantees no
    piece exceeds max_tokens even if the input has no paragraph/sentence
    boundaries (e.g. a dense bullet block with no blank lines or periods)."""
    ids = tokenizer.encode(text).ids
    if len(ids) <= max_tokens:
        return [text]
    effective_max = max_tokens - _HARD_SPLIT_MARGIN
    pieces = []
    step = effective_max - overlap_tokens
    for start in range(0, len(ids), step):
        window = ids[start:start + effective_max]
        pieces.append(tokenizer.decode(window))
        if start + effective_max >= len(ids):
            break
    return pieces


def _enforce_max_tokens(text, max_tokens, overlap_tokens, tokenizer):
    """Final safety net: re-check a chunk's true token count and hard-split
    it if it exceeds max_tokens. Catches cases where packing chunks by
    summing per-piece token counts doesn't match the combined text's actual
    token count (tokenization isn't perfectly additive across a join)."""
    if len(tokenizer.encode(text).ids) <= max_tokens:
        return [text]
    return _hard_split_by_tokens(text, max_tokens, overlap_tokens, tokenizer)


def split_long_section(text, max_tokens, overlap_tokens, tokenizer):
    """Greedily pack paragraphs (splitting oversized paragraphs by sentence)
    into chunks <= max_tokens, with a trailing overlap carried into the next
    chunk for context continuity."""
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    current = []
    current_tokens = 0

    def emit():
        if current:
            chunks.append("\n\n".join(current))

    for para in paragraphs:
        para_tokens = len(tokenizer.encode(para).ids)
        if para_tokens > max_tokens:
            for sent in _split_paragraph_by_sentences(para):
                sent_tokens = len(tokenizer.encode(sent).ids)
                if sent_tokens > max_tokens:
                    if current:
                        emit()
                        current, current_tokens = _overlap_tail(current, overlap_tokens, tokenizer)
                    chunks.extend(_hard_split_by_tokens(sent, max_tokens, overlap_tokens, tokenizer))
                    current, current_tokens = [], 0
                    continue
                if current_tokens + sent_tokens > max_tokens and current:
                    emit()
                    current, current_tokens = _overlap_tail(current, overlap_tokens, tokenizer)
                current.append(sent)
                current_tokens += sent_tokens
            continue

        if current_tokens + para_tokens > max_tokens and current:
            emit()
            current, current_tokens = _overlap_tail(current, overlap_tokens, tokenizer)

        current.append(para)
        current_tokens += para_tokens

    emit()
    return chunks if chunks else [text]


def chunk_markdown(text, max_tokens, overlap_tokens, tokenizer):
    """Full pipeline: heading-scoped sections, then token-budget sub-splits.

    Returns a list of (heading_path, chunk_text) tuples.
    """
    chunks = []
    for heading_path, body in split_into_sections(text):
        token_count = len(tokenizer.encode(body).ids)
        if token_count <= max_tokens:
            pieces = [body]
        else:
            pieces = split_long_section(body, max_tokens, overlap_tokens, tokenizer)
        for piece in pieces:
            for final_piece in _enforce_max_tokens(piece, max_tokens, overlap_tokens, tokenizer):
                chunks.append((heading_path, final_piece))
    return chunks
