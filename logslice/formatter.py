"""Output formatters for parsed log entries."""

import json
import csv
import io
from typing import List, Dict, Any, Optional


SUPPORTED_FORMATS = ("text", "json", "csv", "tsv")


def format_entry(entry: Dict[str, Any], fmt: str = "text") -> str:
    """Format a single parsed log entry as a string.

    Args:
        entry: A parsed log entry dict (e.g. from parse_line).
        fmt: Output format. One of 'text', 'json', 'csv', 'tsv'.

    Returns:
        Formatted string representation of the entry.

    Raises:
        ValueError: If an unsupported format is requested.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "json":
        return json.dumps(entry, default=str)

    if fmt in ("csv", "tsv"):
        delimiter = "," if fmt == "csv" else "\t"
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=entry.keys(), delimiter=delimiter)
        writer.writerow(entry)
        return buf.getvalue().rstrip("\r\n")

    # Default: human-readable text
    parts = []
    for key, value in entry.items():
        if value is not None:
            parts.append(f"{key}={value}")
    return " | ".join(parts)


def format_entries(
    entries: List[Dict[str, Any]],
    fmt: str = "text",
    include_header: bool = True,
) -> str:
    """Format multiple parsed log entries.

    Args:
        entries: List of parsed log entry dicts.
        fmt: Output format. One of 'text', 'json', 'csv', 'tsv'.
        include_header: If True and fmt is 'csv'/'tsv', prepend a header row.

    Returns:
        Formatted multi-line string.
    """
    if not entries:
        return ""

    if fmt == "json":
        return json.dumps(entries, default=str, indent=2)

    if fmt in ("csv", "tsv"):
        delimiter = "," if fmt == "csv" else "\t"
        buf = io.StringIO()
        fieldnames: List[str] = list(entries[0].keys())
        writer = csv.DictWriter(
            buf, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore"
        )
        if include_header:
            writer.writeheader()
        writer.writerows(entries)
        return buf.getvalue().rstrip("\r\n")

    # text
    return "\n".join(format_entry(e, fmt="text") for e in entries)
