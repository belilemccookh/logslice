"""Tests for logslice.merger module."""

import pytest
from datetime import datetime, timedelta
from logslice.merger import merge_entries, merge_sorted, merge_with_source, merge_by_priority


def make_entry(msg="test", level="INFO", ts=None):
    return {"message": msg, "level": level, "timestamp": ts}


# --- merge_entries ---

def test_merge_entries_returns_list():
    result = merge_entries([make_entry("a")], [make_entry("b")])
    assert isinstance(result, list)


def test_merge_entries_combines_all():
    a = [make_entry("a"), make_entry("b")]
    b = [make_entry("c")]
    result = merge_entries(a, b)
    assert len(result) == 3


def test_merge_entries_empty_lists():
    result = merge_entries([], [])
    assert result == []


def test_merge_entries_single_list():
    entries = [make_entry("x"), make_entry("y")]
    result = merge_entries(entries)
    assert len(result) == 2


def test_merge_entries_deduplication_removes_duplicates():
    base = datetime(2024, 1, 1)
    e = make_entry("dup", ts=base)
    result = merge_entries([e, e], deduplicate=True)
    assert len(result) == 1


def test_merge_entries_deduplication_keeps_unique():
    base = datetime(2024, 1, 1)
    a = make_entry("first", ts=base)
    b = make_entry("second", ts=base)
    result = merge_entries([a], [b], deduplicate=True)
    assert len(result) == 2


# --- merge_sorted ---

def test_merge_sorted_returns_list():
    base = datetime(2024, 1, 1)
    a = [make_entry("a", ts=base)]
    b = [make_entry("b", ts=base + timedelta(seconds=5))]
    result = merge_sorted(a, b)
    assert isinstance(result, list)


def test_merge_sorted_orders_by_timestamp():
    base = datetime(2024, 1, 1)
    a = [make_entry("later", ts=base + timedelta(seconds=10))]
    b = [make_entry("earlier", ts=base)]
    result = merge_sorted(a, b, key="timestamp")
    assert result[0]["message"] == "earlier"


def test_merge_sorted_reverse_order():
    base = datetime(2024, 1, 1)
    a = [make_entry("first", ts=base)]
    b = [make_entry("second", ts=base + timedelta(seconds=5))]
    result = merge_sorted(a, b, key="timestamp", reverse=True)
    assert result[0]["message"] == "second"


def test_merge_sorted_none_timestamps_placed_last():
    base = datetime(2024, 1, 1)
    a = [make_entry("no-ts", ts=None)]
    b = [make_entry("with-ts", ts=base)]
    result = merge_sorted(a, b, key="timestamp")
    assert result[-1]["message"] == "no-ts"


# --- merge_with_source ---

def test_merge_with_source_returns_list():
    result = merge_with_source([("app", [make_entry()])])
    assert isinstance(result, list)


def test_merge_with_source_injects_source_field():
    entries = [make_entry("msg1")]
    result = merge_with_source([("myapp", entries)])
    assert result[0]["_source"] == "myapp"


def test_merge_with_source_multiple_sources():
    result = merge_with_source([
        ("src1", [make_entry("a")]),
        ("src2", [make_entry("b"), make_entry("c")])
    ])
    assert len(result) == 3
    sources = {e["_source"] for e in result}
    assert sources == {"src1", "src2"}


def test_merge_with_source_does_not_mutate_original():
    entry = make_entry("original")
    merge_with_source([("src", [entry])])
    assert "_source" not in entry


# --- merge_by_priority ---

def test_merge_by_priority_returns_list():
    result = merge_by_priority([make_entry(level="INFO")])
    assert isinstance(result, list)


def test_merge_by_priority_error_before_info():
    entries = [make_entry("info", level="INFO"), make_entry("err", level="ERROR")]
    result = merge_by_priority(entries)
    assert result[0]["level"] == "ERROR"


def test_merge_by_priority_custom_order():
    entries = [make_entry("low", level="DEBUG"), make_entry("high", level="INFO")]
    result = merge_by_priority(entries, level_order=["INFO", "DEBUG"])
    assert result[0]["level"] == "INFO"


def test_merge_by_priority_unknown_level_placed_last():
    entries = [make_entry("known", level="ERROR"), make_entry("unknown", level="TRACE")]
    result = merge_by_priority(entries)
    assert result[-1]["level"] == "TRACE"
