"""splitter.py — Split log entries into segments based on various criteria."""

from typing import List, Dict, Any, Optional, Callable


def split_by_level_change(entries: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Split entries into segments whenever the log level changes."""
    if not entries:
        return []

    segments = []
    current_segment = [entries[0]]
    current_level = entries[0].get("level")

    for entry in entries[1:]:
        level = entry.get("level")
        if level != current_level:
            segments.append(current_segment)
            current_segment = [entry]
            current_level = level
        else:
            current_segment.append(entry)

    if current_segment:
        segments.append(current_segment)

    return segments


def split_by_field_value(entries: List[Dict[str, Any]], field: str, value: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Split entries into two groups: those matching field=value and those that don't."""
    matching = [e for e in entries if e.get(field) == value]
    non_matching = [e for e in entries if e.get(field) != value]
    return {"matching": matching, "other": non_matching}


def split_at_index(entries: List[Dict[str, Any]], index: int) -> tuple:
    """Split entries into two lists at the given index."""
    if index < 0:
        index = max(0, len(entries) + index)
    return entries[:index], entries[index:]


def split_by_predicate(
    entries: List[Dict[str, Any]],
    predicate: Callable[[Dict[str, Any]], bool]
) -> Dict[str, List[Dict[str, Any]]]:
    """Split entries into two groups based on a predicate function."""
    passing = []
    failing = []
    for entry in entries:
        if predicate(entry):
            passing.append(entry)
        else:
            failing.append(entry)
    return {"passing": passing, "failing": failing}


def split_by_session(
    entries: List[Dict[str, Any]],
    session_field: str = "session_id"
) -> Dict[str, List[Dict[str, Any]]]:
    """Split entries into groups keyed by session identifier."""
    sessions: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        key = str(entry.get(session_field, "unknown"))
        sessions.setdefault(key, []).append(entry)
    return sessions
