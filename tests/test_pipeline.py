"""Tests for the Pipeline class."""

import json
import pytest
from logslice.pipeline import Pipeline


SAMPLE_LINES = [
    "2024-01-10 10:00:00 ERROR Something went wrong",
    "2024-01-10 10:01:00 INFO Service started",
    "2024-01-10 10:02:00 WARNING Disk usage high",
    "2024-01-10 10:03:00 ERROR Connection timeout",
    "2024-01-10 10:04:00 DEBUG Checking heartbeat",
]


def make_pipeline():
    return Pipeline.from_lines(SAMPLE_LINES)


def test_pipeline_from_lines_returns_pipeline():
    p = Pipeline.from_lines(SAMPLE_LINES)
    assert isinstance(p, Pipeline)


def test_pipeline_from_text_returns_pipeline():
    text = "\n".join(SAMPLE_LINES)
    p = Pipeline.from_text(text)
    assert isinstance(p, Pipeline)


def test_pipeline_count_matches_input():
    p = make_pipeline()
    assert p.count() == len(SAMPLE_LINES)


def test_pipeline_entries_returns_list():
    p = make_pipeline()
    assert isinstance(p.entries(), list)


def test_pipeline_filter_level_reduces_entries():
    p = make_pipeline().filter_level("ERROR")
    assert p.count() < len(SAMPLE_LINES)


def test_pipeline_filter_level_keeps_only_matching():
    entries = make_pipeline().filter_level("ERROR").entries()
    for entry in entries:
        assert entry.get("level", "").upper() == "ERROR"


def test_pipeline_filter_pattern_reduces_entries():
    p = make_pipeline().filter_pattern("timeout")
    assert p.count() >= 1


def test_pipeline_filter_pattern_all_match():
    entries = make_pipeline().filter_pattern("timeout").entries()
    for entry in entries:
        assert "timeout" in (entry.get("message") or "").lower()


def test_pipeline_chaining_level_and_pattern():
    p = make_pipeline().filter_level("ERROR").filter_pattern("timeout")
    assert p.count() >= 1


def test_pipeline_apply_custom_function():
    def keep_first(entries):
        return entries[:1]

    p = make_pipeline().apply(keep_first)
    assert p.count() == 1


def test_pipeline_export_returns_string():
    result = make_pipeline().export(fmt="json")
    assert isinstance(result, str)


def test_pipeline_export_json_is_valid():
    result = make_pipeline().export(fmt="json")
    data = json.loads(result)
    assert isinstance(data, list)


def test_pipeline_format_returns_list_of_strings():
    result = make_pipeline().format(fmt="text")
    assert isinstance(result, list)
    assert all(isinstance(s, str) for s in result)


def test_pipeline_empty_input_count_is_zero():
    p = Pipeline.from_lines([])
    assert p.count() == 0


def test_pipeline_filter_on_empty_is_safe():
    p = Pipeline.from_lines([]).filter_level("ERROR")
    assert p.count() == 0
