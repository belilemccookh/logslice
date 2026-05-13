"""Tests for logslice.chunker module."""

import pytest
from datetime import datetime, timedelta
from logslice.chunker import chunk_by_size, chunk_by_field, chunk_by_time, iter_chunks


def make_entry(msg="test", level="INFO", ts=None, source=None):
    entry = {"message": msg, "level": level, "timestamp": ts}
    if source is not None:
        entry["source"] = source
    return entry


# --- chunk_by_size ---

def test_chunk_by_size_returns_list():
    entries = [make_entry() for _ in range(5)]
    result = chunk_by_size(entries, 2)
    assert isinstance(result, list)


def test_chunk_by_size_correct_number_of_chunks():
    entries = [make_entry() for _ in range(6)]
    result = chunk_by_size(entries, 2)
    assert len(result) == 3


def test_chunk_by_size_last_chunk_smaller():
    entries = [make_entry() for _ in range(5)]
    result = chunk_by_size(entries, 2)
    assert len(result[-1]) == 1


def test_chunk_by_size_empty_input():
    assert chunk_by_size([], 3) == []


def test_chunk_by_size_invalid_size_raises():
    with pytest.raises(ValueError):
        chunk_by_size([make_entry()], 0)


def test_chunk_by_size_size_larger_than_entries():
    entries = [make_entry() for _ in range(3)]
    result = chunk_by_size(entries, 10)
    assert len(result) == 1
    assert len(result[0]) == 3


# --- chunk_by_field ---

def test_chunk_by_field_returns_list():
    entries = [make_entry(source="app"), make_entry(source="db"), make_entry(source="web")]
    result = chunk_by_field(entries, "source", 2)
    assert isinstance(result, list)


def test_chunk_by_field_splits_on_unique_values():
    entries = [
        make_entry(source="a"), make_entry(source="b"),
        make_entry(source="c"), make_entry(source="d"),
    ]
    result = chunk_by_field(entries, "source", 2)
    assert len(result) == 2


def test_chunk_by_field_invalid_max_raises():
    with pytest.raises(ValueError):
        chunk_by_field([make_entry()], "source", 0)


def test_chunk_by_field_missing_field_grouped_together():
    entries = [make_entry() for _ in range(4)]  # no 'source' field
    result = chunk_by_field(entries, "source", 2)
    assert sum(len(c) for c in result) == 4


# --- chunk_by_time ---

def test_chunk_by_time_returns_list():
    base = datetime(2024, 1, 1, 12, 0, 0)
    entries = [make_entry(ts=base + timedelta(seconds=i * 10)) for i in range(6)]
    result = chunk_by_time(entries, 30)
    assert isinstance(result, list)


def test_chunk_by_time_splits_correctly():
    base = datetime(2024, 1, 1, 12, 0, 0)
    entries = [make_entry(ts=base + timedelta(seconds=i * 10)) for i in range(6)]
    result = chunk_by_time(entries, 30)
    assert len(result) == 2


def test_chunk_by_time_empty_input():
    assert chunk_by_time([], 60) == []


def test_chunk_by_time_invalid_interval_raises():
    with pytest.raises(ValueError):
        chunk_by_time([make_entry()], 0)


def test_chunk_by_time_no_timestamp_included_in_current_chunk():
    base = datetime(2024, 1, 1)
    entries = [make_entry(ts=None), make_entry(ts=base)]
    result = chunk_by_time(entries, 60)
    assert sum(len(c) for c in result) == 2


# --- iter_chunks ---

def test_iter_chunks_yields_correct_count():
    entries = [make_entry() for _ in range(9)]
    chunks = list(iter_chunks(entries, 3))
    assert len(chunks) == 3


def test_iter_chunks_invalid_size_raises():
    with pytest.raises(ValueError):
        list(iter_chunks([make_entry()], -1))


def test_iter_chunks_is_iterator():
    entries = [make_entry() for _ in range(4)]
    result = iter_chunks(entries, 2)
    assert hasattr(result, '__iter__') and hasattr(result, '__next__')
