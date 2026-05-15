"""Summarizer module for generating human-readable log summaries."""

from typing import Any
from collections import Counter


def top_levels(entries: list[dict], n: int = 5) -> list[tuple[str, int]]:
    """Return the top N most frequent log levels."""
    counts = Counter(
        e["level"].upper()
        for e in entries
        if e.get("level") is not None
    )
    return counts.most_common(n)


def top_messages(entries: list[dict], n: int = 5) -> list[tuple[str, int]]:
    """Return the top N most frequent log messages."""
    counts = Counter(
        e["message"]
        for e in entries
        if e.get("message") is not None
    )
    return counts.most_common(n)


def error_rate(entries: list[dict]) -> float:
    """Return the fraction of entries that are errors (0.0 to 1.0)."""
    if not entries:
        return 0.0
    error_count = sum(
        1 for e in entries
        if str(e.get("level", "")).upper() in ("ERROR", "CRITICAL", "FATAL")
    )
    return error_count / len(entries)


def time_span(entries: list[dict]) -> dict[str, Any]:
    """Return the earliest and latest timestamps found in entries."""
    timestamps = [
        e["timestamp"]
        for e in entries
        if e.get("timestamp") is not None
    ]
    if not timestamps:
        return {"earliest": None, "latest": None}
    return {"earliest": min(timestamps), "latest": max(timestamps)}


def summarize_entries(entries: list[dict], top_n: int = 5) -> dict[str, Any]:
    """Produce a full summary dict for a list of log entries."""
    return {
        "total": len(entries),
        "error_rate": error_rate(entries),
        "top_levels": top_levels(entries, top_n),
        "top_messages": top_messages(entries, top_n),
        "time_span": time_span(entries),
    }
