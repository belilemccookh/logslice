"""Tests for logslice.reporter module."""

import pytest
from logslice.reporter import build_report, format_report


def make_entry(level="INFO", message="msg", **kwargs):
    return {"timestamp": "2024-01-01T00:00:00", "level": level, "message": message, **kwargs}


# --- build_report ---

def test_build_report_returns_dict():
    assert isinstance(build_report([]), dict)


def test_build_report_total_correct():
    entries = [make_entry() for _ in range(4)]
    report = build_report(entries)
    assert report["total"] == 4


def test_build_report_errors_counted():
    entries = [make_entry("ERROR"), make_entry("INFO"), make_entry("CRITICAL")]
    report = build_report(entries)
    assert report["errors"] == 2


def test_build_report_warnings_counted():
    entries = [make_entry("WARNING"), make_entry("WARN"), make_entry("INFO")]
    report = build_report(entries)
    assert report["warnings"] == 2


def test_build_report_by_level_present():
    entries = [make_entry("INFO"), make_entry("ERROR")]
    report = build_report(entries)
    assert "by_level" in report
    assert report["by_level"]["INFO"] == 1


def test_build_report_top_messages_present():
    entries = [make_entry(message="hello")] * 3 + [make_entry(message="world")]
    report = build_report(entries)
    assert "top_messages" in report
    assert report["top_messages"][0]["value"] == "hello"
    assert report["top_messages"][0]["count"] == 3


def test_build_report_top_n_limits_messages():
    entries = [
        make_entry(message=f"msg{i}") for i in range(10)
    ]
    report = build_report(entries, top_n=3)
    assert len(report["top_messages"]) <= 3


def test_build_report_extra_fields_included():
    entries = [make_entry(source="app"), make_entry(source="db")]
    report = build_report(entries, extra_fields=["source"])
    assert "extra" in report
    assert "source" in report["extra"]


def test_build_report_no_extra_fields_by_default():
    report = build_report([make_entry()])
    assert "extra" not in report


def test_build_report_empty_entries():
    report = build_report([])
    assert report["total"] == 0
    assert report["errors"] == 0
    assert report["warnings"] == 0


# --- format_report ---

def test_format_report_returns_string():
    report = build_report([make_entry()])
    assert isinstance(format_report(report), str)


def test_format_report_contains_total():
    entries = [make_entry() for _ in range(3)]
    report = build_report(entries)
    text = format_report(report)
    assert "3" in text


def test_format_report_contains_level_section():
    entries = [make_entry("ERROR")]
    report = build_report(entries)
    text = format_report(report)
    assert "ERROR" in text


def test_format_report_contains_top_messages():
    entries = [make_entry(message="boom")] * 2
    report = build_report(entries)
    text = format_report(report)
    assert "boom" in text


def test_format_report_contains_extra_field_header():
    entries = [make_entry(source="app")]
    report = build_report(entries, extra_fields=["source"])
    text = format_report(report)
    assert "source" in text


def test_format_report_header_present():
    text = format_report(build_report([]))
    assert "Log Report" in text
