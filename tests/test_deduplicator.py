"""Tests for logslice.deduplicator module."""

import pytest
from logslice.deduplicator import (
    deduplicate,
    count_duplicates,
    deduplicate_by_message,
    group_duplicates,
)


def make_entry(level="INFO", message="hello", timestamp="2024-01-01T00:00:00"):
    return {"level": level, "message": message, "timestamp": timestamp}


# --- deduplicate ---

def test_deduplicate_returns_list():
    entries = [make_entry()]
    assert isinstance(deduplicate(entries), list)


def test_deduplicate_no_duplicates_unchanged():
    entries = [
        make_entry(message="one"),
        make_entry(message="two"),
        make_entry(message="three"),
    ]
    result = deduplicate(entries)
    assert len(result) == 3


def test_deduplicate_removes_exact_duplicates():
    entry = make_entry()
    entries = [entry, entry.copy(), entry.copy()]
    result = deduplicate(entries)
    assert len(result) == 1


def test_deduplicate_keeps_first_occurrence():
    e1 = make_entry(message="first")
    e2 = make_entry(message="first")
    result = deduplicate([e1, e2])
    assert result[0] is e1


def test_deduplicate_preserves_order():
    entries = [
        make_entry(message="a"),
        make_entry(message="b"),
        make_entry(message="a"),
        make_entry(message="c"),
    ]
    result = deduplicate(entries)
    assert [e["message"] for e in result] == ["a", "b", "c"]


def test_deduplicate_by_fields_ignores_other_fields():
    e1 = make_entry(message="same", timestamp="2024-01-01T00:00:00")
    e2 = make_entry(message="same", timestamp="2024-01-01T01:00:00")
    result = deduplicate([e1, e2], fields=["message"])
    assert len(result) == 1


def test_deduplicate_by_fields_keeps_distinct():
    e1 = make_entry(message="a")
    e2 = make_entry(message="b")
    result = deduplicate([e1, e2], fields=["message"])
    assert len(result) == 2


def test_deduplicate_empty_input():
    assert deduplicate([]) == []


# --- count_duplicates ---

def test_count_duplicates_returns_int():
    assert isinstance(count_duplicates([make_entry()]), int)


def test_count_duplicates_no_dupes_returns_zero():
    entries = [make_entry(message="x"), make_entry(message="y")]
    assert count_duplicates(entries) == 0


def test_count_duplicates_correct_count():
    entry = make_entry()
    entries = [entry, entry.copy(), entry.copy()]
    assert count_duplicates(entries) == 2


# --- deduplicate_by_message ---

def test_deduplicate_by_message_uses_message_field():
    e1 = make_entry(message="dup", timestamp="2024-01-01")
    e2 = make_entry(message="dup", timestamp="2024-01-02")
    result = deduplicate_by_message([e1, e2])
    assert len(result) == 1


# --- group_duplicates ---

def test_group_duplicates_returns_list():
    assert isinstance(group_duplicates([make_entry()]), list)


def test_group_duplicates_adds_count_field():
    entry = make_entry()
    result = group_duplicates([entry, entry.copy()])
    assert "_count" in result[0]


def test_group_duplicates_correct_count():
    entry = make_entry()
    result = group_duplicates([entry, entry.copy(), entry.copy()])
    assert result[0]["_count"] == 3


def test_group_duplicates_unique_entries_count_one():
    entries = [make_entry(message="a"), make_entry(message="b")]
    result = group_duplicates(entries)
    assert all(e["_count"] == 1 for e in result)


def test_group_duplicates_preserves_unique_count():
    entries = [
        make_entry(message="a"),
        make_entry(message="a"),
        make_entry(message="b"),
    ]
    result = group_duplicates(entries)
    assert len(result) == 2
