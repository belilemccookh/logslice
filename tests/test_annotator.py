"""Tests for logslice.annotator."""

import pytest
from logslice.annotator import (
    annotate_entry,
    annotate_entries,
    annotate_with_index,
    annotate_with_predicate,
    strip_annotations,
)


def make_entry(level="INFO", message="hello"):
    return {"timestamp": "2024-01-01T00:00:00", "level": level, "message": message}


# annotate_entry

def test_annotate_entry_returns_dict():
    result = annotate_entry(make_entry(), "env", "prod")
    assert isinstance(result, dict)


def test_annotate_entry_adds_annotation():
    result = annotate_entry(make_entry(), "env", "prod")
    assert result["annotations"]["env"] == "prod"


def test_annotate_entry_does_not_mutate_original():
    entry = make_entry()
    annotate_entry(entry, "env", "prod")
    assert "annotations" not in entry


def test_annotate_entry_preserves_existing_annotations():
    entry = make_entry()
    entry["annotations"] = {"region": "us-east"}
    result = annotate_entry(entry, "env", "prod")
    assert result["annotations"]["region"] == "us-east"
    assert result["annotations"]["env"] == "prod"


def test_annotate_entry_overwrites_existing_key():
    entry = make_entry()
    entry["annotations"] = {"env": "dev"}
    result = annotate_entry(entry, "env", "prod")
    assert result["annotations"]["env"] == "prod"


# annotate_entries

def test_annotate_entries_returns_list():
    entries = [make_entry(), make_entry()]
    result = annotate_entries(entries, "env", "staging")
    assert isinstance(result, list)


def test_annotate_entries_correct_length():
    entries = [make_entry() for _ in range(5)]
    result = annotate_entries(entries, "env", "staging")
    assert len(result) == 5


def test_annotate_entries_all_annotated():
    entries = [make_entry() for _ in range(3)]
    result = annotate_entries(entries, "env", "staging")
    assert all(e["annotations"]["env"] == "staging" for e in result)


# annotate_with_index

def test_annotate_with_index_adds_index():
    entries = [make_entry(), make_entry(), make_entry()]
    result = annotate_with_index(entries)
    assert [e["annotations"]["index"] for e in result] == [0, 1, 2]


def test_annotate_with_index_custom_start():
    entries = [make_entry(), make_entry()]
    result = annotate_with_index(entries, start=10)
    assert result[0]["annotations"]["index"] == 10
    assert result[1]["annotations"]["index"] == 11


def test_annotate_with_index_custom_key():
    entries = [make_entry()]
    result = annotate_with_index(entries, key="seq")
    assert "seq" in result[0]["annotations"]


# annotate_with_predicate

def test_annotate_with_predicate_applies_function():
    entries = [make_entry(level="ERROR"), make_entry(level="INFO")]
    result = annotate_with_predicate(entries, "is_error", lambda e: e["level"] == "ERROR")
    assert result[0]["annotations"]["is_error"] is True
    assert result[1]["annotations"]["is_error"] is False


# strip_annotations

def test_strip_annotations_removes_all():
    entry = make_entry()
    entry["annotations"] = {"env": "prod", "index": 0}
    result = strip_annotations(entry)
    assert "annotations" not in result


def test_strip_annotations_removes_specific_keys():
    entry = make_entry()
    entry["annotations"] = {"env": "prod", "index": 0}
    result = strip_annotations(entry, keys=["index"])
    assert "index" not in result["annotations"]
    assert result["annotations"]["env"] == "prod"


def test_strip_annotations_no_annotations_unchanged():
    entry = make_entry()
    result = strip_annotations(entry)
    assert "annotations" not in result
