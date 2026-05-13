"""Tests for the runner module."""

import os
import json
import tempfile
import pytest

from logslice.runner import load_lines_from_file, run_pipeline


SAMPLE_LOG = """2024-01-10 10:00:00 ERROR Something went wrong
2024-01-10 10:01:00 INFO Service started
2024-01-10 10:02:00 WARNING Disk usage high
2024-01-10 10:03:00 ERROR Connection timeout
2024-01-10 10:04:00 DEBUG Checking heartbeat
"""


@pytest.fixture
def log_file(tmp_path):
    path = tmp_path / "sample.log"
    path.write_text(SAMPLE_LOG, encoding="utf-8")
    return str(path)


def test_load_lines_from_file_returns_list(log_file):
    lines = load_lines_from_file(log_file)
    assert isinstance(lines, list)


def test_load_lines_from_file_correct_count(log_file):
    lines = load_lines_from_file(log_file)
    assert len(lines) == 5


def test_load_lines_strips_newlines(log_file):
    lines = load_lines_from_file(log_file)
    for line in lines:
        assert not line.endswith("\n")


def test_run_pipeline_returns_list(log_file):
    result = run_pipeline(log_file)
    assert isinstance(result, list)


def test_run_pipeline_no_filter_returns_all(log_file):
    result = run_pipeline(log_file)
    assert len(result) == 5


def test_run_pipeline_level_filter(log_file):
    result = run_pipeline(log_file, level="ERROR")
    assert all(e.get("level", "").upper() == "ERROR" for e in result)


def test_run_pipeline_pattern_filter(log_file):
    result = run_pipeline(log_file, pattern="timeout")
    assert len(result) >= 1
    for entry in result:
        assert "timeout" in (entry.get("message") or "").lower()


def test_run_pipeline_combined_filters(log_file):
    result = run_pipeline(log_file, level="ERROR", pattern="timeout")
    assert len(result) >= 1


def test_run_pipeline_writes_to_file(log_file, tmp_path):
    out_path = str(tmp_path / "output.json")
    run_pipeline(log_file, output_fmt="json", output_path=out_path)
    assert os.path.exists(out_path)


def test_run_pipeline_output_file_is_valid_json(log_file, tmp_path):
    out_path = str(tmp_path / "output.json")
    run_pipeline(log_file, output_fmt="json", output_path=out_path)
    with open(out_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list)


def test_run_pipeline_empty_log(tmp_path):
    empty = tmp_path / "empty.log"
    empty.write_text("", encoding="utf-8")
    result = run_pipeline(str(empty))
    assert result == []
