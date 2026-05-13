"""Inspect individual log entries for anomalies and properties."""

from typing import Any


SEVERE_LEVELS = {"error", "critical", "fatal", "exception"}
WARN_LEVELS = {"warn", "warning"}


def is_severe(entry: dict) -> bool:
    """Return True if the entry's level indicates a severe condition."""
    level = entry.get("level", "")
    return str(level).lower() in SEVERE_LEVELS


def is_warning(entry: dict) -> bool:
    """Return True if the entry's level is a warning."""
    level = entry.get("level", "")
    return str(level).lower() in WARN_LEVELS


def has_field(entry: dict, field: str) -> bool:
    """Return True if the entry contains the given field with a non-None value."""
    return entry.get(field) is not None


def is_complete(entry: dict, required: list[str] | None = None) -> bool:
    """Return True if all required fields are present and non-None."""
    if required is None:
        required = ["timestamp", "level", "message"]
    return all(has_field(entry, f) for f in required)


def missing_fields(entry: dict, required: list[str] | None = None) -> list[str]:
    """Return a list of required fields that are missing from the entry."""
    if required is None:
        required = ["timestamp", "level", "message"]
    return [f for f in required if not has_field(entry, f)]


def entry_size(entry: dict) -> int:
    """Return the total character length of all string values in the entry."""
    return sum(len(str(v)) for v in entry.values() if v is not None)


def find_anomalies(entries: list[dict]) -> list[dict]:
    """Return entries that are incomplete or have a severe level."""
    return [
        e for e in entries
        if not is_complete(e) or is_severe(e)
    ]


def summarize_entry(entry: dict) -> dict[str, Any]:
    """Return a brief summary dict describing key properties of an entry."""
    return {
        "severe": is_severe(entry),
        "warning": is_warning(entry),
        "complete": is_complete(entry),
        "missing": missing_fields(entry),
        "size": entry_size(entry),
    }
