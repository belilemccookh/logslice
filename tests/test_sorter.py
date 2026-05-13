"""Tests for logslice.sorter module."""

import pytest
from logslice.sorter import sort_by_field, sort_by_timestamp, sort_by_level, sort_entries


def make_entry(timestamp=None, level=None, message="msg", **kwargs):
    entry = {"timestamp": timestamp, "level": level, "message": message}
    entry.update(kwargs)
    return entry


# --- sort_by_field ---

def test_sort_by_field_ascending():
    entries = [make_entry(message="b"), make_entry(message="a"), make_entry(message="c")]
    result = sort_by_field(entries, "message")
    assert [e["message"] for e in result] == ["a", "b", "c"]


def test_sort_by_field_descending():
    entries = [make_entry(message="b"), make_entry(message="a"), make_entry(message="c")]
    result = sort_by_field(entries, "message", reverse=True)
    assert [e["message"] for e in result] == ["c", "b", "a"]


def test_sort_by_field_missing_placed_last():
    entries = [make_entry(message="b"), {"level": "INFO"}, make_entry(message="a")]
    result = sort_by_field(entries, "message")
    assert result[-1].get("message") is None


def test_sort_by_field_empty_returns_empty():
    assert sort_by_field([], "message") == []


# --- sort_by_timestamp ---

def test_sort_by_timestamp_ascending():
    entries = [
        make_entry(timestamp="2024-01-03"),
        make_entry(timestamp="2024-01-01"),
        make_entry(timestamp="2024-01-02"),
    ]
    result = sort_by_timestamp(entries)
    assert [e["timestamp"] for e in result] == ["2024-01-01", "2024-01-02", "2024-01-03"]


def test_sort_by_timestamp_descending():
    entries = [
        make_entry(timestamp="2024-01-01"),
        make_entry(timestamp="2024-01-03"),
    ]
    result = sort_by_timestamp(entries, reverse=True)
    assert result[0]["timestamp"] == "2024-01-03"


def test_sort_by_timestamp_none_placed_last():
    entries = [make_entry(timestamp=None), make_entry(timestamp="2024-01-01")]
    result = sort_by_timestamp(entries)
    assert result[-1]["timestamp"] is None


def test_sort_by_timestamp_with_fmt():
    entries = [
        make_entry(timestamp="03/01/2024"),
        make_entry(timestamp="01/01/2024"),
    ]
    result = sort_by_timestamp(entries, fmt="%d/%m/%Y")
    assert result[0]["timestamp"] == "01/01/2024"


# --- sort_by_level ---

def test_sort_by_level_default_order():
    entries = [
        make_entry(level="ERROR"),
        make_entry(level="DEBUG"),
        make_entry(level="INFO"),
    ]
    result = sort_by_level(entries)
    assert [e["level"] for e in result] == ["DEBUG", "INFO", "ERROR"]


def test_sort_by_level_custom_order():
    entries = [make_entry(level="LOW"), make_entry(level="HIGH"), make_entry(level="MED")]
    result = sort_by_level(entries, level_order=["LOW", "MED", "HIGH"])
    assert [e["level"] for e in result] == ["LOW", "MED", "HIGH"]


def test_sort_by_level_unknown_level_placed_last():
    entries = [make_entry(level="UNKNOWN"), make_entry(level="INFO")]
    result = sort_by_level(entries)
    assert result[-1]["level"] == "UNKNOWN"


def test_sort_by_level_case_insensitive():
    entries = [make_entry(level="error"), make_entry(level="debug")]
    result = sort_by_level(entries)
    assert result[0]["level"] == "debug"


# --- sort_entries dispatcher ---

def test_sort_entries_by_timestamp():
    entries = [make_entry(timestamp="2024-02-01"), make_entry(timestamp="2024-01-01")]
    result = sort_entries(entries, by="timestamp")
    assert result[0]["timestamp"] == "2024-01-01"


def test_sort_entries_by_level():
    entries = [make_entry(level="ERROR"), make_entry(level="DEBUG")]
    result = sort_entries(entries, by="level")
    assert result[0]["level"] == "DEBUG"


def test_sort_entries_by_custom_field():
    entries = [make_entry(message="z"), make_entry(message="a")]
    result = sort_entries(entries, by="message")
    assert result[0]["message"] == "a"
