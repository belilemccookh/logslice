"""Tests for logslice.inspector."""

import pytest
from logslice.inspector import (
    is_severe,
    is_warning,
    has_field,
    is_complete,
    missing_fields,
    entry_size,
    find_anomalies,
    summarize_entry,
)


def make_entry(level="INFO", message="hello", timestamp="2024-01-01", **kwargs):
    entry = {"level": level, "message": message, "timestamp": timestamp}
    entry.update(kwargs)
    return entry


# --- is_severe ---

def test_is_severe_error_returns_true():
    assert is_severe(make_entry(level="ERROR")) is True


def test_is_severe_critical_returns_true():
    assert is_severe(make_entry(level="CRITICAL")) is True


def test_is_severe_info_returns_false():
    assert is_severe(make_entry(level="INFO")) is False


def test_is_severe_case_insensitive():
    assert is_severe(make_entry(level="error")) is True


# --- is_warning ---

def test_is_warning_warn_returns_true():
    assert is_warning(make_entry(level="WARN")) is True


def test_is_warning_warning_returns_true():
    assert is_warning(make_entry(level="WARNING")) is True


def test_is_warning_error_returns_false():
    assert is_warning(make_entry(level="ERROR")) is False


# --- has_field ---

def test_has_field_present_returns_true():
    assert has_field(make_entry(), "level") is True


def test_has_field_missing_returns_false():
    assert has_field({}, "level") is False


def test_has_field_none_value_returns_false():
    assert has_field({"level": None}, "level") is False


# --- is_complete ---

def test_is_complete_full_entry_returns_true():
    assert is_complete(make_entry()) is True


def test_is_complete_missing_field_returns_false():
    entry = {"level": "INFO", "message": "hi"}
    assert is_complete(entry) is False


def test_is_complete_custom_required():
    entry = {"host": "server1"}
    assert is_complete(entry, required=["host"]) is True


# --- missing_fields ---

def test_missing_fields_none_missing():
    assert missing_fields(make_entry()) == []


def test_missing_fields_returns_missing_names():
    entry = {"level": "INFO"}
    result = missing_fields(entry)
    assert "timestamp" in result
    assert "message" in result


def test_missing_fields_custom_required():
    entry = {"a": 1}
    result = missing_fields(entry, required=["a", "b"])
    assert result == ["b"]


# --- entry_size ---

def test_entry_size_returns_int():
    assert isinstance(entry_size(make_entry()), int)


def test_entry_size_correct_length():
    entry = {"a": "hello", "b": "world"}
    assert entry_size(entry) == 10


def test_entry_size_skips_none():
    entry = {"a": "hello", "b": None}
    assert entry_size(entry) == 5


# --- find_anomalies ---

def test_find_anomalies_returns_list():
    entries = [make_entry()]
    assert isinstance(find_anomalies(entries), list)


def test_find_anomalies_includes_severe():
    entries = [make_entry(level="ERROR"), make_entry(level="INFO")]
    result = find_anomalies(entries)
    assert any(e["level"] == "ERROR" for e in result)


def test_find_anomalies_includes_incomplete():
    entries = [{"level": "INFO"}, make_entry()]
    result = find_anomalies(entries)
    assert any("timestamp" not in e for e in result)


def test_find_anomalies_normal_entry_excluded():
    entries = [make_entry(level="INFO")]
    assert find_anomalies(entries) == []


# --- summarize_entry ---

def test_summarize_entry_returns_dict():
    assert isinstance(summarize_entry(make_entry()), dict)


def test_summarize_entry_severe_field():
    assert summarize_entry(make_entry(level="ERROR"))["severe"] is True


def test_summarize_entry_complete_field():
    assert summarize_entry(make_entry())["complete"] is True


def test_summarize_entry_missing_field_list():
    result = summarize_entry({"level": "INFO"})
    assert "timestamp" in result["missing"]
