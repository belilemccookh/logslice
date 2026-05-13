"""Entry validation utilities for log entries."""

from typing import Any, Dict, List, Optional, Tuple

REQUIRED_FIELDS = ["timestamp", "level", "message"]
VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def validate_entry(
    entry: Dict,
    required_fields: Optional[List[str]] = None,
    valid_levels: Optional[set] = None,
) -> Tuple[bool, List[str]]:
    """Validate a single log entry. Returns (is_valid, list_of_errors)."""
    errors = []
    fields = required_fields if required_fields is not None else REQUIRED_FIELDS
    levels = valid_levels if valid_levels is not None else VALID_LEVELS

    for field in fields:
        if field not in entry or entry[field] is None:
            errors.append(f"Missing required field: '{field}'")

    if "level" in entry and entry["level"] is not None:
        if entry["level"].upper() not in levels:
            errors.append(f"Invalid level value: '{entry['level']}'")

    return (len(errors) == 0, errors)


def is_valid_entry(entry: Dict, **kwargs) -> bool:
    """Return True if the entry passes validation."""
    valid, _ = validate_entry(entry, **kwargs)
    return valid


def filter_valid(entries: List[Dict], **kwargs) -> List[Dict]:
    """Return only entries that pass validation."""
    return [e for e in entries if is_valid_entry(e, **kwargs)]


def filter_invalid(entries: List[Dict], **kwargs) -> List[Dict]:
    """Return only entries that fail validation."""
    return [e for e in entries if not is_valid_entry(e, **kwargs)]


def validate_entries(
    entries: List[Dict], **kwargs
) -> List[Tuple[Dict, bool, List[str]]]:
    """Return a list of (entry, is_valid, errors) tuples for all entries."""
    return [(e, *validate_entry(e, **kwargs)) for e in entries]
