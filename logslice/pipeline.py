"""Pipeline for chaining log processing steps."""

from typing import List, Dict, Any, Optional
from logslice.parser import parse_lines
from logslice.filter import (
    filter_by_level, filter_by_levels, filter_by_pattern, filter_by_time_range, filter_by_field
)
from logslice.sorter import sort_entries
from logslice.sampler import sample_entries, sample_head, sample_tail
from logslice.deduplicator import deduplicate
from logslice.redactor import redact_entries
from logslice.transformer import rename_field, drop_fields, keep_fields, add_field
from logslice.enricher import enrich_entries
from logslice.validator import filter_valid
from logslice.aggregator import summarize


class Pipeline:
    """Fluent interface for building log processing pipelines."""

    def __init__(self, entries: List[Dict[str, Any]]):
        self._entries = list(entries)

    @classmethod
    def from_lines(cls, lines: List[str]) -> "Pipeline":
        """Build a pipeline by parsing raw log lines."""
        return cls(parse_lines(lines))

    @classmethod
    def from_text(cls, text: str) -> "Pipeline":
        """Build a pipeline from a multi-line log string."""
        return cls.from_lines(text.splitlines())

    def filter_level(self, level: str) -> "Pipeline":
        return Pipeline(filter_by_level(self._entries, level))

    def filter_levels(self, levels: List[str]) -> "Pipeline":
        return Pipeline(filter_by_levels(self._entries, levels))

    def filter_pattern(self, pattern: str, field: str = "message") -> "Pipeline":
        return Pipeline(filter_by_pattern(self._entries, pattern, field))

    def filter_time_range(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> "Pipeline":
        return Pipeline(filter_by_time_range(self._entries, start, end))

    def filter_field(self, field: str, value: Any) -> "Pipeline":
        return Pipeline(filter_by_field(self._entries, field, value))

    def sort(self, by: str = "timestamp", reverse: bool = False, **kwargs) -> "Pipeline":
        return Pipeline(sort_entries(self._entries, by=by, reverse=reverse, **kwargs))

    def deduplicate(self, fields: Optional[List[str]] = None) -> "Pipeline":
        return Pipeline(deduplicate(self._entries, fields=fields))

    def redact(self, fields: Optional[List[str]] = None) -> "Pipeline":
        return Pipeline(redact_entries(self._entries, fields=fields))

    def rename(self, old: str, new: str) -> "Pipeline":
        return Pipeline([rename_field(e, old, new) for e in self._entries])

    def drop(self, fields: List[str]) -> "Pipeline":
        return Pipeline([drop_fields(e, fields) for e in self._entries])

    def keep(self, fields: List[str]) -> "Pipeline":
        return Pipeline([keep_fields(e, fields) for e in self._entries])

    def add(self, field: str, value: Any) -> "Pipeline":
        return Pipeline([add_field(e, field, value) for e in self._entries])

    def enrich(self, **kwargs) -> "Pipeline":
        return Pipeline(enrich_entries(self._entries, **kwargs))

    def valid_only(self) -> "Pipeline":
        return Pipeline(filter_valid(self._entries))

    def head(self, n: int) -> "Pipeline":
        return Pipeline(sample_head(self._entries, n))

    def tail(self, n: int) -> "Pipeline":
        return Pipeline(sample_tail(self._entries, n))

    def sample(self, n: int, seed: Optional[int] = None) -> "Pipeline":
        return Pipeline(sample_entries(self._entries, n, seed=seed))

    def entries(self) -> List[Dict[str, Any]]:
        return list(self._entries)

    def count(self) -> int:
        return len(self._entries)

    def summarize(self, field: str) -> Dict[str, Any]:
        return summarize(self._entries, field)

    def __len__(self) -> int:
        return self.count()

    def __repr__(self) -> str:
        return f"Pipeline({len(self._entries)} entries)"
