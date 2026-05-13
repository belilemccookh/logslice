"""Counter utilities for tracking log entry statistics."""

from collections import Counter
from typing import Any, Dict, List, Optional


def count_entries(entries: List[Dict[str, Any]]) -> int:
    """Return the total number of entries."""
    return len(entries)


def count_by_level(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count entries grouped by their log level."""
    counts: Dict[str, int] = {}
    for entry in entries:
        level = entry.get("level")
        if level is not None:
            key = str(level).upper()
            counts[key] = counts.get(key, 0) + 1
    return counts


def count_errors(entries: List[Dict[str, Any]]) -> int:
    """Count entries where level is ERROR or CRITICAL."""
    error_levels = {"ERROR", "CRITICAL", "FATAL"}
    return sum(
        1 for e in entries
        if str(e.get("level", "")).upper() in error_levels
    )


def count_warnings(entries: List[Dict[str, Any]]) -> int:
    """Count entries where level is WARNING or WARN."""
    warn_levels = {"WARNING", "WARN"}
    return sum(
        1 for e in entries
        if str(e.get("level", "")).upper() in warn_levels
    )


def count_by_field_value(
    entries: List[Dict[str, Any]],
    field: str,
    value: Any,
) -> int:
    """Count entries where the given field equals the given value."""
    return sum(1 for e in entries if e.get(field) == value)


def frequency_table(
    entries: List[Dict[str, Any]],
    field: str,
    top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return a frequency table for a field, sorted by count descending.

    Each item in the result is a dict with 'value' and 'count'.
    """
    counter: Counter = Counter()
    for entry in entries:
        val = entry.get(field)
        if val is not None:
            counter[val] += 1
    items = [{"value": v, "count": c} for v, c in counter.most_common(top_n)]
    return items
