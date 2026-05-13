"""Merger module for combining multiple log entry lists into a unified stream."""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


def merge_entries(
    *entry_lists: List[Dict[str, Any]],
    deduplicate: bool = False
) -> List[Dict[str, Any]]:
    """Merge multiple entry lists into a single flat list."""
    merged: List[Dict[str, Any]] = []
    seen: set = set()

    for entries in entry_lists:
        for entry in entries:
            if deduplicate:
                key = (entry.get("timestamp"), entry.get("level"), entry.get("message"))
                if key in seen:
                    continue
                seen.add(key)
            merged.append(entry)

    return merged


def merge_sorted(
    *entry_lists: List[Dict[str, Any]],
    key: str = "timestamp",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Merge and sort multiple entry lists by a given field."""
    merged = merge_entries(*entry_lists)

    def sort_key(entry: Dict[str, Any]) -> Any:
        value = entry.get(key)
        if value is None:
            return (1, "") if not reverse else (0, "")
        return (0, value) if not reverse else (1, value)

    return sorted(merged, key=sort_key, reverse=reverse)


def merge_with_source(
    labeled: List[tuple],
) -> List[Dict[str, Any]]:
    """Merge entries from labeled sources, injecting a '_source' field.

    Args:
        labeled: list of (source_name, entries) tuples
    """
    result: List[Dict[str, Any]] = []
    for source_name, entries in labeled:
        for entry in entries:
            enriched = dict(entry)
            enriched["_source"] = source_name
            result.append(enriched)
    return result


def merge_by_priority(
    *entry_lists: List[Dict[str, Any]],
    level_order: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Merge entries and sort by log level priority (highest first)."""
    default_order = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    order = [l.upper() for l in (level_order or default_order)]

    def priority(entry: Dict[str, Any]) -> int:
        level = (entry.get("level") or "").upper()
        try:
            return order.index(level)
        except ValueError:
            return len(order)

    merged = merge_entries(*entry_lists)
    return sorted(merged, key=priority)
