"""Section-aware chunking without a tokenizer or external dependencies.

Target 250-450 approximate tokens, measured as ceil(characters / 4), NOT model
tokens. Greedily pack blank-line-delimited blocks up to 450; short sections stay
whole. Tables, contiguous ordered lists, fenced code, and individual paragraphs
are indivisible, even when oversized. Adjacent list blocks are kept together so
blank lines between steps cannot sever a procedure. No token overlap is added;
the section heading and ID are repeated for split chunks.

Document introductory text is prepended only to the first section's first chunk
so scope and synthetic notices are retained without inventing a section ID.
Input document and section order is preserved. No source text is rewritten.
"""

from collections.abc import Iterable
from hashlib import sha256
import json
import re

from payment_ops.knowledge.models import KnowledgeChunk, KnowledgeDocument


CHUNKER_VERSION = "structural-v1"


def approximate_tokens(text: str) -> int:
    """Return a character-based size estimate, not an exact model token count."""
    return (len(text) + 3) // 4


def _blocks(text: str) -> list[str]:
    """Keep fenced blocks and blank-line-separated ordered steps together."""
    blocks = []
    pending = []
    fence = None
    for line in text.split("\n"):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
        if not line.strip() and fence is None:
            if pending:
                blocks.append("\n".join(pending))
                pending = []
        else:
            pending.append(line)
    if pending:
        blocks.append("\n".join(pending))
    merged = []
    for block in blocks:
        is_list = bool(re.match(r"\s*\d+[.)] ", block))
        previous_list = bool(merged and re.match(r"\s*\d+[.)] ", merged[-1]))
        previous_heading = bool(merged and re.fullmatch(r"#{3,6} .+", merged[-1]))
        if merged and ((is_list and previous_list) or previous_heading):
            merged[-1] += "\n\n" + block
        else:
            merged.append(block)
    return merged


def chunk_documents(
    documents: Iterable[KnowledgeDocument], *, max_tokens: int = 450,
) -> tuple[KnowledgeChunk, ...]:
    """Chunk structured ingestion output; max_tokens is a soft structural limit.

IDs include document/version/section/index, chunker version, and a SHA-256
fingerprint of content and configuration. Identical inputs/config yield identical
IDs across processes; changed content or configuration invalidates identity.
"""
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")
    chunks = []
    ids = set()
    for document in documents:
        if not document.sections:
            raise ValueError(f"{document.document_id}: document has no sections")
        first_heading = f"## {document.sections[0].heading}"
        intro, separator, _ = document.text.partition(first_heading)
        if not separator:
            raise ValueError(f"{document.document_id}: first section missing from document text")
        for section_number, section in enumerate(document.sections):
            header = f"## {section.heading}\n\n**section_id: {section.section_id}**"
            if not section.content.startswith(header):
                raise ValueError(f"{document.document_id}/{section.section_id}: invalid section header")
            body = section.content[len(header):].strip("\n")
            if not body.strip():
                raise ValueError(f"{document.document_id}/{section.section_id}: empty section")
            prefix = intro.strip("\n") + "\n\n" if section_number == 0 and intro.strip() else ""
            current = prefix + header
            has_body = False
            contents = []
            for block in _blocks(body):
                candidate = current + "\n\n" + block
                if has_body and approximate_tokens(candidate) > max_tokens:
                    contents.append(current)
                    current = header + "\n\n" + block
                else:
                    current = candidate
                has_body = True
            contents.append(current)
            for index, content in enumerate(contents):
                fingerprint = sha256(json.dumps(
                    [CHUNKER_VERSION, max_tokens, content], ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")).hexdigest()
                chunk_id = (
                    f"{document.document_id}:{document.version}:{section.section_id}:"
                    f"{index}:{CHUNKER_VERSION}:{fingerprint}"
                )
                if chunk_id in ids:
                    raise ValueError(f"duplicate chunk_id: {chunk_id}")
                ids.add(chunk_id)
                chunks.append(KnowledgeChunk(
                    chunk_id=chunk_id, document_id=document.document_id,
                    document_title=document.title, document_version=document.version,
                    effective_date=document.effective_date, document_type=document.document_type,
                    source_path=document.source_path, section_id=section.section_id,
                    section_heading=section.heading, chunk_index=index, content=content,
                ))
    return tuple(chunks)
