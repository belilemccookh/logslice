"""Tests for logslice.redactor."""

import re
import pytest
from logslice.redactor import (
    redact_value,
    redact_entry,
    redact_entries,
    mask_field,
    REDACT_PLACEHOLDER,
    DEFAULT_PATTERNS,
)


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_masks_email():
    result = redact_value("user contact: alice@example.com")
    assert "alice@example.com" not in result
    assert REDACT_PLACEHOLDER in result


def test_redact_value_masks_ip():
    result = redact_value("request from 192.168.1.42")
    assert "192.168.1.42" not in result
    assert REDACT_PLACEHOLDER in result


def test_redact_value_no_sensitive_data_unchanged():
    text = "nothing sensitive here"
    assert redact_value(text) == text


def test_redact_value_non_string_returned_as_is():
    assert redact_value(42) == 42
    assert redact_value(None) is None


def test_redact_value_custom_pattern():
    custom = {"ssn": re.compile(r"\d{3}-\d{2}-\d{4}")}
    result = redact_value("ssn: 123-45-6789", patterns=custom)
    assert "123-45-6789" not in result
    assert REDACT_PLACEHOLDER in result


def test_redact_value_custom_pattern_does_not_apply_defaults():
    custom = {"ssn": re.compile(r"\d{3}-\d{2}-\d{4}")}
    # email should NOT be redacted when custom patterns are given
    result = redact_value("email: bob@test.com", patterns=custom)
    assert "bob@test.com" in result


# ---------------------------------------------------------------------------
# redact_entry
# ---------------------------------------------------------------------------

def test_redact_entry_returns_dict():
    entry = {"level": "INFO", "message": "hello"}
    assert isinstance(redact_entry(entry), dict)


def test_redact_entry_does_not_mutate_original():
    entry = {"message": "ip 10.0.0.1"}
    redact_entry(entry)
    assert "10.0.0.1" in entry["message"]


def test_redact_entry_redacts_message_field():
    entry = {"level": "ERROR", "message": "failed for user@domain.org"}
    result = redact_entry(entry)
    assert REDACT_PLACEHOLDER in result["message"]


def test_redact_entry_specific_fields_only():
    entry = {"message": "ip 10.0.0.1", "raw": "ip 10.0.0.1"}
    result = redact_entry(entry, fields=["message"])
    assert REDACT_PLACEHOLDER in result["message"]
    # raw should be untouched
    assert "10.0.0.1" in result["raw"]


def test_redact_entry_skips_non_string_values():
    entry = {"level": "INFO", "count": 5}
    result = redact_entry(entry)
    assert result["count"] == 5


# ---------------------------------------------------------------------------
# redact_entries
# ---------------------------------------------------------------------------

def test_redact_entries_returns_list():
    entries = [{"message": "hello"}, {"message": "world"}]
    assert isinstance(redact_entries(entries), list)


def test_redact_entries_correct_length():
    entries = [{"message": f"user{i}@example.com"} for i in range(5)]
    result = redact_entries(entries)
    assert len(result) == 5


def test_redact_entries_all_redacted():
    entries = [{"message": "contact me@here.io"}, {"message": "also you@there.net"}]
    result = redact_entries(entries)
    for entry in result:
        assert REDACT_PLACEHOLDER in entry["message"]


# ---------------------------------------------------------------------------
# mask_field
# ---------------------------------------------------------------------------

def test_mask_field_replaces_value():
    entries = [{"user": "alice"}, {"user": "bob"}]
    result = mask_field(entries, "user")
    for entry in result:
        assert entry["user"] == REDACT_PLACEHOLDER


def test_mask_field_missing_key_unchanged():
    entries = [{"level": "INFO"}]
    result = mask_field(entries, "user")
    assert "user" not in result[0]


def test_mask_field_custom_placeholder():
    entries = [{"token": "abc123"}]
    result = mask_field(entries, "token", placeholder="***")
    assert result[0]["token"] == "***"


def test_mask_field_does_not_mutate_original():
    entries = [{"user": "alice"}]
    mask_field(entries, "user")
    assert entries[0]["user"] == "alice"
