"""Field transformation utilities for log entries."""

import re
from typing import Any, Callable, Dict, List, Optional


def rename_field(entry: Dict, old_key: str, new_key: str) -> Dict:
    """Return a new entry with old_key renamed to new_key."""
    result = dict(entry)
    if old_key in result:
        result[new_key] = result.pop(old_key)
    return result


def drop_fields(entry: Dict, fields: List[str]) -> Dict:
    """Return a new entry with specified fields removed."""
    return {k: v for k, v in entry.items() if k not in fields}


def keep_fields(entry: Dict, fields: List[str]) -> Dict:
    """Return a new entry containing only the specified fields."""
    return {k: entry[k] for k in fields if k in entry}


def apply_field(entry: Dict, field: str, func: Callable[[Any], Any]) -> Dict:
    """Return a new entry with func applied to the value of field."""
    result = dict(entry)
    if field in result and result[field] is not None:
        result[field] = func(result[field])
    return result


def add_field(entry: Dict, field: str, value: Any) -> Dict:
    """Return a new entry with an additional field set to value."""
    result = dict(entry)
    result[field] = value
    return result


def normalize_level(entry: Dict, field: str = "level") -> Dict:
    """Uppercase the log level field value if present."""
    return apply_field(entry, field, lambda v: v.upper() if isinstance(v, str) else v)


def transform_entries(
    entries: List[Dict],
    transformations: List[Callable[[Dict], Dict]],
) -> List[Dict]:
    """Apply a sequence of transformation functions to each entry."""
    result = []
    for entry in entries:
        current = entry
        for transform in transformations:
            current = transform(current)
        result.append(current)
    return result
