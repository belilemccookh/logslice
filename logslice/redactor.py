"""Redactor module for masking sensitive data in log entries."""

import re
from typing import Any, Dict, List, Optional

# Default patterns for common sensitive fields
DEFAULT_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "token": re.compile(r"(?i)(?:token|api[_-]?key|secret)[=:\s]+\S+"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}

REDACT_PLACEHOLDER = "[REDACTED]"


def redact_value(value: str, patterns: Optional[Dict[str, re.Pattern]] = None) -> str:
    """Replace sensitive patterns in a string value with a placeholder."""
    if not isinstance(value, str):
        return value
    active_patterns = patterns if patterns is not None else DEFAULT_PATTERNS
    result = value
    for pattern in active_patterns.values():
        result = pattern.sub(REDACT_PLACEHOLDER, result)
    return result


def redact_entry(
    entry: Dict[str, Any],
    fields: Optional[List[str]] = None,
    patterns: Optional[Dict[str, re.Pattern]] = None,
) -> Dict[str, Any]:
    """Redact sensitive data from a single log entry dict.

    If `fields` is provided, only those keys are scanned.
    Otherwise all string-valued keys are scanned.
    """
    redacted = dict(entry)
    keys_to_scan = fields if fields is not None else list(redacted.keys())
    for key in keys_to_scan:
        if key in redacted and isinstance(redacted[key], str):
            redacted[key] = redact_value(redacted[key], patterns)
    return redacted


def redact_entries(
    entries: List[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    patterns: Optional[Dict[str, re.Pattern]] = None,
) -> List[Dict[str, Any]]:
    """Redact sensitive data from a list of log entry dicts."""
    return [redact_entry(entry, fields=fields, patterns=patterns) for entry in entries]


def mask_field(
    entries: List[Dict[str, Any]], field: str, placeholder: str = REDACT_PLACEHOLDER
) -> List[Dict[str, Any]]:
    """Unconditionally replace the value of `field` in every entry."""
    result = []
    for entry in entries:
        copy = dict(entry)
        if field in copy:
            copy[field] = placeholder
        result.append(copy)
    return result
