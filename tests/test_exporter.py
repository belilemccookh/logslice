"""Tests for logslice.exporter module."""

import json
import pytest
from logslice.exporter import (
    export_to_json,
    export_to_csv,
    export_to_text,
    export_entries,
)

SAMPLE_ENTRIES = [
    {"timestamp": "2024-01-01 10:00:00", "level": "INFO", "message": "Server started"},
    {"timestamp": "2024-01-01 10:01:00", "level": "ERROR", "message": "Disk full"},
    {"timestamp": "2024-01-01 10:02:00", "level": "DEBUG", "message": None},
]


def test_export_to_json_returns_string():
    result = export_to_json(SAMPLE_ENTRIES)
    assert isinstance(result, str)


def test_export_to_json_is_valid_json():
    result = export_to_json(SAMPLE_ENTRIES)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 3


def test_export_to_json_omits_none_values():
    result = export_to_json(SAMPLE_ENTRIES)
    parsed = json.loads(result)
    assert "message" not in parsed[2]


def test_export_to_json_custom_indent():
    result = export_to_json(SAMPLE_ENTRIES, indent=4)
    assert "    " in result


def test_export_to_csv_returns_string():
    result = export_to_csv(SAMPLE_ENTRIES)
    assert isinstance(result, str)


def test_export_to_csv_has_header():
    result = export_to_csv(SAMPLE_ENTRIES)
    first_line = result.splitlines()[0]
    assert "timestamp" in first_line
    assert "level" in first_line


def test_export_to_csv_row_count():
    result = export_to_csv(SAMPLE_ENTRIES)
    lines = result.strip().splitlines()
    # header + 3 data rows
    assert len(lines) == 4


def test_export_to_csv_custom_fields():
    result = export_to_csv(SAMPLE_ENTRIES, fields=["level", "message"])
    first_line = result.splitlines()[0]
    assert first_line == "level,message"


def test_export_to_csv_empty_entries():
    result = export_to_csv([])
    assert result == ""


def test_export_to_text_returns_string():
    result = export_to_text(SAMPLE_ENTRIES)
    assert isinstance(result, str)


def test_export_to_text_line_count():
    result = export_to_text(SAMPLE_ENTRIES)
    assert len(result.splitlines()) == 3


def test_export_to_text_contains_values():
    result = export_to_text(SAMPLE_ENTRIES)
    assert "INFO" in result
    assert "Server started" in result


def test_export_to_text_skips_none():
    result = export_to_text(SAMPLE_ENTRIES)
    assert "message=None" not in result


def test_export_entries_json():
    result = export_entries(SAMPLE_ENTRIES, fmt="json")
    json.loads(result)  # should not raise


def test_export_entries_csv():
    result = export_entries(SAMPLE_ENTRIES, fmt="csv")
    assert "level" in result.splitlines()[0]


def test_export_entries_text():
    result = export_entries(SAMPLE_ENTRIES, fmt="text")
    assert "ERROR" in result


def test_export_entries_invalid_format():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_entries(SAMPLE_ENTRIES, fmt="xml")


def test_export_entries_case_insensitive_format():
    result = export_entries(SAMPLE_ENTRIES, fmt="JSON")
    json.loads(result)  # should not raise
