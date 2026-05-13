"""Entry enrichment utilities that add derived fields to log entries."""

import re
from datetime import datetime
from typing import Callable, Dict, List, Optional


SEVERITY_RANK = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4,
}


def enrich_with_severity_rank(entry: Dict) -> Dict:
    """Add a 'severity_rank' field based on the log level."""
    result = dict(entry)
    level = (entry.get("level") or "").upper()
    result["severity_rank"] = SEVERITY_RANK.get(level)
    return result


def enrich_with_line_number(entries: List[Dict]) -> List[Dict]:
    """Add a 'line_number' field (1-based index) to each entry."""
    return [{**e, "line_number": i + 1} for i, e in enumerate(entries)]


def enrich_with_source(entry: Dict, source: str) -> Dict:
    """Add a 'source' field to the entry."""
    result = dict(entry)
    result["source"] = source
    return result


def enrich_with_parsed_timestamp(
    entry: Dict,
    fmt: str = "%Y-%m-%dT%H:%M:%S",
    field: str = "timestamp",
) -> Dict:
    """Add a 'parsed_timestamp' datetime object parsed from the timestamp field."""
    result = dict(entry)
    raw = entry.get(field)
    if raw:
        try:
            result["parsed_timestamp"] = datetime.strptime(raw, fmt)
        except (ValueError, TypeError):
            result["parsed_timestamp"] = None
    else:
        result["parsed_timestamp"] = None
    return result


def enrich_entries(
    entries: List[Dict],
    enrichments: List[Callable[[Dict], Dict]],
) -> List[Dict]:
    """Apply a list of enrichment functions to each entry."""
    result = []
    for entry in entries:
        current = entry
        for enrich in enrichments:
            current = enrich(current)
        result.append(current)
    return result
