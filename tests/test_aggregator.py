"""Tests for logslice.aggregator module."""

import pytest
from logslice.aggregator import count_by_field, group_by_field, summarize


SAMPLE_ENTRIES = [
    {"level": "ERROR", "message": "Disk full", "host": "web01"},
    {"level": "INFO", "message": "Started", "host": "web01"},
    {"level": "ERROR", "message": "Connection refused", "host": "db01"},
    {"level": "WARN", "message": "High memory", "host": "web01"},
    {"level": "INFO", "message": "Stopped", "host": "db01"},
    {"level": "ERROR", "message": "Timeout", "host": "web02"},
]


def test_count_by_field_returns_dict():
    result = count_by_field(SAMPLE_ENTRIES, "level")
    assert isinstance(result, dict)


def test_count_by_field_correct_counts():
    result = count_by_field(SAMPLE_ENTRIES, "level")
    assert result["ERROR"] == 3
    assert result["INFO"] == 2
    assert result["WARN"] == 1


def test_count_by_field_missing_field_skipped():
    entries = [{"level": "INFO"}, {"message": "no level here"}, {"level": "ERROR"}]
    result = count_by_field(entries, "level")
    assert result == {"INFO": 1, "ERROR": 1}


def test_count_by_field_empty_entries():
    result = count_by_field([], "level")
    assert result == {}


def test_group_by_field_returns_dict_of_lists():
    result = group_by_field(SAMPLE_ENTRIES, "level")
    assert isinstance(result, dict)
    assert all(isinstance(v, list) for v in result.values())


def test_group_by_field_correct_grouping():
    result = group_by_field(SAMPLE_ENTRIES, "level")
    assert len(result["ERROR"]) == 3
    assert len(result["INFO"]) == 2
    assert len(result["WARN"]) == 1


def test_group_by_field_entries_preserved():
    result = group_by_field(SAMPLE_ENTRIES, "host")
    assert len(result["web01"]) == 3
    assert result["web01"][0]["message"] == "Disk full"


def test_group_by_field_skips_missing():
    entries = [{"level": "INFO"}, {"message": "orphan"}]
    result = group_by_field(entries, "level")
    assert "INFO" in result
    assert len(result) == 1


def test_summarize_includes_total():
    result = summarize(SAMPLE_ENTRIES)
    assert result["total"] == 6


def test_summarize_default_group_by_level():
    result = summarize(SAMPLE_ENTRIES)
    assert "by_level" in result
    assert result["by_level"]["ERROR"] == 3


def test_summarize_custom_group_field():
    result = summarize(SAMPLE_ENTRIES, group_field="host")
    assert "by_host" in result
    assert result["by_host"]["web01"] == 3


def test_summarize_with_count_field():
    result = summarize(SAMPLE_ENTRIES, group_field="level", count_field="host")
    assert "by_host" in result
    assert result["by_host"]["db01"] == 2


def test_summarize_empty_entries():
    result = summarize([])
    assert result["total"] == 0
    assert result["by_level"] == {}
