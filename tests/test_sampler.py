"""Tests for logslice.sampler."""

import pytest
from logslice.sampler import sample_entries, sample_every_nth, sample_head, sample_tail


def make_entries(n: int):
    return [{"id": i, "message": f"log line {i}"} for i in range(n)]


# --- sample_entries ---

def test_sample_entries_returns_list():
    entries = make_entries(20)
    result = sample_entries(entries, 5, seed=42)
    assert isinstance(result, list)


def test_sample_entries_correct_count():
    entries = make_entries(20)
    result = sample_entries(entries, 5, seed=42)
    assert len(result) == 5


def test_sample_entries_preserves_order():
    entries = make_entries(50)
    result = sample_entries(entries, 10, seed=0)
    ids = [e["id"] for e in result]
    assert ids == sorted(ids)


def test_sample_entries_reproducible_with_seed():
    entries = make_entries(100)
    r1 = sample_entries(entries, 10, seed=7)
    r2 = sample_entries(entries, 10, seed=7)
    assert r1 == r2


def test_sample_entries_different_seeds_differ():
    entries = make_entries(100)
    r1 = sample_entries(entries, 10, seed=1)
    r2 = sample_entries(entries, 10, seed=2)
    assert r1 != r2


def test_sample_entries_n_larger_than_list_returns_all():
    entries = make_entries(5)
    result = sample_entries(entries, 100)
    assert len(result) == 5


def test_sample_entries_n_zero_returns_empty():
    entries = make_entries(10)
    assert sample_entries(entries, 0) == []


def test_sample_entries_n_negative_returns_empty():
    entries = make_entries(10)
    assert sample_entries(entries, -3) == []


def test_sample_entries_empty_input():
    assert sample_entries([], 5) == []


# --- sample_every_nth ---

def test_sample_every_nth_step_1_returns_all():
    entries = make_entries(10)
    assert sample_every_nth(entries, 1) == entries


def test_sample_every_nth_step_2_correct_count():
    entries = make_entries(10)
    result = sample_every_nth(entries, 2)
    assert len(result) == 5


def test_sample_every_nth_correct_indices():
    entries = make_entries(6)
    result = sample_every_nth(entries, 3)
    assert [e["id"] for e in result] == [0, 3]


def test_sample_every_nth_invalid_n_raises():
    with pytest.raises(ValueError):
        sample_every_nth(make_entries(10), 0)


# --- sample_head ---

def test_sample_head_returns_first_n():
    entries = make_entries(10)
    result = sample_head(entries, 3)
    assert [e["id"] for e in result] == [0, 1, 2]


def test_sample_head_n_zero_returns_empty():
    assert sample_head(make_entries(5), 0) == []


def test_sample_head_n_exceeds_length_returns_all():
    entries = make_entries(3)
    assert sample_head(entries, 100) == entries


# --- sample_tail ---

def test_sample_tail_returns_last_n():
    entries = make_entries(10)
    result = sample_tail(entries, 3)
    assert [e["id"] for e in result] == [7, 8, 9]


def test_sample_tail_n_zero_returns_empty():
    assert sample_tail(make_entries(5), 0) == []


def test_sample_tail_n_exceeds_length_returns_all():
    entries = make_entries(3)
    assert sample_tail(entries, 100) == entries
