"""Pipeline module for chaining log processing steps."""

from typing import Any, Callable, Dict, List, Optional

from logslice.parser import parse_lines
from logslice.filter import filter_by_level, filter_by_pattern, filter_by_time_range, filter_by_field
from logslice.formatter import format_entries
from logslice.exporter import export_entries


class Pipeline:
    """Chainable log processing pipeline."""

    def __init__(self, entries: Optional[List[Dict[str, Any]]] = None):
        self._entries: List[Dict[str, Any]] = entries or []
        self._steps: List[Callable] = []

    @classmethod
    def from_lines(cls, lines: List[str]) -> "Pipeline":
        """Create a pipeline from raw log lines."""
        entries = parse_lines(lines)
        return cls(entries)

    @classmethod
    def from_text(cls, text: str) -> "Pipeline":
        """Create a pipeline from a block of log text."""
        lines = text.splitlines()
        return cls.from_lines(lines)

    def filter_level(self, level: str) -> "Pipeline":
        """Filter entries by log level."""
        self._entries = filter_by_level(self._entries, level)
        return self

    def filter_pattern(self, pattern: str, field: str = "message") -> "Pipeline":
        """Filter entries by regex pattern."""
        self._entries = filter_by_pattern(self._entries, pattern, field)
        return self

    def filter_time(self, start: Optional[str] = None, end: Optional[str] = None) -> "Pipeline":
        """Filter entries by time range."""
        self._entries = filter_by_time_range(self._entries, start, end)
        return self

    def filter_field(self, field: str, value: str) -> "Pipeline":
        """Filter entries by exact field value."""
        self._entries = filter_by_field(self._entries, field, value)
        return self

    def apply(self, func: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]) -> "Pipeline":
        """Apply a custom transformation function to the entries."""
        self._entries = func(self._entries)
        return self

    def entries(self) -> List[Dict[str, Any]]:
        """Return the current list of processed entries."""
        return list(self._entries)

    def count(self) -> int:
        """Return the number of entries in the pipeline."""
        return len(self._entries)

    def export(self, fmt: str = "json") -> str:
        """Export the entries to a string in the given format."""
        return export_entries(self._entries, fmt)

    def format(self, fmt: str = "text") -> List[str]:
        """Format entries as a list of strings."""
        return format_entries(self._entries, fmt)
