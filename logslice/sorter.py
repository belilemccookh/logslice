"""Sorting utilities for log entries."""

from typing import List, Dict, Any, Optional
from datetime import datetime


def sort_by_field(
    entries: List[Dict[str, Any]],
    field: str,
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Sort entries by a given field. Entries missing the field are placed last."""
    missing, present = [], []
    for entry in entries:
        (missing if entry.get(field) is None else present).append(entry)
    sorted_present = sorted(present, key=lambda e: e[field], reverse=reverse)
    return sorted_present + missing


def sort_by_timestamp(
    entries: List[Dict[str, Any]],
    fmt: Optional[str] = None,
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Sort entries by the 'timestamp' field, optionally parsing with a format string."""
    def _key(entry: Dict[str, Any]):
        ts = entry.get("timestamp")
        if ts is None:
            return datetime.max
        if fmt:
            try:
                return datetime.strptime(ts, fmt)
            except (ValueError, TypeError):
                return datetime.max
        return ts

    return sorted(entries, key=_key, reverse=reverse)


def sort_by_level(
    entries: List[Dict[str, Any]],
    level_order: Optional[List[str]] = None,
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Sort entries by severity level using a custom or default order."""
    default_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    order = [lvl.upper() for lvl in (level_order or default_order)]

    def _key(entry: Dict[str, Any]) -> int:
        level = (entry.get("level") or "").upper()
        try:
            return order.index(level)
        except ValueError:
            return len(order)

    return sorted(entries, key=_key, reverse=reverse)


def sort_entries(
    entries: List[Dict[str, Any]],
    by: str = "timestamp",
    reverse: bool = False,
    **kwargs: Any
) -> List[Dict[str, Any]]:
    """Unified sort dispatcher. Supports 'timestamp', 'level', or any field name."""
    if by == "timestamp":
        return sort_by_timestamp(entries, reverse=reverse, **kwargs)
    if by == "level":
        return sort_by_level(entries, reverse=reverse, **kwargs)
    return sort_by_field(entries, field=by, reverse=reverse)
