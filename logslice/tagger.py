"""Tagger module: applies string tags to log entries."""

from typing import Any, Callable, Dict, List, Optional


def tag_entry(entry: Dict[str, Any], *tags: str) -> Dict[str, Any]:
    """Return a copy of *entry* with *tags* added to its tag list."""
    result = dict(entry)
    existing: List[str] = list(result.get("tags") or [])
    for tag in tags:
        if tag not in existing:
            existing.append(tag)
    result["tags"] = existing
    return result


def untag_entry(entry: Dict[str, Any], *tags: str) -> Dict[str, Any]:
    """Return a copy of *entry* with the specified *tags* removed."""
    result = dict(entry)
    existing: List[str] = list(result.get("tags") or [])
    result["tags"] = [t for t in existing if t not in tags]
    return result


def tag_entries(
    entries: List[Dict[str, Any]],
    *tags: str,
) -> List[Dict[str, Any]]:
    """Apply *tags* to every entry."""
    return [tag_entry(e, *tags) for e in entries]


def tag_by_predicate(
    entries: List[Dict[str, Any]],
    tag: str,
    predicate: Callable[[Dict[str, Any]], bool],
) -> List[Dict[str, Any]]:
    """Add *tag* to entries for which *predicate* returns True."""
    result = []
    for entry in entries:
        if predicate(entry):
            result.append(tag_entry(entry, tag))
        else:
            result.append(dict(entry))
    return result


def filter_by_tag(
    entries: List[Dict[str, Any]],
    tag: str,
) -> List[Dict[str, Any]]:
    """Return only entries that carry *tag*."""
    return [e for e in entries if tag in (e.get("tags") or [])]


def get_all_tags(entries: List[Dict[str, Any]]) -> List[str]:
    """Return a sorted list of every unique tag present across all entries."""
    seen: set = set()
    for entry in entries:
        for tag in entry.get("tags") or []:
            seen.add(tag)
    return sorted(seen)
