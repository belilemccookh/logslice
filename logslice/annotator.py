"""Annotator module: adds metadata annotations to log entries."""

from typing import Any, Callable, Dict, List, Optional


def annotate_entry(
    entry: Dict[str, Any],
    key: str,
    value: Any,
) -> Dict[str, Any]:
    """Return a copy of entry with an annotation added under 'annotations'."""
    result = dict(entry)
    annotations = dict(result.get("annotations") or {})
    annotations[key] = value
    result["annotations"] = annotations
    return result


def annotate_entries(
    entries: List[Dict[str, Any]],
    key: str,
    value: Any,
) -> List[Dict[str, Any]]:
    """Apply the same annotation to every entry."""
    return [annotate_entry(e, key, value) for e in entries]


def annotate_with_index(
    entries: List[Dict[str, Any]],
    key: str = "index",
    start: int = 0,
) -> List[Dict[str, Any]]:
    """Annotate each entry with its position in the list."""
    return [annotate_entry(e, key, start + i) for i, e in enumerate(entries)]


def annotate_with_predicate(
    entries: List[Dict[str, Any]],
    key: str,
    predicate: Callable[[Dict[str, Any]], Any],
) -> List[Dict[str, Any]]:
    """Annotate each entry using the result of calling *predicate* on it."""
    return [annotate_entry(e, key, predicate(e)) for e in entries]


def strip_annotations(
    entry: Dict[str, Any],
    keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Remove annotation keys from an entry.

    If *keys* is None all annotations are removed.
    """
    result = dict(entry)
    if "annotations" not in result:
        return result
    if keys is None:
        del result["annotations"]
        return result
    annotations = dict(result["annotations"])
    for k in keys:
        annotations.pop(k, None)
    result["annotations"] = annotations
    return result
