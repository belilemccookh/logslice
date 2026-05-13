"""Profile log entries to extract statistical insights."""

from typing import Any
from collections import Counter


def field_value_distribution(entries: list[dict], field: str) -> dict[str, int]:
    """Return a frequency distribution of values for a given field."""
    counts: Counter = Counter()
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            counts[str(value)] += 1
    return dict(counts)


def field_coverage(entries: list[dict], field: str) -> float:
    """Return the fraction of entries that contain a non-None value for field."""
    if not entries:
        return 0.0
    present = sum(1 for e in entries if e.get(field) is not None)
    return present / len(entries)


def all_fields(entries: list[dict]) -> list[str]:
    """Return a sorted list of all unique field names across all entries."""
    seen: set[str] = set()
    for entry in entries:
        seen.update(entry.keys())
    return sorted(seen)


def field_stats(entries: list[dict], field: str) -> dict[str, Any]:
    """Return basic stats (count, unique, top, coverage) for a field."""
    values = [str(e[field]) for e in entries if e.get(field) is not None]
    if not values:
        return {"count": 0, "unique": 0, "top": None, "coverage": 0.0}
    distribution = Counter(values)
    top, top_count = distribution.most_common(1)[0]
    return {
        "count": len(values),
        "unique": len(distribution),
        "top": top,
        "top_count": top_count,
        "coverage": field_coverage(entries, field),
    }


def profile_entries(entries: list[dict]) -> dict[str, Any]:
    """Return a full profile summary over all entries."""
    fields = all_fields(entries)
    return {
        "total": len(entries),
        "fields": fields,
        "field_stats": {f: field_stats(entries, f) for f in fields},
    }
