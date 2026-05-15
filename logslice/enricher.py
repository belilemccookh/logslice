"""Enricher module: attaches derived metadata to log entries."""

from datetime import datetime
from typing import Optional

SEVERITY_RANK: dict[str, int] = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "WARN": 2,
    "ERROR": 3,
    "CRITICAL": 4,
    "FATAL": 4,
}


def enrich_with_severity_rank(entry: dict) -> dict:
    """Add a numeric 'severity_rank' field based on the log level."""
    level = str(entry.get("level", "")).upper()
    rank = SEVERITY_RANK.get(level, -1)
    return {**entry, "severity_rank": rank}


def enrich_with_line_number(entry: dict, line_number: int) -> dict:
    """Attach a 'line_number' field to the entry."""
    return {**entry, "line_number": line_number}


def enrich_with_source(entry: dict, source: str) -> dict:
    """Attach a 'source' label (e.g. filename) to the entry."""
    return {**entry, "source": source}


def enrich_with_parsed_timestamp(
    entry: dict,
    fmt: str = "%Y-%m-%dT%H:%M:%S",
) -> dict:
    """Parse the 'timestamp' string into a datetime object stored as 'parsed_timestamp'."""
    raw: Optional[str] = entry.get("timestamp")
    parsed: Optional[datetime] = None
    if raw:
        try:
            parsed = datetime.strptime(raw, fmt)
        except (ValueError, TypeError):
            parsed = None
    return {**entry, "parsed_timestamp": parsed}


def enrich_entries(
    entries: list[dict],
    source: Optional[str] = None,
    add_severity: bool = True,
    add_line_numbers: bool = True,
    parse_timestamps: bool = False,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%S",
) -> list[dict]:
    """Apply a configurable set of enrichments to every entry in a list."""
    result = []
    for i, entry in enumerate(entries):
        e = entry
        if add_severity:
            e = enrich_with_severity_rank(e)
        if add_line_numbers:
            e = enrich_with_line_number(e, i + 1)
        if source is not None:
            e = enrich_with_source(e, source)
        if parse_timestamps:
            e = enrich_with_parsed_timestamp(e, fmt=timestamp_fmt)
        result.append(e)
    return result
