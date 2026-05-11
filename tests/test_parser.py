"""Unit tests for logslice.parser module."""

import pytest
from logslice.parser import parse_line, parse_lines, PATTERNS


COMMON_LINE = "2024-03-15T08:22:01Z INFO  Application started successfully"
BRACKETED_LINE = "[2024-03-15 08:22:01] [ERROR] Failed to connect to database"
SYSLOG_LINE = "Mar 15 08:22:01 myhost myapp: Something happened"
NO_MATCH_LINE = "this is just plain text with no structure"


class TestParseLine:
    def test_common_pattern_returns_dict(self):
        result = parse_line(COMMON_LINE)
        assert result is not None
        assert isinstance(result, dict)

    def test_common_pattern_fields(self):
        result = parse_line(COMMON_LINE)
        assert result["timestamp"] == "2024-03-15T08:22:01Z"
        assert result["level"] == "INFO"
        assert result["message"] == "Application started successfully"

    def test_bracketed_pattern(self):
        result = parse_line(BRACKETED_LINE, pattern_name="bracketed")
        assert result is not None
        assert result["level"] == "ERROR"
        assert "database" in result["message"]

    def test_syslog_pattern(self):
        result = parse_line(SYSLOG_LINE, pattern_name="syslog")
        assert result is not None
        assert result["host"] == "myhost"
        assert result["process"] == "myapp"
        assert result["message"] == "Something happened"

    def test_no_match_returns_none(self):
        assert parse_line(NO_MATCH_LINE) is None

    def test_unknown_pattern_raises(self):
        with pytest.raises(ValueError, match="Unknown pattern"):
            parse_line(COMMON_LINE, pattern_name="nonexistent")

    def test_warn_normalised_to_warning(self):
        line = "2024-03-15T09:00:00Z WARN  Disk space low"
        result = parse_line(line)
        assert result["level"] == "WARNING"

    def test_fatal_normalised_to_critical(self):
        line = "2024-03-15T09:00:00Z FATAL  System crash"
        result = parse_line(line)
        assert result["level"] == "CRITICAL"

    def test_trailing_newline_stripped(self):
        result = parse_line(COMMON_LINE + "\n")
        assert result is not None
        assert not result["message"].endswith("\n")


class TestParseLines:
    def test_returns_list(self):
        result = parse_lines([COMMON_LINE])
        assert isinstance(result, list)

    def test_skips_non_matching_lines(self):
        lines = [COMMON_LINE, NO_MATCH_LINE, COMMON_LINE]
        result = parse_lines(lines)
        assert len(result) == 2

    def test_empty_input(self):
        assert parse_lines([]) == []

    def test_all_non_matching(self):
        assert parse_lines([NO_MATCH_LINE, "another bad line"]) == []

    def test_multiple_entries_order_preserved(self):
        lines = [
            "2024-03-15T08:00:00Z INFO  First",
            "2024-03-15T08:01:00Z ERROR Second",
        ]
        result = parse_lines(lines)
        assert result[0]["message"] == "First"
        assert result[1]["message"] == "Second"
