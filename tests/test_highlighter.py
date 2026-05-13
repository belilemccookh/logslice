"""Tests for logslice.highlighter module."""

import pytest
from logslice.highlighter import (
    colorize,
    highlight_by_level,
    highlight_pattern,
    highlight_entry,
    ANSI_CODES,
    LEVEL_COLORS,
)


def test_colorize_wraps_text_with_ansi():
    result = colorize("hello", "red")
    assert ANSI_CODES["red"] in result
    assert ANSI_CODES["reset"] in result
    assert "hello" in result


def test_colorize_bold_includes_bold_code():
    result = colorize("hello", "green", bold=True)
    assert ANSI_CODES["bold"] in result


def test_colorize_unknown_color_still_returns_text():
    result = colorize("hello", "ultraviolet")
    assert "hello" in result
    assert ANSI_CODES["reset"] in result


def test_highlight_by_level_error_returns_red():
    result = highlight_by_level("something went wrong", "error")
    assert ANSI_CODES["red"] in result


def test_highlight_by_level_warning_returns_yellow():
    result = highlight_by_level("watch out", "warning")
    assert ANSI_CODES["yellow"] in result


def test_highlight_by_level_info_returns_green():
    result = highlight_by_level("all good", "info")
    assert ANSI_CODES["green"] in result


def test_highlight_by_level_case_insensitive():
    result_upper = highlight_by_level("msg", "ERROR")
    result_lower = highlight_by_level("msg", "error")
    assert result_upper == result_lower


def test_highlight_by_level_unknown_level_returns_original():
    text = "some message"
    result = highlight_by_level(text, "verbose")
    assert result == text


def test_highlight_by_level_empty_level_returns_original():
    text = "some message"
    result = highlight_by_level(text, "")
    assert result == text


def test_highlight_pattern_wraps_match():
    result = highlight_pattern("error occurred at line 42", r"\d+")
    assert ANSI_CODES["yellow"] in result
    assert "42" in result


def test_highlight_pattern_no_match_returns_original():
    text = "nothing to see here"
    result = highlight_pattern(text, r"\d+")
    assert result == text


def test_highlight_pattern_invalid_regex_returns_original():
    text = "some text"
    result = highlight_pattern(text, "[invalid")
    assert result == text


def test_highlight_pattern_empty_pattern_returns_original():
    text = "some text"
    result = highlight_pattern(text, "")
    assert result == text


def test_highlight_entry_returns_string():
    entry = {"timestamp": "2024-01-01T00:00:00", "level": "info", "message": "started"}
    result = highlight_entry(entry)
    assert isinstance(result, str)
    assert "started" in result


def test_highlight_entry_includes_level_color():
    entry = {"timestamp": "2024-01-01T00:00:00", "level": "error", "message": "failed"}
    result = highlight_entry(entry)
    assert ANSI_CODES["red"] in result


def test_highlight_entry_with_pattern_highlights_match():
    entry = {"timestamp": "2024-01-01T00:00:00", "level": "debug", "message": "value=99"}
    result = highlight_entry(entry, pattern=r"\d+")
    assert ANSI_CODES["yellow"] in result


def test_highlight_entry_missing_fields_no_error():
    entry = {"message": "bare message"}
    result = highlight_entry(entry)
    assert "bare message" in result
