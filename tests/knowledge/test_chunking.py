"""Structural boundaries, source preservation, and stable chunk identity."""

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import re

import pytest

from payment_ops.knowledge.chunking import approximate_tokens, chunk_documents
from payment_ops.knowledge.ingestion import load_documents


CORPUS = Path(__file__).resolve().parents[2] / "data/knowledge/documents"


@pytest.fixture
def documents():
    return load_documents(CORPUS)


def fixture_document(documents, body):
    document = documents[0]
    section = document.sections[0]
    header = f"## {section.heading}\n\n**section_id: {section.section_id}**"
    section = replace(section, content=header + "\n\n" + body)
    return replace(document, text=section.content, sections=(section,))


def test_corpus_metadata_order_and_identity(documents):
    chunks = chunk_documents(documents)
    assert chunks == chunk_documents(documents)
    assert len({c.chunk_id for c in chunks}) == len(chunks)
    assert {c.document_id for c in chunks} == {d.document_id for d in documents}
    expected_order = [(d.document_id, s.section_id) for d in documents for s in d.sections]
    actual_order = list(dict.fromkeys((c.document_id, c.section_id) for c in chunks))
    assert actual_order == expected_order
    for d in documents:
        for s in d.sections:
            group = [c for c in chunks if (c.document_id, c.section_id) == (d.document_id, s.section_id)]
            assert [c.chunk_index for c in group] == list(range(len(group)))
            for c in group:
                assert (c.document_title, c.document_version, c.effective_date,
                        c.document_type, c.source_path, c.section_heading) == (
                    d.title, d.version, d.effective_date, d.document_type, d.source_path, s.heading,
                )
                assert f"**section_id: {s.section_id}**" in c.content
                assert f"{d.document_id}:{d.version}:{s.section_id}:{c.chunk_index}:" in c.chunk_id
    with pytest.raises(FrozenInstanceError):
        chunks[0].content = "changed"


def test_all_substantive_content_preserved_in_order(documents):
    before = {p: p.read_bytes() for p in CORPUS.glob("*.md")}
    chunks = chunk_documents(documents)
    for d in documents:
        # Remove only repeated section context and compare all remaining words,
        # including title, scope notices, steps, table cells, and references.
        expected = d.text
        actual = "\n\n".join(c.content for c in chunks if c.document_id == d.document_id)
        for s in d.sections:
            header = f"## {s.heading}\n\n**section_id: {s.section_id}**"
            expected = expected.replace(header, "")
            actual = actual.replace(header, "")
        assert actual.split() == expected.split()
        for line in d.text.splitlines():
            if line.startswith("|") or re.match(r"\d+\. ", line):
                assert line in actual
    assert before == {p: p.read_bytes() for p in before}


def test_short_section_intact(documents):
    d = fixture_document(documents, "Short procedure.\n\n1. Keep the evidence.\n2. Stop.")
    chunks = chunk_documents([d])
    assert len(chunks) == 1
    assert chunks[0].content == d.sections[0].content


def test_oversized_section_paragraph_boundaries(documents):
    paragraphs = [f"Paragraph {i}. " + "operational evidence " * 35 for i in range(5)]
    d = fixture_document(documents, "\n\n".join(paragraphs))
    chunks = chunk_documents([d], max_tokens=250)
    assert len(chunks) == 5
    for paragraph, chunk in zip(paragraphs, chunks, strict=True):
        assert paragraph in chunk.content
        assert approximate_tokens(chunk.content) <= 250


def test_oversized_procedure_and_table_remain_atomic(documents):
    steps = "\n\n".join(f"{i}. Preserve evidence " + "carefully " * 35 for i in range(1, 7))
    table = "| Code | Meaning |\n| --- | --- |\n" + "\n".join(
        f"| SYN-BEN-{i} | Name mismatch; obtain verified correction before retry. |"
        for i in range(301, 330)
    )
    d = fixture_document(documents, "Introduction.\n\n" + steps + "\n\n" + table)
    chunks = chunk_documents([d], max_tokens=100)
    assert any(steps in c.content for c in chunks)
    assert any(table in c.content for c in chunks)
    assert any(approximate_tokens(c.content) > 100 for c in chunks)
    assert any("| SYN-BEN-301 | Name mismatch;" in c.content for c in chunks)


def test_fenced_content_and_subheading_context(documents):
    block = "```text\nfirst\n\nsecond\n```"
    d = fixture_document(documents, "Preface.\n\n### Evidence\n\n" + block)
    chunks = chunk_documents([d], max_tokens=10)
    assert any("### Evidence\n\n" + block in c.content for c in chunks)


def test_fingerprints_change_with_content_version_and_configuration(documents):
    d = fixture_document(documents, "First instruction.")
    original = chunk_documents([d])[0]
    changed = fixture_document(documents, "Changed instruction.")
    assert chunk_documents([changed])[0].chunk_id != original.chunk_id
    assert chunk_documents([replace(d, version="1.0.1")])[0].chunk_id != original.chunk_id
    assert chunk_documents([d], max_tokens=400)[0].chunk_id != original.chunk_id


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_bad_size_rejected(documents, limit):
    with pytest.raises(ValueError, match="positive integer"):
        chunk_documents(documents, max_tokens=limit)


def test_empty_input_and_duplicate_input(documents):
    assert chunk_documents([]) == ()
    with pytest.raises(ValueError, match="duplicate chunk_id"):
        chunk_documents([documents[0], documents[0]])


def test_size_estimate():
    assert approximate_tokens("") == 0
    assert approximate_tokens("12345") == 2
