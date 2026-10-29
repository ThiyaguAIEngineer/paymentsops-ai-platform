"""Immutable source document models; no retrieval or generation concerns."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class KnowledgeSection:
    section_id: str
    heading: str
    content: str  # Cleaned Markdown including heading and explicit ID marker.


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    title: str
    version: str
    effective_date: date
    document_type: str
    source_path: str
    raw_text: str  # Original UTF-8 text, including front matter and line endings.
    text: str  # Cleaned Markdown body, including title and introductory material.
    sections: tuple[KnowledgeSection, ...]


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    document_title: str
    document_version: str
    effective_date: date
    document_type: str
    source_path: str
    section_id: str
    section_heading: str
    chunk_index: int  # Zero-based within the section.
    content: str
