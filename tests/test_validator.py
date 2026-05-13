"""Tests for logslice.validator module."""

import pytest
from logslice.validator import (
    validate_entry,
    is_valid_entry,
    filter_valid,
    filter_invalid,
    validate_entries,
)


def make_entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00", "level": "INFO", "message": "ok"}
    base.update(kwargs)
    return base


def test_validate_entry_valid_returns_true():
    valid, errors = validate_entry(make_entry())
    assert valid is True
    assert errors == []


def test_validate_entry_missing_timestamp_returns_error():
    entry = {"level": "INFO", "message": "test"}
    valid, errors = validate_entry(entry)
    assert valid is False
    assert any("timestamp" in e for e in errors)


def test_validate_entry_missing_level_returns_error():
    entry = {"timestamp": "2024-01-01", "message": "test"}
    valid, errors = validate_entry(entry)
    assert valid is False
    assert any("level" in e for e in errors)


def test_validate_entry_missing_message_returns_error():
    entry = {"timestamp": "2024-01-01", "level": "INFO"}
    valid, errors = validate_entry(entry)
    assert valid is False
    assert any("message" in e for e in errors)


def test_validate_entry_invalid_level_returns_error():
    entry = make_entry(level="VERBOSE")
    valid, errors = validate_entry(entry)
    assert valid is False
    assert any("Invalid level" in e for e in errors)


def test_validate_entry_level_case_insensitive():
    entry = make_entry(level="error")
    valid, errors = validate_entry(entry)
    assert valid is True


def test_validate_entry_none_field_is_invalid():
    entry = make_entry(timestamp=None)
    valid, errors = validate_entry(entry)
    assert valid is False


def test_validate_entry_custom_required_fields():
    entry = {"timestamp": "2024-01-01", "level": "INFO", "message": "ok"}
    valid, errors = validate_entry(entry, required_fields=["host"])
    assert valid is False
    assert any("host" in e for e in errors)


def test_validate_entry_custom_valid_levels():
    entry = make_entry(level="TRACE")
    valid, errors = validate_entry(entry, valid_levels={"TRACE", "DEBUG"})
    assert valid is True


def test_is_valid_entry_true_for_valid():
    assert is_valid_entry(make_entry()) is True


def test_is_valid_entry_false_for_invalid():
    assert is_valid_entry({"message": "no timestamp or level"}) is False


def test_filter_valid_returns_only_valid_entries():
    entries = [
        make_entry(),
        {"message": "missing fields"},
        make_entry(level="ERROR"),
    ]
    result = filter_valid(entries)
    assert len(result) == 2


def test_filter_valid_empty_returns_empty():
    assert filter_valid([]) == []


def test_filter_invalid_returns_only_invalid_entries():
    entries = [
        make_entry(),
        {"message": "missing fields"},
    ]
    result = filter_invalid(entries)
    assert len(result) == 1
    assert result[0]["message"] == "missing fields"


def test_validate_entries_returns_tuples():
    entries = [make_entry(), {"message": "bad"}]
    result = validate_entries(entries)
    assert len(result) == 2
    assert result[0][1] is True
    assert result[1][1] is False


def test_validate_entries_empty_returns_empty():
    assert validate_entries([]) == []
