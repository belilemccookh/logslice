"""Export parsed log entries to various file formats."""

import csv
import json
import io
from typing import List, Dict, Any, Optional


def export_to_json(entries: List[Dict[str, Any]], indent: int = 2) -> str:
    """Serialize log entries to a JSON string."""
    serializable = [
        {k: v for k, v in entry.items() if v is not None}
        for entry in entries
    ]
    return json.dumps(serializable, indent=indent, default=str)


def export_to_csv(entries: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> str:
    """Serialize log entries to a CSV string.

    Args:
        entries: List of parsed log entry dicts.
        fields: Optional list of field names to include as columns.
                Defaults to all keys found across entries.
    """
    if not entries:
        return ""

    if fields is None:
        seen = {}
        for entry in entries:
            for key in entry:
                seen[key] = True
        fields = list(seen.keys())

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for entry in entries:
        writer.writerow({f: entry.get(f, "") or "" for f in fields})

    return output.getvalue()


def export_to_text(entries: List[Dict[str, Any]], delimiter: str = " | ") -> str:
    """Serialize log entries to a plain-text string, one entry per line."""
    lines = []
    for entry in entries:
        parts = [f"{k}={v}" for k, v in entry.items() if v is not None]
        lines.append(delimiter.join(parts))
    return "\n".join(lines)


def export_entries(
    entries: List[Dict[str, Any]],
    fmt: str = "text",
    **kwargs: Any,
) -> str:
    """Dispatch export to the appropriate format handler.

    Args:
        entries: List of parsed log entry dicts.
        fmt: One of 'text', 'json', 'csv'.
        **kwargs: Extra keyword arguments forwarded to the format handler.

    Returns:
        Formatted string representation of the entries.

    Raises:
        ValueError: If an unsupported format is requested.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return export_to_json(entries, **kwargs)
    if fmt == "csv":
        return export_to_csv(entries, **kwargs)
    if fmt == "text":
        return export_to_text(entries, **kwargs)
    raise ValueError(f"Unsupported export format: '{fmt}'. Choose from text, json, csv.")
