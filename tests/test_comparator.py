"""Tests for logslice.comparator."""

import pytest
from logslice.comparator import (
    diff_entries,
    entries_equal,
    compare_field_values,
    added_entries,
    removed_entries,
)


def make_entry(timestamp="2024-01-01T00:00:00", level="INFO", message="msg", **kwargs):
    entry = {"timestamp": timestamp, "level": level, "message": message}
    entry.update(kwargs)
    return entry


# --- diff_entries ---

def test_diff_entries_returns_dict():
    result = diff_entries([], [])
    assert isinstance(result, dict)
    assert "only_left" in result
    assert "only_right" in result
    assert "common" in result


def test_diff_entries_all_common():
    e = make_entry(message="shared")
    result = diff_entries([e], [e])
    assert len(result["common"]) == 1
    assert result["only_left"] == []
    assert result["only_right"] == []


def test_diff_entries_only_left():
    e = make_entry(message="left only")
    result = diff_entries([e], [])
    assert len(result["only_left"]) == 1
    assert result["only_right"] == []


def test_diff_entries_only_right():
    e = make_entry(message="right only")
    result = diff_entries([], [e])
    assert len(result["only_right"]) == 1
    assert result["only_left"] == []


def test_diff_entries_mixed():
    shared = make_entry(message="shared")
    left_only = make_entry(message="left")
    right_only = make_entry(message="right")
    result = diff_entries([shared, left_only], [shared, right_only])
    assert len(result["common"]) == 1
    assert len(result["only_left"]) == 1
    assert len(result["only_right"]) == 1


def test_diff_entries_custom_fields():
    e1 = make_entry(message="a", level="ERROR")
    e2 = make_entry(message="b", level="ERROR")
    result = diff_entries([e1], [e2], fields=["level"])
    assert len(result["common"]) == 1


# --- entries_equal ---

def test_entries_equal_same_returns_true():
    e = make_entry()
    assert entries_equal([e], [e]) is True


def test_entries_equal_different_returns_false():
    e1 = make_entry(message="a")
    e2 = make_entry(message="b")
    assert entries_equal([e1], [e2]) is False


def test_entries_equal_empty_lists():
    assert entries_equal([], []) is True


# --- compare_field_values ---

def test_compare_field_values_returns_dict():
    result = compare_field_values([], [], "level")
    assert "left" in result and "right" in result and "delta" in result


def test_compare_field_values_counts_correctly():
    left = [make_entry(level="ERROR"), make_entry(level="INFO")]
    right = [make_entry(level="ERROR"), make_entry(level="ERROR")]
    result = compare_field_values(left, right, "level")
    assert result["left"]["ERROR"] == 1
    assert result["right"]["ERROR"] == 2
    assert result["delta"]["ERROR"] == 1
    assert result["delta"]["INFO"] == -1


def test_compare_field_values_missing_field_skipped():
    left = [{"level": "INFO"}, {"message": "no level"}]
    result = compare_field_values(left, [], "level")
    assert "INFO" in result["left"]
    assert len(result["left"]) == 1


# --- added_entries / removed_entries ---

def test_added_entries_returns_only_right():
    e = make_entry(message="new")
    result = added_entries([], [e])
    assert len(result) == 1


def test_removed_entries_returns_only_left():
    e = make_entry(message="gone")
    result = removed_entries([e], [])
    assert len(result) == 1


def test_added_entries_empty_when_no_new():
    e = make_entry()
    assert added_entries([e], [e]) == []


def test_removed_entries_empty_when_none_removed():
    e = make_entry()
    assert removed_entries([e], [e]) == []
