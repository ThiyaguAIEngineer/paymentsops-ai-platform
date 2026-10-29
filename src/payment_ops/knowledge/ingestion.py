"""Load the corpus's flat front matter and explicitly identified Markdown sections.

This is intentionally a parser for the existing corpus format, not general YAML
or arbitrary Markdown. Only direct .md children of the configured directory are
discovered; planning files, archives, and evaluation fixtures belong elsewhere.
"""

from datetime import date
from pathlib import Path, PurePosixPath
import re

from payment_ops.knowledge.models import KnowledgeDocument, KnowledgeSection


class IngestionError(ValueError):
    """A source file or corpus cannot be loaded without losing its structure."""


_FIELDS = {
    "document_id", "title", "version", "effective_date", "document_type", "source_path",
}
_SECTION = re.compile(r"## ([A-Z]{2}-[A-Z]+) — (\S.*)")
_REFERENCE = re.compile(r"\b(SYN-[A-Z]+(?:-[A-Z]+)*)/([A-Z]{2}-[A-Z]+)\b")


def clean_text(text: str) -> str:
    """Normalize newlines/trailing spaces; preserve paragraphs and Markdown syntax.

Two trailing spaces are a meaningful Markdown hard break, so retain exactly two
when present on a nonblank line. Do not collapse internal or blank-line spacing.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cleaned = []
    for line in lines:
        stripped = line.rstrip(" \t")
        hard_break = bool(stripped) and line.endswith("  ")
        cleaned.append(stripped + ("  " if hard_break else ""))
    return "\n".join(cleaned)


def load_document(path: Path | str) -> KnowledgeDocument:
    """Read one document without modifying it; cross-file checks occur at corpus load."""
    path = Path(path)

    def fail(message: str) -> None:
        raise IngestionError(f"{path}: {message}")

    try:
        with path.open(encoding="utf-8", newline="") as source:
            raw_text = source.read()
    except (OSError, UnicodeError) as exc:
        raise IngestionError(f"{path}: cannot read UTF-8 document: {exc}") from exc
    if not raw_text.strip():
        fail("empty document")
    lines = clean_text(raw_text).split("\n")
    if lines[0] != "---":
        fail("missing opening front-matter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail("missing closing front-matter delimiter")

    metadata = {}
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z_]+): (\S.*)", line)
        if not match:
            fail(f"malformed metadata line: {line!r}; expected key: value")
        key, value = match.groups()
        if key not in _FIELDS:
            fail(f"unknown metadata field: {key}")
        if key in metadata:
            fail(f"duplicate metadata field: {key}")
        metadata[key] = value.strip()
    missing = _FIELDS - metadata.keys()
    if missing:
        fail(f"missing required metadata: {', '.join(sorted(missing))}")
    if not re.fullmatch(r"SYN-[A-Z]+(?:-[A-Z]+)*", metadata["document_id"]):
        fail("invalid document_id")
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", metadata["version"]):
        fail("version must be a three-part numeric semantic version")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", metadata["effective_date"]):
            raise ValueError("expected YYYY-MM-DD")
        effective_date = date.fromisoformat(metadata["effective_date"])
    except ValueError:
        fail("invalid effective_date; expected a valid YYYY-MM-DD date")
    if metadata["document_type"] not in {"sop", "guide", "catalog", "runbook"}:
        fail("invalid document_type")
    source_path = PurePosixPath(metadata["source_path"])
    if (source_path.is_absolute() or ".." in source_path.parts
            or "\\" in metadata["source_path"] or ":" in metadata["source_path"]
            or source_path.name != path.name or source_path.suffix != ".md"):
        fail("source_path must be a relative POSIX Markdown path matching the filename")

    body = lines[end + 1:]
    title_positions = [i for i, line in enumerate(body) if line.startswith("# ")]
    if (len(title_positions) != 1 or not body or
            next((line for line in body if line.strip()), "") != f"# {metadata['title']}"):
        fail("body must start with one level-one heading matching title")
    starts = [i for i, line in enumerate(body) if line.startswith("## ")]
    if not starts:
        fail("document has no identified sections")
    sections = []
    seen = set()
    marker_positions = []
    for start, stop in zip(starts, [*starts[1:], len(body)], strict=True):
        match = _SECTION.fullmatch(body[start])
        if not match:
            fail(f"invalid section heading: {body[start]!r}")
        section_id, _ = match.groups()
        if section_id in seen:
            fail(f"duplicate section_id: {section_id}")
        seen.add(section_id)
        marker = next((i for i in range(start + 1, stop) if body[i].strip()), None)
        if marker is None or body[marker] != f"**section_id: {section_id}**":
            fail(f"missing or mismatched section identifier for {section_id}")
        if not any(line.strip() for line in body[marker + 1:stop]):
            fail(f"empty section content: {section_id}")
        marker_positions.append(marker)
        sections.append(KnowledgeSection(
            section_id, body[start][3:], "\n".join(body[start:stop]).strip("\n"),
        ))
    actual_markers = [i for i, line in enumerate(body) if "section_id:" in line]
    if marker_positions != actual_markers:
        fail("unexpected or malformed section identifier marker")
    return KnowledgeDocument(
        document_id=metadata["document_id"], title=metadata["title"],
        version=metadata["version"], effective_date=effective_date,
        document_type=metadata["document_type"], source_path=metadata["source_path"],
        raw_text=raw_text, text="\n".join(body).strip("\n"), sections=tuple(sections),
    )


def load_documents(directory: Path | str) -> tuple[KnowledgeDocument, ...]:
    """Load direct Markdown children in filename order; reject broken cross-references."""
    directory = Path(directory)
    if not directory.is_dir():
        raise IngestionError(f"{directory}: document directory is missing or is not a directory")
    try:
        paths = sorted(directory.glob("*.md"), key=lambda path: path.name)
    except OSError as exc:
        raise IngestionError(f"{directory}: cannot discover documents: {exc}") from exc
    if not paths:
        raise IngestionError(f"{directory}: no Markdown documents found")
    documents = []
    by_id = {}
    for path in paths:
        document = load_document(path)
        if document.document_id in by_id:
            raise IngestionError(f"{path}: duplicate document_id: {document.document_id}")
        documents.append(document)
        by_id[document.document_id] = {section.section_id for section in document.sections}
    for document in documents:
        for target, section in _REFERENCE.findall(document.text):
            if target not in by_id or section not in by_id[target]:
                raise IngestionError(
                    f"{document.source_path}: unresolved cross-reference: {target}/{section}",
                )
    return tuple(documents)
