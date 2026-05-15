"""Tests for logslice.summarizer."""

import pytest
from logslice.summarizer import (
    top_levels,
    top_messages,
    error_rate,
    time_span,
    summarize_entries,
)


def make_entry(level="INFO", message="msg", timestamp="2024-01-01T00:00:00"):
    return {"level": level, "message": message, "timestamp": timestamp}


# --- top_levels ---

def test_top_levels_returns_list():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    result = top_levels(entries)
    assert isinstance(result, list)


def test_top_levels_correct_counts():
    entries = [make_entry("INFO")] * 3 + [make_entry("ERROR")] * 2
    result = dict(top_levels(entries))
    assert result["INFO"] == 3
    assert result["ERROR"] == 2


def test_top_levels_case_normalized():
    entries = [make_entry("info"), make_entry("INFO")]
    result = dict(top_levels(entries))
    assert result.get("INFO") == 2


def test_top_levels_skips_none_level():
    entries = [{"level": None, "message": "x", "timestamp": "t"}]
    result = top_levels(entries)
    assert result == []


def test_top_levels_respects_n():
    entries = [make_entry(l) for l in ["A", "B", "C", "D", "E", "F"]]
    result = top_levels(entries, n=3)
    assert len(result) <= 3


# --- top_messages ---

def test_top_messages_returns_list():
    entries = [make_entry(message="hello")]
    assert isinstance(top_messages(entries), list)


def test_top_messages_correct_counts():
    entries = [make_entry(message="foo")] * 4 + [make_entry(message="bar")]
    result = dict(top_messages(entries))
    assert result["foo"] == 4
    assert result["bar"] == 1


def test_top_messages_skips_none_message():
    entries = [{"level": "INFO", "message": None, "timestamp": "t"}]
    assert top_messages(entries) == []


# --- error_rate ---

def test_error_rate_empty_returns_zero():
    assert error_rate([]) == 0.0


def test_error_rate_all_info_returns_zero():
    entries = [make_entry("INFO")] * 5
    assert error_rate(entries) == 0.0


def test_error_rate_all_errors_returns_one():
    entries = [make_entry("ERROR")] * 4
    assert error_rate(entries) == 1.0


def test_error_rate_mixed():
    entries = [make_entry("ERROR")] * 2 + [make_entry("INFO")] * 2
    assert error_rate(entries) == pytest.approx(0.5)


def test_error_rate_includes_critical():
    entries = [make_entry("CRITICAL"), make_entry("INFO")]
    assert error_rate(entries) == pytest.approx(0.5)


# --- time_span ---

def test_time_span_empty_returns_none_values():
    result = time_span([])
    assert result == {"earliest": None, "latest": None}


def test_time_span_single_entry():
    entries = [make_entry(timestamp="2024-06-01T12:00:00")]
    result = time_span(entries)
    assert result["earliest"] == result["latest"] == "2024-06-01T12:00:00"


def test_time_span_returns_min_max():
    entries = [
        make_entry(timestamp="2024-01-01"),
        make_entry(timestamp="2024-06-15"),
        make_entry(timestamp="2024-03-10"),
    ]
    result = time_span(entries)
    assert result["earliest"] == "2024-01-01"
    assert result["latest"] == "2024-06-15"


# --- summarize_entries ---

def test_summarize_entries_returns_dict():
    entries = [make_entry()]
    result = summarize_entries(entries)
    assert isinstance(result, dict)


def test_summarize_entries_has_expected_keys():
    result = summarize_entries([make_entry()])
    assert "total" in result
    assert "error_rate" in result
    assert "top_levels" in result
    assert "top_messages" in result
    assert "time_span" in result


def test_summarize_entries_total_correct():
    entries = [make_entry()] * 7
    assert summarize_entries(entries)["total"] == 7


def test_summarize_entries_empty():
    result = summarize_entries([])
    assert result["total"] == 0
    assert result["error_rate"] == 0.0
    assert result["top_levels"] == []
    assert result["top_messages"] == []
