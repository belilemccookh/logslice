"""Fluent pipeline for chaining log processing steps."""

from logslice.parser import parse_lines
from logslice.filter import (
    filter_by_level,
    filter_by_levels,
    filter_by_pattern,
    filter_by_time_range,
    filter_by_field,
)
from logslice.sampler import sample_entries, sample_head, sample_tail
from logslice.sorter import sort_by_field, sort_by_timestamp, sort_by_level
from logslice.deduplicator import deduplicate, deduplicate_by_message
from logslice.transformer import rename_field, drop_fields, keep_fields, apply_field, add_field
from logslice.redactor import redact_entries
from logslice.enricher import (
    enrich_with_severity_rank,
    enrich_with_line_number,
    enrich_with_source,
    enrich_with_parsed_timestamp,
)
from logslice.tagger import tag_by_predicate, filter_by_tag
from logslice.annotator import annotate_entries, annotate_with_index
from logslice.comparator import diff_entries, added_entries, removed_entries


class Pipeline:
    """Chainable log entry processing pipeline."""

    def __init__(self, entries: list[dict]):
        self._entries = list(entries)

    @classmethod
    def from_lines(cls, lines: list[str]) -> "Pipeline":
        return cls(parse_lines(lines))

    @classmethod
    def from_text(cls, text: str) -> "Pipeline":
        return cls.from_lines(text.splitlines())

    def filter_level(self, level: str) -> "Pipeline":
        return Pipeline(filter_by_level(self._entries, level))

    def filter_levels(self, levels: list[str]) -> "Pipeline":
        return Pipeline(filter_by_levels(self._entries, levels))

    def filter_pattern(self, pattern: str, field: str = "message") -> "Pipeline":
        return Pipeline(filter_by_pattern(self._entries, pattern, field))

    def filter_time_range(self, start: str | None = None, end: str | None = None) -> "Pipeline":
        return Pipeline(filter_by_time_range(self._entries, start, end))

    def filter_field(self, field: str, value: str) -> "Pipeline":
        return Pipeline(filter_by_field(self._entries, field, value))

    def deduplicate(self, fields: list[str] | None = None) -> "Pipeline":
        return Pipeline(deduplicate(self._entries, fields))

    def deduplicate_by_message(self) -> "Pipeline":
        return Pipeline(deduplicate_by_message(self._entries))

    def sort(self, field: str, reverse: bool = False) -> "Pipeline":
        return Pipeline(sort_by_field(self._entries, field, reverse))

    def sort_by_timestamp(self, reverse: bool = False) -> "Pipeline":
        return Pipeline(sort_by_timestamp(self._entries, reverse))

    def sort_by_level(self, reverse: bool = False) -> "Pipeline":
        return Pipeline(sort_by_level(self._entries, reverse))

    def sample(self, n: int, seed: int | None = None) -> "Pipeline":
        return Pipeline(sample_entries(self._entries, n, seed))

    def head(self, n: int) -> "Pipeline":
        return Pipeline(sample_head(self._entries, n))

    def tail(self, n: int) -> "Pipeline":
        return Pipeline(sample_tail(self._entries, n))

    def rename(self, old: str, new: str) -> "Pipeline":
        return Pipeline([rename_field(e, old, new) for e in self._entries])

    def drop(self, fields: list[str]) -> "Pipeline":
        return Pipeline([drop_fields(e, fields) for e in self._entries])

    def keep(self, fields: list[str]) -> "Pipeline":
        return Pipeline([keep_fields(e, fields) for e in self._entries])

    def apply(self, field: str, func) -> "Pipeline":
        return Pipeline([apply_field(e, field, func) for e in self._entries])

    def add(self, field: str, value) -> "Pipeline":
        return Pipeline([add_field(e, field, value) for e in self._entries])

    def redact(self, fields: list[str] | None = None) -> "Pipeline":
        return Pipeline(redact_entries(self._entries, fields))

    def enrich_severity(self) -> "Pipeline":
        return Pipeline([enrich_with_severity_rank(e) for e in self._entries])

    def enrich_line_numbers(self) -> "Pipeline":
        return Pipeline(enrich_with_line_number(self._entries))

    def enrich_source(self, source: str) -> "Pipeline":
        return Pipeline([enrich_with_source(e, source) for e in self._entries])

    def enrich_parsed_timestamp(self) -> "Pipeline":
        return Pipeline([enrich_with_parsed_timestamp(e) for e in self._entries])

    def tag(self, tag: str, predicate) -> "Pipeline":
        return Pipeline(tag_by_predicate(self._entries, tag, predicate))

    def filter_tag(self, tag: str) -> "Pipeline":
        return Pipeline(filter_by_tag(self._entries, tag))

    def annotate(self, key: str, value) -> "Pipeline":
        return Pipeline(annotate_entries(self._entries, key, value))

    def annotate_index(self) -> "Pipeline":
        return Pipeline(annotate_with_index(self._entries))

    def diff(self, other: "Pipeline") -> dict:
        return diff_entries(self._entries, other._entries)

    def added_vs(self, other: "Pipeline") -> "Pipeline":
        return Pipeline(added_entries(other._entries, self._entries))

    def removed_vs(self, other: "Pipeline") -> "Pipeline":
        return Pipeline(removed_entries(other._entries, self._entries))

    def count(self) -> int:
        return len(self._entries)

    def entries(self) -> list[dict]:
        return list(self._entries)

    def first(self) -> dict | None:
        return self._entries[0] if self._entries else None

    def last(self) -> dict | None:
        return self._entries[-1] if self._entries else None
