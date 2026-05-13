"""Chunker module for splitting log entries into fixed-size or time-based chunks."""

from typing import List, Dict, Any, Iterator, Optional
from datetime import datetime


def chunk_by_size(entries: List[Dict[str, Any]], size: int) -> List[List[Dict[str, Any]]]:
    """Split entries into chunks of a fixed size."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    return [entries[i:i + size] for i in range(0, len(entries), size)]


def chunk_by_field(entries: List[Dict[str, Any]], field: str, max_per_chunk: int) -> List[List[Dict[str, Any]]]:
    """Split entries into chunks where each chunk contains at most max_per_chunk unique field values."""
    if max_per_chunk <= 0:
        raise ValueError("max_per_chunk must be greater than 0")
    chunks: List[List[Dict[str, Any]]] = []
    current_chunk: List[Dict[str, Any]] = []
    seen_values: set = set()

    for entry in entries:
        value = entry.get(field)
        if value not in seen_values:
            if len(seen_values) >= max_per_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                seen_values = set()
            seen_values.add(value)
        current_chunk.append(entry)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def chunk_by_time(entries: List[Dict[str, Any]], interval_seconds: int) -> List[List[Dict[str, Any]]]:
    """Split entries into chunks based on timestamp intervals."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than 0")
    if not entries:
        return []

    chunks: List[List[Dict[str, Any]]] = []
    current_chunk: List[Dict[str, Any]] = []
    chunk_start: Optional[datetime] = None

    for entry in entries:
        ts = entry.get("timestamp")
        if not isinstance(ts, datetime):
            current_chunk.append(entry)
            continue

        if chunk_start is None:
            chunk_start = ts

        delta = (ts - chunk_start).total_seconds()
        if delta >= interval_seconds:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [entry]
            chunk_start = ts
        else:
            current_chunk.append(entry)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def iter_chunks(entries: List[Dict[str, Any]], size: int) -> Iterator[List[Dict[str, Any]]]:
    """Yield successive chunks of given size from entries."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    for i in range(0, len(entries), size):
        yield entries[i:i + size]
