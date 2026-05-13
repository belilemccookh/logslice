"""Tests for logslice.writer module."""

import json
from pathlib import Path

import pytest

from logslice.writer import write_to_file, write_to_stdout, write_entries

SAMPLE = [
    {"timestamp": "2024-03-01 08:00:00", "level": "INFO", "message": "Boot"},
    {"timestamp": "2024-03-01 08:01:00", "level": "WARN", "message": "Low memory"},
]


# --- write_to_file ---

def test_write_to_file_creates_file(tmp_path):
    dest = str(tmp_path / "out.txt")
    write_to_file(SAMPLE, dest)
    assert Path(dest).exists()


def test_write_to_file_returns_byte_count(tmp_path):
    dest = str(tmp_path / "out.txt")
    n = write_to_file(SAMPLE, dest)
    assert n > 0
    assert n == Path(dest).stat().st_size


def test_write_to_file_json_extension(tmp_path):
    dest = str(tmp_path / "out.json")
    write_to_file(SAMPLE, dest)
    content = Path(dest).read_text()
    parsed = json.loads(content)
    assert len(parsed) == 2


def test_write_to_file_csv_extension(tmp_path):
    dest = str(tmp_path / "out.csv")
    write_to_file(SAMPLE, dest)
    content = Path(dest).read_text()
    assert "level" in content.splitlines()[0]


def test_write_to_file_explicit_fmt_overrides_extension(tmp_path):
    dest = str(tmp_path / "out.log")
    write_to_file(SAMPLE, dest, fmt="json")
    content = Path(dest).read_text()
    json.loads(content)  # should not raise


def test_write_to_file_text_default(tmp_path):
    dest = str(tmp_path / "out.log")
    write_to_file(SAMPLE, dest)
    content = Path(dest).read_text()
    assert "INFO" in content


# --- write_to_stdout ---

def test_write_to_stdout_text(capsys):
    write_to_stdout(SAMPLE, fmt="text")
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "WARN" in captured.out


def test_write_to_stdout_json(capsys):
    write_to_stdout(SAMPLE, fmt="json")
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert len(parsed) == 2


def test_write_to_stdout_ends_with_newline(capsys):
    write_to_stdout(SAMPLE, fmt="text")
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")


# --- write_entries ---

def test_write_entries_to_file(tmp_path):
    dest = str(tmp_path / "result.json")
    write_entries(SAMPLE, destination=dest, fmt="json")
    assert Path(dest).exists()
    json.loads(Path(dest).read_text())


def test_write_entries_to_stdout(capsys):
    write_entries(SAMPLE, destination=None, fmt="text")
    captured = capsys.readouterr()
    assert "Boot" in captured.out


def test_write_entries_no_destination_defaults_stdout(capsys):
    write_entries(SAMPLE)
    captured = capsys.readouterr()
    assert len(captured.out) > 0
