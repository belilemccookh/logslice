"""Tests for logslice.formatter module."""

import json
import pytest

from logslice.formatter import format_entry, format_entries, SUPPORTED_FORMATS


SAMPLE_ENTRY = {
    "timestamp": "2024-01-15 10:30:00",
    "level": "ERROR",
    "message": "Connection refused",
    "host": None,
}

SAMPLE_ENTRIES = [
    {"timestamp": "2024-01-15 10:00:00", "level": "INFO", "message": "Started"},
    {"timestamp": "2024-01-15 10:01:00", "level": "WARN", "message": "Slow query"},
    {"timestamp": "2024-01-15 10:02:00", "level": "ERROR", "message": "Timeout"},
]


def test_format_entry_text_returns_string():
    result = format_entry(SAMPLE_ENTRY, fmt="text")
    assert isinstance(result, str)


def test_format_entry_text_contains_fields():
    result = format_entry(SAMPLE_ENTRY, fmt="text")
    assert "timestamp=2024-01-15 10:30:00" in result
    assert "level=ERROR" in result
    assert "message=Connection refused" in result


def test_format_entry_text_skips_none_values():
    result = format_entry(SAMPLE_ENTRY, fmt="text")
    assert "host" not in result


def test_format_entry_json_is_valid():
    result = format_entry(SAMPLE_ENTRY, fmt="json")
    parsed = json.loads(result)
    assert parsed["level"] == "ERROR"
    assert parsed["message"] == "Connection refused"


def test_format_entry_csv_contains_values():
    result = format_entry(SAMPLE_ENTRY, fmt="csv")
    assert "ERROR" in result
    assert "Connection refused" in result
    assert "\t" not in result


def test_format_entry_tsv_uses_tab_delimiter():
    result = format_entry(SAMPLE_ENTRY, fmt="tsv")
    assert "\t" in result


def test_format_entry_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_entry(SAMPLE_ENTRY, fmt="xml")


def test_format_entries_empty_returns_empty_string():
    assert format_entries([], fmt="json") == ""
    assert format_entries([], fmt="text") == ""


def test_format_entries_json_returns_list():
    result = format_entries(SAMPLE_ENTRIES, fmt="json")
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 3
    assert parsed[0]["level"] == "INFO"


def test_format_entries_text_returns_multiline():
    result = format_entries(SAMPLE_ENTRIES, fmt="text")
    lines = result.splitlines()
    assert len(lines) == 3


def test_format_entries_csv_with_header():
    result = format_entries(SAMPLE_ENTRIES, fmt="csv", include_header=True)
    lines = result.splitlines()
    assert lines[0] == "timestamp,level,message"
    assert len(lines) == 4  # header + 3 entries


def test_format_entries_csv_without_header():
    result = format_entries(SAMPLE_ENTRIES, fmt="csv", include_header=False)
    lines = result.splitlines()
    assert len(lines) == 3


def test_format_entries_tsv_with_header():
    result = format_entries(SAMPLE_ENTRIES, fmt="tsv", include_header=True)
    header = result.splitlines()[0]
    assert "\t" in header
