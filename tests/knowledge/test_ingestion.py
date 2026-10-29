"""Offline ingestion contracts and lossless handling of operational Markdown."""

from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path
import re

import pytest

from payment_ops.knowledge.ingestion import IngestionError, clean_text, load_document, load_documents


CORPUS = Path(__file__).resolve().parents[2] / "data/knowledge/documents"


@pytest.fixture
def source_text():
    return """---
document_id: SYN-TEST
title: Test Procedure
version: 1.0.0
effective_date: 2026-10-28
document_type: sop
source_path: data/knowledge/documents/test.md
---

# Test Procedure

Synthetic educational material — not an actual bank policy.

## TT-STEPS — Procedure

**section_id: TT-STEPS**

1. Preserve `SYN-BEN-301`; do not bypass checks.
2. Record evidence.

| Code | Meaning |
| --- | --- |
| SYN-BEN-301 | Name mismatch |

See `SYN-TEST/TT-STEPS`.
"""


@pytest.fixture
def source_file(tmp_path, source_text):
    path = tmp_path / "test.md"
    path.write_text(source_text, encoding="utf-8")
    return path


def test_existing_corpus_metadata_and_counts():
    documents = load_documents(CORPUS)
    assert len(documents) == 6
    assert sum(len(document.sections) for document in documents) == 31
    assert len({document.document_id for document in documents}) == 6
    assert {document.document_id for document in documents} == {
        "SYN-WIRE-RECALL", "SYN-ACH-RETURNS", "SYN-ERROR-CATALOG",
        "SYN-BENEFICIARY", "SYN-EXCEPTION", "SYN-STATUS",
    }
    wire = next(document for document in documents if document.document_id == "SYN-WIRE-RECALL")
    assert wire.title == "Wire Recall SOP"
    assert wire.version == "1.0.0"
    assert wire.effective_date == date(2026, 10, 28)
    assert wire.document_type == "sop"
    assert wire.source_path == "data/knowledge/documents/wire_recall_sop.md"
    assert [section.section_id for section in wire.sections] == [
        "WR-SCOPE", "WR-ELIGIBILITY", "WR-REQUEST", "WR-TRACK", "WR-ESCALATE",
    ]


def test_corpus_content_and_original_bytes_preserved():
    before = {path: path.read_bytes() for path in CORPUS.glob("*.md")}
    documents = load_documents(CORPUS)
    for document in documents:
        original = before[CORPUS / Path(document.source_path).name].decode("utf-8")
        assert document.raw_text == original
        body = original.split("---", 2)[2].strip("\n")
        assert document.text == body
        assert document.text.startswith(f"# {document.title}")
        for section in document.sections:
            assert section.content in document.text
            assert section.content.startswith(f"## {section.heading}\n")
            assert f"**section_id: {section.section_id}**" in section.content
        for line in original.splitlines():
            if line.startswith("|") or re.match(r"\d+\. ", line):
                assert line in document.text
        codes = re.findall(r"SYN-(?:WR|ACH|BEN|STS|EXC)-\d{3}", original)
        assert codes == re.findall(r"SYN-(?:WR|ACH|BEN|STS|EXC)-\d{3}", document.text)
        references = re.findall(r"SYN-[A-Z-]+/[A-Z-]+", original)
        assert references == re.findall(r"SYN-[A-Z-]+/[A-Z-]+", document.text)
    assert before == {path: path.read_bytes() for path in before}


def test_cleaning_newlines_whitespace_and_hard_breaks():
    text = "Intro  \r\n\r\n1. Do not retry.\t\r| Code | Meaning | \r\n| X | No |\r\n"
    expected = "Intro  \n\n1. Do not retry.\n| Code | Meaning |\n| X | No |\n"
    assert clean_text(text) == expected
    assert clean_text(expected) == expected


def test_raw_line_endings_and_cleaned_procedures(source_file, source_text):
    original = source_text.replace("\n", "\r\n").encode("utf-8")
    source_file.write_bytes(original)
    document = load_document(source_file)
    assert document.raw_text.encode("utf-8") == original
    assert "\r" not in document.text
    assert "1. Preserve `SYN-BEN-301`; do not bypass checks.\n2. Record evidence." in document.sections[0].content
    assert source_file.read_bytes() == original
    with pytest.raises(FrozenInstanceError):
        document.title = "Changed"
    with pytest.raises(FrozenInstanceError):
        document.sections[0].content = "Changed"


def test_deterministic_loading_and_discovery_scope(tmp_path, source_text):
    for name, doc_id in [("z.md", "SYN-Z"), ("a.md", "SYN-A")]:
        text = source_text.replace("SYN-TEST", doc_id).replace("test.md", name)
        (tmp_path / name).write_text(text, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a source", encoding="utf-8")
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "old.md").write_text("malformed archive", encoding="utf-8")
    first = load_documents(tmp_path)
    assert [document.document_id for document in first] == ["SYN-A", "SYN-Z"]
    assert first == load_documents(tmp_path)


@pytest.mark.parametrize(("old", "new", "message"), [
    ("title: Test Procedure\n", "", "missing required metadata: title"),
    ("title: Test Procedure", "title:", "malformed metadata"),
    ("title: Test Procedure", "title: Test Procedure\ntitle: Duplicate", "duplicate metadata"),
    ("title: Test Procedure", "title: Test Procedure\nextra: value", "unknown metadata"),
    ("document_id: SYN-TEST", "document_id: invalid", "invalid document_id"),
    ("version: 1.0.0", "version: latest", "version must"),
    ("effective_date: 2026-10-28", "effective_date: 2026-02-30", "invalid effective_date"),
    ("effective_date: 2026-10-28", "effective_date: 20261028", "invalid effective_date"),
    ("document_type: sop", "document_type: other", "invalid document_type"),
    ("data/knowledge/documents/test.md", "../test.md", "source_path"),
    ("data/knowledge/documents/test.md", "/test.md", "source_path"),
    ("data/knowledge/documents/test.md", "data/wrong.md", "source_path"),
    ("# Test Procedure", "# Wrong title", "matching title"),
    ("## TT-STEPS — Procedure", "## tt-steps — Procedure", "invalid section heading"),
    ("**section_id: TT-STEPS**", "**section_id: TT-WRONG**", "mismatched section"),
    ("**section_id: TT-STEPS**", "", "mismatched section"),
    ("See `SYN-TEST/TT-STEPS`.", "**section_id: TT-EXTRA**", "unexpected or malformed"),
])
def test_explicit_malformed_document_errors(source_file, source_text, old, new, message):
    source_file.write_text(source_text.replace(old, new), encoding="utf-8")
    with pytest.raises(IngestionError, match=message) as error:
        load_document(source_file)
    assert str(source_file) in str(error.value)


@pytest.mark.parametrize("text,message", [
    (" \n", "empty document"),
    ("# No metadata", "opening front-matter"),
    ("---\ntitle: Unclosed", "closing front-matter"),
])
def test_empty_and_missing_front_matter(source_file, text, message):
    source_file.write_text(text, encoding="utf-8")
    with pytest.raises(IngestionError, match=message):
        load_document(source_file)


def test_section_structure_errors(source_file, source_text):
    prefix = source_text.split("## TT-STEPS")[0]
    for body, message in [
        ("", "no identified sections"),
        ("## TT-STEPS — Procedure\n\n**section_id: TT-STEPS**\n", "empty section content"),
        (source_text.split("## TT-STEPS", 1)[1], "no identified sections"),
    ]:
        source_file.write_text(prefix + body, encoding="utf-8")
        with pytest.raises(IngestionError, match=message):
            load_document(source_file)
    section = source_text[source_text.index("## TT-STEPS"):]
    source_file.write_text(source_text + "\n" + section, encoding="utf-8")
    with pytest.raises(IngestionError, match="duplicate section_id"):
        load_document(source_file)


def test_duplicate_ids_are_not_skipped(tmp_path, source_file, source_text):
    (tmp_path / "copy.md").write_text(source_text.replace("test.md", "copy.md"), encoding="utf-8")
    with pytest.raises(IngestionError, match="duplicate document_id: SYN-TEST"):
        load_documents(tmp_path)


@pytest.mark.parametrize("reference", ["SYN-MISSING/TT-STEPS", "SYN-TEST/TT-MISSING"])
def test_broken_cross_references(tmp_path, source_file, source_text, reference):
    source_file.write_text(source_text.replace("See `SYN-TEST/TT-STEPS`", f"See `{reference}`"), encoding="utf-8")
    with pytest.raises(IngestionError, match="unresolved cross-reference"):
        load_documents(tmp_path)


def test_missing_directory_empty_directory_and_bad_utf8(tmp_path):
    with pytest.raises(IngestionError, match="directory is missing"):
        load_documents(tmp_path / "absent")
    with pytest.raises(IngestionError, match="no Markdown"):
        load_documents(tmp_path)
    with pytest.raises(IngestionError, match="cannot read UTF-8"):
        load_document(tmp_path / "absent.md")
    path = tmp_path / "bad.md"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(IngestionError, match="cannot read UTF-8"):
        load_documents(tmp_path)
