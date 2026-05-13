"""Tests for logslice/splitter.py."""

import pytest
from logslice.splitter import (
    split_by_level_change,
    split_by_field_value,
    split_at_index,
    split_by_predicate,
    split_by_session,
)


def make_entry(level="INFO", message="msg", **kwargs):
    entry = {"level": level, "message": message, "timestamp": "2024-01-01T00:00:00"}
    entry.update(kwargs)
    return entry


# --- split_by_level_change ---

def test_split_by_level_change_empty_returns_empty():
    assert split_by_level_change([]) == []


def test_split_by_level_change_single_entry_one_segment():
    entries = [make_entry("INFO")]
    result = split_by_level_change(entries)
    assert len(result) == 1
    assert result[0] == entries


def test_split_by_level_change_same_level_one_segment():
    entries = [make_entry("ERROR"), make_entry("ERROR"), make_entry("ERROR")]
    result = split_by_level_change(entries)
    assert len(result) == 1


def test_split_by_level_change_creates_segments_on_change():
    entries = [make_entry("INFO"), make_entry("INFO"), make_entry("ERROR"), make_entry("DEBUG")]
    result = split_by_level_change(entries)
    assert len(result) == 3


def test_split_by_level_change_preserves_all_entries():
    entries = [make_entry("INFO"), make_entry("ERROR"), make_entry("INFO")]
    result = split_by_level_change(entries)
    total = sum(len(seg) for seg in result)
    assert total == len(entries)


# --- split_by_field_value ---

def test_split_by_field_value_returns_dict_with_matching_and_other():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    result = split_by_field_value(entries, "level", "ERROR")
    assert "matching" in result
    assert "other" in result


def test_split_by_field_value_correct_groups():
    entries = [make_entry("INFO"), make_entry("ERROR"), make_entry("INFO")]
    result = split_by_field_value(entries, "level", "INFO")
    assert len(result["matching"]) == 2
    assert len(result["other"]) == 1


def test_split_by_field_value_no_match_all_in_other():
    entries = [make_entry("DEBUG"), make_entry("INFO")]
    result = split_by_field_value(entries, "level", "ERROR")
    assert result["matching"] == []
    assert len(result["other"]) == 2


# --- split_at_index ---

def test_split_at_index_splits_correctly():
    entries = [make_entry() for _ in range(5)]
    first, second = split_at_index(entries, 2)
    assert len(first) == 2
    assert len(second) == 3


def test_split_at_index_zero_returns_empty_first():
    entries = [make_entry() for _ in range(3)]
    first, second = split_at_index(entries, 0)
    assert first == []
    assert len(second) == 3


def test_split_at_index_negative_index():
    entries = [make_entry() for _ in range(4)]
    first, second = split_at_index(entries, -1)
    assert len(first) == 3
    assert len(second) == 1


# --- split_by_predicate ---

def test_split_by_predicate_returns_passing_and_failing():
    entries = [make_entry("ERROR"), make_entry("INFO"), make_entry("ERROR")]
    result = split_by_predicate(entries, lambda e: e["level"] == "ERROR")
    assert len(result["passing"]) == 2
    assert len(result["failing"]) == 1


def test_split_by_predicate_all_pass():
    entries = [make_entry("INFO") for _ in range(3)]
    result = split_by_predicate(entries, lambda e: True)
    assert len(result["passing"]) == 3
    assert result["failing"] == []


# --- split_by_session ---

def test_split_by_session_groups_by_session_id():
    entries = [
        make_entry(session_id="abc"),
        make_entry(session_id="xyz"),
        make_entry(session_id="abc"),
    ]
    result = split_by_session(entries, session_field="session_id")
    assert len(result["abc"]) == 2
    assert len(result["xyz"]) == 1


def test_split_by_session_missing_field_uses_unknown():
    entries = [make_entry(), make_entry()]
    result = split_by_session(entries, session_field="session_id")
    assert "unknown" in result
    assert len(result["unknown"]) == 2
