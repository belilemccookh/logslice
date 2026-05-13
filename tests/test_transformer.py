"""Tests for logslice.transformer module."""

import pytest
from logslice.transformer import (
    rename_field,
    drop_fields,
    keep_fields,
    apply_field,
    add_field,
    normalize_level,
    transform_entries,
)


def make_entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00", "level": "info", "message": "test"}
    base.update(kwargs)
    return base


def test_rename_field_renames_existing_key():
    entry = make_entry(host="localhost")
    result = rename_field(entry, "host", "hostname")
    assert "hostname" in result
    assert "host" not in result


def test_rename_field_preserves_value():
    entry = make_entry(host="localhost")
    result = rename_field(entry, "host", "hostname")
    assert result["hostname"] == "localhost"


def test_rename_field_missing_key_unchanged():
    entry = make_entry()
    result = rename_field(entry, "nonexistent", "new_name")
    assert "new_name" not in result
    assert result == entry


def test_rename_field_does_not_mutate_original():
    entry = make_entry(host="localhost")
    rename_field(entry, "host", "hostname")
    assert "host" in entry


def test_drop_fields_removes_listed_keys():
    entry = make_entry(host="localhost", pid="123")
    result = drop_fields(entry, ["host", "pid"])
    assert "host" not in result
    assert "pid" not in result


def test_drop_fields_keeps_unlisted_keys():
    entry = make_entry(host="localhost")
    result = drop_fields(entry, ["host"])
    assert "timestamp" in result
    assert "level" in result
    assert "message" in result


def test_drop_fields_missing_keys_ignored():
    entry = make_entry()
    result = drop_fields(entry, ["nonexistent"])
    assert result == entry


def test_keep_fields_returns_only_listed_keys():
    entry = make_entry(host="localhost")
    result = keep_fields(entry, ["level", "message"])
    assert set(result.keys()) == {"level", "message"}


def test_keep_fields_missing_keys_omitted():
    entry = make_entry()
    result = keep_fields(entry, ["level", "nonexistent"])
    assert "nonexistent" not in result
    assert "level" in result


def test_apply_field_transforms_value():
    entry = make_entry(message="hello")
    result = apply_field(entry, "message", str.upper)
    assert result["message"] == "HELLO"


def test_apply_field_missing_key_unchanged():
    entry = make_entry()
    result = apply_field(entry, "nonexistent", str.upper)
    assert result == entry


def test_apply_field_none_value_skipped():
    entry = make_entry(host=None)
    result = apply_field(entry, "host", str.upper)
    assert result["host"] is None


def test_add_field_inserts_new_key():
    entry = make_entry()
    result = add_field(entry, "env", "production")
    assert result["env"] == "production"


def test_add_field_does_not_mutate_original():
    entry = make_entry()
    add_field(entry, "env", "production")
    assert "env" not in entry


def test_normalize_level_uppercases_level():
    entry = make_entry(level="warning")
    result = normalize_level(entry)
    assert result["level"] == "WARNING"


def test_normalize_level_custom_field():
    entry = make_entry(severity="debug")
    result = normalize_level(entry, field="severity")
    assert result["severity"] == "DEBUG"


def test_transform_entries_applies_all_transforms():
    entries = [make_entry(level="error", host="srv")]
    transforms = [
        normalize_level,
        lambda e: drop_fields(e, ["host"]),
    ]
    result = transform_entries(entries, transforms)
    assert result[0]["level"] == "ERROR"
    assert "host" not in result[0]


def test_transform_entries_empty_list_returns_empty():
    result = transform_entries([], [normalize_level])
    assert result == []


def test_transform_entries_no_transforms_unchanged():
    entries = [make_entry()]
    result = transform_entries(entries, [])
    assert result == entries
