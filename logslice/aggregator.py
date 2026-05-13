"""Aggregation utilities for grouped log analysis."""

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional


def count_by_field(entries: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count log entries grouped by a specific field value.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field name to group and count by.

    Returns:
        A dict mapping field values to their occurrence counts.
    """
    counter: Counter = Counter()
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            counter[str(value)] += 1
    return dict(counter)


def group_by_field(
    entries: Iterable[Dict[str, Any]], field: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Group log entries by a specific field value.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field name to group by.

    Returns:
        A dict mapping field values to lists of matching entries.
    """
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            groups[str(value)].append(entry)
    return dict(groups)


def summarize(
    entries: Iterable[Dict[str, Any]],
    group_field: str = "level",
    count_field: Optional[str] = None,
) -> Dict[str, Any]:
    """Produce a summary report of log entries.

    Args:
        entries: Iterable of parsed log entry dicts.
        group_field: Field to group entries by (default: 'level').
        count_field: Optional additional field to count unique values for.

    Returns:
        A summary dict with total count, grouped counts, and optional field counts.
    """
    entry_list = list(entries)
    summary: Dict[str, Any] = {
        "total": len(entry_list),
        "by_" + group_field: count_by_field(entry_list, group_field),
    }
    if count_field:
        summary["by_" + count_field] = count_by_field(entry_list, count_field)
    return summary
