"""Tests for logslice.profiler."""

import pytest
from logslice.profiler import (
    field_value_distribution,
    field_coverage,
    all_fields,
    field_stats,
    profile_entries,
)


def make_entry(level="INFO", message="msg", host=None):
    entry = {"level": level, "message": message}
    if host is not None:
        entry["host"] = host
    return entry


# --- field_value_distribution ---

def test_field_value_distribution_returns_dict():
    entries = [make_entry("INFO"), make_entry("ERROR"), make_entry("INFO")]
    result = field_value_distribution(entries, "level")
    assert isinstance(result, dict)


def test_field_value_distribution_correct_counts():
    entries = [make_entry("INFO"), make_entry("ERROR"), make_entry("INFO")]
    result = field_value_distribution(entries, "level")
    assert result["INFO"] == 2
    assert result["ERROR"] == 1


def test_field_value_distribution_missing_field_skipped():
    entries = [make_entry(host="a"), make_entry(), make_entry(host="a")]
    result = field_value_distribution(entries, "host")
    assert result == {"a": 2}


def test_field_value_distribution_empty_entries():
    assert field_value_distribution([], "level") == {}


# --- field_coverage ---

def test_field_coverage_full():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    assert field_coverage(entries, "level") == 1.0


def test_field_coverage_partial():
    entries = [make_entry(host="x"), make_entry(), make_entry(host="y"), make_entry()]
    assert field_coverage(entries, "host") == 0.5


def test_field_coverage_empty_entries():
    assert field_coverage([], "level") == 0.0


def test_field_coverage_no_match():
    entries = [make_entry(), make_entry()]
    assert field_coverage(entries, "nonexistent") == 0.0


# --- all_fields ---

def test_all_fields_returns_sorted_list():
    entries = [{"b": 1, "a": 2}, {"c": 3}]
    result = all_fields(entries)
    assert result == ["a", "b", "c"]


def test_all_fields_empty_entries():
    assert all_fields([]) == []


# --- field_stats ---

def test_field_stats_returns_dict():
    entries = [make_entry("INFO"), make_entry("INFO"), make_entry("ERROR")]
    result = field_stats(entries, "level")
    assert isinstance(result, dict)


def test_field_stats_correct_count():
    entries = [make_entry("INFO"), make_entry("INFO"), make_entry("ERROR")]
    result = field_stats(entries, "level")
    assert result["count"] == 3


def test_field_stats_correct_unique():
    entries = [make_entry("INFO"), make_entry("INFO"), make_entry("ERROR")]
    result = field_stats(entries, "level")
    assert result["unique"] == 2


def test_field_stats_top_is_most_common():
    entries = [make_entry("INFO"), make_entry("INFO"), make_entry("ERROR")]
    result = field_stats(entries, "level")
    assert result["top"] == "INFO"
    assert result["top_count"] == 2


def test_field_stats_empty_returns_zeros():
    result = field_stats([], "level")
    assert result["count"] == 0
    assert result["top"] is None


# --- profile_entries ---

def test_profile_entries_returns_dict():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    result = profile_entries(entries)
    assert isinstance(result, dict)


def test_profile_entries_total_correct():
    entries = [make_entry(), make_entry(), make_entry()]
    result = profile_entries(entries)
    assert result["total"] == 3


def test_profile_entries_fields_present():
    entries = [make_entry()]
    result = profile_entries(entries)
    assert "level" in result["fields"]
    assert "message" in result["fields"]


def test_profile_entries_field_stats_included():
    entries = [make_entry("WARN")]
    result = profile_entries(entries)
    assert "level" in result["field_stats"]
    assert result["field_stats"]["level"]["top"] == "WARN"
