"""Pipeline module — fluent interface for chaining log-processing steps."""

from typing import Any, Dict, List, Optional, Pattern
import re

from logslice.parser import parse_lines
from logslice.filter import (
    filter_by_level,
    filter_by_levels,
    filter_by_pattern,
    filter_by_time_range,
    filter_by_field,
)
from logslice.sampler import sample_entries, sample_head, sample_tail
from logslice.deduplicator import deduplicate, deduplicate_by_message
from logslice.redactor import redact_entries, mask_field


Entry = Dict[str, Any]


class Pipeline:
    """Chainable pipeline for parsing and transforming log entries."""

    def __init__(self, entries: List[Entry]) -> None:
        self._entries: List[Entry] = entries

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_lines(cls, lines: List[str]) -> "Pipeline":
        """Build a pipeline by parsing a list of raw log lines."""
        return cls(parse_lines(lines))

    @classmethod
    def from_text(cls, text: str) -> "Pipeline":
        """Build a pipeline by parsing a multi-line log string."""
        return cls.from_lines(text.splitlines())

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_level(self, level: str) -> "Pipeline":
        return Pipeline(filter_by_level(self._entries, level))

    def filter_levels(self, levels: List[str]) -> "Pipeline":
        return Pipeline(filter_by_levels(self._entries, levels))

    def filter_pattern(self, pattern: str) -> "Pipeline":
        return Pipeline(filter_by_pattern(self._entries, pattern))

    def filter_time_range(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> "Pipeline":
        return Pipeline(filter_by_time_range(self._entries, start=start, end=end))

    def filter_field(self, field: str, value: Any) -> "Pipeline":
        return Pipeline(filter_by_field(self._entries, field, value))

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def sample(self, n: int, seed: Optional[int] = None) -> "Pipeline":
        return Pipeline(sample_entries(self._entries, n, seed=seed))

    def head(self, n: int) -> "Pipeline":
        return Pipeline(sample_head(self._entries, n))

    def tail(self, n: int) -> "Pipeline":
        return Pipeline(sample_tail(self._entries, n))

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def deduplicate(self, fields: Optional[List[str]] = None) -> "Pipeline":
        return Pipeline(deduplicate(self._entries, fields=fields))

    def deduplicate_by_message(self) -> "Pipeline":
        return Pipeline(deduplicate_by_message(self._entries))

    # ------------------------------------------------------------------
    # Redaction
    # ------------------------------------------------------------------

    def redact(self, fields: Optional[List[str]] = None) -> "Pipeline":
        return Pipeline(redact_entries(self._entries, fields=fields))

    def mask(self, field: str, placeholder: str = "[REDACTED]") -> "Pipeline":
        return Pipeline(mask_field(self._entries, field, placeholder=placeholder))

    # ------------------------------------------------------------------
    # Terminal operations
    # ------------------------------------------------------------------

    def entries(self) -> List[Entry]:
        """Return the current list of entries."""
        return list(self._entries)

    def count(self) -> int:
        """Return the number of entries in the pipeline."""
        return len(self._entries)

    def first(self) -> Optional[Entry]:
        """Return the first entry, or None if empty."""
        return self._entries[0] if self._entries else None

    def last(self) -> Optional[Entry]:
        """Return the last entry, or None if empty."""
        return self._entries[-1] if self._entries else None
