"""Tests for logslice.filter module."""

import pytest
from datetime import datetime
from logslice.filter import (
    filter_by_level,
    filter_by_levels,
    filter_by_pattern,
    filter_by_time_range,
    filter_by_field,
    apply_filters,
)

SAMPLE_ENTRIES = [
    {"timestamp": "2024-01-15 10:00:00", "level": "INFO", "message": "Server started"},
    {"timestamp": "2024-01-15 10:01:00", "level": "DEBUG", "message": "Connecting to DB"},
    {"timestamp": "2024-01-15 10:02:00", "level": "ERROR", "message": "Connection refused"},
    {"timestamp": "2024-01-15 10:03:00", "level": "WARNING", "message": "Retry attempt 1"},
    {"timestamp": "2024-01-15 10:04:00", "level": "INFO", "message": "Request received from 192.168.1.1"},
]


def test_filter_by_level_returns_matching():
    result = filter_by_level(SAMPLE_ENTRIES, "INFO")
    assert len(result) == 2
    assert all(e["level"] == "INFO" for e in result)


def test_filter_by_level_case_insensitive():
    result = filter_by_level(SAMPLE_ENTRIES, "error")
    assert len(result) == 1
    assert result[0]["message"] == "Connection refused"


def test_filter_by_level_no_match():
    result = filter_by_level(SAMPLE_ENTRIES, "CRITICAL")
    assert result == []


def test_filter_by_levels_multiple():
    result = filter_by_levels(SAMPLE_ENTRIES, ["ERROR", "WARNING"])
    assert len(result) == 2
    levels = {e["level"] for e in result}
    assert levels == {"ERROR", "WARNING"}


def test_filter_by_pattern_message():
    result = filter_by_pattern(SAMPLE_ENTRIES, r"Connection")
    assert len(result) == 2


def test_filter_by_pattern_regex():
    result = filter_by_pattern(SAMPLE_ENTRIES, r"\d{1,3}\.\d{1,3}")
    assert len(result) == 1
    assert "192.168.1.1" in result[0]["message"]


def test_filter_by_pattern_no_match():
    result = filter_by_pattern(SAMPLE_ENTRIES, r"nonexistent_xyz")
    assert result == []


def test_filter_by_time_range_start_only():
    start = datetime(2024, 1, 15, 10, 2, 0)
    result = filter_by_time_range(SAMPLE_ENTRIES, start=start)
    assert len(result) == 3


def test_filter_by_time_range_end_only():
    end = datetime(2024, 1, 15, 10, 1, 0)
    result = filter_by_time_range(SAMPLE_ENTRIES, end=end)
    assert len(result) == 2


def test_filter_by_time_range_both():
    start = datetime(2024, 1, 15, 10, 1, 0)
    end = datetime(2024, 1, 15, 10, 3, 0)
    result = filter_by_time_range(SAMPLE_ENTRIES, start=start, end=end)
    assert len(result) == 3


def test_filter_by_time_range_skips_missing_timestamp():
    entries = [{"level": "INFO", "message": "no timestamp"}]
    result = filter_by_time_range(entries, start=datetime(2024, 1, 1))
    assert result == []


def test_filter_by_field():
    result = filter_by_field(SAMPLE_ENTRIES, "level", "DEBUG")
    assert len(result) == 1
    assert result[0]["message"] == "Connecting to DB"


def test_apply_filters_chaining():
    f1 = lambda entries: filter_by_levels(entries, ["INFO", "ERROR"])
    f2 = lambda entries: filter_by_pattern(entries, r"Server")
    result = apply_filters(SAMPLE_ENTRIES, f1, f2)
    assert len(result) == 1
    assert result[0]["message"] == "Server started"


def test_apply_filters_empty_pipeline():
    result = apply_filters(SAMPLE_ENTRIES)
    assert result == SAMPLE_ENTRIES
