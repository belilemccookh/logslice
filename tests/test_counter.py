"""Tests for logslice.counter module."""

import pytest
from logslice.counter import (
    count_entries,
    count_by_level,
    count_errors,
    count_warnings,
    count_by_field_value,
    frequency_table,
)


def make_entry(level="INFO", message="msg", **kwargs):
    return {"timestamp": "2024-01-01T00:00:00", "level": level, "message": message, **kwargs}


# --- count_entries ---

def test_count_entries_empty():
    assert count_entries([]) == 0


def test_count_entries_returns_int():
    entries = [make_entry() for _ in range(5)]
    assert isinstance(count_entries(entries), int)


def test_count_entries_correct_count():
    entries = [make_entry() for _ in range(7)]
    assert count_entries(entries) == 7


# --- count_by_level ---

def test_count_by_level_returns_dict():
    assert isinstance(count_by_level([make_entry()]), dict)


def test_count_by_level_correct_counts():
    entries = [
        make_entry("INFO"),
        make_entry("INFO"),
        make_entry("ERROR"),
    ]
    result = count_by_level(entries)
    assert result["INFO"] == 2
    assert result["ERROR"] == 1


def test_count_by_level_case_normalised():
    entries = [make_entry("info"), make_entry("INFO")]
    result = count_by_level(entries)
    assert result.get("INFO") == 2


def test_count_by_level_skips_missing_level():
    entries = [{"message": "no level"}]
    result = count_by_level(entries)
    assert result == {}


# --- count_errors ---

def test_count_errors_empty():
    assert count_errors([]) == 0


def test_count_errors_counts_error_and_critical():
    entries = [
        make_entry("ERROR"),
        make_entry("CRITICAL"),
        make_entry("FATAL"),
        make_entry("INFO"),
    ]
    assert count_errors(entries) == 3


def test_count_errors_case_insensitive():
    entries = [make_entry("error"), make_entry("critical")]
    assert count_errors(entries) == 2


# --- count_warnings ---

def test_count_warnings_empty():
    assert count_warnings([]) == 0


def test_count_warnings_counts_warn_and_warning():
    entries = [make_entry("WARN"), make_entry("WARNING"), make_entry("INFO")]
    assert count_warnings(entries) == 2


# --- count_by_field_value ---

def test_count_by_field_value_matches():
    entries = [
        make_entry(source="app"),
        make_entry(source="app"),
        make_entry(source="db"),
    ]
    assert count_by_field_value(entries, "source", "app") == 2


def test_count_by_field_value_no_match():
    entries = [make_entry(source="app")]
    assert count_by_field_value(entries, "source", "db") == 0


# --- frequency_table ---

def test_frequency_table_returns_list():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    assert isinstance(frequency_table(entries, "level"), list)


def test_frequency_table_sorted_descending():
    entries = [make_entry("INFO")] * 3 + [make_entry("ERROR")] * 1
    result = frequency_table(entries, "level")
    assert result[0]["value"] == "INFO"
    assert result[0]["count"] == 3


def test_frequency_table_top_n_limits_results():
    entries = [make_entry("INFO")] * 3 + [make_entry("ERROR")] * 2 + [make_entry("DEBUG")] * 1
    result = frequency_table(entries, "level", top_n=2)
    assert len(result) == 2


def test_frequency_table_skips_none_values():
    entries = [{"level": None, "message": "x"}, make_entry("INFO")]
    result = frequency_table(entries, "level")
    assert all(item["value"] is not None for item in result)
