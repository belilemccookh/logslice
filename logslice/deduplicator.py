"""Deduplication utilities for log entries."""

from typing import List, Dict, Any, Optional
import hashlib
import json


def _entry_hash(entry: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """Compute a hash for a log entry based on specified fields or all fields."""
    if fields:
        subset = {k: entry.get(k) for k in fields}
    else:
        subset = {k: v for k, v in entry.items() if v is not None}

    serialized = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def deduplicate(entries: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Remove duplicate entries, keeping the first occurrence.

    Args:
        entries: List of parsed log entry dicts.
        fields: Optional list of field names to use for comparison.
                If None, all non-None fields are used.

    Returns:
        List of unique entries in original order.
    """
    seen = set()
    result = []
    for entry in entries:
        h = _entry_hash(entry, fields)
        if h not in seen:
            seen.add(h)
            result.append(entry)
    return result


def count_duplicates(entries: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> int:
    """Return the number of duplicate entries that would be removed.

    Args:
        entries: List of parsed log entry dicts.
        fields: Optional list of field names to use for comparison.

    Returns:
        Count of duplicate entries (total minus unique count).
    """
    unique = deduplicate(entries, fields)
    return len(entries) - len(unique)


def deduplicate_by_message(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to deduplicate entries based on the message field only."""
    return deduplicate(entries, fields=["message"])


def group_duplicates(entries: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Group duplicate entries and annotate each unique entry with a repeat count.

    Args:
        entries: List of parsed log entry dicts.
        fields: Optional list of field names to use for comparison.

    Returns:
        List of unique entries, each with an added '_count' field.
    """
    counts: Dict[str, int] = {}
    order: List[str] = []
    first: Dict[str, Dict[str, Any]] = {}

    for entry in entries:
        h = _entry_hash(entry, fields)
        if h not in counts:
            counts[h] = 0
            order.append(h)
            first[h] = entry
        counts[h] += 1

    result = []
    for h in order:
        annotated = dict(first[h])
        annotated["_count"] = counts[h]
        result.append(annotated)
    return result
