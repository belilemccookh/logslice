"""Filter utilities for parsed log entries."""

import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


def filter_by_level(entries: List[Dict[str, Any]], level: str) -> List[Dict[str, Any]]:
    """Filter log entries by log level (case-insensitive)."""
    level_upper = level.upper()
    return [e for e in entries if e.get("level", "").upper() == level_upper]


def filter_by_levels(entries: List[Dict[str, Any]], levels: List[str]) -> List[Dict[str, Any]]:
    """Filter log entries by a list of log levels (case-insensitive)."""
    levels_upper = {l.upper() for l in levels}
    return [e for e in entries if e.get("level", "").upper() in levels_upper]


def filter_by_pattern(entries: List[Dict[str, Any]], pattern: str, field: str = "message") -> List[Dict[str, Any]]:
    """Filter log entries where the given field matches a regex pattern."""
    compiled = re.compile(pattern)
    return [e for e in entries if compiled.search(str(e.get(field, "")))]


def filter_by_time_range(
    entries: List[Dict[str, Any]],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    time_field: str = "timestamp",
    time_format: str = "%Y-%m-%d %H:%M:%S",
) -> List[Dict[str, Any]]:
    """Filter log entries within an optional start/end datetime range."""
    result = []
    for entry in entries:
        raw = entry.get(time_field)
        if raw is None:
            continue
        try:
            ts = datetime.strptime(raw, time_format)
        except (ValueError, TypeError):
            continue
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        result.append(entry)
    return result


def filter_by_field(entries: List[Dict[str, Any]], field: str, value: Any) -> List[Dict[str, Any]]:
    """Filter log entries where a specific field equals the given value."""
    return [e for e in entries if e.get(field) == value]


def apply_filters(entries: List[Dict[str, Any]], *filters: Callable) -> List[Dict[str, Any]]:
    """Apply multiple filter functions sequentially to a list of entries."""
    result = entries
    for f in filters:
        result = f(result)
    return result
